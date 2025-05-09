# Generated by Django 4.2.7 on 2025-04-10 01:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipient_id', models.IntegerField()),
                ('recipient_type', models.CharField(choices=[('PATIENT', 'Patient'), ('DOCTOR', 'Doctor'), ('NURSE', 'Nurse'), ('ADMIN', 'Administrator'), ('PHARMACIST', 'Pharmacist'), ('INSURANCE_PROVIDER', 'Insurance Provider'), ('LAB_TECHNICIAN', 'Laboratory Technician'), ('OTHER', 'Other')], max_length=20)),
                ('recipient_email', models.EmailField(blank=True, max_length=254, null=True)),
                ('recipient_phone', models.CharField(blank=True, max_length=20, null=True)),
                ('notification_type', models.CharField(choices=[('APPOINTMENT', 'Appointment'), ('BILLING', 'Billing'), ('MEDICAL_RECORD', 'Medical Record'), ('LAB_RESULT', 'Lab Result'), ('PRESCRIPTION', 'Prescription'), ('SYSTEM', 'System'), ('OTHER', 'Other')], max_length=20)),
                ('channel', models.CharField(choices=[('EMAIL', 'Email'), ('SMS', 'SMS'), ('PUSH', 'Push Notification'), ('IN_APP', 'In-App Notification')], max_length=10)),
                ('subject', models.CharField(max_length=255)),
                ('content', models.TextField()),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('SENT', 'Sent'), ('DELIVERED', 'Delivered'), ('FAILED', 'Failed'), ('CANCELLED', 'Cancelled')], default='PENDING', max_length=10)),
                ('sent_at', models.DateTimeField(blank=True, null=True)),
                ('delivered_at', models.DateTimeField(blank=True, null=True)),
                ('error_message', models.TextField(blank=True, null=True)),
                ('reference_id', models.CharField(blank=True, max_length=100, null=True)),
                ('reference_type', models.CharField(blank=True, max_length=20, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='NotificationTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('notification_type', models.CharField(choices=[('APPOINTMENT', 'Appointment'), ('BILLING', 'Billing'), ('MEDICAL_RECORD', 'Medical Record'), ('LAB_RESULT', 'Lab Result'), ('PRESCRIPTION', 'Prescription'), ('SYSTEM', 'System'), ('OTHER', 'Other')], max_length=20)),
                ('channel', models.CharField(choices=[('EMAIL', 'Email'), ('SMS', 'SMS'), ('PUSH', 'Push Notification'), ('IN_APP', 'In-App Notification')], max_length=10)),
                ('subject_template', models.CharField(max_length=255)),
                ('content_template', models.TextField()),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='NotificationSchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipient_id', models.IntegerField()),
                ('recipient_type', models.CharField(choices=[('PATIENT', 'Patient'), ('DOCTOR', 'Doctor'), ('NURSE', 'Nurse'), ('ADMIN', 'Administrator'), ('PHARMACIST', 'Pharmacist'), ('INSURANCE_PROVIDER', 'Insurance Provider'), ('LAB_TECHNICIAN', 'Laboratory Technician'), ('OTHER', 'Other')], max_length=20)),
                ('recipient_email', models.EmailField(blank=True, max_length=254, null=True)),
                ('recipient_phone', models.CharField(blank=True, max_length=20, null=True)),
                ('notification_type', models.CharField(choices=[('APPOINTMENT', 'Appointment'), ('BILLING', 'Billing'), ('MEDICAL_RECORD', 'Medical Record'), ('LAB_RESULT', 'Lab Result'), ('PRESCRIPTION', 'Prescription'), ('SYSTEM', 'System'), ('OTHER', 'Other')], max_length=20)),
                ('channel', models.CharField(choices=[('EMAIL', 'Email'), ('SMS', 'SMS'), ('PUSH', 'Push Notification'), ('IN_APP', 'In-App Notification')], max_length=10)),
                ('subject', models.CharField(max_length=255)),
                ('content', models.TextField()),
                ('scheduled_at', models.DateTimeField()),
                ('status', models.CharField(choices=[('SCHEDULED', 'Scheduled'), ('PROCESSING', 'Processing'), ('COMPLETED', 'Completed'), ('FAILED', 'Failed'), ('CANCELLED', 'Cancelled')], default='SCHEDULED', max_length=10)),
                ('reference_id', models.CharField(blank=True, max_length=100, null=True)),
                ('reference_type', models.CharField(blank=True, max_length=20, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('template', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='notification.notificationtemplate')),
            ],
        ),
    ]
