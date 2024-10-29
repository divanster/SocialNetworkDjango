# notifications/admin.py

from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
    'sender', 'receiver', 'notification_type', 'content_object', 'is_read',
    'created_at',)
    search_fields = ('sender__username', 'receiver__username', 'text',)
    list_filter = ('notification_type', 'is_read', 'created_at',)
    date_hierarchy = 'created_at'
