from rest_framework import serializers
from conductorapp.models import (
    BusModels, ConductorModels, BusLocationModels, 
    BusRouteModels, PickupDropEvent
)
from adminapp.models import ChildModels


class ConductorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConductorModels
        fields = ['conductor_id', 'conductor_name', 'conductor_phone', 
                  'conductor_email', 'conductor_address', 'is_active']
        read_only_fields = ['conductor_id']


class BusLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusLocationModels
        fields = ['location_id', 'latitude', 'longitude', 'speed', 
                  'heading', 'timestamp', 'updated_at']
        read_only_fields = ['location_id', 'timestamp', 'updated_at']


class BusRouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusRouteModels
        fields = ['route_id', 'route_name', 'route_stops', 'bus']
        read_only_fields = ['route_id']


class BusSerializer(serializers.ModelSerializer):
    locations = BusLocationSerializer(many=True, read_only=True)
    latest_location = serializers.SerializerMethodField()
    
    class Meta:
        model = BusModels
        fields = ['bus_id', 'bus_number', 'bus_route', 'bus_class', 'bus_status', 
                  'conductor', 'locations', 'latest_location', 'created_at', 'updated_at']
        read_only_fields = ['bus_id', 'created_at', 'updated_at']
    
    def get_latest_location(self, obj):
        latest = obj.locations.first()
        if latest:
            return BusLocationSerializer(latest).data
        return None


class PickupDropEventSerializer(serializers.ModelSerializer):
    child_name = serializers.CharField(source='child.children_name', read_only=True)
    bus_number = serializers.CharField(source='bus.bus_number', read_only=True)
    
    class Meta:
        model = PickupDropEvent
        fields = ['event_id', 'child_name', 'bus_number', 'event_type', 
                  'location_latitude', 'location_longitude', 'event_time', 'parent_notified']
        read_only_fields = ['event_id', 'event_time']


class BusDetailedSerializer(serializers.ModelSerializer):
    conductor_details = ConductorSerializer(source='conductor', read_only=True)
    locations = BusLocationSerializer(many=True, read_only=True)
    recent_events = serializers.SerializerMethodField()
    
    class Meta:
        model = BusModels
        fields = ['bus_id', 'bus_number', 'bus_route', 'bus_class', 'bus_status', 
                  'conductor_details', 'locations', 'recent_events', 'created_at', 'updated_at']
    
    def get_recent_events(self, obj):
        recent_events = obj.events.all()[:10]
        return PickupDropEventSerializer(recent_events, many=True).data


class RealTimeLocationUpdateSerializer(serializers.Serializer):
    bus_id = serializers.IntegerField()
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    speed = serializers.FloatField(required=False, default=0)
    heading = serializers.FloatField(required=False)
    
    def validate_latitude(self, value):
        if not -90 <= value <= 90:
            raise serializers.ValidationError("Latitude must be between -90 and 90")
        return value
    
    def validate_longitude(self, value):
        if not -180 <= value <= 180:
            raise serializers.ValidationError("Longitude must be between -180 and 180")
        return value
