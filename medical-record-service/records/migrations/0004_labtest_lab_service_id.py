# Generated by Django 4.2.7 on 2025-04-19 02:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0003_diagnosis_prescription_ids'),
    ]

    operations = [
        migrations.AddField(
            model_name='labtest',
            name='lab_service_id',
            field=models.IntegerField(blank=True, help_text='ID của xét nghiệm trong laboratory-service', null=True),
        ),
    ]
