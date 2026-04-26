from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('analytics/', views.analytics_view, name='analytics'),
    path('health/', views.health_check, name='health_check'),
]