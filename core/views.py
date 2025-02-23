from django.shortcuts import render
from accounts.models import *

# Create your views here.

def homepage(request):
    how_it_work_section = request.GET.get('type', 'customerSection')  # Default to 'customerSection'
    cities = city.objects.all()
    user = None

    if request.user.is_authenticated:
        user = request.user

    data = {
        'type': how_it_work_section,
        'user': user,
        'cities': cities,
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
