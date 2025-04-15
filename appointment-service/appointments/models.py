from django.db import models
from django.utils import timezone


class DoctorAvailability(models.Model):
    """Lịch làm việc của bác sĩ"""
    WEEKDAY_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]

    doctor_id = models.IntegerField(help_text="ID của bác sĩ trong user-service")
    weekday = models.IntegerField(choices=WEEKDAY_CHOICES, help_text="Ngày trong tuần (0: Thứ 2, 6: Chủ nhật)")
    start_time = models.TimeField(help_text="Giờ bắt đầu làm việc")
    end_time = models.TimeField(help_text="Giờ kết thúc làm việc")
    is_available = models.BooleanField(default=True, help_text="Trạng thái hoạt động của lịch làm việc")
    location = models.CharField(max_length=255, help_text="Địa điểm làm việc", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        status = "Active" if self.is_available else "Inactive"
        return f"Dr. {self.doctor_id} - {self.get_weekday_display()} ({self.start_time} - {self.end_time}) - {status}"

    class Meta:
        verbose_name = "Doctor Availability"
        verbose_name_plural = "Doctor Availabilities"
        unique_together = ['doctor_id', 'weekday', 'start_time', 'end_time']


class TimeSlot(models.Model):
    """Khung giờ khám bệnh"""
    doctor_id = models.IntegerField(help_text="ID của bác sĩ trong user-service")
    date = models.DateField(help_text="Ngày khám")
    start_time = models.TimeField(help_text="Giờ bắt đầu")
    end_time = models.TimeField(help_text="Giờ kết thúc")
    is_available = models.BooleanField(default=True, help_text="Khung giờ có sẵn sàng không")
    availability = models.ForeignKey(DoctorAvailability, on_delete=models.CASCADE, related_name='time_slots', null=True, blank=True)
    location = models.CharField(max_length=255, help_text="Địa điểm khám", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        status = "Available" if self.is_available else "Booked"
        return f"Dr. {self.doctor_id} - {self.date} ({self.start_time} - {self.end_time}) - {status}"

    class Meta:
        verbose_name = "Time Slot"
        verbose_name_plural = "Time Slots"
        unique_together = ['doctor_id', 'date', 'start_time', 'end_time']
        ordering = ['date', 'start_time']


class Appointment(models.Model):
    """Lịch hẹn khám bệnh"""
    STATUS_CHOICES = [
        ('PENDING', 'Chờ xác nhận'),
        ('CONFIRMED', 'Đã xác nhận'),
        ('CANCELLED', 'Đã hủy'),
        ('COMPLETED', 'Đã hoàn thành'),
        ('NO_SHOW', 'Không đến'),
    ]

    patient_id = models.IntegerField(help_text="ID của bệnh nhân trong user-service")
    time_slot = models.OneToOneField(TimeSlot, on_delete=models.CASCADE, related_name='appointment')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    reason = models.TextField(help_text="Lý do khám", blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    medical_record_id = models.IntegerField(null=True, blank=True, help_text="ID hồ sơ y tế liên quan")
    insurance_id = models.CharField(max_length=100, blank=True, null=True, help_text="Mã bảo hiểm")
    created_by = models.IntegerField(help_text="ID người tạo lịch hẹn", null=True, blank=True)

    # Các trường liên kết với service khác
    prescription_id = models.IntegerField(null=True, blank=True, help_text="ID đơn thuốc liên quan")
    lab_request_id = models.IntegerField(null=True, blank=True, help_text="ID yêu cầu xét nghiệm liên quan")
    billing_id = models.IntegerField(null=True, blank=True, help_text="ID hóa đơn liên quan")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Các phương thức tiện ích
    @property
    def doctor_id(self):
        return self.time_slot.doctor_id

    @property
    def appointment_date(self):
        return self.time_slot.date

    @property
    def start_time(self):
        return self.time_slot.start_time

    @property
    def end_time(self):
        return self.time_slot.end_time

    @property
    def location(self):
        return self.time_slot.location

    def __str__(self):
        return f"Appointment: Patient {self.patient_id} with Dr. {self.doctor_id} on {self.appointment_date} ({self.start_time} - {self.end_time})"

    class Meta:
        verbose_name = "Appointment"
        verbose_name_plural = "Appointments"
        ordering = ['time_slot__date', 'time_slot__start_time']


class AppointmentReminder(models.Model):
    """Nhắc nhở lịch hẹn"""
    REMINDER_TYPE_CHOICES = [
        ('EMAIL', 'Email'),
        ('SMS', 'SMS'),
        ('PUSH', 'Push Notification'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Chờ gửi'),
        ('SENT', 'Đã gửi'),
        ('FAILED', 'Gửi thất bại'),
    ]

    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='reminders')
    reminder_type = models.CharField(max_length=10, choices=REMINDER_TYPE_CHOICES)
    scheduled_time = models.DateTimeField(help_text="Thời gian dự kiến gửi nhắc nhở")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    sent_at = models.DateTimeField(null=True, blank=True)
    message = models.TextField(help_text="Nội dung tin nhắn nhắc nhở")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_reminder_type_display()} reminder for appointment {self.appointment.id} - {self.get_status_display()}"

    class Meta:
        verbose_name = "Appointment Reminder"
        verbose_name_plural = "Appointment Reminders"
        ordering = ['scheduled_time']
