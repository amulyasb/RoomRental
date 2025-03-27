from django.shortcuts import render, redirect
from accounts.models import *
from rooms.models import *
from notifications.models import *
from appointments.models import *
from payment.models import *
from django.core.paginator import Paginator
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect



# notification handler
def seller_mark_notifications_as_read(request):
    if request.user.is_authenticated:
        # Update notifications for the logged-in user
        notifications = Notification.objects.filter(user=request.user, is_read=False)
        notifications.update(is_read=True)  # Mark all as read

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'seller_dashboard'))

def customer_mark_notifications_as_read(request):
    if request.user.is_authenticated:
        # Update notifications for the logged-in user
        notifications = Notification.objects.filter(user=request.user, is_read=False)
        notifications.update(is_read=True)  # Mark all as read

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'homepage'))


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
    notifications = None
    unread_notifications_count = None

    if request.user.is_authenticated:
        user = request.user
        # Check if the user is not a customer
        if request.user.user_type != 'customer':  
            return redirect('login_user')
        
        # Delete expired notifications
        Notification.delete_old_notifications()

        # Fetch notifications for the seller
        notifications = Notification.objects.filter(user=user, expire_status=False).order_by('-created_at')

        # Count unread notifications
        unread_notifications_count = Notification.objects.filter(user=user, is_read=False, expire_status=False).count()

        # fetch room section
        all_rooms = Room.objects.all().order_by("-id")
        paginator = Paginator(all_rooms, 12)

        page_number = request.GET.get("page") 
        all_rooms = paginator.get_page(page_number)


    data={
        'cities':cities,
        'all_rooms': all_rooms,
        'user': user,
        'notifications': notifications,
        'unread_notifications_count': unread_notifications_count,
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



###### seller #########
####### seller dashboard 
def seller_dashboard(request):
    subscription_remaning_days = None
    cities = city.objects.all()
    if request.user.is_authenticated:
        user = request.user
        if request.user.user_type != 'seller':
            return redirect('login_user')
        else:
            user.check_subscription_status()

        # calculate seller subscription remaning days
        if user.subscription_end_date:
            now = timezone.now()
            subscription_remaning_days = (user.subscription_end_date - now).days
            if subscription_remaning_days < 0:
                subscription_remaning_days = 0

        # Delete expired notifications
        Notification.delete_old_notifications()

        # Delete rejected notification
        appointments = Appointment.objects.filter(seller=user, status='rejected')
        for appointment in appointments:
            appointment.delete_rejected_appointments()  

        # for fetching rooms in room table
        seller_rooms_table = Room.objects.filter(seller=user).order_by("-id")[:2]

        # for total added rooms of seller in frontend
        seller_total_rooms = Room.objects.filter(seller=user).count()

        # Fetch appointment requests for the seller
        appointment_requests = Appointment.objects.filter(seller=user, status='hold').order_by('date')[:2]

        # Total appointments requests
        total_appointment_requests = appointment_requests.count()

        # Fetch pending appointments (accepted but not completed)
        pending_appointments = Appointment.objects.filter(seller=user, status='pending').order_by('date')[:2]

        # Total pending appointments
        total_pending_appointments = pending_appointments.count()

        # Fetch notifications for the seller
        notifications = Notification.objects.filter(user=user, expire_status=False).order_by('-created_at')

        # Count unread notifications
        unread_notifications_count = Notification.objects.filter(user=user, is_read=False, expire_status=False).count()
    else:
        messages.error(request, "Unauthorized User")
        return redirect('login_user')
    
    data = {
        'user': user,
        'cities': cities,
        'subscription_remaning_days': subscription_remaning_days,
        'seller_rooms_table':seller_rooms_table,
        'seller_total_rooms': seller_total_rooms,
        'notifications': notifications,
        'unread_notifications_count':unread_notifications_count,
        'appointment_requests': appointment_requests,
        'pending_appointments': pending_appointments,
        'total_appointment_requests': total_appointment_requests,
        'total_pending_appointments': total_pending_appointments,
    }
    return render(request, "seller/seller_dashboard.html", data)


# seller all rooms
def seller_rooms(request):
    cities = city.objects.all()

    if request.user.is_authenticated:
        user = request.user
        if request.user.user_type != 'seller':
            return redirect('login_user')
        else:
            user.check_subscription_status()
        
        # Delete expired notifications
        Notification.delete_old_notifications()

        
        # Fetch notifications for the seller
        notifications = Notification.objects.filter(user=user, expire_status=False).order_by('-created_at')
        
        # Count unread notifications
        unread_notifications_count = Notification.objects.filter(user=user, is_read=False, expire_status=False).count()
        
        # for fetching seller room object in frontend
        seller_rooms_table = Room.objects.filter(seller=user).order_by("-id")
    else:
        messages.error(request, "Unauthorized User")
        return redirect('login_user')

    data = {
        'cities': cities,
        'seller_rooms_table': seller_rooms_table,
        'user': user,
        'notifications':notifications,
        'unread_notifications_count': unread_notifications_count,
    }

    return render(request, "seller/seller_rooms.html", data)


# seller appointment 
def seller_appointments(request):

    cities = city.objects.all()
    if request.user.is_authenticated:
        user = request.user
        if request.user.user_type != 'seller':
            return redirect('login_user')
        else:
            user.check_subscription_status()
        
        # calculate seller subscription remaning days
        if user.is_subscribed and user.subscription_end_date:
            now = timezone.now()
            subscription_remaning_days = (user.subscription_end_date - now).days
            if subscription_remaning_days < 0:
                subscription_remaning_days = 0

        # Delete expired notifications
        Notification.delete_old_notifications()
    
        # Fetch notifications for the seller
        notifications = Notification.objects.filter(user=user, expire_status=False).order_by('-created_at')
        
        # Count unread notifications
        unread_notifications_count = Notification.objects.filter(user=user, is_read=False, expire_status=False).count()

        # Delete rejected notification
        appointments = Appointment.objects.filter(seller=user, status='rejected')
        for appointment in appointments:
            appointment.delete_rejected_appointments()  

        # Fetch appointment requests for the seller
        appointment_requests = Appointment.objects.filter(seller=user, status='hold').order_by('date')

        # Fetch pending appointments (accepted but not completed)
        pending_appointments = Appointment.objects.filter(seller=user, status='pending').order_by('date')

        # fetching finished appointments
        finished_appointments = Appointment.objects.filter(seller=user, status='finished').order_by('date')

        # fetching canceled appointments
        canceled_appointments = Appointment.objects.filter(seller=user, status='cancel').order_by('date')

        # Get filter value from URL
        filter_option = request.GET.get('filter', 'requests') 
                
    else:
        messages.error(request, "Unauthorized User")
        return redirect('login_user')


        
    data={
        'appointment_requests': appointment_requests,
        'pending_appointments': pending_appointments,
        'finished_appointments': finished_appointments,
        'canceled_appointments': canceled_appointments,            'notifications':notifications,
        'unread_notifications_count': unread_notifications_count,
        'filter_option': filter_option,
    }

    return render(request, "seller/seller_appointments.html", data)


# Seller Subscription
def seller_subscription(request):
    cities = city.objects.all()
    if request.user.is_authenticated:
        user = request.user
        if request.user.user_type != 'seller':
            return redirect('login_user')
        else:
            user.check_subscription_status()
        
        # calculate seller subscription remaning days
        if user.is_subscribed and user.subscription_end_date:
            now = timezone.now()
            subscription_remaning_days = (user.subscription_end_date - now).days
            if subscription_remaning_days < 0:
                subscription_remaning_days = 0

        # Delete expired notifications
        Notification.delete_old_notifications()
    
        # Fetch notifications for the seller
        notifications = Notification.objects.filter(user=user, expire_status=False).order_by('-created_at')
        
        # Count unread notifications
        unread_notifications_count = Notification.objects.filter(user=user, is_read=False, expire_status=False).count()

        # Delete rejected notification
        appointments = Appointment.objects.filter(seller=user, status='rejected')
        for appointment in appointments:
            appointment.delete_rejected_appointments()  

        
        subscriptions = Subscription.objects.filter(seller=user).order_by("-id")[:1]
        payments = Payment.objects.filter(seller=user).order_by("-id")
                
    else:
        messages.error(request, "Unauthorized User")
        return redirect('login_user')


    data={
        'notifications': notifications,
        'unread_notifications_count': unread_notifications_count,
        'cities': cities,
        'subscriptions': subscriptions,
        'payments':payments,
    }

    return render(request, "seller/seller_subscription.html", data)



# seller profile
def seller_profile(request):

    cities = city.objects.all()
    if request.user.is_authenticated:
        user = request.user
        if request.user.user_type != 'seller':
            return redirect('login_user')
        else:
            user.check_subscription_status()
        # Delete expired notifications
        Notification.delete_old_notifications()
        
        # Fetch notifications for the seller
        notifications = Notification.objects.filter(user=user, expire_status=False).order_by('-created_at')
            
        # Count unread notifications
        unread_notifications_count = Notification.objects.filter(user=user, is_read=False, expire_status=False).count()
        
    else:
        messages.error(request, "Unauthorized User")
        return redirect('login_user')
    
    data={
        'cities':cities,
        'notifications':notifications,
        'unread_notifications_count': unread_notifications_count,
    }
        
    return render(request, "seller/seller_profile.html", data)


# update seller profile
def update_profile_seller(request):
    if request.method == 'POST':
        seller_name = request.POST.get("name")
        seller_email = request.POST.get("email")
        seller_password = request.POST.get("password")
        seller_phone = request.POST.get("phone")
        seller_city = request.POST.get("city")
        seller_img = request.FILES.get("profile_image")
        seller_id = request.user.id

        seller = get_user_model().objects.get(id=seller_id)

            
        # Check if the email already exists
        if seller_email and seller_email != seller.email and get_user_model().objects.filter(email=seller_email).exclude(id=seller_id).exists(): 
        #exclude checks for duplicate email in databse exclude remove the user and checks other user 
            messages.error(request, "Email already exists!")
            return redirect("seller_profile")
        

        # Check if phone is changed and already used by another user
        if seller_phone and seller_phone != seller.phone and get_user_model().objects.filter(phone=seller_phone).exclude(id=seller_id).exists():
            messages.error(request, "This phone number is already in use by another account.")
            return redirect('seller_profile')

        # fetch the user
        seller.name = seller_name
        seller.email = seller_email
        seller.phone = seller_phone

        # Update city only if a new city is provided
        if seller_city:
            try:
                seller.city = city.objects.get(city=seller_city)
            except city.DoesNotExist:
                messages.error(request, "Invalid City Selected")
                return redirect("seller_profile")

        # Update profile image if provided
        if seller_img:
            seller.user_image = seller_img
        
        # Update password only if provided
        if seller_password:
            seller.set_password(seller_password)
            seller.save()
            messages.success(request, "Profile Updated Succesfully please login again")
            return redirect("login_user")

        
        seller.save()
        messages.success(request, "Profile Updated Succesfully")
        return redirect("seller_profile")
    
    return render(request, "seller/seller_profile.html")




