# authentication/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from authentication.models import UserModel
from django.utils.translation import gettext_lazy as _

@admin.register(UserModel)
class CustomUserAdmin(UserAdmin):
    model = UserModel
    ordering = ['id']
    list_display = ['id', 'phone_number', 'country', 'is_staff', 'is_active']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'country']
    search_fields = ['phone_number']

    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        (_('Personal info'), {'fields': ('country',)}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'country', 'password1', 'password2', 'is_staff', 'is_active'),
        }),
    )

    # `username` yo‘q, shuning uchun `USERNAME_FIELD` ga mos
    filter_horizontal = ('groups', 'user_permissions',)
