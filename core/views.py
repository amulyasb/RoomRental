from django.shortcuts import render, redirect
from accounts.models import *
from rooms.models import *

# Create your views here.

def homepage(request):
    how_it_work_section = request.GET.get('type', 'customerSection')  # Default to 'customerSection'
    cities = city.objects.all()
    user = None
    featured_rooms = Room.objects.all().order_by("-id")[:4]


    if request.user.is_authenticated:
        user = request.user
        # Check if the user is not a customer
        if request.user.user_type != 'customer':  
            return redirect('login_user')
        
        featured_rooms = Room.objects.all().order_by("-id")[:4]


    data = {
        'type': how_it_work_section,
        'user': user,
        'cities': cities,
        'featured_rooms': featured_rooms,
    }
    return render(request, "core/homepage.html", data)

def roomlist(request):
    cities = city.objects.all()

    data={
        'cities':cities,
    }
    return render(request, "core/roomlist.html", data)

def roomdetail(request):
    return render(request, "core/roomdetail.html")



