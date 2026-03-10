# Quick Start Guide - Real-Time Bus Tracking System

## 🚀 Get Started in 5 Minutes

### Step 1: Verify Installation
```bash
cd "c:\Users\HP\Downloads\MIPL-PMJ-25037 QR SCAN BASED INTELLIGENT SYSTEM FOR SCHOOL BUS TRACKING"
pip list | findstr "django rest framework channels"
```

### Step 2: Run Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 3: Create Test Data
```bash
python manage.py shell

# In the shell:
from conductorapp.models import BusModels, ConductorModels, BusLocationModels

# Create conductor
conductor = ConductorModels.objects.create(
    conductor_name="John Doe",
    conductor_phone="9876543210",
    conductor_email="john@school.com",
    conductor_password="securepass123",
    conductor_address="123 Main Street"
)

# Create bus
bus = BusModels.objects.create(
    bus_number="BUS001",
    bus_route="Home to School Route",
    conductor=conductor,
    bus_status='active'
)

# Add location
location = BusLocationModels.objects.create(
    bus=bus,
    latitude=20.5937,
    longitude=78.9629,
    speed=45.5
)

print("Test data created successfully!")
exit()
```

### Step 4: Start the Server
```bash
# For WebSocket support (Recommended):
daphne -b 0.0.0.0 -p 8000 qrcodeproject.asgi:application

# OR regular Django server:
python manage.py runserver
```

### Step 5: Access Dashboard
- **Admin Tracking**: http://localhost:8000/admin/realtime-tracking/
- **Conductor Dashboard**: http://localhost:8000/conductor-dashboard/
- **Admin Panel**: http://localhost:8000/admin/

---

## 🌟 Key Features to Try

### 1. Real-Time Maps
- Open admin tracking dashboard
- See buses displayed on interactive map
- Click on bus for details
- Watch location updates in real-time (every 5 seconds)

### 2. QR Scanning
- Go to conductor dashboard
- Click "Board Child" button
- Scan a child's QR code
- See child status update immediately

### 3. Live Updates
- Multiple users can see same bus on map
- Location updates broadcast to all users
- No page refresh needed

### 4. API Testing
```bash
# Get all buses
curl http://localhost:8000/api/v1/tracking/buses/

# Update bus location
curl -X POST http://localhost:8000/api/v1/tracking/buses/1/update_location/ \
  -H "Content-Type: application/json" \
  -d '{"latitude": 20.6, "longitude": 78.97, "speed": 50}'

# Get latest locations
curl http://localhost:8000/api/v1/tracking/locations/latest/
```

---

## 📦 Project Structure

```
├── conductorapp/
│   ├── models.py              # ✅ GPS & tracking models
│   ├── serializers.py         # ✅ API serializers
│   ├── api_views.py           # ✅ REST API endpoints
│   ├── consumers.py           # ✅ WebSocket consumers
│   ├── views.py              # ✅ Enhanced views
│   └── urls.py               # ✅ API routing
│
├── assets/template/
│   ├── admin/
│   │   └── realtime-tracking.html    # ✅ Admin dashboard
│   └── conductor/
│       └── conductor-dashboard.html   # ✅ Conductor dashboard
│
├── qrcodeproject/
│   ├── settings.py           # ✅ Updated with new packages
│   ├── urls.py              # ✅ API routes added
│   └── asgi.py              # ✅ WebSocket routing
│
└── REALTIME_TRACKING_GUIDE.md # ✅ Full documentation
```

---

## 🔧 Configuration

### Enable Google Maps (Optional)
```python
# In settings.py
GOOGLE_MAPS_API_KEY = 'your_api_key_here'
```

### Configure Parent Notifications
```python
# In settings.py for SMS
TWILIO_ACCOUNT_SID = 'your_sid'
TWILIO_AUTH_TOKEN = 'your_token'

# For Email
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'your_email@gmail.com'
```

---

## ✅ Verification Checklist

- [ ] All packages installed successfully
- [ ] Migrations ran without errors
- [ ] Server starts without issues
- [ ] Admin dashboard loads on http://localhost:8000/admin/realtime-tracking/
- [ ] Conductor dashboard loads on http://localhost:8000/conductor-dashboard/
- [ ] API endpoints respond with data
- [ ] WebSocket connection works (check browser console)
- [ ] Real-time updates work (buses move on map)
- [ ] QR scanning functionality works

---

## 🎯 Next Steps

1. **Populate Data**: Add real buses and conductors
2. **Test QR Codes**: Generate QR codes for children
3. **Set Up Notifications**: Configure SMS/Email
4. **Mobile App**: Create mobile version for parents
5. **Deployment**: Deploy to production server

---

## 💡 Tips & Tricks

### View Server Logs
```bash
# In another terminal
tail -f qrenv/Scripts/log_file.txt
```

### Reset Database (Development Only)
```bash
python manage.py flush --no-input
python manage.py migrate
```

### Create Superuser
```bash
python manage.py createsuperuser
```

### Generate Dummy Data
```bash
python manage.py shell < generate_test_data.py
```

---

## 🐛 Common Issues

| Issue | Solution |
|-------|----------|
| WebSocket fails | Make sure Daphne is running, not Django dev server |
| Location not updating | Check if POST data is being sent correctly |
| QR not scanning | Verify pyzbar is installed: `pip install pyzbar` |
| Database error | Run `python manage.py migrate` |
| Port 8000 in use | Use different port: `python manage.py runserver 8080` |

---

## 📚 Documentation

- **Full Guide**: See `REALTIME_TRACKING_GUIDE.md`
- **API Docs**: Check `/api/v1/tracking/` endpoints
- **Models**: Review `conductorapp/models.py`
- **WebSocket**: Check `conductorapp/consumers.py`

---

## 🎉 Congratulations!

Your real-time bus tracking system is now ready!

**Key Achievements:**
✅ Real-time GPS tracking with maps
✅ WebSocket live updates
✅ Enhanced QR scanning
✅ REST API for integrations
✅ Admin & Conductor dashboards
✅ Automated parent notifications
✅ Complete documentation

**Ready to go live? Check the deployment section in the full guide!**

---

Need help? Check troubleshooting section in REALTIME_TRACKING_GUIDE.md

Happy tracking! 🚌📍
