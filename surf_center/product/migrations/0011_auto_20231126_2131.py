# Generated by Django 3.2.22 on 2023-11-26 21:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0010_rename_base_price_service_price'),
    ]

    operations = [
        migrations.RenameField(
            model_name='lessonschedule',
            old_name='is_available',
            new_name='is_booked',
        ),
        migrations.RemoveField(
            model_name='lessonschedule',
            name='service',
        ),
    ]
