# 🚌 Bus Tracker - Test & Troubleshooting Guide

## ✅ Quick Start (See the Bus Marker)

### **Option 1: View Demo Marker (EASIEST)**
1. **Open** the user tracking page: `http://localhost:8000/user-view-status/`
2. **Open Browser Console**: Press `F12` then click "Console" tab
3. **Look for** the debug panel (yellow box) that says "🔧 Debug Info"
4. **Click** "Demo Bus (TEST)" button
5. **Result:** You should see a **purple bus marker** on the map at New Delhi (28.6139°N, 77.2090°E)

### **Option 2: Test with Real API Data**
1. **Open** tracking page: `http://localhost:8000/user-view-status/`
2. **In the search box**, enter bus number: `BUS001` (or any bus in your database)
3. **Select** a destination (e.g., "School")
4. **Click** "Track" button
5. **Check Browser Console** (F12) for messages like:
   - `[TRACKER] Loading bus status for: <bus_id>`
   - `[TRACKER] Received bus data: {...}`
   - `[TRACKER] Placing marker at: ...`
6. **Result:** Bus marker should appear on the map (if your bus has location data)

---

## 🔍 Debugging: Why Can't I See the Marker?

### **Step 1: Check Browser Console (F12)**
Open the console and look for these messages:

✅ **Good signs:**
```
🚌 School Bus Tracker Loaded
[INFO] Map is initializing...
[INFO] Map initialized
[TRACKER] Placing marker at: 28.6139, 77.2090, heading: 45
```

❌ **Bad signs:**
```
[ERROR] Failed to fetch bus data
[ERROR] ReferenceError: map is not defined
CORS error
```

### **Step 2: Verify Bus Data Exists**
Open Django shell and check:
```bash
python manage.py shell
```
Then run:
```python
from conductorapp.models import BusModels, BusLocationModels
print(BusModels.objects.count())  # Should show number of buses
print(BusLocationModels.objects.count())  # Should show location records
```

### **Step 3: Test API Directly**
Open in browser: `http://localhost:8000/api/v1/tracking/bus/status/?bus_id=1`

**Expected Response:**
```json
{
  "bus_id": 1,
  "bus_number": "BUS001",
  "status": "active",
  "latest_location": {
    "latitude": 28.6139,
    "longitude": 77.2090,
    "speed": 35.5,
    "heading": 45
  },
  "boarded_count": 5,
  "dropped_count": 0
}
```

**If you get `"latest_location": null`** → No location data for that bus yet. Send test data:

```bash
curl -X POST http://localhost:8000/api/v1/tracking/location-update/ \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 28.6139,
    "longitude": 77.2090,
    "speed": 45.5,
    "heading": 120
  }'
```

---

## 🛠️ Common Issues & Fixes

### **Issue: Map loads but no marker**
- **Cause:** Bus has no location data
- **Fix:** Send location via API or Demo button

### **Issue: Button says "Demo Bus (TEST)" but nothing happens**
- **Cause:** Button might not be visible (debug panel hidden)
- **Fix:** Press `F12` → Console → Look for debug panel at bottom

### **Issue: "Bus Not Found" error**
- **Cause:** Bus number doesn't exist in database
- **Fix:** Check exact bus number in database:
  ```python
  from conductorapp.models import BusModels
  for b in BusModels.objects.all():
      print(b.bus_number)
  ```

### **Issue: Marker appears but doesn't move**
- **Cause:** Marker placed but WebSocket not connected
- **Fix:** Check console for [WS] messages. Polling every 3s is normal fallback.

---

## 📊 Test Data Creation

### **Create a Test Bus with Location**
```bash
python manage.py shell
```

```python
from conductorapp.models import BusModels, BusLocationModels
from django.utils import timezone

# Create bus
bus = BusModels.objects.create(
    bus_number='BUS001',
    bus_route='Delhi - Gurgaon',
    bus_status='active'
)

# Add location
loc = BusLocationModels.objects.create(
    bus=bus,
    latitude=28.6139,
    longitude=77.2090,
    speed=45.5,
    heading=120
)

print(f"Created {bus.bus_number} with location at {loc.latitude}, {loc.longitude}")
```

Then visit: `http://localhost:8000/user-view-status/`
- Enter "BUS001" in search
- Click Track
- **Marker should appear!**

---

## 🎯 Testing Checklist

- [ ] Map loads when page opens
- [ ] Can click "Demo Bus" and see purple marker
- [ ] Console shows `[TRACKER] Placed marker at...` messages
- [ ] Demo marker appears in correct location (New Delhi)
- [ ] Bus search finds bus by number
- [ ] Marker animates when bus moves
- [ ] Speed/Status info updates on screen
- [ ] Map controls work (zoom, center, refresh)

---

## 📱 Browser Requirements

- ✅ Chrome, Firefox, Safari, Edge (all modern versions)
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)
- ✅ JavaScript must be enabled
- ✅ WebSocket support (for live updates)
- ✅ Location permission (for actual GPS tracking)

---

## 🚀 Next Steps

1. **Test Demo Mode** → Click "Demo Bus (TEST)"
2. **Check Console** → Press F12, note any errors
3. **Add Test Bus** → Use Django shell to create bus + location
4. **Search & Track** → Use bus number search
5. **Verify Marker** → Should see purple bus icon on map

---

**Questions?** Check the browser console with `F12` - it logs everything!
