# Quick Testing Guide: Route Navigation Feature

## What to Test

Your bus tracking app now has **animated route navigation**. When you select a destination, the bus marker will smoothly animate from its current location to the destination, following a calculated path.

## Pre-Test Checklist

✅ Django server running (`python manage.py runserver`)
✅ Daphne WebSocket server running (separate terminal)
✅ Database has bus data (see below for creating test data)
✅ Logged into parent/user account

## Test Data Setup

### Option A: Quick Demo (No DB setup needed)
1. Click **"Demo Bus (TEST)"** button (yellow button in debug panel)
2. A test bus marker will appear at New Delhi (28.6139, 77.2090)
3. Skip to "Test Navigation" section below

### Option B: Real Data (Requires database)
Create a test bus with location:
```python
python manage.py shell

# Inside Python shell:
from conductorapp.models import BusModels, BusLocationModels, ConductorModels
from userapp.models import ParentModels

# Create a test bus
bus = BusModels.objects.create(
    bus_number='TEST001',
    bus_route='Test Route',
    bus_status='active'
)

# Set location at Noida
location = BusLocationModels.objects.create(
    bus=bus,
    latitude=28.5355,
    longitude=77.3910,
    speed=0,
    heading=0
)

print(f"Bus created: {bus.bus_number} (ID: {bus.bus_id})")
exit()
```

## Test Navigation

### Step 1: Search for Bus
1. Open http://localhost:8000/user-view-status/
2. In "Bus Number" field, type: `TEST001`
3. Click **"Track"** button (blue button)
4. **Expected Result**: Bus marker appears on map at Noida location

### Step 2: Select Destination
1. From "Destination" dropdown, select **"School"**
2. **Expected Result**: "Start Navigation" button appears (pink/red gradient button)

### Step 3: Start Animated Navigation
1. Click **"Start Navigation"** button
2. **Expected Result**:
   - Dashed blue line appears showing route to School
   - 🏫 School marker appears at destination (top-right of map)
   - Bus marker starts moving smoothly
   - "Stop" button (red) appears, "Start Navigation" hides
   - Distance and ETA appear in info cards

### Step 4: Watch Animation
- Bus smooth animates from Noida (28.5355, 77.3910) to School (28.6292, 77.2197)
- Takes approximately 5 seconds to reach destination
- Bus heading (red arrow) rotates to face direction of travel
- Speed shown as "40 km/h" in info card
- **NOT jerky or teleporting** - should be smooth continuous movement

### Step 5: Verify Route Info
Check the "Route Information" section:
- Bus Route: Shows bus route name
- Destination: Shows selected destination (School)

### Step 6: Stop Navigation
1. Click **"Stop"** button (red)
2. **Expected Result**:
   - Animation halts
   - Dashed route line disappears
   - 🏫 School destination marker disappears
   - Bus marker stays at its current position
   - "Start Navigation" button reappears

### Step 7: Try Other Destinations
1. Select **"Home"** from dropdown
2. Click **"Start Navigation"** again
3. Bus animates to Home location (28.5355, 77.3910)
4. Stop and try other destinations:
   - Stop 1 (28.6195, 77.2310)
   - Stop 2 (28.6089, 77.2275)

## Browser Console Testing (F12)

Open Developer Tools (F12) and check Console tab for debug logs:

```
[NAV] Starting navigation to school {lat: 28.6292, lng: 77.2197, name: 'School', icon: '🏫'}
[NAV] Route generated: 15.5 km, ETA: 24 min
[NAV] Navigation stopped!
```

**What to look for:**
- `[NAV]` logs appear for each navigation action
- No red `Error` messages
- WebSocket logs `[WS] Received location update` as bus moves

## Detailed Test Scenarios

### Test 1: Marker Visibility
**Scenario**: Ensure markers appear correctly
1. Click Demo Bus button
2. **Expected**: 🚌 Bus marker visible on map
3. Select "School" destination
4. Click "Start Navigation"
5. **Expected**: 🏫 School marker visible at marker
6. **Pass**: Both markers clearly visible

### Test 2: Route Line
**Scenario**: Route polyline shows correct path
1. Start navigation to any destination
2. **Expected**: Blue dashed line from current to destination
3. **Pass**: Line is clearly visible and follows logical path

### Test 3: Smooth Animation
**Scenario**: Movement is smooth, not jerky
1. Start navigation to School
2. **Expected**: Bus moves smoothly every 100ms
3. **NOT Expected**: Marker should NOT jump/teleport
4. **Pass**: Smooth continuous motion

### Test 4: Heading Rotation
**Scenario**: Bus arrow points in direction of travel
1. During navigation, watch bus marker
2. Red arrow inside 🚌 emoji should rotate
3. Arrow should point toward next waypoint
4. Should NOT spin randomly
5. **Pass**: Arrow rotates smoothly toward destination

### Test 5: Distance/ETA Accuracy
**Scenario**: Distance and time calculations are reasonable
1. Start navigation
2. Check distance shown (should be 15-20 km for School)
3. Check ETA (should be 20-30 min at 40 km/h)
4. **Pass**: Numbers seem reasonable (not 1 km or 500 km)

### Test 6: Stop Button Works
**Scenario**: Stop button halts animation
1. Start navigation
2. Wait 2-3 seconds
3. Click "Stop" button
4. **Expected**: 
   - Marker stops moving
   - Route line disappears
   - Destination marker disappears
   - Button changes back to "Start Navigation"
5. **Pass**: Animation properly halted

### Test 7: Multiple Routes
**Scenario**: Can navigate to different destinations sequentially
1. Navigate to School, wait 2 sec, click Stop
2. Select "Home", click "Start Navigation"
3. Bus animates to Home location
4. Click Stop
5. Select "Stop 1", click "Start Navigation"
6. Bus animates to Stop 1
7. **Pass**: Works correctly for multiple destinations

### Test 8: Map Controls Work
**Scenario**: While animating, map controls still function
1. Start navigation
2. During animation:
   - Click "+" (zoom in) - should zoom
   - Click "-" (zoom out) - should zoom
   - Click target icon (center on bus) - map should recenter
   - Click refresh - should reload bus data
3. **Pass**: All controls responsive during animation

### Test 9: WebSocket Integration
**Scenario**: Animation works with live WebSocket updates
1. Start navigation to destination
2. If you have conductor app running and sending location updates:
   - Bus should move on real location updates
   - Should blend WebSocket updates with animation
3. **Pass**: No data conflicts, smooth integration

### Test 10: No API Keys Required
**Scenario**: Feature works without external API keys
1. Open map in isolation
2. Route calculation happens instantly
3. No API calls to Google/Mapbox/etc. needed
4. **Pass**: Completely client-side operation

## What's Under the Hood

The animation works by:
1. **Calculating Path**: Generates 50 waypoints from start → destination
2. **Looping Animation**: Every 100ms, moves bus to next waypoint
3. **Updating Heading**: Calculates compass bearing based on next waypoint
4. **Rotating Arrow**: CSS `transform: rotate()` shows direction
5. **Auto-stop**: Animation ends when all waypoints visited

## Troubleshooting

### Problem: "Marker doesn't animate"
**Solution**:
1. Check console (F12) for `[NAV]` logs
2. Verify "Start Navigation" button is visible (destination must be selected)
3. Verify bus marker is visible first (it should show before animation)
4. Try Demo bus button to confirm basic marker works

### Problem: "Bus teleports instead of animating"
**Solution**:
1. Check animation interval (should be 100ms between waypoints)
2. Verify JavaScript is running (check console for errors)
3. Refresh page and try again
4. Try different destination

### Problem: "Route line doesn't appear"
**Solution**:
1. Check if destination coordinates are correct
2. Verify Leaflet map is fully loaded
3. Try zooming to fit bounds manually (button on map)
4. Check console for drawing errors

### Problem: "Buttons don't appear"
**Solution**:
1. Verify bus marker appears first (from Track action)
2. Select a destination from dropdown - buttons appear based on selection
3. Refresh page and try again
4. Check browser console for JavaScript errors (F12)

## Performance Baseline

On normal hardware:
- Route loads: <1 second
- Animation smooth: 60 FPS (browser native)
- Marker rotation: No lag
- Web socket data: <100ms to display

If slower, check:
- Browser developer tools Performance tab
- Other processes consuming CPU
- WebSocket connection (in console, look for messages)

## Next Steps

After route navigation working:

1. **Test with Real Bus Data**
   - Create more test buses in database
   - Have conductor app send location updates
   - Watch routes update in real-time

2. **Test with Real Parents**
   - Have parents/guardians log in
   - Track their children's assigned bus
   - Get feedback on UX

3. **Advanced Testing**
   - Test on mobile devices
   - Test in different browsers
   - Test map edge cases (zoomed out, very far away)

## Quick Checklist to Verify

```
✅ Track button works (bus marker appears)
✅ Destination dropdown shows options
✅ Start Navigation button appears when destination selected
✅ Animation starts (marker moves)
✅ Route line shows (dashed blue)
✅ Destination marker shows (emoji icon)
✅ Heading arrow rotates
✅ Distance/ETA shows correctly
✅ Stop button halts animation
✅ Can chain multiple navigations
✅ Map controls work during animation
✅ No JavaScript errors in console
✅ Works on multiple browsers
```

## Support

See detailed implementation in: **ROUTE_NAVIGATION_GUIDE.md**

Common issues? Check the browser console (F12) - logs will tell you exactly what's happening!
