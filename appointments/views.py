from django.shortcuts import render, redirect
from rooms.models import Room
from notifications.models import Notification
from appointments.models import Appointment
from django.utils import timezone
from datetime import timedelta


# Create your views here.

def send_appointment_request(request, room_id):
    if request.method == 'POST':
        room = Room.objects.get(id=room_id)
        seller = room.seller
        date = request.POST.get('appointment_date')
        time = request.POST.get('appointment_time')

        # Delete expired notifications
        Notification.delete_old_notifications()

        # Create a new appointment request
        appointment = Appointment.objects.create(
            room=room,
            customer=request.user,
            seller=seller,
            date=date,
            time=time,
            status='hold'
        )

        # Create a notification for the seller with auto-delete after 30 days
        Notification.objects.create(
            user=seller,
            message=f"New appointment request from {request.user.name} for {room.title}.",
            expires_at=timezone.now() + timedelta(minutes=2)
        )
        return redirect('roomdetail', slug=room.room_slug)

