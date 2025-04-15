from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0002_add_is_available_to_timeslot'),
    ]

    operations = [
        migrations.RunSQL(
            "ALTER TABLE appointments_timeslot DROP COLUMN IF EXISTS is_booked;",
            "ALTER TABLE appointments_timeslot ADD COLUMN is_booked BOOLEAN DEFAULT FALSE;"
        ),
    ]
