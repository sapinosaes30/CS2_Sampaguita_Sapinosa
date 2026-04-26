from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Custom admin for User model with role-based features"""

    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'is_deleted', 'created_at')
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser', 'is_deleted', 'created_at')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'house_id')
    ordering = ('-created_at',)

    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('role', 'province', 'city', 'barangay', 'house_id', 'address')
        }),
        ('Soft Delete', {
            'fields': ('is_deleted', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('created_at', 'updated_at', 'deleted_at')

    def get_queryset(self, request):
        """Show all users including soft deleted ones for admins"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs  # Show all including deleted
        return qs.filter(is_deleted=False)  # Hide deleted for regular admins

    def has_delete_permission(self, request, obj=None):
        """Prevent hard deletion, use soft delete instead"""
        return False

    actions = ['soft_delete_users', 'restore_users']

    @admin.action(description='Soft delete selected users')
    def soft_delete_users(self, request, queryset):
        queryset.update(is_deleted=True, deleted_at=timezone.now())

    @admin.action(description='Restore selected users')
    def restore_users(self, request, queryset):
        queryset.update(is_deleted=False, deleted_at=None)
