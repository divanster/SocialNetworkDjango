# messenger/admin.py

from django.contrib import admin
from .models import Message

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'content_snippet', 'is_read', 'created_at',)
    search_fields = ('sender__username', 'receiver__username', 'content',)
    list_filter = ('is_read', 'created_at',)
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)

    def content_snippet(self, obj):
        return obj.content[:50]
    content_snippet.short_description = 'Content Snippet'
