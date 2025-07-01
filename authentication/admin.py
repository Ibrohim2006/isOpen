from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from authentication.models import UserModel


@admin.register(UserModel)
class CustomUserAdmin(UserAdmin):
    model = UserModel
    ordering = ['-created_at']
    list_display = [
        'id', 'phone_number', 'country', 'is_verified',
        'is_staff', 'is_active', 'created_at'
    ]
    list_filter = [
        'is_staff', 'is_superuser', 'is_active',
        'is_verified', 'country', 'created_at'
    ]
    search_fields = ['phone_number', 'country']
    list_per_page = 25

    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        (_('Personal info'), {'fields': ('country', 'is_verified')}),
        (_('Permissions'), {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions'
            ),
        }),
        (_('Important dates'), {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'phone_number', 'country', 'password1', 'password2',
                'is_staff', 'is_active'
            ),
        }),
    )

    readonly_fields = ('created_at', 'updated_at', 'date_joined', 'last_login')
    filter_horizontal = ('groups', 'user_permissions',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related()
