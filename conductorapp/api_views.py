from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils import timezone
from conductorapp.models import (
    BusModels, ConductorModels, BusLocationModels, 
    BusRouteModels, PickupDropEvent
)
from conductorapp.serializers import (
    BusSerializer, ConductorSerializer, BusLocationSerializer,
    BusRouteSerializer, PickupDropEventSerializer, BusDetailedSerializer,
    RealTimeLocationUpdateSerializer
)
from adminapp.models import ChildModels


class ConductorViewSet(viewsets.ModelViewSet):
    queryset = ConductorModels.objects.all()
    serializer_class = ConductorSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['conductor_name', 'conductor_phone', 'conductor_email']
    ordering_fields = ['conductor_name', 'created_at']
    
    @action(detail=True, methods=['get'])
    def bus(self, request, pk=None):
        """Get the bus assigned to this conductor"""
        conductor = self.get_object()
        try:
            bus = conductor.bus
            serializer = BusDetailedSerializer(bus)
            return Response(serializer.data)
        except:
            return Response({'error': 'No bus assigned'}, status=status.HTTP_404_NOT_FOUND)


class BusViewSet(viewsets.ModelViewSet):
    queryset = BusModels.objects.all()
    serializer_class = BusSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['bus_number', 'bus_route', 'bus_class']
    ordering_fields = ['bus_number', 'bus_status', 'created_at']

    def get_queryset(self):
        qs = super().get_queryset()
        bus_class = self.request.GET.get('bus_class')
        if bus_class:
            qs = qs.filter(bus_class__iexact=bus_class)
        return qs
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BusDetailedSerializer
        return BusSerializer
    
    @action(detail=True, methods=['get'])
    def location_history(self, request, pk=None):
        """Get location history for a bus"""
        bus = self.get_object()
        locations = bus.locations.all()[:100]  # Last 100 locations
        serializer = BusLocationSerializer(locations, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def update_location(self, request, pk=None):
        """Update the current location of the bus (Real-time tracking)"""
        bus = self.get_object()
        serializer = RealTimeLocationUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            data = serializer.validated_data
            
            # Create new location entry
            location = BusLocationModels.objects.create(
                bus=bus,
                latitude=data['latitude'],
                longitude=data['longitude'],
                speed=data.get('speed', 0),
                heading=data.get('heading')
            )

            # Broadcast to channel layer so websocket clients receive update
            try:
                from asgiref.sync import async_to_sync
                from channels.layers import get_channel_layer
                location_serializer = BusLocationSerializer(location)
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f'bus_{bus.bus_id}',
                    {
                        'type': 'location_update',
                        'data': location_serializer.data
                    }
                )
            except Exception:
                pass

            # Return the created location
            location_serializer = BusLocationSerializer(location)
            return Response(location_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def active_status(self, request, pk=None):
        """Get detailed active status of the bus"""
        bus = self.get_object()
        latest_location = bus.locations.first()
        recent_events = bus.events.all()[:10]
        
        data = {
            'bus_id': bus.bus_id,
            'bus_number': bus.bus_number,
            'status': bus.bus_status,
            'conductor': ConductorSerializer(bus.conductor).data if bus.conductor else None,
            'current_location': BusLocationSerializer(latest_location).data if latest_location else None,
            'recent_events': PickupDropEventSerializer(recent_events, many=True).data,
            'total_children_boarded': bus.events.filter(event_type='pickup').count(),
            'total_children_dropped': bus.events.filter(event_type='drop').count(),
        }
        return Response(data)
    
    @action(detail=True, methods=['post'])
    def end_trip(self, request, pk=None):
        """Mark the trip as ended"""
        bus = self.get_object()
        bus.bus_status = 'ended'
        bus.save()
        serializer = self.get_serializer(bus)
        return Response(serializer.data)


class BusLocationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BusLocationModels.objects.all()
    serializer_class = BusLocationSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ['timestamp']
    
    @action(detail=False, methods=['get'])
    def by_bus(self, request):
        """Get locations for a specific bus"""
        bus_id = request.query_params.get('bus_id')
        if not bus_id:
            return Response({'error': 'bus_id parameter is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        locations = BusLocationModels.objects.filter(bus_id=bus_id).order_by('-timestamp')[:100]
        serializer = self.get_serializer(locations, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        """Get the latest location for all active buses"""
        active_buses = BusModels.objects.filter(bus_status='active')
        locations = []
        
        for bus in active_buses:
            latest_location = bus.locations.first()
            if latest_location:
                locations.append(BusLocationSerializer(latest_location).data)
        
        return Response(locations)


class BusRouteViewSet(viewsets.ModelViewSet):
    queryset = BusRouteModels.objects.all()
    serializer_class = BusRouteSerializer
    filter_backends = [SearchFilter]
    search_fields = ['route_name', 'bus__bus_number']
    
    @action(detail=True, methods=['get'])
    def stops(self, request, pk=None):
        """Get all stops in a route"""
        route = self.get_object()
        return Response({'stops': route.route_stops})


class PickupDropEventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PickupDropEvent.objects.all()
    serializer_class = PickupDropEventSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['child__children_name', 'bus__bus_number']
    ordering_fields = ['event_time']
    
    @action(detail=False, methods=['get'])
    def by_child(self, request):
        """Get events for a specific child"""
        child_id = request.query_params.get('child_id')
        if not child_id:
            return Response({'error': 'child_id parameter is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        events = PickupDropEvent.objects.filter(child_id=child_id).order_by('-event_time')
        serializer = self.get_serializer(events, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_bus(self, request):
        """Get all events for a specific bus"""
        bus_id = request.query_params.get('bus_id')
        if not bus_id:
            return Response({'error': 'bus_id parameter is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        events = PickupDropEvent.objects.filter(bus_id=bus_id).order_by('-event_time')
        serializer = self.get_serializer(events, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def create_event(self, request):
        """Create a pickup/drop event"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
