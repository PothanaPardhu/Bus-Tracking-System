from django.db import models
from django.utils import timezone
from adminapp.models import *

# Create your models here.
class QRModels(models.Model):
    qrcode=models.ImageField(blank=True,upload_to='media/',null=True)
    
    class Meta:
        db_table='qrcode_data'


class BusModels(models.Model):
    bus_id = models.AutoField(primary_key=True)
    bus_number = models.CharField(max_length=50, unique=True)
    bus_route = models.CharField(max_length=200)
    # class/grade this bus serves (1-10). optional
    bus_class = models.CharField(max_length=5, null=True, blank=True, help_text='Grade/class assigned to this bus')
    conductor = models.OneToOneField('ConductorModels', on_delete=models.CASCADE, null=True, related_name='bus')
    bus_status = models.CharField(max_length=50, default='idle', choices=[
        ('idle', 'Idle'),
        ('active', 'Active'),
        ('ended', 'Trip Ended')
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'bus_data'
    
    def __str__(self):
        return f"Bus {self.bus_number}"


class ConductorModels(models.Model):
    conductor_id = models.AutoField(primary_key=True)
    conductor_name = models.CharField(max_length=100)
    conductor_phone = models.CharField(max_length=15)
    conductor_email = models.EmailField()
    conductor_password = models.CharField(max_length=100)
    conductor_address = models.TextField()
    conductor_image = models.ImageField(upload_to='conductor/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'conductor_data'
    
    def __str__(self):
        return self.conductor_name


class BusLocationModels(models.Model):
    location_id = models.AutoField(primary_key=True)
    bus = models.ForeignKey(BusModels, on_delete=models.CASCADE, related_name='locations')
    latitude = models.FloatField()
    longitude = models.FloatField()
    speed = models.FloatField(default=0)
    heading = models.FloatField(default=0, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'bus_location_data'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.bus.bus_number} - {self.timestamp}"


class BusRouteModels(models.Model):
    route_id = models.AutoField(primary_key=True)
    route_name = models.CharField(max_length=200)
    route_stops = models.JSONField(help_text='Array of stops with lat, lng, name')
    bus = models.ForeignKey(BusModels, on_delete=models.CASCADE, related_name='routes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'bus_route_data'
    
    def __str__(self):
        return self.route_name


class PickupDropEvent(models.Model):
    event_id = models.AutoField(primary_key=True)
    child = models.ForeignKey(ChildModels, on_delete=models.CASCADE, related_name='pickup_drop_events')
    bus = models.ForeignKey(BusModels, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=50, choices=[
        ('pickup', 'Pickup'),
        ('drop', 'Drop')
    ])
    location_latitude = models.FloatField(null=True)
    location_longitude = models.FloatField(null=True)
    event_time = models.DateTimeField(auto_now_add=True)
    parent_notified = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'pickup_drop_event'
        ordering = ['-event_time']
    
    def __str__(self):
        return f"{self.child.children_name} - {self.event_type} - {self.event_time}"