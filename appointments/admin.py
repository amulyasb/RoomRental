from django.contrib import admin
from .models import Appointment

class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('customer', 'seller', 'room', 'date', 'time', 'status', 'created_at')
    list_filter = ('status', 'date', 'room')
    search_fields = ('customer__name', 'seller__name', 'room__name')
    ordering = ('-created_at',)
    list_editable = ('status',)
    readonly_fields = ('created_at','rejected_at')

    fieldsets = (
        ('Basic Information', {
            'fields': ('customer', 'seller', 'room')
        }),
        ('Appointment Details', {
            'fields': ('date', 'time', 'status')
        }),
        ('Metadata', {
            'fields': ('created_at','rejected_at'),
            'classes': ('collapse',),
        }),
    )

admin.site.register(Appointment, AppointmentAdmin)
