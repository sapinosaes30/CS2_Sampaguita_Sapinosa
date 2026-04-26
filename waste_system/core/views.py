from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.db.models import Q, Count
from django.utils import timezone
from .models import Pickup, WasteType, PickupWasteType
from .forms import PickupForm, PickupUpdateForm


class StaffRequiredMixin(UserPassesTestMixin):
    """Mixin to require staff or admin role"""
    def test_func(self):
        return self.request.user.role in ['admin', 'staff']


class PickupListView(LoginRequiredMixin, ListView):
    """List view for pickups"""
    model = Pickup
    template_name = 'core/pickup_list.html'
    context_object_name = 'pickups'
    paginate_by = 20

    def get_queryset(self):
        queryset = Pickup.objects.filter(is_deleted=False).select_related('user', 'assigned_staff')

        # Filter based on user role
        if self.request.user.role == 'user':
            queryset = queryset.filter(user=self.request.user)
        elif self.request.user.role in ['admin', 'staff']:
            # Staff can see all, but can filter by assignment
            pass

        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(user__username__icontains=search_query) |
                Q(user__email__icontains=search_query) |
                Q(notes__icontains=search_query)
            )

        # Status filter
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        # Date filter
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Pickup.STATUS_CHOICES
        context['waste_types'] = WasteType.objects.filter(is_active=True)
        return context


class PickupDetailView(LoginRequiredMixin, DetailView):
    """Detail view for pickups"""
    model = Pickup
    template_name = 'core/pickup_detail.html'
    context_object_name = 'pickup'

    def get_queryset(self):
        queryset = Pickup.objects.filter(is_deleted=False).select_related('user', 'assigned_staff')

        # Users can only see their own pickups
        if self.request.user.role == 'user':
            queryset = queryset.filter(user=self.request.user)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['waste_types'] = self.object.pickupwastetype_set.all().select_related('waste_type')
        return context


class PickupCreateView(LoginRequiredMixin, CreateView):
    """Create view for pickups"""
    model = Pickup
    form_class = PickupForm
    template_name = 'core/pickup_form.html'
    success_url = reverse_lazy('pickup_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)

        # Handle waste types
        waste_types_data = self.request.POST.getlist('waste_types')
        quantities = self.request.POST.getlist('quantities')

        for waste_type_id, quantity in zip(waste_types_data, quantities):
            if waste_type_id and quantity:
                try:
                    waste_type = WasteType.objects.get(id=waste_type_id)
                    PickupWasteType.objects.create(
                        pickup=self.object,
                        waste_type=waste_type,
                        quantity=int(quantity)
                    )
                except (WasteType.DoesNotExist, ValueError):
                    continue

        messages.success(self.request, 'Pickup request created successfully!')
        return response


class PickupUpdateView(LoginRequiredMixin, UpdateView):
    """Update view for pickups"""
    model = Pickup
    form_class = PickupUpdateForm
    template_name = 'core/pickup_form.html'

    def get_queryset(self):
        queryset = Pickup.objects.filter(is_deleted=False)

        # Users can only update their own pickups
        if self.request.user.role == 'user':
            queryset = queryset.filter(user=self.request.user, status='pending')
        # Staff can update assigned pickups
        elif self.request.user.role in ['admin', 'staff']:
            queryset = queryset.filter(
                Q(user=self.request.user) |
                Q(assigned_staff=self.request.user)
            )

        return queryset

    def get_success_url(self):
        return reverse('pickup_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Pickup updated successfully!')
        return response


@login_required
def assign_pickup(request, pk):
    """Assign pickup to staff member"""
    if request.user.role not in ['admin', 'staff']:
        messages.error(request, 'You do not have permission to assign pickups.')
        return redirect('pickup_list')

    pickup = get_object_or_404(Pickup, pk=pk, is_deleted=False)

    if request.method == 'POST':
        staff_id = request.POST.get('staff_id')
        if staff_id:
            from users.models import User
            try:
                staff = User.objects.get(id=staff_id, role__in=['admin', 'staff'], is_active=True)
                pickup.assign_staff(staff)
                messages.success(request, f'Pickup assigned to {staff.username}.')
            except User.DoesNotExist:
                messages.error(request, 'Invalid staff member selected.')
        else:
            messages.error(request, 'Please select a staff member.')

    return redirect('pickup_detail', pk=pk)


@login_required
def complete_pickup(request, pk):
    """Mark pickup as completed"""
    if request.user.role not in ['admin', 'staff']:
        messages.error(request, 'You do not have permission to complete pickups.')
        return redirect('pickup_list')

    pickup = get_object_or_404(Pickup, pk=pk, is_deleted=False)

    if request.method == 'POST':
        completion_notes = request.POST.get('completion_notes', '')
        pickup.mark_completed(completion_notes)
        messages.success(request, 'Pickup marked as completed!')

    return redirect('pickup_detail', pk=pk)


class PickupDeleteView(LoginRequiredMixin, DeleteView):
    """Delete view for pickups (soft delete)"""
    model = Pickup
    template_name = 'core/pickup_confirm_delete.html'
    success_url = reverse_lazy('pickup_list')

    def get_queryset(self):
        queryset = Pickup.objects.filter(is_deleted=False)

        # Users can only delete their own pending pickups
        if self.request.user.role == 'user':
            queryset = queryset.filter(user=self.request.user, status='pending')
        # Staff can delete any pickup
        elif self.request.user.role in ['admin', 'staff']:
            pass

        return queryset

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.soft_delete()
        messages.success(request, 'Pickup deleted successfully!')
        return redirect(self.success_url)
