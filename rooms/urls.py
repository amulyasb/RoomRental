from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rooms import views


urlpatterns = [
    # seller views
    path("seller_dashboard/", views.seller_dashboard, name="seller_dashboard"),
    path("seller_rooms/", views.seller_rooms, name="seller_rooms"),

    # seller functions
    path("addroom/", views.add_room, name="add_rooms"),
    path("editroom/<int:room_id>", views.edit_room, name="edit_room"),
    path('delete_thumbnail/<int:thumbnail_id>/', views.delete_thumbnail, name='delete_thumbnail'),
    path('delete_room/<int:room_id>/', views.delete_room, name="delete_room"),
    path('seller_profile/', views.seller_profile, name="seller_profile"),
    path('update_profile_seller/', views.update_profile_seller, name="update_profile_seller"),

]