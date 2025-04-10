from rest_framework import viewsets, generics, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import datetime, timedelta
import logging

from .models import DoctorAvailability, TimeSlot, Appointment, AppointmentReminder
from .serializers import (
    DoctorAvailabilitySerializer,
    TimeSlotSerializer,
    AppointmentSerializer,
    AppointmentCreateSerializer,
    AppointmentReminderSerializer
)
from .permissions import (
    CanViewAppointments, CanCreateAppointment, CanUpdateAppointment,
    CanDeleteAppointment, CanManageDoctorSchedule, IsAdmin
)
from .authentication import CustomJWTAuthentication

logger = logging.getLogger(__name__)


class DoctorAvailabilityViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing doctor availabilities.
    """
    queryset = DoctorAvailability.objects.all()
    serializer_class = DoctorAvailabilitySerializer
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [CanManageDoctorSchedule]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['doctor_id', 'weekday', 'is_available']
    ordering_fields = ['weekday', 'start_time']
    
    def get_queryset(self):
        """
        Filter availabilities based on user role.
        """
        queryset = DoctorAvailability.objects.all()
        
        # Get user information from authentication
        user_role = getattr(self.request.user, 'role', None)
        user_id = getattr(self.request.user, 'id', None)
        
        # Doctors can only see their own availabilities
        if user_role == 'DOCTOR':
            queryset = queryset.filter(doctor_id=user_id)
        
        return queryset
    
    def perform_create(self, serializer):
        """
        Set doctor_id to the current user's ID if not provided.
        """
        user_role = getattr(self.request.user, 'role', None)
        user_id = getattr(self.request.user, 'id', None)
        
        # If the user is a doctor and doctor_id is not provided, use the user's ID
        if user_role == 'DOCTOR' and 'doctor_id' not in serializer.validated_data:
            serializer.save(doctor_id=user_id)
        else:
            serializer.save()
    
    @action(detail=False, methods=['post'])
    def generate_time_slots(self, request):
        """
        Generate time slots for a doctor based on their availability.
        """
        doctor_id = request.data.get('doctor_id')
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        slot_duration = request.data.get('slot_duration', 30)  # in minutes
        
        if not doctor_id or not start_date or not end_date:
            return Response(
                {"error": "doctor_id, start_date, and end_date are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {"error": "Invalid date format. Use YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get doctor's availabilities
        availabilities = DoctorAvailability.objects.filter(
            doctor_id=doctor_id,
            is_available=True
        )
        
        if not availabilities:
            return Response(
                {"error": "No availabilities found for this doctor"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Generate time slots
        time_slots = []
        current_date = start_date
        
        while current_date <= end_date:
            # Get weekday (0 = Monday, 6 = Sunday)
            weekday = current_date.weekday()
            
            # Find availabilities for this weekday
            day_availabilities = availabilities.filter(weekday=weekday)
            
            for availability in day_availabilities:
                # Convert time to minutes for easier calculation
                start_minutes = availability.start_time.hour * 60 + availability.start_time.minute
                end_minutes = availability.end_time.hour * 60 + availability.end_time.minute
                
                # Generate slots
                current_minutes = start_minutes
                while current_minutes + slot_duration <= end_minutes:
                    slot_start_time = f"{current_minutes // 60:02d}:{current_minutes % 60:02d}"
                    current_minutes += slot_duration
                    slot_end_time = f"{current_minutes // 60:02d}:{current_minutes % 60:02d}"
                    
                    # Check if slot already exists
                    if not TimeSlot.objects.filter(
                        doctor_id=doctor_id,
                        date=current_date,
                        start_time=slot_start_time,
                        end_time=slot_end_time
                    ).exists():
                        # Create time slot
                        time_slot = TimeSlot.objects.create(
                            doctor_id=doctor_id,
                            date=current_date,
                            start_time=slot_start_time,
                            end_time=slot_end_time,
                            is_booked=False
                        )
                        time_slots.append(time_slot)
            
            # Move to next day
            current_date += timedelta(days=1)
        
        # Serialize and return the created time slots
        serializer = TimeSlotSerializer(time_slots, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TimeSlotViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing time slots.
    """
    queryset = TimeSlot.objects.all()
    serializer_class = TimeSlotSerializer
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [CanViewAppointments]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['doctor_id', 'date', 'is_booked']
    ordering_fields = ['date', 'start_time']
    
    def get_queryset(self):
        """
        Filter time slots based on user role and query parameters.
        """
        queryset = TimeSlot.objects.all()
        
        # Get user information from authentication
        user_role = getattr(self.request.user, 'role', None)
        user_id = getattr(self.request.user, 'id', None)
        
        # Doctors can only see their own time slots
        if user_role == 'DOCTOR':
            queryset = queryset.filter(doctor_id=user_id)
        
        # Filter by availability
        available_only = self.request.query_params.get('available', None)
        if available_only == 'true':
            queryset = queryset.filter(is_booked=False)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(date__gte=start_date)
            except ValueError:
                pass
        
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(date__lte=end_date)
            except ValueError:
                pass
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """
        Get available time slots for a specific doctor and date range.
        """
        doctor_id = request.query_params.get('doctor_id')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        queryset = self.get_queryset()
        
        if doctor_id:
            queryset = queryset.filter(doctor_id=doctor_id)
        
        # Only show available slots
        queryset = queryset.filter(is_booked=False)
        
        # Filter by date range
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(date__gte=start_date)
            except ValueError:
                pass
        
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(date__lte=end_date)
            except ValueError:
                pass
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class AppointmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing appointments.
    """
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [CanViewAppointments]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['patient_id', 'doctor_id', 'appointment_date', 'status']
    ordering_fields = ['appointment_date', 'start_time', 'status']
    
    def get_serializer_class(self):
        """
        Use different serializers for different actions.
        """
        if self.action == 'create':
            return AppointmentCreateSerializer
        return AppointmentSerializer
    
    def get_queryset(self):
        """
        Filter appointments based on user role.
        """
        queryset = Appointment.objects.all()
        
        # Get user information from authentication
        user_role = getattr(self.request.user, 'role', None)
        user_id = getattr(self.request.user, 'id', None)
        
        # Patients can only see their own appointments
        if user_role == 'PATIENT':
            queryset = queryset.filter(patient_id=user_id)
        
        # Doctors can only see appointments assigned to them
        elif user_role == 'DOCTOR':
            queryset = queryset.filter(doctor_id=user_id)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(appointment_date__gte=start_date)
            except ValueError:
                pass
        
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(appointment_date__lte=end_date)
            except ValueError:
                pass
        
        return queryset
    
    def perform_create(self, serializer):
        """
        Set patient_id to the current user's ID if not provided.
        """
        user_role = getattr(self.request.user, 'role', None)
        user_id = getattr(self.request.user, 'id', None)
        
        # If the user is a patient and patient_id is not provided, use the user's ID
        if user_role == 'PATIENT' and 'patient_id' not in serializer.validated_data:
            serializer.save(patient_id=user_id)
        else:
            serializer.save()
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Cancel an appointment.
        """
        self.check_object_permissions(request, self.get_object())
        appointment = self.get_object()
        
        # Check if the appointment can be cancelled
        if appointment.status in ['COMPLETED', 'CANCELLED']:
            return Response(
                {"error": f"Cannot cancel an appointment with status '{appointment.status}'"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update appointment status
        appointment.status = 'CANCELLED'
        appointment.save()
        
        # Free up the time slot
        if appointment.time_slot:
            appointment.time_slot.is_booked = False
            appointment.time_slot.save()
        
        serializer = self.get_serializer(appointment)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """
        Mark an appointment as completed.
        """
        appointment = self.get_object()
        
        # Check if the appointment can be completed
        if appointment.status != 'CONFIRMED':
            return Response(
                {"error": f"Cannot complete an appointment with status '{appointment.status}'"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update appointment status
        appointment.status = 'COMPLETED'
        appointment.save()
        
        serializer = self.get_serializer(appointment)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """
        Get upcoming appointments for the current user.
        """
        user_role = getattr(self.request.user, 'role', None)
        user_id = getattr(self.request.user, 'id', None)
        
        # Get today's date
        today = timezone.now().date()
        
        # Filter appointments
        queryset = self.get_queryset().filter(
            appointment_date__gte=today,
            status__in=['PENDING', 'CONFIRMED']
        )
        
        # Order by date and time
        queryset = queryset.order_by('appointment_date', 'start_time')
        
        # Paginate results
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class AppointmentReminderViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing appointment reminders.
    """
    queryset = AppointmentReminder.objects.all()
    serializer_class = AppointmentReminderSerializer
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAdmin]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['appointment', 'reminder_type', 'status']
    ordering_fields = ['scheduled_time', 'status']
    
    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        """
        Send a reminder manually.
        """
        reminder = self.get_object()
        
        # Check if the reminder can be sent
        if reminder.status != 'PENDING':
            return Response(
                {"error": f"Cannot send a reminder with status '{reminder.status}'"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # In a real application, you would send the reminder here
        # For now, we'll just update the status
        reminder.status = 'SENT'
        reminder.sent_at = timezone.now()
        reminder.save()
        
        serializer = self.get_serializer(reminder)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """
        Get pending reminders that are due to be sent.
        """
        # Get current time
        now = timezone.now()
        
        # Filter reminders
        queryset = self.get_queryset().filter(
            status='PENDING',
            scheduled_time__lte=now
        )
        
        # Order by scheduled time
        queryset = queryset.order_by('scheduled_time')
        
        # Paginate results
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
