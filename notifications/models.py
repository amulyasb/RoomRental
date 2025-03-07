from django.db import models
from django.utils.timezone import now, timedelta
from accounts.models import *
from django.utils import timezone


# Create your models here.


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    expire_status = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)

    @staticmethod
    def delete_old_notifications():
        expired_notifications = Notification.objects.filter(expires_at__lt=now())
        if expired_notifications.exists():
            Notification.expire_status = True
            expired_notifications.delete()

    def __str__(self):
        return f"Notification for {self.user.email} - {self.message}"