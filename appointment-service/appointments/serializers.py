from rest_framework import serializers
from .models import DoctorAvailability, TimeSlot, Appointment, AppointmentReminder


class DoctorAvailabilitySerializer(serializers.ModelSerializer):
    weekday_name = serializers.CharField(source='get_weekday_display', read_only=True)

    class Meta:
        model = DoctorAvailability
        fields = ['id', 'doctor_id', 'weekday', 'weekday_name', 'start_time', 'end_time', 'is_available', 'location', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class TimeSlotSerializer(serializers.ModelSerializer):
    availability_id = serializers.PrimaryKeyRelatedField(source='availability', read_only=True)

    class Meta:
        model = TimeSlot
        fields = ['id', 'doctor_id', 'date', 'start_time', 'end_time', 'is_available', 'availability_id', 'location', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class AppointmentReminderSerializer(serializers.ModelSerializer):
    reminder_type_name = serializers.CharField(source='get_reminder_type_display', read_only=True)
    status_name = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = AppointmentReminder
        fields = ['id', 'appointment', 'reminder_type', 'reminder_type_name', 'scheduled_time', 'status', 'status_name', 'sent_at', 'message', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'sent_at']


class AppointmentSerializer(serializers.ModelSerializer):
    status_name = serializers.CharField(source='get_status_display', read_only=True)
    reminders = AppointmentReminderSerializer(many=True, read_only=True)
    doctor_id = serializers.IntegerField(read_only=True)
    appointment_date = serializers.DateField(source='time_slot.date', read_only=True)
    start_time = serializers.TimeField(source='time_slot.start_time', read_only=True)
    end_time = serializers.TimeField(source='time_slot.end_time', read_only=True)
    location = serializers.CharField(source='time_slot.location', read_only=True)

    class Meta:
        model = Appointment
        fields = [
            'id', 'patient_id', 'doctor_id', 'time_slot', 'appointment_date', 'start_time', 'end_time',
            'status', 'status_name', 'reason', 'notes', 'reminders', 'medical_record_id', 'insurance_id',
            'prescription_id', 'lab_request_id', 'billing_id', 'location', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'doctor_id', 'appointment_date', 'start_time', 'end_time']

    def create(self, validated_data):
        # If time_slot is provided, update it to not available
        time_slot = validated_data.get('time_slot')
        if time_slot:
            time_slot.is_available = False
            time_slot.save()

        # Create the appointment
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Handle time slot changes
        old_time_slot = instance.time_slot
        new_time_slot = validated_data.get('time_slot', old_time_slot)

        # If time slot changed, update availability status
        if old_time_slot and old_time_slot != new_time_slot:
            old_time_slot.is_available = True
            old_time_slot.save()

        if new_time_slot and new_time_slot != old_time_slot:
            new_time_slot.is_available = False
            new_time_slot.save()

        # Update the appointment
        return super().update(instance, validated_data)


class AppointmentCreateSerializer(serializers.ModelSerializer):
    doctor_id = serializers.IntegerField(write_only=True)
    appointment_date = serializers.DateField(write_only=True)
    start_time = serializers.TimeField(write_only=True)
    end_time = serializers.TimeField(write_only=True)
    created_by = serializers.IntegerField(required=False)

    class Meta:
        model = Appointment
        fields = [
            'patient_id', 'doctor_id', 'appointment_date', 'start_time', 'end_time',
            'reason', 'notes', 'insurance_id', 'created_by'
        ]

    def validate(self, data):
        """
        Validate that the appointment time is available for the doctor.
        """
        doctor_id = data.pop('doctor_id')
        appointment_date = data.pop('appointment_date')
        start_time = data.pop('start_time')
        end_time = data.pop('end_time')

        # Check if there's an available time slot
        try:
            time_slot = TimeSlot.objects.get(
                doctor_id=doctor_id,
                date=appointment_date,
                start_time=start_time,
                end_time=end_time,
                is_available=True
            )
        except TimeSlot.DoesNotExist:
            raise serializers.ValidationError("Khung giờ đã chọn không khả dụng.")

        # Add the time slot to the validated data
        data['time_slot'] = time_slot

        return data

    def create(self, validated_data):
        # Mark the time slot as not available
        time_slot = validated_data.get('time_slot')
        time_slot.is_available = False
        time_slot.save()

        # Create the appointment
        appointment = Appointment.objects.create(**validated_data)

        # Create a reminder for the appointment (24 hours before)
        from django.utils import timezone
        import datetime

        reminder_time = datetime.datetime.combine(
            time_slot.date,
            time_slot.start_time,
            tzinfo=timezone.get_current_timezone()
        ) - datetime.timedelta(hours=24)

        AppointmentReminder.objects.create(
            appointment=appointment,
            reminder_type='EMAIL',
            scheduled_time=reminder_time,
            message=f"Nhắc nhở: Bạn có lịch hẹn khám bệnh với bác sĩ vào ngày {time_slot.date} lúc {time_slot.start_time}."
        )

        return appointment
