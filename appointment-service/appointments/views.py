from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import datetime, timedelta
from rest_framework.views import APIView
import logging

from .models import DoctorAvailability, TimeSlot, Appointment, AppointmentReminder, PatientVisit, AppointmentReason
from .serializers import (
    DoctorAvailabilitySerializer,
    TimeSlotSerializer,
    AppointmentSerializer,
    AppointmentCreateSerializer,
    AppointmentReminderSerializer,
    PatientVisitSerializer,
    AppointmentReasonSerializer
)
from .permissions import (
    CanViewAppointments, CanManageDoctorSchedule, IsAdmin
)
from .authentication import CustomJWTAuthentication
from rest_framework.permissions import IsAuthenticated
from .integrations import send_notification

logger = logging.getLogger(__name__)

# Endpoint test đơn giản để kiểm tra xác thực
@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Yêu cầu xác thực nhưng không cần kiểm tra vai trò
def test_endpoint(request):
    """
    Simple test endpoint to verify authentication is working.
    """
    # Log thông tin user để debug
    user = request.user
    user_id = getattr(user, 'id', None) or getattr(user, 'user_id', None)
    user_role = getattr(user, 'role', None)

    logger.info(f"Test endpoint accessed by user: {user_id}, role: {user_role}")

    # Trả về thông tin user và một thông báo thành công đơn giản
    return Response({
        "message": "Authentication successful!",
        "user_id": user_id,
        "role": user_role,
        "email": getattr(user, 'email', None),
        "name": f"{getattr(user, 'first_name', '')} {getattr(user, 'last_name', '')}".strip()
    })


class DoctorAvailabilityViewSet(viewsets.ModelViewSet):
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
    def create_schedule(self, request):
        """
        Tạo lịch làm việc cho bác sĩ và tự động tạo khung giờ khám bệnh.
        Hỗ trợ tạo lịch hàng tuần hoặc lịch cho ngày cụ thể.
        """
        # Log dữ liệu đầu vào để debug
        logger.info(f"create_schedule received data: {request.data}")

        doctor_id = request.data.get('doctor_id')
        schedule_type = request.data.get('schedule_type', 'REGULAR')  # REGULAR, TEMPORARY, DAY_OFF
        weekdays = request.data.get('weekdays', [])  # [0, 1, 2] - Thứ 2, 3, 4
        start_time = request.data.get('start_time')
        end_time = request.data.get('end_time')
        effective_date = request.data.get('effective_date')

        # Kiểm tra dữ liệu đầu vào
        if not doctor_id:
            return Response(
                {"error": "doctor_id là bắt buộc"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if schedule_type == 'REGULAR' and not weekdays:
            return Response(
                {"error": "weekdays là bắt buộc cho lịch thường xuyên"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if schedule_type in ['TEMPORARY', 'DAY_OFF'] and not effective_date:
            return Response(
                {"error": "effective_date là bắt buộc cho lịch tạm thời hoặc nghỉ phép"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if schedule_type != 'DAY_OFF' and (not start_time or not end_time):
            return Response(
                {"error": "start_time và end_time là bắt buộc"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Tạo lịch làm việc
        created_schedules = []

        # Cấu hình tự động tạo khung giờ - mặc định là True
        auto_generate_slots = request.data.get('auto_generate_slots', True)
        # Khoảng thời gian cho việc tạo khung giờ
        slot_duration = request.data.get('slot_duration', 30)  # mặc định 30 phút

        try:
            if schedule_type == 'REGULAR':
                # Tạo lịch làm việc hàng tuần
                for weekday in weekdays:
                    try:
                        # Thử tìm kiếm lịch làm việc đã tồn tại
                        existing_schedule = DoctorAvailability.objects.filter(
                            doctor_id=doctor_id,
                            weekday=weekday,
                            schedule_type='REGULAR'
                        ).first()

                        if existing_schedule:
                            # Cập nhật lịch đã tồn tại
                            existing_schedule.start_time = start_time
                            existing_schedule.end_time = end_time
                            existing_schedule.is_available = True
                            existing_schedule.location = request.data.get('location')
                            existing_schedule.department = request.data.get('department')
                            existing_schedule.room = request.data.get('room')
                            existing_schedule.slot_duration = request.data.get('slot_duration', 30)
                            existing_schedule.max_patients_per_slot = request.data.get('max_patients_per_slot', 1)
                            existing_schedule.notes = request.data.get('notes')
                            existing_schedule.save()
                            schedule = existing_schedule
                        else:
                            # Tạo lịch mới
                            schedule = DoctorAvailability.objects.create(
                                doctor_id=doctor_id,
                                weekday=weekday,
                                start_time=start_time,
                                end_time=end_time,
                                schedule_type='REGULAR',
                                is_available=True,
                                location=request.data.get('location'),
                                department=request.data.get('department'),
                                room=request.data.get('room'),
                                slot_duration=request.data.get('slot_duration', 30),
                                max_patients_per_slot=request.data.get('max_patients_per_slot', 1),
                                notes=request.data.get('notes')
                            )

                        created_schedules.append(schedule)
                    except Exception as e:
                        logger.error(f"Error creating schedule for weekday {weekday}: {str(e)}")
                        return Response(
                            {"error": f"Lỗi khi tạo lịch làm việc cho thứ {weekday + 1}: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR
                        )
            else:
                # Tạo lịch tạm thời hoặc nghỉ phép
                try:
                    effective_date_obj = datetime.strptime(effective_date, '%Y-%m-%d').date()
                    weekday = effective_date_obj.weekday()

                    # Nếu là nghỉ phép, không cần start_time và end_time
                    if schedule_type == 'DAY_OFF':
                        schedule, created = DoctorAvailability.objects.update_or_create(
                            doctor_id=doctor_id,
                            weekday=weekday,
                            effective_date=effective_date_obj,
                            schedule_type='DAY_OFF',
                            defaults={
                                'is_available': False,
                                'notes': request.data.get('notes')
                            }
                        )
                        created_schedules.append(schedule)

                        # Hủy các khung giờ đã tạo trong ngày nghỉ
                        affected_slots = TimeSlot.objects.filter(
                            doctor_id=doctor_id,
                            date=effective_date_obj
                        )

                        # Lấy danh sách lịch hẹn bị ảnh hưởng
                        from django.db.models import Prefetch
                        affected_appointments = Appointment.objects.filter(
                            time_slot__in=affected_slots,
                            status__in=['PENDING', 'CONFIRMED']
                        ).select_related('time_slot')

                        # Xử lý các lịch hẹn bị ảnh hưởng
                        cancelled_appointments = []
                        for appointment in affected_appointments:
                            try:
                                # Đánh dấu lịch hẹn là bị hủy bởi bác sĩ
                                appointment.transition_to(
                                    'CANCELLED',
                                    user_id=getattr(request.user, 'id', None),
                                    notes=f"Bác sĩ nghỉ phép ngày {effective_date_obj}"
                                )

                                # Gửi thông báo cho bệnh nhân
                                from .integrations import send_notification
                                send_notification(
                                    user_id=appointment.patient_id,
                                    notification_type='DOCTOR_CANCELLED',
                                    message=f"Lịch hẹn của bạn vào ngày {appointment.time_slot.date} đã bị hủy do bác sĩ nghỉ phép. Vui lòng đặt lịch hẹn mới."
                                )

                                cancelled_appointments.append(appointment.id)
                            except Exception as e:
                                logger.error(f"Error cancelling appointment {appointment.id}: {str(e)}")

                        # Cập nhật trạng thái các khung giờ
                        affected_slots.update(is_available=False, status='CANCELLED')

                        # Thêm thông tin về các lịch hẹn bị hủy vào response
                        if cancelled_appointments:
                            logger.info(f"Cancelled {len(cancelled_appointments)} appointments due to doctor day off")
                            schedule.notes = (schedule.notes or "") + f"\nHủy {len(cancelled_appointments)} lịch hẹn: {', '.join(map(str, cancelled_appointments))}"
                            schedule.save(update_fields=['notes'])
                    else:
                        # Lịch tạm thời
                        schedule, created = DoctorAvailability.objects.update_or_create(
                            doctor_id=doctor_id,
                            weekday=weekday,
                            start_time=start_time,
                            end_time=end_time,
                            effective_date=effective_date_obj,
                            defaults={
                                'schedule_type': 'TEMPORARY',
                                'is_available': True,
                                'location': request.data.get('location'),
                                'department': request.data.get('department'),
                                'room': request.data.get('room'),
                                'slot_duration': request.data.get('slot_duration', 30),
                                'max_patients_per_slot': request.data.get('max_patients_per_slot', 1),
                                'notes': request.data.get('notes')
                            }
                        )
                        created_schedules.append(schedule)
                except ValueError:
                    return Response(
                        {"error": "Định dạng ngày không hợp lệ. Sử dụng YYYY-MM-DD"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # Tạo khung giờ tự động - mặc định là True
            created_time_slots = []
            if auto_generate_slots and schedule_type != 'DAY_OFF':
                # Xác định khoảng thời gian tạo khung giờ
                if schedule_type == 'REGULAR':
                    # Tạo khung giờ cho 2 tuần tới cho lịch định kỳ
                    start_date = timezone.now().date()
                    end_date = start_date + timedelta(days=14)

                    # Chuẩn bị dữ liệu để tạo khung giờ
                    time_slot_data = {
                        'start_date': start_date.strftime('%Y-%m-%d'),
                        'end_date': end_date.strftime('%Y-%m-%d'),
                        'slot_duration': slot_duration,
                        'location': request.data.get('location'),
                        'department': request.data.get('department'),
                        'room': request.data.get('room'),
                        'max_patients': request.data.get('max_patients_per_slot', 1)
                    }

                    # Gọi hàm tạo khung giờ
                    created_time_slots = self._generate_time_slots_for_schedules(created_schedules, time_slot_data)

                elif schedule_type == 'TEMPORARY':
                    # Tạo khung giờ chỉ cho ngày cụ thể
                    for schedule in created_schedules:
                        slots = self._create_time_slots_for_date(
                            doctor_id=schedule.doctor_id,
                            date=schedule.effective_date,
                            start_time=schedule.start_time,
                            end_time=schedule.end_time,
                            slot_duration=slot_duration,
                            availability=schedule,
                            location=schedule.location,
                            department=schedule.department,
                            room=schedule.room,
                            max_patients=schedule.max_patients_per_slot
                        )
                        created_time_slots.extend(slots)

            # Trả về kết quả
            response_data = {
                "schedules": self.get_serializer(created_schedules, many=True).data,
                "time_slots_created": len(created_time_slots),
                "auto_generated": auto_generate_slots
            }

            # Thêm thông tin chi tiết về khung giờ đã tạo nếu có
            if created_time_slots and len(created_time_slots) > 0:
                response_data["time_slots"] = TimeSlotSerializer(created_time_slots[:10], many=True).data
                if len(created_time_slots) > 10:
                    response_data["time_slots_note"] = f"Showing 10 of {len(created_time_slots)} created time slots"

            return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Error in create_schedule: {str(e)}")
            return Response(
                {"error": f"Lỗi khi tạo lịch làm việc: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _generate_time_slots_for_schedules(self, schedules, data):
        """
        Tạo khung giờ từ lịch làm việc
        """
        slot_duration = data.get('slot_duration', 30)  # in minutes
        created_slots = []

        for schedule in schedules:
            # Nếu là lịch thường xuyên, tạo khung giờ cho khoảng thời gian
            if schedule.schedule_type == 'REGULAR':
                start_date = data.get('start_date')
                end_date = data.get('end_date')

                if not start_date or not end_date:
                    continue

                try:
                    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                except ValueError:
                    logger.error(f"Invalid date format: start_date={start_date}, end_date={end_date}")
                    continue

                # Tạo khung giờ cho các ngày trong khoảng
                current_date = start_date
                while current_date <= end_date:
                    # Chỉ tạo khung giờ cho ngày trùng với weekday của lịch
                    if current_date.weekday() == schedule.weekday:
                        try:
                            slots = self._create_time_slots_for_date(
                                doctor_id=schedule.doctor_id,
                                date=current_date,
                                start_time=schedule.start_time,
                                end_time=schedule.end_time,
                                slot_duration=slot_duration,
                                availability=schedule,
                                location=schedule.location,
                                department=schedule.department,
                                room=schedule.room,
                                max_patients=schedule.max_patients_per_slot
                            )
                            created_slots.extend(slots)
                        except Exception as e:
                            logger.error(f"Error creating time slots for date {current_date}: {str(e)}")
                    current_date += timedelta(days=1)
            # Nếu là lịch tạm thời, chỉ tạo khung giờ cho ngày cụ thể
            elif schedule.schedule_type == 'TEMPORARY' and schedule.effective_date:
                try:
                    slots = self._create_time_slots_for_date(
                        doctor_id=schedule.doctor_id,
                        date=schedule.effective_date,
                        start_time=schedule.start_time,
                        end_time=schedule.end_time,
                        slot_duration=slot_duration,
                        availability=schedule,
                        location=schedule.location,
                        department=schedule.department,
                        room=schedule.room,
                        max_patients=schedule.max_patients_per_slot
                    )
                    created_slots.extend(slots)
                except Exception as e:
                    logger.error(f"Error creating time slots for date {schedule.effective_date}: {str(e)}")

        return created_slots

    def _create_time_slots_for_date(self, doctor_id, date, start_time, end_time, slot_duration,
                                   availability=None, location=None, department=None, room=None, max_patients=1):
        """
        Tạo khung giờ cho một ngày cụ thể sử dụng bulk_create để tối ưu hóa database queries
        """
        # Đảm bảo start_time và end_time là đối tượng time
        from datetime import datetime, time

        # Nếu start_time là chuỗi, chuyển đổi nó thành đối tượng time
        if isinstance(start_time, str):
            try:
                start_time = datetime.strptime(start_time, '%H:%M').time()
            except ValueError:
                # Log lỗi và trả về danh sách rỗng
                logger.error(f"Invalid start_time format: {start_time}")
                return []

        # Nếu end_time là chuỗi, chuyển đổi nó thành đối tượng time
        if isinstance(end_time, str):
            try:
                end_time = datetime.strptime(end_time, '%H:%M').time()
            except ValueError:
                # Log lỗi và trả về danh sách rỗng
                logger.error(f"Invalid end_time format: {end_time}")
                return []

        # Convert time to minutes for easier calculation
        start_minutes = start_time.hour * 60 + start_time.minute
        end_minutes = end_time.hour * 60 + end_time.minute

        # Generate slots
        current_minutes = start_minutes
        created_slots = []
        slots_to_create = []
        slot_times = []

        # Đầu tiên, tạo danh sách tất cả các khung giờ cần tạo
        while current_minutes + slot_duration <= end_minutes:
            slot_start_time = f"{current_minutes // 60:02d}:{current_minutes % 60:02d}"
            current_minutes += slot_duration
            slot_end_time = f"{current_minutes // 60:02d}:{current_minutes % 60:02d}"

            # Lưu lại thời gian để kiểm tra sau
            slot_times.append((slot_start_time, slot_end_time))

        # Kiểm tra các khung giờ đã tồn tại
        existing_slots = {}
        if slot_times:
            for slot in TimeSlot.objects.filter(
                doctor_id=doctor_id,
                date=date,
                start_time__in=[st for st, _ in slot_times],
                end_time__in=[et for _, et in slot_times]
            ):
                # Dùng tuple (start_time, end_time) làm key để tìm kiếm nhanh
                key = (str(slot.start_time)[:5], str(slot.end_time)[:5])
                existing_slots[key] = slot
                if slot.is_available:
                    created_slots.append(slot)

        # Tạo các slot mới chưa tồn tại
        for start_time_str, end_time_str in slot_times:
            key = (start_time_str, end_time_str)
            if key not in existing_slots:
                slots_to_create.append(
                    TimeSlot(
                        doctor_id=doctor_id,
                        date=date,
                        start_time=start_time_str,
                        end_time=end_time_str,
                        is_available=True,
                        status='AVAILABLE',
                        availability=availability,
                        location=location,
                        department=department,
                        room=room,
                        duration=slot_duration,
                        max_patients=max_patients,
                        current_patients=0
                    )
                )

        # Tạo hàng loạt các time slot mới nếu có
        if slots_to_create:
            created_bulk = TimeSlot.objects.bulk_create(slots_to_create)
            created_slots.extend(created_bulk)

        return created_slots

    @action(detail=False, methods=['post'])
    def generate_time_slots(self, request):
        """
        Tạo khung giờ khám bệnh từ lịch làm việc.

        Hỗ trợ hai chế độ:
        1. Tạo khung giờ cho khoảng thời gian dựa trên lịch làm việc hàng tuần
        2. Tạo khung giờ cho ngày cụ thể với thời gian tùy chỉnh
        """
        doctor_id = request.data.get('doctor_id')
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        slot_duration = request.data.get('slot_duration', 30)  # in minutes
        specific_dates = request.data.get('specific_dates', None)  # Format: [{date: '2023-05-01', start_time: '09:00', end_time: '12:00'}, ...]

        if not doctor_id:
            return Response(
                {"error": "doctor_id là bắt buộc"},
                status=status.HTTP_400_BAD_REQUEST
            )

        time_slots = []

        # Chế độ 1: Tạo khung giờ cho ngày cụ thể với thời gian tùy chỉnh
        if specific_dates:
            try:
                for date_info in specific_dates:
                    date_str = date_info.get('date')
                    start_time_str = date_info.get('start_time')
                    end_time_str = date_info.get('end_time')

                    if not date_str or not start_time_str or not end_time_str:
                        return Response(
                            {"error": "Mỗi ngày cụ thể phải bao gồm date, start_time và end_time"},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                    try:
                        date = datetime.strptime(date_str, '%Y-%m-%d').date()
                        start_time = datetime.strptime(start_time_str, '%H:%M').time()
                        end_time = datetime.strptime(end_time_str, '%H:%M').time()
                    except ValueError:
                        return Response(
                            {"error": "Định dạng ngày hoặc giờ không hợp lệ. Sử dụng YYYY-MM-DD cho ngày và HH:MM cho giờ"},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                    # Tạo khung giờ cho ngày này
                    slots = self._create_time_slots_for_date(
                        doctor_id=doctor_id,
                        date=date,
                        start_time=start_time,
                        end_time=end_time,
                        slot_duration=slot_duration,
                        location=request.data.get('location'),
                        department=request.data.get('department'),
                        room=request.data.get('room'),
                        max_patients=request.data.get('max_patients', 1)
                    )
                    time_slots.extend(slots)

                # Serialize and return the created time slots
                serializer = TimeSlotSerializer(time_slots, many=True)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response(
                    {"error": f"Lỗi khi tạo khung giờ cho ngày cụ thể: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        # Chế độ 2: Tạo khung giờ cho khoảng thời gian dựa trên lịch làm việc hàng tuần
        if not start_date or not end_date:
            return Response(
                {"error": "start_date và end_date là bắt buộc cho chế độ khoảng thời gian"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {"error": "Định dạng ngày không hợp lệ. Sử dụng YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get doctor's availabilities
        availabilities = DoctorAvailability.objects.filter(
            doctor_id=doctor_id,
            is_available=True,
            schedule_type='REGULAR'
        )

        if not availabilities:
            return Response(
                {"error": "Không tìm thấy lịch làm việc cho bác sĩ này"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Generate time slots
        current_date = start_date

        while current_date <= end_date:
            # Get weekday (0 = Monday, 6 = Sunday)
            weekday = current_date.weekday()

            # Kiểm tra xem có lịch nghỉ phép không
            day_off = DoctorAvailability.objects.filter(
                doctor_id=doctor_id,
                schedule_type='DAY_OFF',
                effective_date=current_date
            ).exists()

            if day_off:
                # Bỏ qua ngày nghỉ
                current_date += timedelta(days=1)
                continue

            # Kiểm tra xem có lịch tạm thời không
            temp_schedules = DoctorAvailability.objects.filter(
                doctor_id=doctor_id,
                schedule_type='TEMPORARY',
                effective_date=current_date,
                is_available=True
            )

            if temp_schedules.exists():
                # Sử dụng lịch tạm thời
                for schedule in temp_schedules:
                    slots = self._create_time_slots_for_date(
                        doctor_id=doctor_id,
                        date=current_date,
                        start_time=schedule.start_time,
                        end_time=schedule.end_time,
                        slot_duration=slot_duration,
                        availability=schedule,
                        location=schedule.location,
                        department=schedule.department,
                        room=schedule.room,
                        max_patients=schedule.max_patients_per_slot
                    )
                    time_slots.extend(slots)
            else:
                # Sử dụng lịch thường xuyên
                day_availabilities = availabilities.filter(weekday=weekday)

                for availability in day_availabilities:
                    slots = self._create_time_slots_for_date(
                        doctor_id=doctor_id,
                        date=current_date,
                        start_time=availability.start_time,
                        end_time=availability.end_time,
                        slot_duration=slot_duration,
                        availability=availability,
                        location=availability.location,
                        department=availability.department,
                        room=availability.room,
                        max_patients=availability.max_patients_per_slot
                    )
                    time_slots.extend(slots)

            # Move to next day
            current_date += timedelta(days=1)

        # Serialize and return the created time slots
        serializer = TimeSlotSerializer(time_slots, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TimeSlotViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing time slots.

    Supports both URL structures:
    - /api/time-slots/
    - /api/appointments/time-slots/
    """
    queryset = TimeSlot.objects.all()
    serializer_class = TimeSlotSerializer
    authentication_classes = [CustomJWTAuthentication]
    # Thay đổi từ CanViewAppointments thành IsAuthenticated để cho phép tất cả người dùng đã xác thực truy cập
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['doctor_id', 'date', 'is_available', 'location']
    ordering_fields = ['date', 'start_time']
    search_fields = ['location']

    def get_queryset(self):
        """
        Filter time slots based on user role and query parameters.
        """
        from datetime import datetime
        from django.utils import timezone
        from django.db.models import Q

        queryset = TimeSlot.objects.all()

        # Get user information from authentication
        user_role = getattr(self.request.user, 'role', None)
        user_id = getattr(self.request.user, 'id', None)

        # Doctors can only see their own time slots
        if user_role == 'DOCTOR':
            queryset = queryset.filter(doctor_id=user_id)

        # Không hiển thị các khung giờ trong quá khứ
        current_datetime = timezone.now()
        current_date = current_datetime.date()
        current_time = current_datetime.time()

        # Lọc các khung giờ trong quá khứ
        queryset = queryset.filter(
            # Ngày lớn hơn ngày hiện tại
            Q(date__gt=current_date) |
            # Hoặc cùng ngày nhưng giờ bắt đầu lớn hơn giờ hiện tại
            Q(date=current_date, start_time__gt=current_time)
        )

        # Filter by availability
        available_only = self.request.query_params.get('available', None)
        if available_only == 'true':
            queryset = queryset.filter(is_available=True)

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

        # Filter by specialty (requires integration with user-service)
        specialty = self.request.query_params.get('specialty', None)
        if specialty:
            # Lấy danh sách bác sĩ thuộc chuyên khoa
            from .integrations import get_doctors_by_specialty
            token = getattr(self.request, 'auth', None)
            doctor_ids = get_doctors_by_specialty(specialty, token)
            if doctor_ids:
                queryset = queryset.filter(doctor_id__in=doctor_ids)
            else:
                # Nếu không tìm thấy bác sĩ nào, trả về queryset rỗng
                queryset = queryset.none()

        # Filter by department
        department = self.request.query_params.get('department', None)
        if department:
            # Lấy danh sách bác sĩ thuộc khoa
            from .integrations import get_doctors_by_department
            token = getattr(self.request, 'auth', None)
            doctor_ids = get_doctors_by_department(department, token)
            if doctor_ids:
                queryset = queryset.filter(doctor_id__in=doctor_ids)
            else:
                # Nếu không tìm thấy bác sĩ nào, trả về queryset rỗng
                queryset = queryset.none()

        # Filter by weekday
        weekday = self.request.query_params.get('weekday', None)
        if weekday is not None:
            try:
                weekday = int(weekday)
                # Lọc các khung giờ có ngày thuộc weekday
                queryset = queryset.filter(date__week_day=(weekday % 7) + 1)  # Django uses 1-7 for week_day
            except ValueError:
                pass

        # Filter by location (search)
        location = self.request.query_params.get('location', None)
        if location:
            queryset = queryset.filter(location__icontains=location)

        return queryset

    @action(detail=False, methods=['get'])
    def available(self, request):
        """
        Get available time slots for a specific doctor and date range.
        """
        doctor_id = request.query_params.get('doctor_id')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        # Sử dụng get_queryset để đảm bảo áp dụng các bộ lọc chung
        # bao gồm lọc các khung giờ trong quá khứ
        queryset = self.get_queryset()

        if doctor_id:
            queryset = queryset.filter(doctor_id=doctor_id)

        # Only show available slots
        queryset = queryset.filter(is_available=True)

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

    Supports both URL structures:
    - /api/appointments/
    - /api/appointments/appointments/ (nested)
    """
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [CanViewAppointments]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['patient_id', 'time_slot__doctor_id', 'time_slot__date', 'status']
    ordering_fields = ['time_slot__date', 'time_slot__start_time', 'status']

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
            queryset = queryset.filter(time_slot__doctor_id=user_id)

        # Filter by date range
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)

        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(time_slot__date__gte=start_date)
            except ValueError:
                pass

        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(time_slot__date__lte=end_date)
            except ValueError:
                pass

        return queryset

    def perform_create(self, serializer):
        """
        Set patient_id to the current user's ID if not provided.
        """
        user_role = getattr(self.request.user, 'role', None)
        user_id = getattr(self.request.user, 'id', None)

        # Save the appointment and notify
        if user_role == 'PATIENT' and 'patient_id' not in serializer.validated_data:
            appointment = serializer.save(patient_id=user_id)
        else:
            appointment = serializer.save()

        # Send notification for created appointment
        from .integrations import send_appointment_notification
        send_appointment_notification(appointment, 'CREATED')

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Cancel an appointment.

        Không cho phép hủy lịch hẹn trong vòng 24 giờ trước giờ hẹn,
        trừ khi người hủy là bác sĩ hoặc admin.
        """
        self.check_object_permissions(request, self.get_object())
        appointment = self.get_object()

        # Lấy lý do hủy từ request
        notes = request.data.get('notes', '')
        user_id = getattr(self.request.user, 'id', None)
        user_role = getattr(self.request.user, 'role', None)

        # Kiểm tra thời gian hủy lịch
        from django.utils import timezone
        import datetime

        # Tính thời gian còn lại đến lịch hẹn
        appointment_time = datetime.datetime.combine(
            appointment.time_slot.date,
            appointment.time_slot.start_time,
            tzinfo=timezone.get_current_timezone()
        )
        time_until_appointment = appointment_time - timezone.now()
        hours_until_appointment = time_until_appointment.total_seconds() / 3600

        # Nếu thời gian còn lại ít hơn 24 giờ và người dùng không phải bác sĩ hoặc admin
        if hours_until_appointment < 24 and user_role not in ['DOCTOR', 'ADMIN']:
            return Response(
                {"error": "Không thể hủy lịch hẹn trong vòng 24 giờ trước giờ hẹn. Vui lòng liên hệ trực tiếp với phòng khám."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Sử dụng phương thức transition_to mới
            appointment.transition_to('CANCELLED', user_id=user_id, notes=notes)

            # Gửi thông báo
            from .integrations import send_notification
            send_notification(
                user_id=appointment.patient_id,
                notification_type='APPOINTMENT_CANCELLED',
                message=f"Lịch hẹn của bạn vào ngày {appointment.time_slot.date} lúc {appointment.time_slot.start_time} đã bị hủy."
            )

            # Nếu bác sĩ hủy lịch hẹn, gửi thông báo với lý do
            if user_role == 'DOCTOR':
                send_notification(
                    user_id=appointment.patient_id,
                    notification_type='DOCTOR_CANCELLED',
                    message=f"Bác sĩ đã hủy lịch hẹn của bạn vào ngày {appointment.time_slot.date}. Lý do: {notes}"
                )

            serializer = self.get_serializer(appointment)
            return Response(serializer.data)

        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """
        Mark an appointment as completed.
        """
        appointment = self.get_object()

        # Lấy ghi chú từ request
        notes = request.data.get('notes', '')
        user_id = getattr(self.request.user, 'id', None)

        try:
            # Sử dụng phương thức transition_to mới
            appointment.transition_to('COMPLETED', user_id=user_id, notes=notes)

            # Gửi thông báo
            from .integrations import send_notification
            send_notification(
                user_id=appointment.patient_id,
                notification_type='APPOINTMENT_COMPLETED',
                message=f"Lịch hẹn của bạn vào ngày {appointment.time_slot.date} đã hoàn thành."
            )

            serializer = self.get_serializer(appointment)
            return Response(serializer.data)

        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def reschedule(self, request, pk=None):
        """
        Reschedule an appointment to a new time slot.

        Cho phép đổi lịch hẹn thay vì hủy hoàn toàn.
        Nếu thời gian còn lại ít hơn 24 giờ, chỉ bác sĩ hoặc admin mới có thể đổi lịch.
        """
        appointment = self.get_object()

        # Lấy thông tin từ request
        new_time_slot_id = request.data.get('time_slot_id')
        notes = request.data.get('notes', '')
        user_id = getattr(self.request.user, 'id', None)
        user_role = getattr(self.request.user, 'role', None)

        # Kiểm tra thời gian đổi lịch
        from django.utils import timezone
        import datetime

        # Tính thời gian còn lại đến lịch hẹn
        appointment_time = datetime.datetime.combine(
            appointment.time_slot.date,
            appointment.time_slot.start_time,
            tzinfo=timezone.get_current_timezone()
        )
        time_until_appointment = appointment_time - timezone.now()
        hours_until_appointment = time_until_appointment.total_seconds() / 3600

        # Nếu thời gian còn lại ít hơn 24 giờ và người dùng không phải bác sĩ hoặc admin
        if hours_until_appointment < 24 and user_role not in ['DOCTOR', 'ADMIN']:
            return Response(
                {"error": "Không thể đổi lịch hẹn trong vòng 24 giờ trước giờ hẹn. Vui lòng liên hệ trực tiếp với phòng khám."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not new_time_slot_id:
            return Response(
                {"error": "time_slot_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Lấy time slot mới
            new_time_slot = TimeSlot.objects.get(id=new_time_slot_id)

            # Kiểm tra xem time slot có khả dụng không
            if not new_time_slot.is_available:
                # Tìm các khung giờ thay thế
                doctor_id = new_time_slot.doctor_id
                date = new_time_slot.date

                # Tìm các khung giờ trống của bác sĩ trong ngày đó
                alternative_slots_same_day = TimeSlot.objects.filter(
                    doctor_id=doctor_id,
                    date=date,
                    is_available=True
                ).order_by('start_time')[:5]

                # Nếu không có khung giờ trống trong ngày, tìm các ngày gần nhất
                if not alternative_slots_same_day.exists():
                    # Tìm các khung giờ trống trong 7 ngày tiếp theo
                    next_week = date + timedelta(days=7)
                    alternative_slots = TimeSlot.objects.filter(
                        doctor_id=doctor_id,
                        date__gt=date,
                        date__lte=next_week,
                        is_available=True
                    ).order_by('date', 'start_time')[:10]
                else:
                    alternative_slots = alternative_slots_same_day

                # Serialize các khung giờ thay thế
                serializer = TimeSlotSerializer(alternative_slots, many=True, context={'request': request})

                return Response({
                    "error": "Khung giờ đã chọn không còn khả dụng",
                    "alternatives": serializer.data,
                    "message": "Vui lòng chọn một trong các khung giờ thay thế sau"
                }, status=status.HTTP_400_BAD_REQUEST)

            # Kiểm tra xem time slot mới có phải trong tương lai không
            new_appointment_time = datetime.datetime.combine(
                new_time_slot.date,
                new_time_slot.start_time,
                tzinfo=timezone.get_current_timezone()
            )
            if new_appointment_time < timezone.now():
                return Response(
                    {"error": "Cannot reschedule to a past time"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Lưu time slot cũ để trả lại sau
            old_time_slot = appointment.time_slot

            # Đánh dấu lịch hẹn là đã đổi lịch
            appointment.transition_to('RESCHEDULED', user_id=user_id, notes=notes)

            # Tạo lịch hẹn mới với time slot mới
            new_appointment = Appointment.objects.create(
                patient_id=appointment.patient_id,
                time_slot=new_time_slot,
                status='PENDING',  # Lịch hẹn mới sẽ có trạng thái PENDING
                appointment_type=appointment.appointment_type,
                priority=appointment.priority,
                reason_text=appointment.reason_text,
                reason_category=appointment.reason_category,
                is_recurring=appointment.is_recurring,
                recurrence_pattern=appointment.recurrence_pattern,
                recurrence_end_date=appointment.recurrence_end_date,
                is_follow_up=appointment.is_follow_up,
                medical_record_id=appointment.medical_record_id,
                insurance_id=appointment.insurance_id,
                created_by=user_id,
                notes=f"Rescheduled from appointment {appointment.id}"
            )

            # Đánh dấu time slot mới là đã đặt
            new_time_slot.add_patient()

            # Tạo các nhắc nhở cho lịch hẹn mới
            from .serializers import AppointmentCreateSerializer
            serializer_instance = AppointmentCreateSerializer()
            serializer_instance._create_appointment_reminders(new_appointment, new_time_slot)

            # Gửi thông báo
            from .integrations import send_notification
            send_notification(
                user_id=appointment.patient_id,
                notification_type='APPOINTMENT_RESCHEDULED',
                message=f"Lịch hẹn của bạn đã được đổi sang ngày {new_time_slot.date} lúc {new_time_slot.start_time}."
            )

            # Nếu bác sĩ đổi lịch hẹn, gửi thông báo với lý do
            if user_role == 'DOCTOR':
                send_notification(
                    user_id=appointment.patient_id,
                    notification_type='DOCTOR_RESCHEDULED',
                    message=f"Bác sĩ đã đổi lịch hẹn của bạn sang ngày {new_time_slot.date} lúc {new_time_slot.start_time}. Lý do: {notes}"
                )

            # Trả về thông tin lịch hẹn mới
            serializer = self.get_serializer(new_appointment)
            return Response(serializer.data)

        except TimeSlot.DoesNotExist:
            return Response(
                {"error": "Time slot not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

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
            time_slot__date__gte=today,
            status__in=['PENDING', 'CONFIRMED']
        )

        # Order by date and time
        queryset = queryset.order_by('time_slot__date', 'time_slot__start_time')

        # Paginate results
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def create_follow_up(self, request, pk=None):
        """
        Tạo lịch hẹn tái khám từ lịch hẹn hiện tại
        """
        # Lấy lịch hẹn gốc
        parent_appointment = self.get_object()

        # Kiểm tra quyền truy cập
        self.check_object_permissions(request, parent_appointment)

        # Lấy thông tin từ request
        time_slot_id = request.data.get('time_slot_id')
        follow_up_date = request.data.get('follow_up_date')
        follow_up_time = request.data.get('follow_up_time')
        notes = request.data.get('notes', '')
        reason_text = request.data.get('reason_text', 'Tái khám')
        user_id = getattr(request.user, 'id', None)

        # Kiểm tra các trường bắt buộc
        if not time_slot_id and not (follow_up_date and follow_up_time):
            return Response(
                {"error": "Phải cung cấp time_slot_id hoặc cả follow_up_date và follow_up_time"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Nếu cung cấp time_slot_id, sử dụng nó
            if time_slot_id:
                time_slot = TimeSlot.objects.get(id=time_slot_id)

                # Kiểm tra xem time slot có khả dụng không
                if not time_slot.is_available:
                    # Tìm các khung giờ thay thế
                    doctor_id = time_slot.doctor_id
                    date = time_slot.date

                    # Tìm các khung giờ trống của bác sĩ trong ngày đó
                    alternative_slots_same_day = TimeSlot.objects.filter(
                        doctor_id=doctor_id,
                        date=date,
                        is_available=True
                    ).order_by('start_time')[:5]

                    # Nếu không có khung giờ trống trong ngày, tìm các ngày gần nhất
                    if not alternative_slots_same_day.exists():
                        # Tìm các khung giờ trống trong 7 ngày tiếp theo
                        next_week = date + timedelta(days=7)
                        alternative_slots = TimeSlot.objects.filter(
                            doctor_id=doctor_id,
                            date__gt=date,
                            date__lte=next_week,
                            is_available=True
                        ).order_by('date', 'start_time')[:10]
                    else:
                        alternative_slots = alternative_slots_same_day

                    # Serialize các khung giờ thay thế
                    from .serializers import TimeSlotSerializer
                    serializer = TimeSlotSerializer(alternative_slots, many=True, context={'request': request})

                    return Response({
                        "error": "Khung giờ đã chọn không còn khả dụng",
                        "alternatives": serializer.data,
                        "message": "Vui lòng chọn một trong các khung giờ thay thế sau"
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Nếu không cung cấp time_slot_id, tạo time slot mới
                from datetime import datetime

                # Chuyển đổi chuỗi ngày và giờ thành đối tượng date và time
                try:
                    follow_up_date_obj = datetime.strptime(follow_up_date, '%Y-%m-%d').date()
                    follow_up_time_obj = datetime.strptime(follow_up_time, '%H:%M').time()

                    # Tính end_time (mặc định là 30 phút sau start_time)
                    from datetime import timedelta
                    follow_up_datetime = datetime.combine(follow_up_date_obj, follow_up_time_obj)
                    end_datetime = follow_up_datetime + timedelta(minutes=30)
                    follow_up_end_time = end_datetime.time()
                except ValueError:
                    return Response(
                        {"error": "Invalid date or time format. Use YYYY-MM-DD for date and HH:MM for time"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Kiểm tra xem đã có time slot nào vào thởi điểm này chưa
                existing_slots = TimeSlot.objects.filter(
                    doctor_id=parent_appointment.doctor_id,
                    date=follow_up_date_obj,
                    start_time=follow_up_time_obj
                )

                if existing_slots.exists():
                    time_slot = existing_slots.first()

                    # Kiểm tra xem time slot có khả dụng không
                    if not time_slot.is_available:
                        return Response(
                            {"error": "Khung giờ đã chọn không còn khả dụng"},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                else:
                    # Tạo time slot mới
                    time_slot = TimeSlot.objects.create(
                        doctor_id=parent_appointment.doctor_id,
                        date=follow_up_date_obj,
                        start_time=follow_up_time_obj,
                        end_time=follow_up_end_time,
                        is_available=True,
                        status='AVAILABLE',
                        max_patients=1,
                        current_patients=0,
                        department=getattr(parent_appointment.time_slot, 'department', None),
                        location=getattr(parent_appointment.time_slot, 'location', None),
                        room=getattr(parent_appointment.time_slot, 'room', None)
                    )

            # Tạo lịch hẹn tái khám
            follow_up_appointment = Appointment.objects.create(
                patient_id=parent_appointment.patient_id,
                time_slot=time_slot,
                status='PENDING',
                appointment_type='FOLLOW_UP',
                priority=parent_appointment.priority,
                reason_text=reason_text,
                reason_category=parent_appointment.reason_category,
                is_recurring=False,
                recurrence_pattern=None,
                recurrence_end_date=None,
                is_follow_up=True,
                follow_up_to=parent_appointment.id,
                medical_record_id=parent_appointment.medical_record_id,
                insurance_id=parent_appointment.insurance_id,
                created_by=user_id,
                notes=notes or f"Tái khám từ lịch hẹn {parent_appointment.id}"
            )

            # Đánh dấu time slot là đã đặt
            time_slot.add_patient()

            # Tạo các nhắc nhở cho lịch hẹn mới
            from .serializers import AppointmentCreateSerializer
            serializer_instance = AppointmentCreateSerializer()
            serializer_instance._create_appointment_reminders(follow_up_appointment, time_slot)

            # Gửi thông báo
            from .integrations import send_appointment_notification
            send_appointment_notification(
                appointment=follow_up_appointment,
                notification_type='CREATED',
                message=f"Lịch hẹn tái khám của bạn đã được tạo vào ngày {time_slot.date.strftime('%d/%m/%Y')} lúc {time_slot.start_time.strftime('%H:%M')}."
            )

            # Trả về thông tin lịch hẹn mới
            serializer = self.get_serializer(follow_up_appointment)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except TimeSlot.DoesNotExist:
            return Response(
                {"error": "Không tìm thấy khung giờ với ID đã cung cấp"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def patient_appointments(self, request):
        """
        Get all appointments for the current patient.
        This endpoint specifically addresses the API call to /api/appointments/patient-appointments/
        """
        user_role = getattr(self.request.user, 'role', None)
        user_id = getattr(self.request.user, 'id', None)

        # Log user information for debugging
        logger.info(f"Patient appointments requested by user: {user_id}, role: {user_role}")

        # Only allow patients to use this endpoint
        if user_role != 'PATIENT':
            logger.warning(f"Non-patient user {user_id} tried to access patient appointments")
            return Response(
                {"error": "Only patients can access this endpoint"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Get all appointments for this patient
        queryset = Appointment.objects.filter(patient_id=user_id)

        # Allow filtering by status
        appointment_status = request.query_params.get('status', None)
        if appointment_status:
            queryset = queryset.filter(status=appointment_status.upper())

        # Order by date (newest first) and time
        queryset = queryset.order_by('-time_slot__date', 'time_slot__start_time')

        # Paginate results
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class PatientVisitViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing patient visits (check-ins).

    Supports both URL structures:
    - /api/patient-visits/
    - /api/appointments/visits/
    """
    queryset = PatientVisit.objects.all()
    serializer_class = PatientVisitSerializer
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [CanViewAppointments]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['appointment', 'status', 'checked_in_at']
    ordering_fields = ['checked_in_at', 'status']

    def get_queryset(self):
        """
        Filter visits based on user role.
        """
        queryset = PatientVisit.objects.all()

        # Get user information from authentication
        user_role = getattr(self.request.user, 'role', None)
        user_id = getattr(self.request.user, 'id', None)

        # Patients can only see their own visits
        if user_role == 'PATIENT':
            queryset = queryset.filter(appointment__patient_id=user_id)

        # Doctors can only see visits for their appointments
        elif user_role == 'DOCTOR':
            queryset = queryset.filter(appointment__time_slot__doctor_id=user_id)

        return queryset

    @action(detail=False, methods=['post'])
    def check_in(self, request):
        """
        Check in a patient for their appointment.
        """
        appointment_id = request.data.get('appointment_id')
        notes = request.data.get('notes', '')

        if not appointment_id:
            return Response(
                {"error": "appointment_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Get the appointment
            appointment = Appointment.objects.get(id=appointment_id)

            # Check if the appointment is today
            today = timezone.now().date()
            if appointment.time_slot.date != today:
                return Response(
                    {"error": "Can only check in for appointments scheduled today"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if the appointment is in the right status
            if appointment.status not in ['CONFIRMED', 'PENDING']:
                return Response(
                    {"error": f"Cannot check in for appointment with status {appointment.status}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if a visit already exists
            if hasattr(appointment, 'visit'):
                return Response(
                    {"error": "Patient is already checked in for this appointment"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create the visit
            visit = PatientVisit.objects.create(
                appointment=appointment,
                status='WAITING',
                checked_in_at=timezone.now(),
                checked_in_by=getattr(request.user, 'id', None),
                notes=notes
            )

            # Update appointment status
            appointment.transition_to('CHECKED_IN', user_id=getattr(request.user, 'id', None), notes=f"Checked in at {timezone.now()}")

            # Return the visit data
            serializer = self.get_serializer(visit)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Appointment.DoesNotExist:
            return Response(
                {"error": "Appointment not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """
        Update the status of a patient visit.
        """
        visit = self.get_object()
        new_status = request.data.get('status')
        notes = request.data.get('notes', '')

        if not new_status:
            return Response(
                {"error": "status is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if the status is valid
        valid_statuses = [choice[0] for choice in PatientVisit.VISIT_STATUS_CHOICES]
        if new_status not in valid_statuses:
            return Response(
                {"error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update the visit status
        visit.status = new_status

        # Update additional fields based on status
        if new_status == 'WITH_NURSE':
            visit.nurse_id = getattr(request.user, 'id', None)
        elif new_status == 'WITH_DOCTOR':
            visit.doctor_start_time = timezone.now()
            # Update appointment status
            visit.appointment.transition_to('IN_PROGRESS', user_id=getattr(request.user, 'id', None))
        elif new_status == 'COMPLETED':
            visit.doctor_end_time = timezone.now()
            # Calculate waiting time
            if visit.checked_in_at and visit.doctor_start_time:
                waiting_minutes = (visit.doctor_start_time - visit.checked_in_at).total_seconds() / 60
                visit.waiting_time = int(waiting_minutes)
            # Update appointment status
            visit.appointment.transition_to('COMPLETED', user_id=getattr(request.user, 'id', None))

        # Add notes if provided
        if notes:
            visit.notes = (visit.notes or "") + f"\n[{timezone.now().strftime('%Y-%m-%d %H:%M')}] {notes}"

        visit.save()

        serializer = self.get_serializer(visit)
        return Response(serializer.data)


class AppointmentReminderViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing appointment reminders.

    Supports both URL structures:
    - /api/appointment-reminders/
    - /api/appointments/reminders/
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


class AppointmentReasonViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing appointment reasons.
    """
    queryset = AppointmentReason.objects.all()
    serializer_class = AppointmentReasonSerializer
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [CanViewAppointments]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['department', 'priority', 'is_active']
    ordering_fields = ['priority', 'name']
    search_fields = ['name', 'description']


@api_view(['GET'])
def appointment_types(request):
    """
    API endpoint for getting appointment types.
    """
    # Xác thực người dùng
    if not request.user.is_authenticated:
        return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

    # Lấy danh sách loại khám bệnh từ model Appointment
    appointment_types = [
        {
            'id': choice[0],
            'code': choice[0],
            'name': choice[1],
            'price': _get_price_for_appointment_type(choice[0])
        }
        for choice in Appointment.APPOINTMENT_TYPE_CHOICES
    ]
    return Response(appointment_types)


@api_view(['GET'])
def priorities(request):
    """
    API endpoint for getting priorities.
    """
    # Xác thực người dùng
    if not request.user.is_authenticated:
        return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

    # Lấy danh sách mức độ ưu tiên từ model Appointment
    priorities = [
        {
            'id': str(choice[0]),
            'code': str(choice[0]),
            'name': choice[1],
            'description': _get_description_for_priority(choice[0])
        }
        for choice in Appointment.PRIORITY_CHOICES
    ]
    return Response(priorities)


@api_view(['GET'])
def locations(request):
    """
    API endpoint for getting locations.
    """
    # Xác thực người dùng
    if not request.user.is_authenticated:
        return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

    # Trong thực tế, dữ liệu này sẽ được lấy từ database
    locations = [
        {
            'id': 1,
            'name': "Phòng khám chính",
            'address': "Tầng 1, Tòa nhà A, 123 Đường ABC, Quận 1",
            'phone': "028.1234.5678",
            'email': "phongkham@example.com"
        },
        {
            'id': 2,
            'name': "Phòng khám chi nhánh 1",
            'address': "Tầng 2, Tòa nhà B, 456 Đường XYZ, Quận 2",
            'phone': "028.2345.6789",
            'email': "chinhanh1@example.com"
        },
        {
            'id': 3,
            'name': "Phòng khám chi nhánh 2",
            'address': "Tầng 3, Tòa nhà C, 789 Đường DEF, Quận 3",
            'phone': "028.3456.7890",
            'email': "chinhanh2@example.com"
        },
    ]
    return Response(locations)


def _get_price_for_appointment_type(appointment_type):
    """
    Get price for appointment type.
    """
    # Giá dịch vụ mặc định (trong thực tế sẽ lấy từ cấu hình hoặc bảng giá)
    base_price = 200000  # 200k VND cho khám thông thường

    # Điều chỉnh giá theo loại lịch hẹn
    if appointment_type == 'FOLLOW_UP':
        return int(base_price * 0.7)  # Giảm 30% cho tái khám
    elif appointment_type == 'EMERGENCY':
        return int(base_price * 1.5)  # Tăng 50% cho cấp cứu
    elif appointment_type == 'CONSULTATION':
        return int(base_price * 0.8)  # Giảm 20% cho tư vấn
    elif appointment_type == 'TELEHEALTH':
        return int(base_price * 0.9)  # Giảm 10% cho khám từ xa
    elif appointment_type == 'IN_PERSON':
        return int(base_price * 1.1)  # Tăng 10% cho khám trực tiếp
    else:
        return base_price


def _get_description_for_priority(priority):
    """
    Get description for priority.
    """
    if priority == 0:
        return "Khám thông thường, không cần ưu tiên đặc biệt"
    elif priority == 1:
        return "Ưu tiên khám trước cho các trường hợp đặc biệt"
    elif priority == 2:
        return "Khẩn cấp, cần khám ngay lập tức"
    else:
        return ""


@api_view(['GET'])
def doctor_working_days(request):
    """
    API endpoint for getting doctor working days.
    """
    # Xác thực người dùng
    if not request.user.is_authenticated:
        return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

    doctor_id = request.query_params.get('doctor_id')
    if not doctor_id:
        return Response({"error": "doctor_id is required"}, status=status.HTTP_400_BAD_REQUEST)

    # Lấy lịch làm việc của bác sĩ
    availabilities = DoctorAvailability.objects.filter(
        doctor_id=doctor_id,
        is_available=True
    )

    # Tạo danh sách các ngày trong tuần bác sĩ làm việc
    working_days = []
    for availability in availabilities:
        if availability.weekday not in working_days:
            working_days.append(availability.weekday)

    # Lấy các khung giờ có sẵn
    time_slots = TimeSlot.objects.filter(
        doctor_id=doctor_id,
        is_available=True,
        date__gte=timezone.now().date()
    ).values('date').distinct()

    available_dates = [slot['date'].strftime('%Y-%m-%d') for slot in time_slots]

    # Lấy thông tin chi tiết về lịch làm việc
    availability_details = []
    for availability in availabilities:
        availability_details.append({
            'id': availability.id,
            'weekday': availability.weekday,
            'weekday_name': [
                'Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7', 'Chủ nhật'
            ][availability.weekday],
            'start_time': availability.start_time,
            'end_time': availability.end_time,
            'location': availability.location,
            'department': availability.department,
            'room': availability.room,
            'schedule_type': availability.schedule_type
        })

    return Response({
        "working_days": working_days,
        "available_dates": available_dates,
        "availabilities": availability_details
    })


@api_view(['GET'])
def available_doctors(request):
    """
    API endpoint for getting doctors with available time slots in a date range.

    Query parameters:
    - start_date: Start date in YYYY-MM-DD format (required)
    - end_date: End date in YYYY-MM-DD format (required)
    - specialty: Filter by specialty (optional)
    - department: Filter by department (optional)
    """
    # Xác thực người dùng
    if not request.user.is_authenticated:
        return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

    # Lấy và validate các tham số
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    specialty = request.query_params.get('specialty')
    department = request.query_params.get('department')

    # Nếu không có start_date hoặc end_date, sử dụng ngày hiện tại và 30 ngày sau
    if not start_date:
        start_date_obj = timezone.now().date()
        start_date = start_date_obj.strftime('%Y-%m-%d')
    else:
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {"error": "Invalid start_date format. Use YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST
            )

    if not end_date:
        end_date_obj = start_date_obj + timedelta(days=30)
        end_date = end_date_obj.strftime('%Y-%m-%d')
    else:
        try:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {"error": "Invalid end_date format. Use YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST
            )

    # Log thông tin tìm kiếm
    logger.info(f"Searching for available doctors from {start_date} to {end_date}")
    if specialty:
        logger.info(f"Filtering by specialty: {specialty}")
    if department:
        logger.info(f"Filtering by department: {department}")

    # Tìm các bác sĩ có khung giờ trống trong khoảng thời gian
    available_slots = TimeSlot.objects.filter(
        date__gte=start_date_obj,
        date__lte=end_date_obj,
        is_available=True
    )

    # Lọc theo department nếu có
    if department:
        available_slots = available_slots.filter(department=department)

    # Lấy danh sách ID bác sĩ có lịch trống
    doctor_ids = available_slots.values_list('doctor_id', flat=True).distinct()

    logger.info(f"Found {len(doctor_ids)} doctors with available slots")

    # Lấy thông tin chi tiết về bác sĩ từ user-service
    from .integrations import get_doctors_info
    token = getattr(request, 'auth', None)
    doctors = get_doctors_info(list(doctor_ids), token)

    # Nếu không lấy được thông tin từ user-service, tạo thông tin cơ bản
    if not doctors:
        logger.warning("Could not get doctor information from user-service, using basic info")
        doctors = [{
            'id': doctor_id,
            'name': f'Bác sĩ (ID: {doctor_id})'
        } for doctor_id in doctor_ids]

    # Lọc theo specialty nếu có
    if specialty and doctors:
        doctors = [d for d in doctors if d.get('specialty') == specialty or d.get('specialization') == specialty]
        logger.info(f"After specialty filter: {len(doctors)} doctors")

    # Thêm thông tin về ngày có lịch trống cho mỗi bác sĩ
    for doctor in doctors:
        doctor_id = doctor.get('id')

        # Lấy các ngày có lịch trống
        available_dates = available_slots.filter(
            doctor_id=doctor_id
        ).values_list('date', flat=True).distinct()

        doctor['available_dates'] = [date.strftime('%Y-%m-%d') for date in available_dates]

        # Lấy số lượng khung giờ trống
        doctor['available_slots_count'] = available_slots.filter(doctor_id=doctor_id).count()

        # Lấy thông tin về khoa/phòng làm việc
        departments = available_slots.filter(
            doctor_id=doctor_id
        ).values_list('department', flat=True).distinct()

        doctor['departments'] = list(filter(None, departments))

    logger.info(f"Returning {len(doctors)} available doctors")
    return Response(doctors)


@api_view(['GET'])
def specialties(request):
    """
    API endpoint for getting specialties.
    """
    # Xác thực người dùng
    if not request.user.is_authenticated:
        return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

    # Lấy danh sách chuyên khoa từ user-service
    from .integrations import get_specialties
    token = getattr(request, 'auth', None)
    specialties_list = get_specialties(token)

    # Nếu không lấy được từ user-service, trả về danh sách mẫu
    if not specialties_list:
        specialties_list = [
            {
                'id': 1,
                'code': 'CARDIOLOGY',
                'name': 'Tim mạch',
                'description': 'Chuyên khoa về tim mạch và hệ tuần hoàn'
            },
            {
                'id': 2,
                'code': 'NEUROLOGY',
                'name': 'Thần kinh',
                'description': 'Chuyên khoa về hệ thần kinh'
            },
            {
                'id': 3,
                'code': 'ORTHOPEDICS',
                'name': 'Chỉnh hình',
                'description': 'Chuyên khoa về xương khớp'
            },
            {
                'id': 4,
                'code': 'PEDIATRICS',
                'name': 'Nhi',
                'description': 'Chuyên khoa về trẻ em'
            },
            {
                'id': 5,
                'code': 'DERMATOLOGY',
                'name': 'Da liễu',
                'description': 'Chuyên khoa về da'
            },
        ]

    return Response(specialties_list)


@api_view(['GET'])
def departments(request):
    """
    API endpoint for getting departments.
    """
    # Xác thực người dùng
    if not request.user.is_authenticated:
        return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

    # Lấy danh sách khoa từ user-service
    from .integrations import get_departments
    token = getattr(request, 'auth', None)
    departments_list = get_departments(token)

    # Nếu không lấy được từ user-service, trả về danh sách mẫu
    if not departments_list:
        departments_list = [
            {
                'id': 1,
                'code': 'INTERNAL_MEDICINE',
                'name': 'Khoa Nội',
                'description': 'Khoa Nội tổng hợp'
            },
            {
                'id': 2,
                'code': 'SURGERY',
                'name': 'Khoa Ngoại',
                'description': 'Khoa Ngoại tổng hợp'
            },
            {
                'id': 3,
                'code': 'EMERGENCY',
                'name': 'Khoa Cấp cứu',
                'description': 'Khoa Cấp cứu'
            },
            {
                'id': 4,
                'code': 'OBSTETRICS',
                'name': 'Khoa Sản',
                'description': 'Khoa Sản phụ khoa'
            },
            {
                'id': 5,
                'code': 'PEDIATRICS',
                'name': 'Khoa Nhi',
                'description': 'Khoa Nhi'
            },
        ]

    return Response(departments_list)


@api_view(['GET'])
def patient_insurance(request):
    """
    API endpoint for getting patient insurance information.
    """
    # Xác thực người dùng
    if not request.user.is_authenticated:
        return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

    # Kiểm tra quyền truy cập
    user_role = getattr(request.user, 'role', None)
    user_id = getattr(request.user, 'id', None)

    # Lấy patient_id từ query parameter hoặc từ user hiện tại
    patient_id = request.query_params.get('patient_id', user_id)

    # Nếu không phải PATIENT và không phải ADMIN/DOCTOR, chỉ cho phép xem thông tin của chính mình
    if user_role != 'PATIENT' and user_role not in ['ADMIN', 'DOCTOR'] and str(user_id) != str(patient_id):
        return Response(
            {"error": "Bạn không có quyền xem thông tin bảo hiểm của bệnh nhân khác"},
            status=status.HTTP_403_FORBIDDEN
        )

    # Lấy thông tin bảo hiểm của bệnh nhân
    from .integrations import get_patient_insurance
    token = getattr(request, 'auth', None)
    insurance_list = get_patient_insurance(patient_id, token)

    return Response(insurance_list)


@api_view(['POST'])
def verify_insurance(request):
    """
    API endpoint for verifying insurance coverage for a service.
    """
    # Xác thực người dùng
    if not request.user.is_authenticated:
        return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

    # Lấy thông tin từ request
    insurance_id = request.data.get('insurance_id')
    service_code = request.data.get('service_code')
    amount = request.data.get('amount')

    # Kiểm tra các trường bắt buộc
    if not all([insurance_id, service_code, amount]):
        return Response(
            {"error": "insurance_id, service_code và amount là bắt buộc"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Xác minh bảo hiểm
    from .integrations import verify_insurance as verify_insurance_service
    token = getattr(request, 'auth', None)
    verification_result = verify_insurance_service(insurance_id, service_code, float(amount), token)

    return Response(verification_result)
