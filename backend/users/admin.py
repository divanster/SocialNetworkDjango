from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext as _
from .models import CustomUser

class UserAdmin(BaseUserAdmin):
    ordering = ['id']
    list_display = ['email', 'username', 'first_name', 'last_name', 'is_staff', 'profile_picture_thumbnail']
    list_filter = ['is_staff', 'is_active', 'gender']  # Added filters
    search_fields = ('email', 'username')
    readonly_fields = ['date_joined', 'last_login']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('first_name', 'last_name', 'username', 'profile_picture', 'gender', 'date_of_birth')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'username', 'password1', 'password2', 'profile_picture', 'gender', 'date_of_birth',
                'is_active', 'is_staff', 'is_superuser'),
        }),
    )

    def profile_picture_thumbnail(self, obj):
        if obj.profile_picture:
            return '<img src="%s" width="50" height="50" />' % obj.profile_picture.url
        return 'No Image'
    profile_picture_thumbnail.short_description = 'Profile Picture'
    profile_picture_thumbnail.allow_tags = True

admin.site.register(CustomUser, UserAdmin)
