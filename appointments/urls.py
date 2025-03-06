from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from appointments import views


urlpatterns = [
    path('appointment_booking/', views.appointment_booking, name="appointment_booking"),
]