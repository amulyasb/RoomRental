from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from appointments import views


urlpatterns = [
    path('send_appointment_request/<int:room_id>/', views.send_appointment_request, name='send_appointment_request'),
    path('approve_appointment_request/<int:appointment_id>/', views.approve_appointment_request, name='approve_appointment_request'),
    path('reject_appointment_request/<int:appointment_id>/', views.reject_appointment_request, name='reject_appointment_request'),
    path('finished_appointment_request/<int:appointment_id>/', views.finished_appointment_request, name='finished_appointment_request'),
    path('cancel_appointment_request/<int:appointment_id>/', views.cancel_appointment_request, name='cancel_appointment_request'),
]