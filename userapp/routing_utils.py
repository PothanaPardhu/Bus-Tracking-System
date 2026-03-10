"""
Utility functions for route calculation using OSRM (Open Source Routing Machine)
Provides free routing without API keys
"""

import requests
from django.core.cache import cache
import json

OSRM_API_URL = "http://router.project-osrm.org/route/v1/driving"


def get_route_coordinates(source_lat, source_lng, dest_lat, dest_lng):
    """
    Get route coordinates from source to destination using OSRM API
    
    Args:
        source_lat: Source latitude
        source_lng: Source longitude
        dest_lat: Destination latitude
        dest_lng: Destination longitude
    
    Returns:
        List of [lat, lng] coordinates representing the route
    """
    try:
        # Create cache key to avoid repeated API calls
        cache_key = f"route_{source_lng:.4f}_{source_lat:.4f}_{dest_lng:.4f}_{dest_lat:.4f}"
        cached_route = cache.get(cache_key)
        
        if cached_route:
            return cached_route
        
        # OSRM expects coordinates as lng,lat (not lat,lng)
        url = f"{OSRM_API_URL}/{source_lng},{source_lat};{dest_lng},{dest_lat}"
        
        params = {
            "overview": "full",
            "geometries": "geojson",
            "steps": "false",
            "annotations": "distance,duration"
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code != 200:
            raise Exception(f"OSRM API Error: {response.status_code}")
        
        data = response.json()
        
        if not data.get('routes') or len(data['routes']) == 0:
            raise Exception("No route found")
        
        # Extract coordinates from GeoJSON
        coordinates = data['routes'][0]['geometry']['coordinates']
        
        # Convert from [lng, lat] to [[lat, lng], ...] for Leaflet
        route_coords = [[coord[1], coord[0]] for coord in coordinates]
        
        # Cache the route for 24 hours
        cache.set(cache_key, route_coords, 86400)
        
        return route_coords
        
    except requests.exceptions.RequestException as e:
        print(f"OSRM Request Error: {e}")
        # Return direct line if API fails
        return [[source_lat, source_lng], [dest_lat, dest_lng]]
    except Exception as e:
        print(f"Route Error: {e}")
        # Fallback to direct line
        return [[source_lat, source_lng], [dest_lat, dest_lng]]


def calculate_distance(route_coords):
    """
    Calculate total distance of route in km using Haversine formula
    
    Args:
        route_coords: List of [lat, lng] coordinates
    
    Returns:
        Distance in kilometers
    """
    import math
    
    if not route_coords or len(route_coords) < 2:
        return 0
    
    total_distance = 0
    R = 6371  # Earth's radius in km
    
    for i in range(len(route_coords) - 1):
        lat1, lng1 = route_coords[i]
        lat2, lng2 = route_coords[i + 1]
        
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)
        
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(delta_lng / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        total_distance += R * c
    
    return round(total_distance, 2)


def get_route_eta(distance_km, average_speed_kmh=40):
    """
    Calculate ETA based on distance and average speed
    
    Args:
        distance_km: Distance in kilometers
        average_speed_kmh: Average speed in km/h (default: 40 for city traffic)
    
    Returns:
        Dict with hours, minutes, and total_seconds
    """
    if distance_km <= 0 or average_speed_kmh <= 0:
        return {"hours": 0, "minutes": 0, "total_seconds": 0}
    
    total_seconds = int((distance_km / average_speed_kmh) * 3600)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    
    return {
        "hours": hours,
        "minutes": minutes,
        "total_seconds": total_seconds
    }
