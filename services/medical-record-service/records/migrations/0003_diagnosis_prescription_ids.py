# Generated by Django 4.2.7 on 2025-04-19 01:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0002_encounter_appointment_id_encounter_chief_complaint_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='diagnosis',
            name='prescription_ids',
            field=models.JSONField(blank=True, default=list, help_text='Danh sách ID của các đơn thuốc liên quan từ pharmacy-service'),
        ),
    ]
