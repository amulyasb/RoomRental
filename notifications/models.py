from django.db import models
from django.utils.timezone import now, timedelta
from accounts.models import *

# Create your models here.


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=now() + timedelta(days=3))
    is_read = models.BooleanField(default=False)

    @staticmethod
    def delete_old_notifications():
        """Deletes expired notifications."""
        Notification.objects.filter(expires_at__lt=now()).delete()

    def __str__(self):
        return f"Notification for {self.user.email} - {self.message}"