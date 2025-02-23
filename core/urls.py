from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views


urlpatterns = [
    path("", views.homepage, name="homepage"),
    path("roomlist/", views.roomlist, name="roomlist"),
    path("roomdetail/", views.roomdetail, name="roomdetail"),

]