from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext as _
from .models import CustomUser


class UserAdmin(BaseUserAdmin):
    ordering = ['id']
    list_display = ['email', 'username', 'first_name', 'last_name', 'is_staff']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('first_name', 'last_name', 'username', 'profile_picture')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'username', 'password1', 'password2', 'profile_picture', 'is_active', 'is_staff',
                'is_superuser'),
        }),
    )
    search_fields = ('email', 'username')
    readonly_fields = ['date_joined', 'last_login']


admin.site.register(CustomUser, UserAdmin)
