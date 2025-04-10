from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Q
import logging

from .models import (
    Medication, Prescription, PrescriptionItem,
    Inventory, Dispensing, DispensingItem
)
from .serializers import (
    MedicationSerializer, PrescriptionSerializer, PrescriptionItemSerializer,
    InventorySerializer, DispensingSerializer, DispensingItemSerializer,
    PrescriptionCreateSerializer, DispensingCreateSerializer
)
from .authentication import CustomJWTAuthentication
from .permissions import IsPharmacist, IsDoctor, IsPatient, IsAdmin

logger = logging.getLogger(__name__)


class MedicationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing medications.
    """
    queryset = Medication.objects.all()
    serializer_class = MedicationSerializer
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsPharmacist]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'dosage_form', 'requires_prescription', 'manufacturer']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'category', 'created_at']

    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Search medications by name, description, or category.
        """
        query = request.query_params.get('q', '')
        if not query:
            return Response(
                {"error": "Search query parameter 'q' is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        medications = self.queryset.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__icontains=query)
        )

        page = self.paginate_queryset(medications)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(medications, many=True)
        return Response(serializer.data)


class PrescriptionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing prescriptions.
    """
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsPharmacist | IsDoctor | IsPatient]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['patient_id', 'doctor_id', 'status']
    ordering_fields = ['date_prescribed', 'created_at', 'status']

    def get_serializer_class(self):
        if self.action == 'create':
            return PrescriptionCreateSerializer
        return PrescriptionSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_queryset(self):
        """
        Filter prescriptions based on user role.
        """
        queryset = Prescription.objects.all()

        # Get user information from authentication
        user_role = getattr(self.request.user, 'role', None)
        user_id = getattr(self.request.user, 'id', None)

        # Patients can only see their own prescriptions
        if user_role == 'PATIENT':
            queryset = queryset.filter(patient_id=user_id)

        # Doctors can only see prescriptions they created
        elif user_role == 'DOCTOR':
            queryset = queryset.filter(doctor_id=user_id)

        # Filter by date range
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)

        if start_date:
            queryset = queryset.filter(date_prescribed__gte=start_date)

        if end_date:
            queryset = queryset.filter(date_prescribed__lte=end_date)

        return queryset

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Cancel a prescription.
        """
        prescription = self.get_object()

        # Check if the prescription can be cancelled
        if prescription.status not in ['PENDING', 'PROCESSING']:
            return Response(
                {"error": f"Cannot cancel a prescription with status '{prescription.status}'"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update prescription status
        prescription.status = 'CANCELLED'
        prescription.save()

        serializer = self.get_serializer(prescription)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def pending(self, request):
        """
        Get pending prescriptions.
        """
        queryset = self.get_queryset().filter(status='PENDING')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class PrescriptionItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing prescription items.
    """
    queryset = PrescriptionItem.objects.all()
    serializer_class = PrescriptionItemSerializer
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsPharmacist | IsDoctor]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['prescription', 'medication']

    def get_queryset(self):
        """
        Filter prescription items based on user role.
        """
        queryset = PrescriptionItem.objects.all()

        # Get user information from authentication
        user_role = getattr(self.request.user, 'role', None)
        user_id = getattr(self.request.user, 'id', None)

        # Doctors can only see prescription items they created
        if user_role == 'DOCTOR':
            queryset = queryset.filter(prescription__doctor_id=user_id)

        return queryset


class InventoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing inventory.
    """
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsPharmacist]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['medication', 'batch_number']
    ordering_fields = ['expiry_date', 'quantity', 'created_at']

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """
        Get inventory items with low stock (less than 10 units).
        """
        queryset = self.queryset.filter(quantity__lt=10)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def expiring_soon(self, request):
        """
        Get inventory items expiring within 30 days.
        """
        today = timezone.now().date()
        expiry_threshold = today + timezone.timedelta(days=30)

        queryset = self.queryset.filter(
            expiry_date__gte=today,
            expiry_date__lte=expiry_threshold
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class DispensingViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing dispensing.
    """
    queryset = Dispensing.objects.all()
    serializer_class = DispensingSerializer
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsPharmacist]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['prescription', 'pharmacist_id', 'status']
    ordering_fields = ['date_dispensed', 'created_at', 'status']

    def get_serializer_class(self):
        if self.action == 'create':
            return DispensingCreateSerializer
        return DispensingSerializer

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Cancel a dispensing.
        """
        dispensing = self.get_object()

        # Check if the dispensing can be cancelled
        if dispensing.status != 'PENDING':
            return Response(
                {"error": f"Cannot cancel a dispensing with status '{dispensing.status}'"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update dispensing status
        dispensing.status = 'CANCELLED'
        dispensing.save()

        # Update prescription status
        prescription = dispensing.prescription
        prescription.status = 'PENDING'
        prescription.save()

        # Return inventory items
        for item in dispensing.items.all():
            inventory = item.inventory
            inventory.quantity += item.quantity_dispensed
            inventory.save()

        serializer = self.get_serializer(dispensing)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """
        Mark a dispensing as completed.
        """
        dispensing = self.get_object()

        # Check if the dispensing can be completed
        if dispensing.status != 'PENDING':
            return Response(
                {"error": f"Cannot complete a dispensing with status '{dispensing.status}'"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update dispensing status
        dispensing.status = 'COMPLETED'
        dispensing.save()

        serializer = self.get_serializer(dispensing)
        return Response(serializer.data)


class DispensingItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing dispensing items.
    """
    queryset = DispensingItem.objects.all()
    serializer_class = DispensingItemSerializer
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsPharmacist]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['dispensing', 'prescription_item', 'inventory']

    def get_queryset(self):
        """
        Filter dispensing items based on user role.
        """
        queryset = DispensingItem.objects.all()

        # Get user information from authentication
        user_role = getattr(self.request.user, 'role', None)
        user_id = getattr(self.request.user, 'id', None)

        # Pharmacists can only see dispensing items they created
        if user_role == 'PHARMACIST':
            queryset = queryset.filter(dispensing__pharmacist_id=user_id)

        return queryset
