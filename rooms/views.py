from django.shortcuts import render, redirect
from accounts.models import *
from notifications.models import *
from appointments.models import *
from django.utils import timezone
from .models import Room, Room_thumbnail, Room_specification
from accounts.models import User, city
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect



# seller functions
# seller add room
def add_room(request):
    cities = city.objects.all()

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
        return redirect('seller_rooms') 

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
        return redirect(request.META.get('HTTP_REFERER'))


# for deleting rooms
def delete_room(request, room_id):
    seller = get_user_model().objects.get(id=request.user.id)
    rooms = Room.objects.filter(id=room_id, seller=seller)
    if request.method == "POST":
        rooms.delete()
        messages.error(request, "Room Deleted Successfully")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'seller_rooms'))

    


