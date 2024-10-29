# social/admin.py

from django.contrib import admin
from .models import Post, PostImage, Rating, Story


class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 1
    fields = ('image',)
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" width="100" height="100" />'
        return ''

    image_preview.short_description = 'Image Preview'
    image_preview.allow_tags = True


class RatingInline(admin.TabularInline):
    model = Rating
    extra = 0
    fields = ('user', 'value',)
    readonly_fields = ('user', 'value',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'average_rating', 'created_at',)
    search_fields = ('title', 'content', 'author__username',)
    list_filter = ('created_at',)
    date_hierarchy = 'created_at'
    inlines = [PostImageInline, RatingInline]
    readonly_fields = ('average_rating',)


@admin.register(PostImage)
class PostImageAdmin(admin.ModelAdmin):
    list_display = ('post', 'image', 'created_at',)
    search_fields = ('post__title',)
    list_filter = ('created_at',)
    date_hierarchy = 'created_at'


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('post', 'user', 'value', 'created_at',)
    search_fields = ('post__title', 'user__username',)
    list_filter = ('value', 'created_at',)
    date_hierarchy = 'created_at'


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'media_type', 'is_active', 'created_at',)
    search_fields = ('user__username', 'content',)
    list_filter = ('media_type', 'is_active', 'created_at',)
    date_hierarchy = 'created_at'
