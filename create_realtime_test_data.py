#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qrcodeproject.settings')
django.setup()

from adminapp.models import ChildModels
from conductorapp.models import BusModels, PickupDropEvent
from django.utils import timezone
import random

# Get the existing bus
bus = BusModels.objects.first()

if bus:
    # Create test children
    child_names = [
        "Aarav Sharma", "Ishita Gupta", "Rohan Patel",
        "Zara Khan", "Arjun Singh", "Priya Verma",
        "Vikram Yadav", "Neha Iyer", "Karan Nair"
    ]
    
    children = []
    for name in child_names:
        try:
            child = ChildModels.objects.create(
                children_name=name,
                children_contact="9876543210",
                children_email=f"{name.lower().replace(' ', '.')}@school.com",
                children_mothername="Mother",
                children_fathername="Father",
                children_address="School Address",
                children_class="12",
                children_status1="At Home",
                children_status2="Waiting"
            )
            children.append(child)
            print(f"✓ Created child: {name}")
        except Exception as e:
            print(f"Error creating {name}: {e}")
    
    if children:
        # Simulate some boarding events
        boarded_count = random.randint(3, 6)
        for i in range(boarded_count):
            child = children[i]
            location = bus.locations.first()
            if location:
                event = PickupDropEvent.objects.create(
                    child=child,
                    bus=bus,
                    event_type='pickup',
                    location_latitude=location.latitude,
                    location_longitude=location.longitude,
                    parent_notified=True
                )
                child.children_status1 = 'Boarded'
                child.children_status2 = 'In Transit'
                child.save()
                print(f"✓ {child.children_name} - Boarded at {location.timestamp.strftime('%H:%M:%S')}")
        
        # Simulate some drop events
        dropped_count = random.randint(1, 3)
        for i in range(dropped_count):
            if i + boarded_count < len(children):
                child = children[i + boarded_count]
                location = bus.locations.last()
                if location:
                    event = PickupDropEvent.objects.create(
                        child=child,
                        bus=bus,
                        event_type='drop',
                        location_latitude=location.latitude,
                        location_longitude=location.longitude,
                        parent_notified=True
                    )
                    child.children_status1 = 'Dropped'
                    child.children_status2 = 'At Home'
                    child.save()
                    print(f"✓ {child.children_name} - Dropped at {location.timestamp.strftime('%H:%M:%S')}")
    
    print(f"\n✓ Real-time test data created:")
    print(f"  Total Children: {len(children)}")
    print(f"  Boarded: {boarded_count}")
    print(f"  Dropped: {dropped_count}")
    print(f"  Bus: {bus.bus_number}")
    print(f"\nRefresh conductor-dashboard/ to see real-time updates!")
else:
    print("No bus found. Run create_test_data.py first.")
