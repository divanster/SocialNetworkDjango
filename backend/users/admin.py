from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext as _
from .models import CustomUser, UserProfile

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


class UserAdmin(BaseUserAdmin):
    ordering = ['id']
    list_display = ['email', 'username', 'get_first_name', 'get_last_name', 'is_staff', 'get_profile_picture_thumbnail']
    list_filter = ['is_staff', 'is_active', 'profile__gender']  # Added filters
    search_fields = ('email', 'username', 'profile__first_name', 'profile__last_name')
    readonly_fields = ['date_joined', 'last_login']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'username', 'password1', 'password2',
                'is_active', 'is_staff', 'is_superuser'),
        }),
    )
    inlines = [UserProfileInline]

    def get_first_name(self, obj):
        return obj.profile.first_name
    get_first_name.short_description = 'First Name'

    def get_last_name(self, obj):
        return obj.profile.last_name
    get_last_name.short_description = 'Last Name'

    def get_profile_picture_thumbnail(self, obj):
        if obj.profile.profile_picture:
            return '<img src="%s" width="50" height="50" />' % obj.profile.profile_picture.url
        return 'No Image'
    get_profile_picture_thumbnail.short_description = 'Profile Picture'
    get_profile_picture_thumbnail.allow_tags = True

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        return super().get_inline_instances(request, obj)


admin.site.register(CustomUser, UserAdmin)
