# reactions/admin.py

from django.contrib import admin
from .models import Reaction


@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'emoji', 'content_object', 'created_at',)
    search_fields = ('user__username', 'emoji',)
    list_filter = ('emoji', 'created_at',)
    date_hierarchy = 'created_at'
