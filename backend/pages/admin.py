# pages/admin.py

from django.contrib import admin
from .models import Page


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at',)
    search_fields = ('title', 'content', 'user__username',)
    list_filter = ('created_at',)
    date_hierarchy = 'created_at'
