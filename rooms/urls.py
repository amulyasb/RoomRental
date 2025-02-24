from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rooms import views


urlpatterns = [
    # seller functions
    path("seller_dashboard/", views.seller_dashboard, name="seller_dashboard"),
    
    path("addroom/", views.add_room, name="add_rooms"),
]