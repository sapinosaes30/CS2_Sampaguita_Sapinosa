from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import PickupViewSet, WasteTypeViewSet, UserViewSet

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'pickups', PickupViewSet, basename='pickup')
router.register(r'waste-types', WasteTypeViewSet, basename='wastetype')
router.register(r'users', UserViewSet, basename='user')

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('api/', include(router.urls)),
]