from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0003_remove_is_booked_from_timeslot'),
    ]

    operations = [
        migrations.AddField(
            model_name='timeslot',
            name='availability',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='time_slots', to='appointments.doctoravailability'),
        ),
    ]
