from django.contrib import admin
from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'post', 'content', 'created_at', 'updated_at')
    search_fields = ('user__username', 'content')
    list_filter = ('created_at',)
