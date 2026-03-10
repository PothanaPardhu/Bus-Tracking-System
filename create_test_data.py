#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qrcodeproject.settings')
django.setup()

from conductorapp.models import BusModels, BusLocationModels

# Get or create two buses for testing
bus1, created = BusModels.objects.get_or_create(bus_number='BUS001', defaults={'bus_route':'Route A', 'bus_class':'1'})
bus2, created2 = BusModels.objects.get_or_create(bus_number='BUS002', defaults={'bus_route':'Route B', 'bus_class':'10'})

# add some locations to bus1 if not many exist
if bus1.locations.count() < 3:
    locations = [
        (19.0760, 72.8777, 25),
        (19.0761, 72.8778, 30),
        (19.0762, 72.8779, 35),
    ]
    for lat, lng, speed in locations:
        BusLocationModels.objects.create(
            bus=bus1,
            latitude=lat,
            longitude=lng,
            speed=speed,
            heading=90
        )
    print(f'✓ Added location records for {bus1.bus_number}')

# add some locations to bus2
if bus2.locations.count() < 3:
    locations2 = [
        (19.0800, 72.8800, 20),
        (19.0805, 72.8805, 22),
        (19.0810, 72.8810, 24),
    ]
    for lat, lng, speed in locations2:
        BusLocationModels.objects.create(
            bus=bus2,
            latitude=lat,
            longitude=lng,
            speed=speed,
            heading=45
        )
    print(f'✓ Added location records for {bus2.bus_number}')

print(f'Bus1: {bus1.bus_number}, route {bus1.bus_route}, locations {bus1.locations.count()}')
print(f'Bus2: {bus2.bus_number}, route {bus2.bus_route}, locations {bus2.locations.count()}')
