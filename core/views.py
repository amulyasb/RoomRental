from django.shortcuts import render, redirect
from accounts.models import *
from rooms.models import *
from notifications.models import *
from appointments.models import *
from payment.models import *
from core.models import *
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
    featured_rooms = Room.objects.filter(
        seller__is_subscribed=True
    ).order_by("-id")[:4]

    # Delete expired notifications
    Notification.delete_old_notifications()

    # Delete rejected notification
    appointments = Appointment.objects.filter(customer=user, status='rejected')
    for appointment in appointments:
            appointment.delete_rejected_appointments()  


    if request.user.is_authenticated:
        user = request.user
        # Check if the user is not a customer
        if request.user.user_type == 'seller':  
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
        
        all_rooms = Room.objects.filter(
            seller__is_subscribed=True
        ).order_by("-id").all()

        # Handle city filter from URL parameter
        city_id = request.GET.get('city')
        if city_id:
            all_rooms = all_rooms.filter(city_id=city_id).all()
        
        if request.method == "POST":
            searched_room = request.POST.get("searched_room_name")
            min_price = request.POST.get("min-price")
            max_price = request.POST.get("max-price")
            searched_city = request.POST.get("searched_city")
            print(searched_city)

            # for filter rooms
            # Filter by room title
            if searched_room:
                all_rooms = all_rooms.filter(title__icontains = searched_room)
            
            # Filter by city
            if min_price and max_price:
                all_rooms = all_rooms.filter(price__gte=min_price, price__lte=max_price)
            elif min_price:
                all_rooms = all_rooms.filter(price__gte=min_price)
            elif max_price:
                all_rooms = all_rooms.filter(price__lte=max_price)

            # filter by city
            if searched_city:
                all_rooms = all_rooms.filter(city=searched_city)

        
        # Delete expired notifications
        Notification.delete_old_notifications()

        # Fetch notifications for the seller
        notifications = Notification.objects.filter(user=user, expire_status=False).order_by('-created_at')

        # Count unread notifications
        unread_notifications_count = Notification.objects.filter(user=user, is_read=False, expire_status=False).count()

        # fetch room section
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
    notifications = None
    unread_notifications_count = None
    room_detail = Room.objects.get(room_slug = slug)
    room_specifications = Room_specification.objects.filter(room=room_detail)
    room_thumbnails = Room_thumbnail.objects.filter(room=room_detail)
    user=request.user
    seller = room_detail.seller
    
    # Delete expired notifications
    Notification.delete_old_notifications()

    # Fetch notifications for the seller
    notifications = Notification.objects.filter(user=user, expire_status=False).order_by('-created_at')
        
    # Count unread notifications
    unread_notifications_count = Notification.objects.filter(user=user, is_read=False, expire_status=False).count()

    data = {
        "room_detail": room_detail,
        "room_specifications": room_specifications,
        "room_thumbnails": room_thumbnails,
        "seller": seller,
        "notifications": notifications,
        "unread_notifications_count": unread_notifications_count,
    }

    return render(request, "core/roomdetail.html", data)

def customer_profile(request):
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

    data={
        'cities':cities,
        'notifications':notifications,
        'unread_notifications_count': unread_notifications_count,
    }

    return render(request, "core/customer_profile.html", data)

def update_profile_customer(request):
    if request.method == 'POST':
        customer_name = request.POST.get("name")
        customer_email = request.POST.get("email")
        customer_password = request.POST.get("password")
        customer_phone = request.POST.get("phone")
        customer_city = request.POST.get("city")
        customer_img = request.FILES.get("profile_image")
        customer_id = request.user.id
        print(customer_img)

        customer = get_user_model().objects.get(id=customer_id)

            
        # Check if the email already exists
        if customer_email and customer_email != customer.email and get_user_model().objects.filter(email=customer_email).exclude(id=customer_id).exists(): 
        #exclude checks for duplicate email in databse exclude remove the user and checks other user 
            messages.error(request, "Email already exists!")
            return redirect("customer_profile")
        

        # Check if phone is changed and already used by another user
        if customer_phone and customer_phone != customer.phone and get_user_model().objects.filter(phone=customer_phone).exclude(id=customer_id).exists():
            messages.error(request, "This phone number is already in use by another account.")
            return redirect('customer_profile')

        # fetch the user
        customer.name = customer_name
        customer.email = customer_email
        customer.phone = customer_phone

        # Update city only if a new city is provided
        if customer_city:
            try:
                customer.city = city.objects.get(city=customer_city)
            except city.DoesNotExist:
                messages.error(request, "Invalid City Selected")
                return redirect("customer_profile")

        # Update profile image if provided
        if customer_img:
            customer.user_image = customer_img
        
        # Update password only if provided
        if customer_password:
            customer.set_password(customer_password)
            customer.save()
            messages.success(request, "Profile Updated Succesfully please login again")
            return redirect("login_user")
        customer.save()
        messages.success(request, "Profile Updated Succesfully")
        return redirect("customer_profile")
    
    return render(request, "core/customer_profile.html")


def customer_contact(request):
    user = None
    notifications = None
    unread_notifications_count = None

    if request.user.is_authenticated:
        user=request.user
        # Delete expired notifications
        Notification.delete_old_notifications()

        # Fetch notifications for the seller
        notifications = Notification.objects.filter(user=user, expire_status=False).order_by('-created_at')

        # Count unread notifications
        unread_notifications_count = Notification.objects.filter(user=user, is_read=False, expire_status=False).count()

    data={
        'notifications': notifications,
        'unread_notifications_count': unread_notifications_count,
        'user': user,
    }
    return render(request, "core/customer_contact.html", data)

def seller_contact(request):
    notifications = None
    unread_notifications_count = None

    if request.user.is_authenticated:
        user=request.user
        # Delete expired notifications
        Notification.delete_old_notifications()

        # Fetch notifications for the seller
        notifications = Notification.objects.filter(user=user, expire_status=False).order_by('-created_at')

        # Count unread notifications
        unread_notifications_count = Notification.objects.filter(user=user, is_read=False, expire_status=False).count()

    data={
        'notifications': notifications,
        'unread_notifications_count': unread_notifications_count,
        }
    return render(request, "seller/seller_contact.html", data)

def  manage_contact(request):
    user = request.user
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        message = request.POST.get("message")
        type = request.POST.get("type")

        contact_form = contact.objects.create(
            name = name,
            email = email,
            subject = subject,
            message = message,
            type = type
        )
        contact_form.save()
        Notification.objects.create(
            user = request.user,
            message=f"{user.name.upper()}: Your Contact Form has been sent Successfully, We will figure out your issue and get back to you soon",
            expires_at=timezone.now() + timedelta(days=30)
        )
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    
def about(request):
    notifications = None
    unread_notifications_count = None

    if request.user.is_authenticated:
        user=request.user
        # Delete expired notifications
        Notification.delete_old_notifications()

        # Fetch notifications for the seller
        notifications = Notification.objects.filter(user=user, expire_status=False).order_by('-created_at')

        # Count unread notifications
        unread_notifications_count = Notification.objects.filter(user=user, is_read=False, expire_status=False).count()
        
    data={
        'notifications': notifications,
        'unread_notifications_count': unread_notifications_count,
    }
    return render(request, "core/aboutUs.html", data)






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


        # payment sorting through days
        payment_filter = request.GET.get('days')
        if payment_filter:
            days = int(payment_filter)
            filtered_payment= timezone.now() - timedelta(days=days)
            payments = payments.filter(payment_date__gte=filtered_payment)
        else:
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
        'payment_filter': payment_filter,
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




