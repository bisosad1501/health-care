# Generated by Django 4.2.7 on 2025-04-19 01:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pharmacy', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='prescription',
            name='diagnosis_id',
            field=models.IntegerField(blank=True, help_text='ID of the diagnosis in medical-record-service', null=True),
        ),
        migrations.AddField(
            model_name='prescription',
            name='encounter_id',
            field=models.IntegerField(blank=True, help_text='ID of the encounter in medical-record-service', null=True),
        ),
    ]
