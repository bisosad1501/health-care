from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='timeslot',
            name='is_available',
            field=models.BooleanField(default=True, help_text='Khung giờ có sẵn sàng không'),
        ),
    ]
