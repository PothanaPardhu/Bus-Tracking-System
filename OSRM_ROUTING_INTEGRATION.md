# OSRM Routing Integration Documentation

## Overview

This document describes the integration of **OSRM (Open Source Routing Machine)** into the School Bus Tracking System. OSRM provides free, real-time route calculation and navigation for vehicles.

## What is OSRM?

**Open Source Routing Machine (OSRM)** is a free, open-source routing engine that calculates the shortest routes between points on Earth. The public OSRM service is available at:
- **API Endpoint**: `http://router.project-osrm.org/route/v1/driving/`
- **Features**: Free to use, no API key required, supports multiple vehicles types
- **Accuracy**: Uses OpenStreetMap data for highly accurate real-world routing

## Implementation Architecture

### 1. **Backend Layer** (`routing_utils.py`)

Location: `userapp/routing_utils.py`

#### Functions Implemented:

**`get_route_coordinates(source_lat, source_lng, dest_lat, dest_lng)`**
- Queries OSRM API for route coordinates
- Converts GeoJSON response to `[[latitude, longitude], ...]` format
- Implements 24-hour caching to reduce API calls
- Returns fallback route (direct line) if API fails
- **Parameters**: Source and destination coordinates (must be valid lat/lng values)
- **Returns**: List of coordinate pairs representing the route

**`calculate_distance(route_coords)`**
- Uses Haversine formula to calculate route distance
- Earth radius: 6371 km
- **Parameters**: List of `[lat, lng]` coordinates
- **Returns**: Distance in kilometers

**`get_route_eta(distance_km, average_speed_kmh=40)`**
- Calculates estimated time of arrival
- Default assumption: 40 km/h average city speed
- **Parameters**: Distance in kilometers, optional speed (km/h)
- **Returns**: ETA in seconds (can be converted to hours/minutes)

### 2. **API Endpoint** (`userapp/views.py`)

#### Route: `/api/v1/routing/calculate_route/`

**Method**: `POST`

**Request Body**:
```json
{
  "source_lat": 20.0044,
  "source_lng": 77.1234,
  "dest_lat": 20.0155,
  "dest_lng": 77.1345
}
```

**Response** (Success):
```json
{
  "success": true,
  "route": [
    [20.0044, 77.1234],
    [20.0050, 77.1240],
    [20.0100, 77.1290],
    [20.0155, 77.1345]
  ],
  "distance_km": 8.45,
  "distance_miles": 5.25,
  "eta_seconds": 762,
  "eta_human": "12m 42s"
}
```

**Response** (Error):
```json
{
  "success": false,
  "error": "Invalid destination coordinates"
}
```

**Error Codes**:
- `400`: Invalid request format or invalid coordinates
- `500`: OSRM API unreachable or server error

### 3. **Frontend Integration** (`user-tracking-realtime.html`)

#### New JavaScript Functions:

**`calculateRouteWithOSRM(destLat, destLng)`**
- Async function that calls the routing API endpoint
- Converts route response to waypoints format
- Updates map display with route visualization
- Handles CSRF token for Django security
- **Returns**: `true` if successful, `false` otherwise

**`animateAlongRoute()`**
- Animates bus marker along the calculated route
- Smooth easing animation (1 second per waypoint)
- Updates progress percentage in real-time
- Alerts user when destination reached
- **Uses**: Smooth easing function (`easeInOutQuad`)

**`getCookie(name)`**
- Helper function to retrieve Django CSRF token
- Required for POST requests to Django API

**`startTrackingToDestination(destKey)`**
- Main entry point for destination tracking
- Looks up predefined destination
- Calculates route via OSRM
- Starts animation automatically
- **Parameters**: Destination key (e.g., 'school_main', 'demo_dest1')

#### Predefined Destinations:

The system includes 5 pre-configured destinations:

```javascript
PREDEFINED_DESTINATIONS = {
  'school_main': {
    name: 'Main School Campus',
    lat: 20.0044,
    lng: 77.1234,
    description: 'Central school building'
  },
  'school_branch1': {...},  // North campus
  'school_branch2': {...},  // South campus
  'demo_dest1': {...},      // Test location 1
  'demo_dest2': {...}       // Test location 2
}
```

### 4. **URL Configuration** (`qrcodeproject/urls.py`)

New route added:
```python
path('api/v1/routing/calculate_route/', userapp_views.api_calculate_route, name='api_calculate_route'),
```

## How It Works (Flow Diagram)

```
User chooses destination
         ↓
   (button onclick)
         ↓
startTrackingToDestination(destKey)
         ↓
calculateRouteWithOSRM(lat, lng)
         ↓
POST /api/v1/routing/calculate_route/
         ↓
  api_calculate_route view
         ↓
get_route_coordinates() [OSRM API call]
         ↓
calculate_distance() [Haversine formula]
         ↓
get_route_eta() [Time calculation]
         ↓
Return JSON response (route, distance, ETA)
         ↓
animateAlongRoute()
         ↓
Smooth animation along route waypoints
         ↓
Bus marker moves to destination
```

## User Interface (Destination Selection)

A new section added to the tracking page:

```html
<!-- Destination Selection -->
<div style="background: #f0f7ff; border-left: 4px solid #667eea;">
  <label>Select Destination for Route Tracking</label>
  <div>
    <button onclick="startTrackingToDestination('school_main')">School Main</button>
    <button onclick="startTrackingToDestination('school_branch1')">Campus North</button>
    <button onclick="startTrackingToDestination('school_branch2')">Campus South</button>
    <button onclick="startTrackingToDestination('demo_dest1')">Demo Dest 1</button>
    <button onclick="startTrackingToDestination('demo_dest2')">Demo Dest 2</button>
  </div>
</div>
```

**Usage**:
1. Parents click on a destination button
2. Route is calculated by OSRM (2-3 seconds)
3. Route displayed on map with distance and ETA
4. Bus marker animates along the route
5. Progress shows percentage completion
6. Alert when destination reached

## Features

### ✅ Implemented

- [x] Free OSRM API integration (no API key needed)
- [x] Real route calculation based on actual road networks
- [x] Distance calculation using Haversine formula
- [x] ETA calculation at configurable speed
- [x] Route caching (24 hours) to reduce API calls
- [x] Smooth bus marker animation along route
- [x] Multiple predefined destinations
- [x] Real-time progress display
- [x] Error handling with fallback to direct line
- [x] CSRF token handling for Django security
- [x] Console debugging with `[ROUTING]` prefix
- [x] Route visualization on Leaflet map

### 🚀 Possible Enhancements

- [ ] User-input custom destinations (not just predefined)
- [ ] Real-time GPS updates instead of animation
- [ ] Multiple bus tracking on same route
- [ ] Route polyline styling (gradient colors for speed)
- [ ] Traffic-aware routing (requires paid OSRM service)
- [ ] Alternative route suggestions
- [ ] Offline caching of routes
- [ ] WebSocket integration for live updates
- [ ] Historical route tracking/playback
- [ ] Multi-stop route optimization

## Configuration

### Speed Assumptions
- **Default**: 40 km/h average city speed
- **Customizable** in `get_route_eta()` function
- Adjust based on local traffic conditions

### Coordinate System
- **Format**: WGS84 (Latitude, Longitude)
- **India Center**: Lat 20.5937, Lng 78.9629
- **Valid Range**: Lat [-90, 90], Lng [-180, 180]

### Caching
- **Duration**: 24 hours
- **Mechanism**: Django cache framework
- **Bypass**: Modify `routing_utils.py` to disable caching

### Distance Units
- **API**: Kilometers
- **Response**: Both km and miles provided
- **Conversion**: 1 km = 0.621371 miles

## Error Handling

### Common Issues and Solutions

**Issue**: "Could not calculate route"
- **Cause**: Invalid coordinates or OSRM API unreachable
- **Solution**: Check coordinates are valid, verify internet connection, try again

**Issue**: "Invalid coordinate values"
- **Cause**: Non-numeric or out-of-range coordinates
- **Solution**: Ensure lat ∈ [-90, 90], lng ∈ [-180, 180]

**Issue**: "Server error calculating route"
- **Cause**: Backend error or OSRM service down
- **Solution**: Check /api/v1/routing/calculate_route/ endpoint logs, retry

**Issue**: OSRM API timing out
- **Cause**: Network latency or OSRM service slow
- **Solution**: Check network connection, fallback to cached route, try again

## Testing

### Manual Testing Steps

1. **Open tracking page**: Navigate to `/user-view-status/`
2. **Verify destination buttons**: All 5 destination buttons visible
3. **Click a destination**: Route should calculate within 2-3 seconds
4. **Check console**: Should show `[ROUTING]` debug messages
5. **Verify map**: Route polyline should appear on the map
6. **Watch animation**: Bus marker should smoothly animate along route
7. **Check distance/ETA**: Should display correct values
8. **Monitor progress**: Percentage should increase from 0% to 100%
9. **Verify completion**: Alert should show when destination reached

### Browser Console Messages

Expected output when selecting a destination:
```
[ROUTING] Starting tracking to: Main School Campus
[ROUTING] Requesting route from OSRM...
[ROUTING] Route calculated: 8.45km, 12m 42s
[ROUTING] Route drawn with 127 waypoints
[ROUTING] Starting route animation with 127 waypoints
[ROUTING] Route Progress: 0% | Waypoint 1/127
[ROUTING] Route Progress: 50% | Waypoint 64/127
[ROUTING] Route Progress: 100% | Waypoint 127/127
[ROUTING] Route animation completed
```

## Performance Considerations

### API Call Frequency
- **Current**: 1 call per destination selection
- **Caching**: Prevents duplicate calls for same route (24 hours)
- **Optimization**: Routes are cached by (source, destination) pair

### Animation Performance
- **Waypoints**: Up to 200+ per route (varies by distance)
- **Animation Speed**: 1 second per waypoint (customizable)
- **Frame Rate**: 60 FPS (uses requestAnimationFrame)
- **Memory**: Minimal (typically <5MB for route data)

### Bandwidth
- **API Request**: ~200 bytes
- **API Response**: 2-5 KB per route (varies)
- **Cached**: ~2 KB per route in database

## Security Considerations

✅ **CSRF Protection**: Django CSRF token included in requests
✅ **Input Validation**: Coordinates validated on backend
✅ **Error Messages**: No sensitive info exposed to client
✅ **Coordinate Range**: Checked to prevent injection attacks

## Dependencies

- **Frontend**: Leaflet.js 1.9.4 (already included)
- **Backend**: 
  - Django (already installed)
  - requests library (for OSRM API calls)
  - Django cache framework (for caching)
- **External**: OSRM public API (free, no key required)

## Troubleshooting

### Route not calculating?
1. Check browser console for error messages
2. Verify coordinates are valid numbers
3. Check internet connection
4. Test OSRM API directly: `http://router.project-osrm.org/route/v1/driving/77.1234,20.0044;77.1345,20.0155`

### Animation choppy or slow?
1. Check browser performance (F12 Performance tab)
2. Reduce number of waypoints (modify OSRM request)
3. Increase animation duration per waypoint
4. Close other browser tabs using GPU

### Buttons not responding?
1. Check browser console for JavaScript errors
2. Verify CSRF token is present
3. Clear browser cache and reload
4. Test GET /api/v1/routing/calculate_route/ first

## References

- **OSRM Documentation**: https://project-osrm.org/docs/v5.5.1/api/stable
- **Leaflet Documentation**: https://leafletjs.com/
- **Django Views**: https://docs.djangoproject.com/en/4.1/topics/http/views/
- **Haversine Formula**: https://en.wikipedia.org/wiki/Haversine_formula

## Files Modified

1. **userapp/routing_utils.py** (NEW) - OSRM API integration functions
2. **userapp/views.py** - Added `api_calculate_route()` endpoint
3. **qrcodeproject/urls.py** - Added route for `/api/v1/routing/calculate_route/`
4. **assets/template/user/user-tracking-realtime.html** - Added OSRM integration JS and UI

## Next Steps

1. **Test the integration**: Open `/user-view-status/` and click destination buttons
2. **Monitor console**: Check browser F12 console for [ROUTING] messages
3. **Verify animations**: Watch bus marker move along routes
4. **Customize destinations**: Edit `PREDEFINED_DESTINATIONS` with actual school locations
5. **Optimize speed**: Adjust `average_speed_kmh` in `get_route_eta()` based on local conditions
6. **Add real GPS**: Replace animation with real bus GPS data when available

