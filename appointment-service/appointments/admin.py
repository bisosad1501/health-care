from django.contrib import admin
from .models import DoctorAvailability, TimeSlot, Appointment, AppointmentReminder


@admin.register(DoctorAvailability)
class DoctorAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('doctor_id', 'weekday', 'start_time', 'end_time', 'is_available')
    list_filter = ('weekday', 'is_available')
    search_fields = ('doctor_id',)


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('doctor_id', 'date', 'start_time', 'end_time', 'is_booked')
    list_filter = ('date', 'is_booked')
    search_fields = ('doctor_id',)
    date_hierarchy = 'date'


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient_id', 'doctor_id', 'appointment_date', 'start_time', 'end_time', 'status')
    list_filter = ('status', 'appointment_date')
    search_fields = ('patient_id', 'doctor_id')
    date_hierarchy = 'appointment_date'


@admin.register(AppointmentReminder)
class AppointmentReminderAdmin(admin.ModelAdmin):
    list_display = ('appointment', 'reminder_type', 'scheduled_time', 'status', 'sent_at')
    list_filter = ('reminder_type', 'status')
    search_fields = ('appointment__patient_id', 'appointment__doctor_id')
    date_hierarchy = 'scheduled_time'
