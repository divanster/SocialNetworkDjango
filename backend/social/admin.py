# backend/social/admin.py
from django.contrib import admin
from .models import Post, Rating, PostImage, Tag


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'author', 'created_at']
    list_filter = ['author', 'tags', 'created_at']
    search_fields = ['title', 'author__username']


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ['id', 'post', 'user', 'value']
    list_filter = ['post', 'user', 'value']
    search_fields = ['post__title', 'user__username']


@admin.register(PostImage)
class PostImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'post', 'image']
    list_filter = ['post']
    search_fields = ['post__title']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']
