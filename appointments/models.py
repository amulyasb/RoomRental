from django.db import models
from rooms.models import *

class Appointment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('hold', 'Hold'),
    )

    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='appointments')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_appointments')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seller_appointments')
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.name} -> {self.seller.name}: {self.date} {self.time}"
    

