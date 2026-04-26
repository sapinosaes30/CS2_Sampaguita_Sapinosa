from django.contrib import admin
from django.utils import timezone
from .models import Pickup, WasteType, PickupWasteType


class PickupWasteTypeInline(admin.TabularInline):
    """Inline admin for pickup waste types"""
    model = PickupWasteType
    extra = 1
    autocomplete_fields = ['waste_type']


@admin.register(Pickup)
class PickupAdmin(admin.ModelAdmin):
    """Admin for Pickup model"""

    list_display = ('id', 'user', 'date', 'time', 'priority', 'status', 'assigned_staff', 'created_at')
    list_filter = ('status', 'priority', 'date', 'assigned_staff', 'created_at')
    search_fields = ('user__username', 'user__email', 'notes')
    ordering = ('-created_at',)
    date_hierarchy = 'date'

    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'date', 'time', 'priority', 'notes')
        }),
        ('Status & Assignment', {
            'fields': ('status', 'assigned_staff')
        }),
        ('Completion', {
            'fields': ('completed_at', 'completion_notes'),
            'classes': ('collapse',)
        }),
        ('Soft Delete', {
            'fields': ('is_deleted', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('created_at', 'updated_at', 'completed_at', 'deleted_at')
    inlines = [PickupWasteTypeInline]

    def get_queryset(self, request):
        """Show all pickups including soft deleted ones for admins"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs  # Show all including deleted
        return qs.filter(is_deleted=False)  # Hide deleted for regular admins

    def has_delete_permission(self, request, obj=None):
        """Prevent hard deletion, use soft delete instead"""
        return False

    actions = ['mark_completed', 'assign_to_me', 'soft_delete_pickups', 'restore_pickups']

    @admin.action(description='Mark selected pickups as completed')
    def mark_completed(self, request, queryset):
        updated = queryset.update(
            status='completed',
            completed_at=timezone.now()
        )
        self.message_user(request, f'{updated} pickups marked as completed.')

    @admin.action(description='Assign selected pickups to me')
    def assign_to_me(self, request, queryset):
        if request.user.role in ['admin', 'staff']:
            updated = queryset.update(
                assigned_staff=request.user,
                status='scheduled'
            )
            self.message_user(request, f'{updated} pickups assigned to you.')
        else:
            self.message_user(request, 'You do not have permission to assign pickups.', level='error')

    @admin.action(description='Soft delete selected pickups')
    def soft_delete_pickups(self, request, queryset):
        queryset.update(is_deleted=True, deleted_at=timezone.now())

    @admin.action(description='Restore selected pickups')
    def restore_pickups(self, request, queryset):
        queryset.update(is_deleted=False, deleted_at=None)


@admin.register(WasteType)
class WasteTypeAdmin(admin.ModelAdmin):
    """Admin for WasteType model"""

    list_display = ('name', 'recyclable', 'hazardous', 'base_fee', 'is_active')
    list_filter = ('recyclable', 'hazardous', 'is_active')
    search_fields = ('name', 'description')
    ordering = ('name',)

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description')
        }),
        ('Properties', {
            'fields': ('recyclable', 'hazardous')
        }),
        ('Pricing', {
            'fields': ('base_fee',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )

    readonly_fields = ('created_at', 'updated_at')
