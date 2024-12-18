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
    actions = ['hard_delete_selected', 'restore_selected']

    # Action to permanently delete albums
    def hard_delete_selected(self, request, queryset):
        queryset.hard_delete()
        self.message_user(request, f"{queryset.count()} albums deleted permanently.")

    hard_delete_selected.short_description = "Permanently delete selected albums"

    # Action to restore soft-deleted albums
    def restore_selected(self, request, queryset):
        queryset.update(is_deleted=False)
        self.message_user(request, f"{queryset.count()} albums restored.")

    restore_selected.short_description = "Restore selected albums"

    # Ensure soft deleted albums are not listed unless you explicitly allow it
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs.all()  # Allow admin users to see deleted items
        return qs.filter(is_deleted=False)  # Non-admin users won't see deleted items


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('album', 'description', 'created_at', 'is_deleted',)
    list_filter = ('album', 'created_at', 'is_deleted',)
    search_fields = ('description', 'album__title',)
    readonly_fields = ('image_tag',)
    actions = ['hard_delete_selected_photos', 'restore_selected_photos']

    # Action to permanently delete photos
    def hard_delete_selected_photos(self, request, queryset):
        queryset.hard_delete()
        self.message_user(request, f"{queryset.count()} photos deleted permanently.")

    hard_delete_selected_photos.short_description = "Permanently delete selected photos"

    # Action to restore soft-deleted photos
    def restore_selected_photos(self, request, queryset):
        queryset.update(is_deleted=False)
        self.message_user(request, f"{queryset.count()} photos restored.")

    restore_selected_photos.short_description = "Restore selected photos"

    # Ensure soft deleted photos are not listed unless you explicitly allow it
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs.all()  # Allow admin users to see deleted items
        return qs.filter(is_deleted=False)  # Non-admin users won't see deleted items

    def image_tag(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" width="100" height="100" />'
        return ''

    image_tag.short_description = 'Image Preview'
    image_tag.allow_tags = True
