# Generated by Django 5.1.6 on 2025-04-11 16:14

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0004_alter_appointment_status'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='customer',
            field=models.ForeignKey(limit_choices_to={'user_type': 'customer'}, on_delete=django.db.models.deletion.CASCADE, related_name='customer_appointments', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='seller',
            field=models.ForeignKey(limit_choices_to={'user_type': 'seller'}, on_delete=django.db.models.deletion.CASCADE, related_name='seller_appointments', to=settings.AUTH_USER_MODEL),
        ),
    ]
