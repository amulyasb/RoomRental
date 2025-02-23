from django.db import models
from accounts.models import *
from autoslug import AutoSlugField


# Create your models here.
class Room(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='Seller_rooms')
    title = models.CharField(max_length=25)
    address = models.CharField(max_length=50)
    city = models.ForeignKey(city, on_delete=models.CASCADE, related_name='room_city')
    price = models.IntegerField()
    room_img = models.ImageField(upload_to='img/room_img', default='')
    created_at = models.DateTimeField(auto_now_add=True)
    room_slug = AutoSlugField(populate_from='title', unique=True, null=True, default=None)
    Sold = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    
class Room_specification(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    spec_name = models.CharField(max_length=50)
    spec_detail = models.CharField(max_length=200)

class Room_thumbnail(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    thumbnail_img = models.ImageField(upload_to="img/rooms_img", default="", null=True)