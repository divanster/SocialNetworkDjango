from django.contrib import admin
from .models import Story


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    """
    Admin configuration for managing stories.
    """
    list_display = (
    'id', 'user', 'content_preview', 'media_type', 'is_active', 'created_at',
    'updated_at')
    list_filter = ('media_type', 'is_active', 'created_at')
    search_fields = ('user__username', 'content', 'media_type')
    readonly_fields = ('created_at', 'updated_at', 'viewed_by_count')

    def content_preview(self, obj):
        """
        Return a preview of the story content for easy identification in the list display.
        """
        return obj.content[:50] + ('...' if len(obj.content) > 50 else '')

    content_preview.short_description = 'Content Preview'

    def viewed_by_count(self, obj):
        """
        Show the number of users who have viewed the story.
        """
        return obj.viewed_by.count()

    viewed_by_count.short_description = 'Viewed By Count'

    # Customizing the form in the admin
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'content', 'media_type', 'media_url', 'is_active')
        }),
        ('Additional Information', {
            'fields': ('viewed_by', 'tags')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
        }),
    )

    filter_horizontal = ('viewed_by',)

