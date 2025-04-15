from django.db import models
from accounts.models import User


class contact(models.Model):
    name = models.CharField(max_length=30, blank=False, null=False)
    email = models.EmailField()
    subject = models.CharField(max_length=100)
    message = models.TextField()
    type = models.CharField(max_length=20)

    def __str__(self):
        return f" {self.subject} - {self.email} - {self.type}"
