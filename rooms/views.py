from django.shortcuts import render, redirect
from accounts.models import *
from django.utils import timezone
from .models import Room, Room_thumbnail, Room_specification
from accounts.models import User, city
from django.contrib import messages
from django.contrib.auth import get_user_model




# seller dashboard
def seller_dashboard(request):
    subscription_remaning_days = None
    cities = city.objects.all()
    if request.user.is_authenticated:
        user = request.user
        if request.user.user_type != 'seller':
            return redirect('login_user')
        
        # calculate seller subscription remaning days
        if user.is_subscribed and user.subscription_end_date:
            now = timezone.now()
            subscription_remaning_days = (user.subscription_end_date - now).days
            if subscription_remaning_days < 0:
                subscription_remaning_days = 0

        # for fetching rooms in room table
        seller_rooms_table = Room.objects.filter(seller=user).order_by("-id")[:2]

        # for total added rooms of seller in frontend
        seller_total_rooms = Room.objects.filter(seller=user).count()
        

    data = {
        'user': user,
        'cities': cities,
        'subscription_remaning_days': subscription_remaning_days,
        'seller_rooms_table':seller_rooms_table,
        'seller_total_rooms': seller_total_rooms,

    }
    return render(request, "seller/seller_dashboard.html", data)


# seller all rooms
def seller_rooms(request):
    cities = city.objects.all()

    if request.user.is_authenticated:
        user = request.user
        if request.user.user_type != 'seller':
            return redirect('login_user')
        
        # for fetching seller room object in frontend
        seller_rooms_table = Room.objects.filter(seller=user).order_by("-id")

    data = {
        'cities': cities,
        'seller_rooms_table': seller_rooms_table,
        'user': user,
    }

    return render(request, "seller/seller_rooms.html", data)

# seller profile
def seller_profile(request):
    cities = city.objects.all()
        
    return render(request, "seller/seller_profile.html", {'cities': cities})

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




# seller functions
# seller add room
def add_room(request):
    cities = city.objects.all()  # Assuming you have a City model

    if request.method == 'POST':
        room_title = request.POST.get('room_title')
        room_description = request.POST.get('desc')
        city_id = request.POST.get('city')
        rent = request.POST.get('rent')
        room_image = request.FILES.get('room_image')
        room_slug = room_title.replace(" ", "-").lower()

        city_obj = city.objects.filter(id = city_id).first()

        # creating room
        room = Room.objects.create(
            seller = request.user,
            title = room_title,
            address = room_description,
            price = rent,
            room_img = room_image,
            city = city_obj,
            room_slug = room_slug
        )

        # Handle multiple room images (thumbnails)
        thumbnails = []
        for i in range(1, 11):  # Adjust range if more thumbnails are expected
            thumbnail = request.FILES.get(f'room_image_{i}')
            if thumbnail:
                thumbnails.append(thumbnail)

        for thumbnail in thumbnails:
            Room_thumbnail.objects.create(room=room, thumbnail_img=thumbnail)


        # Handle room specifications
        spec_names = request.POST.getlist('spec_name[]')
        spec_details = request.POST.getlist('spec_detail[]')

        for name, detail in zip(spec_names, spec_details):
            Room_specification.objects.create(room=room, spec_name=name, spec_detail=detail)
        return redirect('seller_dashboard') 

    data = {
        'cities': cities,
    }
    return render(request, "seller/add_room.html", data)


# edit room
def edit_room(request, room_id):
    cities = city.objects.all()
    user = request.user
    room_to_update = Room.objects.get(id=room_id, seller=user)

    if request.method == 'POST':
        # update room fields
        room_to_update.title = request.POST.get("room_title", room_to_update.title)
        room_to_update.price = request.POST.get("rent", room_to_update.price)
        room_to_update.address = request.POST.get("desc", room_to_update.address)

        selected_city = request.POST.get("city", room_to_update.city.city)
        room_to_update.city = city.objects.get(city=selected_city)  
        
        # Update main image 
        if "room_image" in request.FILES:
            room_to_update.room_img = request.FILES["room_image"]
        # room_to_update.room_img = request.FILES.get("room_image", room_to_update.room_img)
        room_to_update.save()


        # Update Thumbnail Room
        thumbnails = []
        for i in range(1, 11):  # Adjust range if more thumbnails are expected
            thumbnail = request.FILES.get(f'new_thumb_image_{i}')
            if thumbnail:
                thumbnails.append(thumbnail)

        for thumbnail in thumbnails:
            Room_thumbnail.objects.create(room=room_to_update, thumbnail_img=thumbnail)

        
        # Update Existing Specifications
        old_spec_names = request.POST.getlist("old_spec_name[]")
        old_spec_details = request.POST.getlist("old_spec_detail[]")

        existing_specs = Room_specification.objects.filter(room=room_to_update)

        for spec_obj, new_name, new_detail in zip(existing_specs, old_spec_names, old_spec_details):
            if new_name.strip() and new_detail.strip():  # Ensure non-empty values
                spec_obj.spec_name = new_name
                spec_obj.spec_detail = new_detail
                spec_obj.save()

        # Add New Specifications
        new_spec_names = request.POST.getlist("new_spec_name[]")
        new_spec_details = request.POST.getlist("new_spec_detail[]")

        for name, detail in zip(new_spec_names, new_spec_details):
            if name.strip() and detail.strip():  # Avoid creating empty specifications
                Room_specification.objects.create(room=room_to_update, spec_name=name, spec_detail=detail)
        messages.success(request, "Room Updated Successfully")
        return redirect('seller_rooms')


# for deleting thumbnail while updating rooms if necessary
def delete_thumbnail(request, thumbnail_id):
    thumbnail = Room_thumbnail.objects.filter(id=thumbnail_id).first()
    
    if thumbnail:
        # If thumbnail exists, delete it
        thumbnail.delete()    
    return redirect('seller_rooms')


# for deleting rooms
def delete_room(request, room_id):
    seller = get_user_model().objects.get(id=request.user.id)
    rooms = Room.objects.filter(id=room_id, seller=seller)
    if request.method == "POST":
        rooms.delete()
        messages.error(request, "Room Deleted Successfully")
        return redirect('seller_rooms')
    


