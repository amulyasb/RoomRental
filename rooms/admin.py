from django.contrib import admin
from .models import *

# Register your models here.
class RoomSpec_Inline(admin.TabularInline):
    model = Room_specification

class Room_thumb(admin.TabularInline):
    model = Room_thumbnail

class Add_spec_thumb(admin.ModelAdmin):
    inlines = (RoomSpec_Inline, Room_thumb)

admin.site.register(Room, Add_spec_thumb)
