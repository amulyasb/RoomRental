from django.shortcuts import render, redirect
from rooms.models import Room
from notifications.models import Notification
from appointments.models import Appointment
from django.utils import timezone
from datetime import timedelta


# customer appointment view
def send_appointment_request(request, room_id):
    if request.method == 'POST':
        room = Room.objects.get(id=room_id)
        seller = room.seller
        date = request.POST.get('appointment_date')
        time = request.POST.get('appointment_time')

        # Delete expired notifications
        Notification.delete_old_notifications()

        # Creating a new appointment request
        appointment = Appointment.objects.create(
            room=room,
            customer=request.user,
            seller=seller,
            date=date,
            time=time,
            status='hold'
        )

        Notification.objects.create(
            user=seller,
            message=f"New appointment request from {request.user.name} for {room.title}.",
            expires_at=timezone.now() + timedelta(minutes=2)
        )
        return redirect('roomdetail', slug=room.room_slug)
    

# seller appointment management
def approve_appointment_request(request, appointment_id):        
    if request.method == "POST":
        appointment = Appointment.objects.get(id=appointment_id)
        print(f"Appointment found: {appointment}")  # Debugging


        # ensuring only the seller can approve
        if appointment.seller == request.user:
            print("Seller is authorized")  # Debugging

            appointment.status = 'pending'
            appointment.save()

            print(f"Status updated to {appointment.status}")  # Debugging


            # create notification to the customer 
            Notification.objects.create(
                user = appointment.customer,
                message=f"Your appointment request for {appointment.room.title} has been approved by {appointment.seller.name}.",
                expires_at=timezone.now() + timedelta(minutes=2)
            )
            return redirect("seller_dashboard")

