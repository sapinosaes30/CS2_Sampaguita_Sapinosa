from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Pickup CRUD
    path('pickups/', views.PickupListView.as_view(), name='pickup_list'),
    path('pickups/create/', views.PickupCreateView.as_view(), name='pickup_create'),
    path('pickups/<int:pk>/', views.PickupDetailView.as_view(), name='pickup_detail'),
    path('pickups/<int:pk>/update/', views.PickupUpdateView.as_view(), name='pickup_update'),
    path('pickups/<int:pk>/delete/', views.PickupDeleteView.as_view(), name='pickup_delete'),

    # Pickup actions
    path('pickups/<int:pk>/assign/', views.assign_pickup, name='assign_pickup'),
    path('pickups/<int:pk>/complete/', views.complete_pickup, name='complete_pickup'),
]