from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import datetime, timedelta

from .models import DoctorAvailability, TimeSlot, Appointment, AppointmentReminder


@receiver(post_save, sender=DoctorAvailability)
def update_time_slots(sender, instance, created, **kwargs):
    """
    Tự động tạo/cập nhật khung giờ khi lịch làm việc thay đổi.
    """
    if instance.is_available:
        # Tạo khung giờ cho 4 tuần tới
        start_date = timezone.now().date()
        end_date = start_date + timedelta(days=28)

        current_date = start_date
        while current_date <= end_date:
            if current_date.weekday() == instance.weekday:
                # Kiểm tra xem đã có khung giờ chưa
                existing = TimeSlot.objects.filter(
                    doctor_id=instance.doctor_id,
                    date=current_date,
                    start_time=instance.start_time,
                    end_time=instance.end_time
                ).first()

                if not existing:
                    # Tạo khung giờ mới mà không sử dụng trường is_available
                    TimeSlot.objects.create(
                        doctor_id=instance.doctor_id,
                        date=current_date,
                        start_time=instance.start_time,
                        end_time=instance.end_time,
                        availability=instance,
                        location=instance.location
                    )
            current_date += timedelta(days=1)
    else:
        # Nếu lịch làm việc không còn active, hủy các khung giờ chưa được đặt
        TimeSlot.objects.filter(
            availability=instance
        ).delete()


@receiver(post_save, sender=Appointment)
def create_appointment_reminder(sender, instance, created, **kwargs):
    """
    Tự động tạo nhắc nhở cho lịch hẹn.
    """
    if created or instance.status == 'CONFIRMED':
        # Tạo nhắc nhở 24 giờ trước lịch hẹn
        reminder_time = datetime.combine(
            instance.time_slot.date,
            instance.time_slot.start_time,
            tzinfo=timezone.get_current_timezone()
        ) - timedelta(hours=24)

        # Kiểm tra xem đã có nhắc nhở chưa
        existing = AppointmentReminder.objects.filter(
            appointment=instance,
            reminder_type='EMAIL'
        ).first()

        if not existing:
            AppointmentReminder.objects.create(
                appointment=instance,
                reminder_type='EMAIL',
                scheduled_time=reminder_time,
                message=f"Nhắc nhở: Bạn có lịch hẹn khám bệnh vào lúc {instance.time_slot.start_time} ngày {instance.time_slot.date}."
            )
