from django.contrib import admin
from accounts.models import User, city
from django.contrib.auth.admin import UserAdmin

# Register your models here.
class CustomUserAdmin(UserAdmin):
    # Fields to display in the admin list view
    list_display = ('name', 'email', 'user_type', 'phone', 'city', 'is_staff', 'is_active')
    search_fields = ("name", "email", "phone")
    list_filter = ("user_type", "is_staff", "is_active", "is_subscribed")
    ordering = ("email",)

    # Fields to include in the edit form
    fieldsets = (
        (None, {'fields': ('name', 'email', 'password', 'user_image')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('User Type', {'fields': ('user_type', 'phone', 'city')}),
        ('Subscription', {'fields': ('is_subscribed', 'subscription_end_date')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('name', 'email', 'password1', 'password2', 'user_type', 'phone', 'city', 'is_active', 'is_staff')}
        ),
    )

# Register models
admin.site.register(User, CustomUserAdmin) 
admin.site.register(city)  
