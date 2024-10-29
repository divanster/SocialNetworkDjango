# friends/admin.py

from django.contrib import admin
from .models import FriendRequest, Friendship, Block


@admin.register(FriendRequest)
class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'status', 'created_at',)
    search_fields = ('sender__username', 'receiver__username',)
    list_filter = ('status', 'created_at',)
    date_hierarchy = 'created_at'


@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ('user1', 'user2', 'created_at',)
    search_fields = ('user1__username', 'user2__username',)
    list_filter = ('created_at',)
    date_hierarchy = 'created_at'


@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ('blocker', 'blocked', 'created_at',)
    search_fields = ('blocker__username', 'blocked__username',)
    list_filter = ('created_at',)
    date_hierarchy = 'created_at'
