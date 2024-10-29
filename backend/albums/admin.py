# albums/admin.py

from django.contrib import admin
from .models import Album, Photo


class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 1
    fields = ('image', 'description',)
    readonly_fields = ('image_tag',)

    def image_tag(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" width="100" height="100" />'
        return ''

    image_tag.short_description = 'Image Preview'
    image_tag.allow_tags = True


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'is_deleted', 'created_at',)
    list_filter = ('is_deleted', 'created_at',)
    search_fields = ('title', 'description', 'user__username',)
    inlines = [PhotoInline]
    date_hierarchy = 'created_at'


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('album', 'description', 'created_at',)
    list_filter = ('album', 'created_at',)
    search_fields = ('description', 'album__title',)
    readonly_fields = ('image_tag',)

    def image_tag(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" width="100" height="100" />'
        return ''

    image_tag.short_description = 'Image Preview'
    image_tag.allow_tags = True
