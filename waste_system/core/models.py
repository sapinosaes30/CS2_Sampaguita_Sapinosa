from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import User


class Pickup(models.Model):
    """Waste pickup request model"""

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='pickups',
        help_text="User who requested the pickup"
    )

    date = models.DateField(help_text="Requested pickup date")
    time = models.TimeField(help_text="Requested pickup time")

    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='normal',
        help_text="Pickup priority level"
    )

    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes for the pickup"
    )

    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Current status of the pickup"
    )

    # Assignment fields
    assigned_staff = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='assigned_pickups',
        limit_choices_to={'role__in': ['admin', 'staff']},
        help_text="Staff member assigned to this pickup"
    )

    # Completion fields
    completed_at = models.DateTimeField(blank=True, null=True)
    completion_notes = models.TextField(blank=True, null=True)

    # Soft delete fields
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(blank=True, null=True)

    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pickups'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['date']),
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
            models.Index(fields=['assigned_staff']),
            models.Index(fields=['is_deleted']),
        ]

    def __str__(self):
        return f"Pickup #{self.pk} - {self.user.username} ({self.date})"

    def mark_completed(self, completion_notes=None):
        """Mark pickup as completed"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        if completion_notes:
            self.completion_notes = completion_notes
        self.save()

    def assign_staff(self, staff_user):
        """Assign staff to pickup"""
        if staff_user.role in ['admin', 'staff']:
            self.assigned_staff = staff_user
            self.status = 'scheduled'
            self.save()


class WasteType(models.Model):
    """Types of waste that can be collected"""

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    recyclable = models.BooleanField(default=False)
    hazardous = models.BooleanField(default=False)

    # Pricing
    base_fee = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)]
    )

    # Soft delete
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'waste_types'
        ordering = ['name']

    def __str__(self):
        return self.name


class PickupWasteType(models.Model):
    """Many-to-many relationship between pickups and waste types"""

    pickup = models.ForeignKey(Pickup, on_delete=models.CASCADE)
    waste_type = models.ForeignKey(WasteType, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    weight_kg = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        db_table = 'pickup_waste_types'
        unique_together = ['pickup', 'waste_type']

    def __str__(self):
        return f"{self.pickup} - {self.waste_type} ({self.quantity})"
