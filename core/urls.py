from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views


urlpatterns = [
    path("", views.homepage, name="homepage"),
    path("roomlist/", views.roomlist, name="roomlist"),
    path("roomdetail/<slug>", views.roomdetail, name="roomdetail"),

    # notification hanlder
    path('customer_mark_notifications_as_read/', views.customer_mark_notifications_as_read, name="customer_mark_notifications_as_read"),


]