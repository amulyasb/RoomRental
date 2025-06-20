# Generated by Django 5.1.6 on 2025-03-07 14:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0002_notification_is_read_alter_notification_expires_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='expire_status',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='notification',
            name='expires_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
