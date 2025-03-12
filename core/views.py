from django.shortcuts import render, redirect
from accounts.models import *
from rooms.models import *
from notifications.models import *
from appointments.models import *
from django.core.paginator import Paginator


# Create your views here.
# notification handler
def customer_mark_notifications_as_read(request):
    if request.user.is_authenticated:
        # Update notifications for the logged-in user
        notifications = Notification.objects.filter(user=request.user, is_read=False)
        notifications.update(is_read=True)  # Mark all as read

    return redirect('homepage') 


def homepage(request):
    how_it_work_section = request.GET.get('type', 'customerSection')  # Default to 'customerSection'
    cities = city.objects.all()
    user = None
    notifications = None
    unread_notifications_count = None

    # fetch featured room section
    featured_rooms = Room.objects.all().order_by("-id")[:4]

    # Delete expired notifications
    Notification.delete_old_notifications()

    # Delete rejected notification
    appointments = Appointment.objects.filter(customer=user, status='rejected')
    for appointment in appointments:
            appointment.delete_rejected_appointments()  


    if request.user.is_authenticated:
        user = request.user
        # Check if the user is not a customer
        if request.user.user_type != 'customer':  
            return redirect('login_user')
        
        # Fetch notifications for the seller
        notifications = Notification.objects.filter(user=user, expire_status=False).order_by('-created_at')

        # Count unread notifications
        unread_notifications_count = Notification.objects.filter(user=user, is_read=False, expire_status=False).count()


    data = {
        'type': how_it_work_section,
        'user': user,
        'cities': cities,
        'featured_rooms': featured_rooms,
        'notifications': notifications,
        'unread_notifications_count': unread_notifications_count,
    }
    return render(request, "core/homepage.html", data)

def roomlist(request):
    cities = city.objects.all()

    if request.user.is_authenticated:
        user = request.user
        # Check if the user is not a customer
        if request.user.user_type != 'customer':  
            return redirect('login_user')
        # fetch featured room section
        all_rooms = Room.objects.all().order_by("-id")
        paginator = Paginator(all_rooms, 12)

        page_number = request.GET.get("page") 
        all_rooms = paginator.get_page(page_number)


    data={
        'cities':cities,
        'all_rooms': all_rooms,
        'user': user,
    }
    return render(request, "core/roomlist.html", data)

def roomdetail(request,slug):
    room_detail = Room.objects.get(room_slug = slug)
    room_specifications = Room_specification.objects.filter(room=room_detail)
    room_thumbnails = Room_thumbnail.objects.filter(room=room_detail)
    seller = room_detail.seller
    
    # Delete expired notifications
    Notification.delete_old_notifications()

    data = {
        "room_detail": room_detail,
        "room_specifications": room_specifications,
        "room_thumbnails": room_thumbnails,
        "seller": seller,
    }

    return render(request, "core/roomdetail.html", data)



