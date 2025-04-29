from django.contrib import admin
from core.models import *

# admin.site.register(contact)

@admin.register(contact)
class ContactAdmin(admin.ModelAdmin):
    # Display fields in list view
    list_display = ('name', 'email', 'subject', 'type', 'created_at')

    # Make email and subject searchable
    search_fields = ('email', 'subject', 'name')
    
    # Add filters for type and date
    list_filter = ('type', 'created_at')
    # Fields to display in edit form (grouped logically)
    fieldsets = (
        (None, {
            'fields': ('name', 'email', 'type')
        }),
        ('Message Details', {
            'fields': ('subject', 'message'),
            'classes': ('wide',),
        }),
    )
    # Make name and email clickable in admin list
    list_display_links = ('name', 'email')
    # Set default ordering
    ordering = ('-created_at',)
    # Add a text area for the message field
    formfield_overrides = {
        models.TextField: {'widget': admin.widgets.AdminTextareaWidget(
            attrs={'rows': 4, 'cols': 60}
        )},
    }