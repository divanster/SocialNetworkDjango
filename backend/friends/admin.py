# backend/friends/admin.py

from django.contrib import admin
from .models import FriendRequest, Friendship, Block


class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ('sender_username', 'receiver_username', 'status', 'created_at')
    search_fields = ('sender_username', 'receiver_username', 'status')
    list_filter = ('status', 'created_at')


class FriendshipAdmin(admin.ModelAdmin):
    list_display = ('user1_username', 'user2_username', 'created_at')
    search_fields = ('user1_username', 'user2_username')
    list_filter = ('created_at',)


class BlockAdmin(admin.ModelAdmin):
    list_display = ('blocker_username', 'blocked_username', 'created_at')
    search_fields = ('blocker_username', 'blocked_username')
    list_filter = ('created_at',)


# Register the models with the corrected admin configurations
admin.site.register(FriendRequest, FriendRequestAdmin)
admin.site.register(Friendship, FriendshipAdmin)
admin.site.register(Block, BlockAdmin)
