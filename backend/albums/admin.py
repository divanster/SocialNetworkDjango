from django.contrib import admin
from .models import Album, Photo


class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 1


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'user', 'created_at']
    list_filter = ['user', 'created_at']
    search_fields = ['title', 'user__username']
    inlines = [PhotoInline]


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ['id', 'album', 'image', 'created_at']
    list_filter = ['album', 'created_at']
    search_fields = ['album__title']
