# Maps Not Visible - Complete Troubleshooting Guide

## 🔍 Quick Diagnosis Steps

### STEP 1: Test Basic Map Functionality
1. Double-click **MAP_TEST.html** in Explorer to open it in your browser
2. You should immediately see a map with test location
3. Try the buttons to verify interaction works
4. **If this works** → Maps library is fine, issue is elsewhere
5. **If this doesn't work** → Browser/Leaflet issue (see below)

---

### STEP 2: Check Browser Console for Errors
**On the actual tracking page:**

1. Navigate to: `http://localhost:8000/user-view-status/`
2. Press **F12** to open Developer Tools
3. Click **Console** tab
4. Look for messages starting with **[TRACKER]** - these show what's happening
5. Look for any **RED ERROR** messages
6. Screenshot any errors and note them

**What messages you should see:**
```
[TRACKER] Script loaded
[TRACKER] CONFIG: {DEFAULT_LAT: 20.5937, ...}
[TRACKER] Initializing map...
[TRACKER] Map element found, creating Leaflet instance
[TRACKER] Map initialized successfully
[TRACKER] Setting up map controls
[TRACKER] DOM Content Loaded
```

---

### STEP 3: Check Map Container in Browser Inspector

1. Press **F12** to open Developer Tools
2. Click **Inspector** (or Elements) tab
3. Press **Ctrl+Shift+C** to select element
4. Click on the gray area where map should be
5. Look at the HTML structure - should show:
   ```html
   <div class="map-wrapper">
       <div id="map"></div>
       <div class="map-controls">...</div>
   </div>
   ```
6. Right-click the `<div id="map">` element
7. Choose **Edit as HTML** and verify:
   - It has `width: 100%` and `height: 100%` in inline styles OR CSS
   - It's visible (no `display: none`)
   - It has content loading

---

### STEP 4: Check Network Requests

In Developer Tools, click **Network** tab:

1. Reload the page
2. Look for requests to:
   - ✅ Should load: `leaflet.js` and `leaflet.css` 
   - ✅ Should load: OpenStreetMap tiles (URLs like `tile.openstreetmap.org`)
   - ❌ If any show RED = failed to load

**Common failures:**
- Leaflet CDN down → Try different CDN (see below)
- Network blocked → Check firewall/proxy

---

### STEP 5: Check CSS Override Issue

The existing CSS files might be hiding the map:

```css
/* Your CSS (in user-tracking-realtime.html) */
.map-wrapper {
    height: 600px !important;  /* ← This forces the height */
    background: white !important;
}

#map {
    width: 100% !important;
    height: 100% !important;
}
```

**If still not visible:**
1. Open Browser Inspector (F12)
2. Click on map area
3. In Inspector, find `.map-wrapper` element
4. In right panel under "Computed" style, check:
   - Height should be **600px**
   - Width should be **100%**
   - `display` should be **block** (not none or flex)
   - Background should be **white**

If you see different values, an external CSS is overriding it.

---

## 🔧 Common Fixes

### Fix 1: Map Shows But Empty (Gray/Blank)
**Cause**: Leaflet CSS not loading

**Solution**: Add this to `<head>` FIRST, before other stylesheets:
```html
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
```

### Fix 2: Map Area Visible But No Tiles
**Cause**: OpenStreetMap tiles blocked or slow

**Solution**: You can try alternative tile providers. Replace this in JavaScript:
```javascript
// Current
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap contributors'
}).addTo(state.map);

// Alternative 1: CartoDB
L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    maxZoom: 19,
    attribution: '&copy; CARTO'
}).addTo(state.map);

// Alternative 2: Google Maps (requires API key, not free)
// Alternative 3: Stamen Terrain
L.tileLayer('https://stamen-tiles-{s}.a.ssl.fastly.net/terrain/{z}/{x}/{y}{r}.png', {
    maxZoom: 18,
    attribution: 'Map tiles by Stamen Design'
}).addTo(state.map);
```

### Fix 3: Demo Button Doesn't Work
**Cause**: JavaScript error in setup

**Solution**: 
1. Open browser console (F12)
2. Type: `state.demoMode = true; runDemoTracking();`
3. Press Enter
4. Should show demo bus moving
5. If not, check console for errors

### Fix 4: Conflicting CSS from style.css, style1.css, responsive.css
**Cause**: Old CSS files collapsing the map

**Solution A**: Add this in `<style>` (after line 170 in user-tracking-realtime.html):
```css
/* Force map visibility - override any external styles */
.map-wrapper {
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
    position: relative !important;
    height: 600px !important;
    min-height: 600px !important;
    width: 100% !important;
    background: white !important;
    border: 2px solid #ddd !important;
}

#map {
    display: block !important;
    width: 100% !important;
    height: 100% !important;
    visibility: visible !important;
}
```

**Solution B**: Disable external CSS temporarily for testing:
1. Go to user-tracking-realtime.html line 14-16
2. Comment out the CSS lines:
```html
<!-- 
<link href="{% static 'user/css/style.css' %}" rel="stylesheet" />
<link href="{% static 'user/css/responsive.css' %}" rel="stylesheet" />
<link href="{% static 'user/css/style1.css' %}" rel="stylesheet" />
-->
```
3. Reload page - if map appears, one of those files is the culprit
4. Add back one at a time to find which one

---

## 📝 Information to Collect If Still Not Working

If you try all above steps and maps still not visible, run this in browser console (F12):

```javascript
// Copy the output and send it
console.log('=== DEBUG INFO ===');
console.log('Map created:', state.map !== null);
console.log('Map element exists:', document.getElementById('map') !== null);
console.log('Map container:', document.querySelector('.map-wrapper'));
console.log('Map dimensions:', {
    width: document.getElementById('map')?.offsetWidth,
    height: document.getElementById('map')?.offsetHeight
});
console.log('Leaflet version:', L.version);
console.log('CONFIG:', CONFIG);
console.log('Errors in console above?');
```

**What to send:**
- Screenshots of F12 Console showing [TRACKER] messages
- Output of above debug code
- Which fix you tried and result
- Browser name and version

---

## 🚀 Verification - Map Should Work When:

✅ You see gray map background  
✅ You can zoom in/out with buttons or mouse scroll  
✅ Clicking "Demo" button shows animated bus moving  
✅ Map tiles load and show streets/regions  
✅ Console shows `[TRACKER] Map initialized successfully`  

---

## 📌 Important Notes

1. **First load is slow**: Leaflet and tiles take 2-3 seconds to load
2. **Demo mode works offline**: Doesn't need API connection
3. **Mobile test**: Open on phone to test responsive design
4. **Private browsing**: Can affect CDN loading (try normal mode)

---

## Contact Support With:

If you email for help, include:
1. Screenshot of page with what you see
2. Browser console screenshot (F12 → Console)
3. Which step failed
4. Browser name + version
5. Error messages (if any)
