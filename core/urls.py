from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views


urlpatterns = [
    path("", views.homepage, name="homepage"),
    path("roomlist/", views.roomlist, name="roomlist"),
    path("roomdetail/<slug>", views.roomdetail, name="roomdetail"),
    path("customer_profile/", views.customer_profile, name="customer_profile"),
    path("update_profile_customer/", views.update_profile_customer, name="update_profile_customer"),
    path ("customer_contact/", views.customer_contact, name="customer_contact"),
    path ("seller_contact/", views.seller_contact, name="seller_contact"),
    path ("manage_contact/", views.manage_contact, name="manage_contact"),
    path ("about-us/", views.about, name="about"),

    # seller views
    path("seller_dashboard/", views.seller_dashboard, name="seller_dashboard"),
    path("seller_rooms/", views.seller_rooms, name="seller_rooms"),
    path('seller_profile/', views.seller_profile, name="seller_profile"),
    path('update_profile_seller/', views.update_profile_seller, name="update_profile_seller"),
    path('seller_appointments/', views.seller_appointments, name="seller_appointments"),
    path('seller_subscription/', views.seller_subscription, name="seller_subscription"),

    # notification hanlder
    path('customer_mark_notifications_as_read/', views.customer_mark_notifications_as_read, name="customer_mark_notifications_as_read"),
    path('seller_mark-notifications-as-read/', views.seller_mark_notifications_as_read, name='seller_mark_notifications_as_read'),


]