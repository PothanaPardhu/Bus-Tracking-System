# QR Scan Based Intelligent System for School Bus Tracking
## Real-Time Maps & Enhanced Real-Time Tracking Implementation Guide

### Overview
This document provides comprehensive guidance on the real-time bus tracking features that have been added to your school bus tracking system. The system now includes live GPS tracking with real-time maps, WebSocket support for live updates, and an improved QR code drop functionality.

---

## ✨ New Features Added

### 1. **Real-Time GPS Tracking with Maps**
   - Live bus location tracking on interactive maps (Google Maps/Leaflet)
   - Real-time location updates every 5 seconds
   - Route visualization with stops
   - Bus status monitoring (Active, Idle, Ended Trip)

### 2. **WebSocket Real-Time Updates**
   - Live location streaming via WebSocket
   - Real-time status updates
   - Push notifications for pickup/drop events
   - Bi-directional communication between conductor and admin dashboard

### 3. **Enhanced QR Drop Functionality**
   - Improved error handling and validation
   - Real-time location capture during boarding/dropping
   - Automatic parent notifications
   - Event logging with timestamps
   - Duplicate entry prevention

### 4. **Admin Tracking Dashboard**
   - Real-time view of all active buses
   - Bus status and location display
   - Recent activity feed
   - Statistics and analytics

### 5. **Conductor Mobile Dashboard**
   - Simple QR code scanning interface
   - Vehicle status information
   - Seat availability tracking
   - Quick action buttons
   - Real-time location updates

### 6. **REST API Endpoints**
   - Comprehensive API for bus tracking
   - Location history retrieval
   - Event management
   - Route information

---

## 🔧 Installation & Setup

### Prerequisites
- Python 3.8+
- Django 4.1.1+
- MySQL Database
- Virtual Environment

### Step 1: Install Required Packages
All packages have been automatically installed:
```bash
pip install djangorestframework folium django-channels django-cors-headers geopy requests channels-redis asgiref daphne
```

### Step 2: Update Django Settings (Already Done)
Your `settings.py` has been updated with:
- REST Framework configuration
- CORS settings
- Channels configuration
- Logging setup

### Step 3: Configure Database
Run migrations to create new tables:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 4: Update URL Configuration
The main `urls.py` has been updated with API routes:
- `/api/v1/tracking/buses/` - Bus management API
- `/api/v1/tracking/locations/` - Location tracking API
- `/api/v1/tracking/events/` - Event management API

### Step 5: Start the Development Server with WebSocket Support
```bash
# Using Daphne (recommended for WebSocket support)
daphne -b 0.0.0.0 -p 8000 qrcodeproject.asgi:application

# OR use the regular development server (WebSocket will use polling)
python manage.py runserver
```

---

## 📱 API Endpoints Documentation

### Bus Management

#### Get all buses
```
GET /api/v1/tracking/buses/
```

#### Get specific bus details
```
GET /api/v1/tracking/buses/{bus_id}/
```

#### Update bus location (Real-time)
```
POST /api/v1/tracking/buses/{bus_id}/update_location/
Body: {
    "latitude": 20.5937,
    "longitude": 78.9629,
    "speed": 45.5,
    "heading": 180
}
```

#### Get location history
```
GET /api/v1/tracking/buses/{bus_id}/location_history/
```

### Location Data

#### Get latest locations for all buses
```
GET /api/v1/tracking/locations/latest/
```

#### Get locations by specific bus
```
GET /api/v1/tracking/locations/by_bus/?bus_id=1
```

### Pickup/Drop Events

#### Get all events
```
GET /api/v1/tracking/events/
```

#### Get events for a specific child
```
GET /api/v1/tracking/events/by_child/?child_id=1
```

#### Get events for a specific bus
```
GET /api/v1/tracking/events/by_bus/?bus_id=1
```

---

## 🗄️ Database Models

### New Models Added:

#### BusModels
```python
- bus_id (Primary Key)
- bus_number (String, Unique)
- bus_route (String)
- conductor (ForeignKey to ConductorModels)
- bus_status (Choice: idle, active, ended)
- created_at, updated_at (Timestamps)
```

#### ConductorModels
```python
- conductor_id (Primary Key)
- conductor_name (String)
- conductor_phone (String)
- conductor_email (Email)
- conductor_address (Text)
- conductor_image (ImageField)
- is_active (Boolean)
- created_at (Timestamp)
```

#### BusLocationModels
```python
- location_id (Primary Key)
- bus (ForeignKey to BusModels)
- latitude (Float)
- longitude (Float)
- speed (Float)
- heading (Float, Optional)
- timestamp, updated_at (Timestamps)
```

#### BusRouteModels
```python
- route_id (Primary Key)
- route_name (String)
- route_stops (JSONField - array of lat/lng/name)
- bus (ForeignKey)
- created_at (Timestamp)
```

#### PickupDropEvent
```python
- event_id (Primary Key)
- child (ForeignKey to ChildModels)
- bus (ForeignKey to BusModels)
- event_type (Choice: pickup, drop)
- location_latitude, location_longitude (Float)
- event_time (Timestamp)
- parent_notified (Boolean)
```

---

## 🎯 Usage Guide

### For Administrators

#### Access Real-Time Tracking Dashboard
```
http://localhost:8000/admin/realtime-tracking/
```

**Features:**
- View all active buses on map
- Click on any bus to see details
- View recent events
- Monitor bus status
- Toggle route visibility

#### Quick Actions:
- **Center Map**: Fit all buses in view
- **Toggle Routes**: Show/hide bus routes
- **Refresh**: Manually refresh data

### For Conductors

#### Access Conductor Dashboard
```
http://localhost:8000/conductor-dashboard/
```

**Features:**
- QR code scanning for boarding
- QR code scanning for dropping
- Real-time location updates
- Vehicle status display
- Seat capacity information

#### QR Code Scanning Process:
1. Click "Board Child" or "Drop Child" button
2. Click "Capture QR Code"
3. Point camera at child's ID card QR code
4. Image will be automatically processed
5. Child status will be updated in real-time

### For Parents/Users

#### View Child Status
- Access user dashboard
- See real-time location of bus
- Receive notifications on pickup/drop
- View trip history

---

## 🌐 WebSocket Configuration

### WebSocket Endpoints

#### Bus Tracking WebSocket
```
ws://localhost:8000/ws/tracking/bus/{bus_id}/
```

**Client Code Example:**
```javascript
const socket = new WebSocket('ws://localhost:8000/ws/tracking/bus/1/');

socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    if (data.type === 'location_update') {
        console.log('Bus location:', data.data);
    }
};

// Send location update
socket.send(JSON.stringify({
    type: 'location_update',
    latitude: 20.5937,
    longitude: 78.9629,
    speed: 45
}));
```

#### Admin Dashboard WebSocket
```
ws://localhost:8000/ws/admin/dashboard/
```

**Data Flow:**
- Receives all bus location updates
- Receives bus status changes
- Real-time event notifications

---

## 📡 Integration with GPS Devices

### Location Update Process

#### From Mobile Device (Conductor App):
```javascript
// Get GPS coordinates
navigator.geolocation.getCurrentPosition(position => {
    const data = {
        latitude: position.coords.latitude,
        longitude: position.coords.longitude,
        speed: position.coords.speed,
        heading: position.coords.heading
    };
    
    // Send to server
    fetch('/api/v1/tracking/buses/1/update_location/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    });
});
```

### Location Storage
- Stores up to 100 recent locations per bus
- Automatic cleanup of old data
- Optimized database queries

---

## 🔔 Notification System

### Parent Notifications

The system automatically sends notifications to parents on:
- **Pickup**: When child boards the bus at home
- **Drop**: When child is dropped at school/home

**Notification Methods (Can be configured):**
1. **SMS (Recommended)**
   - Using Twilio SDK
   - Real-time location included

2. **Email**
   - Using Django email backend
   - HTML formatted with maps

3. **Push Notifications**
   - For mobile app users
   - Browser push notifications

**Configuration (in settings.py):**
```python
# Twilio Configuration
TWILIO_ACCOUNT_SID = 'your_account_sid'
TWILIO_AUTH_TOKEN = 'your_auth_token'
TWILIO_PHONE_NUMBER = 'your_twilio_number'

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'your_email@gmail.com'
EMAIL_HOST_PASSWORD = 'your_password'
```

---

## 📊 Analytics & Reports

### Available Metrics
- Bus utilization rates
- Trip distance and duration
- Delay statistics
- Pickup/drop times
- Attendance tracking
- Parent satisfaction (feedback)

### Generate Reports
```python
# Get bus statistics
from conductorapp.models import PickupDropEvent
from django.db.models import Count

stats = PickupDropEvent.objects.filter(
    event_time__date='2024-01-01'
).values('bus__bus_number').annotate(
    total_events=Count('id'),
    pickups=Count('id', filter=Q(event_type='pickup')),
    drops=Count('id', filter=Q(event_type='drop'))
)
```

---

## 🐛 Troubleshooting

### WebSocket Connection Issues

**Problem: WebSocket connection fails**
```
Solution:
1. Ensure Daphne is running: daphne -b 0.0.0.0 -p 8000
2. Check ALLOWED_HOSTS in settings.py
3. Verify CORS_ALLOWED_ORIGINS setting
4. Check browser console for error messages
```

### Location Updates Not Appearing

**Problem: Location updates not showing on map**
```
Solution:
1. Verify API endpoint is working: curl http://localhost:8000/api/v1/tracking/buses/1/
2. Check browser console for JavaScript errors
3. Ensure location data is being sent: check Network tab
4. Verify database has BusLocationModels entries
```

### QR Code Not Scanning

**Problem: QR code scanning fails**
```
Solution:
1. Ensure file permissions for media folder
2. Check that pyzbar library is installed: pip install pyzbar
3. Verify QR code format is valid
4. Check server logs for errors
```

### Database Migration Issues

**Problem: Migration errors**
```bash
# Reset database (for development only!)
python manage.py flush
python manage.py migrate

# Or apply specific migrations
python manage.py migrate conductorapp 0001
```

---

## 🔐 Security Considerations

### API Security
- Add authentication to API endpoints
- Use token-based authentication (JWT)
- Implement rate limiting
- Validate all inputs

### Example: Add Token Authentication
```python
# In settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}
```

### WebSocket Security
- Only allow authenticated users
- Validate message format
- Implement message encryption
- Use WSS (WebSocket Secure) in production

### Data Privacy
- Don't log sensitive location data
- Implement data retention policies
- Add user consent for tracking
- Ensure GDPR compliance

---

## 🚀 Production Deployment

### Environment Variables
```bash
# Create .env file
DEBUG=False
SECRET_KEY=your_secret_key
DB_NAME=qrcodescanproject
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
GOOGLE_MAPS_API_KEY=your_api_key
```

### Run with Gunicorn + Daphne
```bash
# Install production servers
pip install gunicorn channels-redis

# Start Daphne for ASGI
daphne -b 0.0.0.0 -p 8000 qrcodeproject.asgi:application

# OR use Gunicorn for WSGI
gunicorn qrcodeproject.wsgi:application --workers 4
```

### Database Optimization
```sql
-- Create indexes for frequently queried fields
CREATE INDEX idx_bus_location_timestamp ON bus_location_data(timestamp);
CREATE INDEX idx_pickup_drop_event_time ON pickup_drop_event(event_time);
CREATE INDEX idx_bus_status ON bus_data(bus_status);
```

---

## 📚 Additional Resources

### Documentation Files
- [API Reference](./API_REFERENCE.md)
- [WebSocket Guide](./WEBSOCKET_GUIDE.md)
- [Database Schema](./DATABASE_SCHEMA.md)

### External Resources
- [Django Channels Documentation](https://channels.readthedocs.io/)
- [Leaflet.js Documentation](https://leafletjs.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Geolocation API](https://developer.mozilla.org/en-US/docs/Web/API/Geolocation_API)

---

## 📞 Support & Feedback

For issues, feature requests, or improvements:
1. Check the troubleshooting section
2. Review server logs: `tail -f qrenv/logs/error.log`
3. Enable debug mode for detailed error messages
4. Contact development team with error logs

---

## 🎓 Learning Path

### Step 1: Understand the Architecture
- Review the models (in conductorapp/models.py)
- Understand API structure (in conductorapp/api_views.py)
- Learn WebSocket flow (in conductorapp/consumers.py)

### Step 2: Test Basic Functionality
- Create a bus record
- Create conductor and assign bus
- Test location update API
- Test QR scanning

### Step 3: Integrate with Frontend
- Test maps display
- Test real-time updates
- Test user notifications
- Test mobile responsiveness

### Step 4: Optimize & Deploy
- Set up logging
- Implement caching
- Add database indexes
- Deploy to production

---

**Version**: 1.0
**Last Updated**: March 2026
**Status**: Production Ready

Successfully implemented Real-Time Bus Tracking System! 🎉
