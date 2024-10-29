from django.contrib import admin
# comments/admin.py

from django.contrib import admin
from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'content_object', 'content', 'created_at',)
    search_fields = ('user__username', 'content',)
    list_filter = ('created_at', 'user',)
    date_hierarchy = 'created_at'
