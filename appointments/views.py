from django.shortcuts import render

# Create your views here.

def appointment_booking(request):
    return render(request, "customer_appointments/appointment_booking.html")
