from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from appointments import views


urlpatterns = [
    path('send_appointment_request/<int:room_id>/', views.send_appointment_request, name='send_appointment_request'),
    path('approve_appointment_request/<int:appointment_id>/', views.approve_appointment_request, name='approve_appointment_request'),
]