from django.db import models
from django.contrib.auth.models import AbstractUser
from accounts.manager import CustomManager


# Create your models here.
class city(models.Model):
    city = models.CharField(max_length=15, null=True)

    def __str__(self):
        return self.city
    

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('seller', 'Seller'),
        ('customer', 'Customer')
    )
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=30, null=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    phone = models.CharField(max_length=10, unique=True)
    city = models.ForeignKey(city, on_delete=models.CASCADE, null=True, blank=True, default=None)
    is_subscribed = models.BooleanField(default=False)
    subscription_end_date = models.DateTimeField(null=True, blank=True)
    user_image = models.ImageField(upload_to="img/user_img", default="", null=True)

    username = None

    # Use email as the unique identifier
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomManager()


    def __str__(self):
        return self.email
