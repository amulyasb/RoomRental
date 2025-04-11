from django.db import models
from rooms.models import *
from django.utils import timezone
from datetime import timedelta

class Appointment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('finished', 'Finished'),
        ('rejected', 'Rejected'),
        ('hold', 'Hold'),
        ('cancel', 'Cancel'),
    )

    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='appointments')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_appointments', limit_choices_to={'user_type': 'customer'})
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seller_appointments', limit_choices_to={'user_type': 'seller'})
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    rejected_at = models.DateTimeField(null=True, blank=True)

    def delete_rejected_appointments(self):
        # Check if the appointment is rejected
        if self.status == 'rejected' and self.rejected_at:
            time_limit = self.rejected_at + timedelta(minutes=10)
            if timezone.now() > time_limit:
                self.delete() 

    def __str__(self):
        return f"{self.customer.name} -> {self.seller.name}: {self.date} {self.time}"
    

