from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import Pickup, WasteType
from .serializers import (
    PickupSerializer, PickupCreateSerializer,
    WasteTypeSerializer, UserSerializer
)
from users.models import User


class PickupViewSet(viewsets.ModelViewSet):
    """API viewset for Pickup model"""

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'priority', 'date']

    def get_serializer_class(self):
        if self.action == 'create':
            return PickupCreateSerializer
        return PickupSerializer

    def get_queryset(self):
        queryset = Pickup.objects.filter(is_deleted=False).select_related('user', 'assigned_staff')

        # Role-based filtering
        user = self.request.user
        if user.role == 'user':
            queryset = queryset.filter(user=user)
        # Staff can see all pickups

        # Search functionality
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(user__username__icontains=search) |
                Q(user__email__icontains=search) |
                Q(notes__icontains=search)
            )

        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """Assign pickup to staff member"""
        if request.user.role not in ['admin', 'staff']:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )

        pickup = self.get_object()
        staff_id = request.data.get('staff_id')

        if not staff_id:
            return Response(
                {'error': 'staff_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            staff = User.objects.get(id=staff_id, role__in=['admin', 'staff'], is_active=True)
            pickup.assign_staff(staff)
            return Response({'message': f'Pickup assigned to {staff.username}'})
        except User.DoesNotExist:
            return Response(
                {'error': 'Invalid staff member'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark pickup as completed"""
        if request.user.role not in ['admin', 'staff']:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )

        pickup = self.get_object()
        completion_notes = request.data.get('completion_notes', '')
        pickup.mark_completed(completion_notes)

        return Response({'message': 'Pickup marked as completed'})

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get pickup statistics"""
        queryset = self.get_queryset()

        stats = {
            'total': queryset.count(),
            'pending': queryset.filter(status='pending').count(),
            'completed': queryset.filter(status='completed').count(),
            'in_progress': queryset.filter(status='in_progress').count(),
        }

        return Response(stats)


class WasteTypeViewSet(viewsets.ModelViewSet):
    """API viewset for WasteType model"""

    queryset = WasteType.objects.filter(is_active=True)
    serializer_class = WasteTypeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['recyclable', 'hazardous']

    def get_permissions(self):
        """Only staff can modify waste types"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated]  # Add staff check
        return super().get_permissions()

    def check_permissions(self, request):
        """Custom permission check for staff actions"""
        super().check_permissions(request)
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            if request.user.role not in ['admin', 'staff']:
                self.permission_denied(request, message="Only staff can modify waste types")


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only API viewset for User model"""

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = User.objects.filter(is_deleted=False, is_active=True)

        # Users can only see their own profile, staff can see all
        if self.request.user.role == 'user':
            queryset = queryset.filter(id=self.request.user.id)

        return queryset