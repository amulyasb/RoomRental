from django.shortcuts import render, redirect
from accounts.models import *
from django.utils import timezone




# Create your views here.
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
        

    data = {
        'user': user,
        'cities': cities,
        'subscription_remaning_days': subscription_remaning_days,
    }
    return render(request, "seller/seller_dashboard.html", data)


def add_room(request):

    return render(request, "seller/add_room.html")