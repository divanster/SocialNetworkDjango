# tagging/admin.py

from django.contrib import admin
from .models import TaggedItem


@admin.register(TaggedItem)
class TaggedItemAdmin(admin.ModelAdmin):
    list_display = ('tagged_user', 'tagged_by', 'content_object', 'created_at',)
    search_fields = ('tagged_user__username', 'tagged_by__username',)
    list_filter = ('created_at',)
    date_hierarchy = 'created_at'
