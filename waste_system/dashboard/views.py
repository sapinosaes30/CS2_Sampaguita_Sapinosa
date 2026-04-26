from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from core.models import Pickup
from users.models import User


class DashboardView(LoginRequiredMixin, TemplateView):
    """Main dashboard view with analytics"""

    template_name = 'dashboard/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Base queryset
        pickups = Pickup.objects.filter(is_deleted=False)

        # Role-based filtering
        if user.role == 'user':
            pickups = pickups.filter(user=user)
        elif user.role in ['admin', 'staff']:
            # Staff see all pickups
            pass

        # Time periods
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)

        # Analytics data
        context.update({
            'total_pickups': pickups.count(),
            'pending_pickups': pickups.filter(status='pending').count(),
            'completed_pickups': pickups.filter(status='completed').count(),
            'today_pickups': pickups.filter(date=today).count(),
            'week_pickups': pickups.filter(date__gte=week_ago).count(),
            'month_pickups': pickups.filter(date__gte=month_ago).count(),

            # Status breakdown
            'status_data': self.get_status_chart_data(pickups),

            # Priority breakdown
            'priority_data': self.get_priority_chart_data(pickups),

            # Recent pickups
            'recent_pickups': pickups.select_related('user', 'assigned_staff')[:10],

            # User stats (for admin/staff)
            'user_stats': self.get_user_stats() if user.role in ['admin', 'staff'] else None,
        })

        return context

    def get_status_chart_data(self, pickups):
        """Get data for status pie chart"""
        status_counts = pickups.values('status').annotate(count=Count('status')).order_by('status')
        return list(status_counts)

    def get_priority_chart_data(self, pickups):
        """Get data for priority bar chart"""
        priority_counts = pickups.values('priority').annotate(count=Count('priority')).order_by('priority')
        return list(priority_counts)

    def get_user_stats(self):
        """Get user statistics for admin/staff"""
        return {
            'total_users': User.objects.filter(is_deleted=False).count(),
            'active_users': User.objects.filter(is_deleted=False, is_active=True).count(),
            'staff_count': User.objects.filter(role__in=['admin', 'staff'], is_deleted=False).count(),
            'new_users_month': User.objects.filter(
                created_at__gte=timezone.now() - timedelta(days=30),
                is_deleted=False
            ).count(),
        }


@login_required
def analytics_view(request):
    """Detailed analytics view"""
    if request.user.role not in ['admin', 'staff']:
        return render(request, '403.html', status=403)

    # Comprehensive analytics
    pickups = Pickup.objects.filter(is_deleted=False)

    # Monthly trends (last 12 months)
    monthly_data = []
    for i in range(11, -1, -1):
        date = timezone.now() - timedelta(days=i*30)
        month_start = date.replace(day=1)
        next_month = (month_start + timedelta(days=32)).replace(day=1)
        month_end = next_month - timedelta(days=1)

        count = pickups.filter(created_at__range=(month_start, month_end)).count()
        monthly_data.append({
            'month': month_start.strftime('%b %Y'),
            'count': count
        })

    # Top users by pickup count
    top_users = User.objects.filter(
        is_deleted=False,
        pickups__is_deleted=False
    ).annotate(
        pickup_count=Count('pickups')
    ).order_by('-pickup_count')[:10]

    # Performance metrics
    avg_completion_time = pickups.filter(
        status='completed',
        completed_at__isnull=False
    ).extra(
        select={'completion_time': 'julianday(completed_at) - julianday(created_at)'}
    ).values('completion_time')

    context = {
        'monthly_data': monthly_data,
        'top_users': top_users,
        'total_revenue': 0,  # Placeholder for future pricing
        'completion_rate': pickups.filter(status='completed').count() / max(pickups.count(), 1) * 100,
        'avg_pickups_per_user': pickups.count() / max(User.objects.filter(is_deleted=False).count(), 1),
    }

    return render(request, 'dashboard/analytics.html', context)
