from django.urls import path, include
from rest_framework.routers import DefaultRouter
from conductorapp.api_views import (
    BusViewSet, ConductorViewSet, BusLocationViewSet,
    BusRouteViewSet, PickupDropEventViewSet
)
from conductorapp import views

router = DefaultRouter()
router.register(r'buses', BusViewSet, basename='bus')
router.register(r'conductors', ConductorViewSet, basename='conductor')
router.register(r'locations', BusLocationViewSet, basename='location')
router.register(r'routes', BusRouteViewSet, basename='route')
router.register(r'events', PickupDropEventViewSet, basename='event')

urlpatterns = [
    path('', include(router.urls)),
    path('boarding-status/', views.conductor_boarding_status, name='conductor_boarding_status'),
    path('drop-status/', views.conductor_drop_status, name='conductor_drop_status'),
    path('location-update/', views.update_location_api, name='location_update'),
    path('scan-token/', views.api_scan_token, name='api_scan_token'),
    path('assign-bus/', views.api_assign_bus, name='api_assign_bus'),
    path('bus/status/', views.api_bus_status, name='api_bus_status'),
]
