from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rooms import views


urlpatterns = [


    # seller functions
    path("addroom/", views.add_room, name="add_rooms"),
    path("editroom/<int:room_id>", views.edit_room, name="edit_room"),
    path('delete_thumbnail/<int:thumbnail_id>/', views.delete_thumbnail, name='delete_thumbnail'),
    path('delete_room/<int:room_id>/', views.delete_room, name="delete_room"),

]