from django.contrib import admin

# Register your models here.

from django.contrib import admin
from django.utils.timezone import now
from .models import Notification

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message_summary', 'created_at', 'expires_at', 'is_expired')
    list_filter = ('created_at', 'expires_at')
    search_fields = ('user__email', 'message')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'expires_at')

    def is_expired(self, obj):
        """Check if a notification is expired."""
        return obj.expires_at < now()
    is_expired.boolean = True
    is_expired.short_description = "Expired?"

    def message_summary(self, obj):
        """Display a truncated version of the notification message."""

        return (obj.message[:50] + '...') if len(obj.message) > 50 else obj.message
    message_summary.short_description = "Message"

    actions = ['delete_expired_notifications']

    def delete_expired_notifications(self, request, queryset):
        """Admin action to remove all expired notifications."""
        count, _ = Notification.objects.filter(expires_at__lt=now()).delete()
        self.message_user(request, f"Deleted {count} expired notifications.")
    delete_expired_notifications.short_description = "Delete expired notifications"

    def mark_as_read(self, request, queryset):
        """Admin action to mark selected notifications as read."""
        count = queryset.update(is_read=True)
        self.message_user(request, f"Marked {count} notifications as read.")
    mark_as_read.short_description = "Mark selected as read"

admin.site.register(Notification, NotificationAdmin)
