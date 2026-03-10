from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
import json
import os
import logging

# Image processing
from PIL import Image, ImageDraw
from pyzbar.pyzbar import decode

# Models
from adminapp.models import ChildModels
from conductorapp.models import (
    QRModels, BusModels, ConductorModels, 
    PickupDropEvent, BusLocationModels
)
from conductorapp.utils.qr_tokens import verify_token, TokenValidationError

# Setup logging
logger = logging.getLogger(__name__)


def conductor_index(request):
    """Main conductor dashboard"""
    conductor = None
    bus = None
    
    # Try to get conductor from session or user ID
    if hasattr(request, 'user') and request.user.is_authenticated:
        try:
            conductor = ConductorModels.objects.get(conductor_email=request.user.email)
            bus = conductor.bus
        except ConductorModels.DoesNotExist:
            pass
    
    context = {
        'conductor': conductor,
        'bus': bus,
    }
    return render(request, 'conductor/conductor-index.html', context)


def conductor_dashboard(request):
    """Real-time conductor dashboard with tracking"""
    conductor = None
    bus = None
    
    # Try to get conductor from session or user ID
    if hasattr(request, 'user') and request.user.is_authenticated:
        try:
            conductor = ConductorModels.objects.get(conductor_email=request.user.email)
            bus = conductor.bus
        except ConductorModels.DoesNotExist:
            pass
    
    context = {
        'conductor': conductor,
        'bus': bus,
    }
    return render(request, 'conductor/conductor-dashboard.html', context)


def conductor_home_school(request):
    """Handle QR scanning for home to school (boarding)"""
    context = {'action': 'boarding'}
    
    if request.method == 'POST':
        if 'image' in request.FILES:
            try:
                return handle_qr_scan(request, 'boarding')
            except Exception as e:
                logger.error(f"Error in QR scan: {str(e)}")
                messages.error(request, 'Error processing QR code. Please try again.')
        else:
            messages.error(request, 'No image file provided')
    
    return render(request, 'conductor/conductor-home-school.html', context)


def conductor_school_home(request):
    """Handle QR scanning for school to home (dropping)"""
    context = {'action': 'dropping'}
    
    if request.method == 'POST':
        if 'image' in request.FILES:
            try:
                return handle_qr_scan(request, 'dropping')
            except Exception as e:
                logger.error(f"Error in QR scan: {str(e)}")
                messages.error(request, 'Error processing QR code. Please try again.')
        else:
            messages.error(request, 'No image file provided')
    
    return render(request, 'conductor/conductor-school-home.html', context)


def handle_qr_scan(request, action_type):
    """
    Enhanced QR scanning handler with real-time updates
    action_type: 'boarding' or 'dropping'
    """
    qr_file = request.FILES.get('image')
    
    if not qr_file:
        messages.error(request, 'No image provided')
        return redirect('conductor_home_school' if action_type == 'boarding' else 'conductor_school_home')
    
    # Create temporary QR object
    qr_obj = QRModels.objects.create(qrcode=qr_file)
    qr_path = f'media/{str(qr_obj.qrcode)}'
    
    try:
        # Decode QR code
        decoded_data = decode(Image.open(qr_path))
        
        if not decoded_data:
            messages.error(request, 'Invalid QR code')
            return redirect('conductor_home_school' if action_type == 'boarding' else 'conductor_school_home')
        
        # Extract child ID from QR code
        child_id = decoded_data[0].data.decode('utf-8')
        
        # Get child and bus information
        child = get_object_or_404(ChildModels, pk=child_id)
        
        # Get conductor and bus from session/user
        bus = None
        if hasattr(request, 'user') and request.user.is_authenticated:
            try:
                conductor = ConductorModels.objects.get(conductor_email=request.user.email)
                bus = conductor.bus
            except ConductorModels.DoesNotExist:
                pass
        
        # Get current location (if available)
        current_location = None
        if bus:
            current_location = bus.locations.first()
        
        # Handle boarding
        if action_type == 'boarding':
            child.children_status1 = 'Boarded'
            child.children_status2 = 'In Transit'
            child.save(update_fields=['children_status1', 'children_status2'])
            
            # Create pickup event
            if bus and current_location:
                event = PickupDropEvent.objects.create(
                    child=child,
                    bus=bus,
                    event_type='pickup',
                    location_latitude=current_location.latitude,
                    location_longitude=current_location.longitude,
                    parent_notified=False
                )
                send_parent_notification(child, 'pickup', current_location)
            
            messages.success(request, f'{child.children_name} boarded successfully!')
            return redirect('conductor_boarding_status')
        
        # Handle dropping
        elif action_type == 'dropping':
            child.children_status1 = 'Dropped'
            child.children_status2 = 'At Home' if 'home' in request.path.lower() else 'At School'
            child.save(update_fields=['children_status1', 'children_status2'])
            
            # Create drop event
            if bus and current_location:
                event = PickupDropEvent.objects.create(
                    child=child,
                    bus=bus,
                    event_type='drop',
                    location_latitude=current_location.latitude,
                    location_longitude=current_location.longitude,
                    parent_notified=False
                )
                send_parent_notification(child, 'drop', current_location)
            
            messages.success(request, f'{child.children_name} dropped successfully!')
            return redirect('conductor_drop_status')
    
    except IndexError:
        messages.error(request, 'Failed to decode QR code. Please ensure it\'s a valid QR code.')
    except ChildModels.DoesNotExist:
        messages.error(request, f'Child with ID {child_id} not found in system.')
    except Exception as e:
        logger.error(f"Unexpected error in QR processing: {str(e)}")
        messages.error(request, 'An unexpected error occurred. Please try again.')
    
    finally:
        # Clean up temporary file
        try:
            if os.path.exists(qr_path):
                os.remove(qr_path)
            qr_obj.delete()
        except Exception as e:
            logger.warning(f"Error cleaning up QR file: {str(e)}")
    
    return redirect('conductor_home_school' if action_type == 'boarding' else 'conductor_school_home')


def conductor_bus_delay(request):
    """Handle bus delay updates"""
    if request.method == 'POST':
        delay_status = request.POST.get('delay_status', '')
        delay_minutes = request.POST.get('delay_minutes', 0)
        
        try:
            delay_minutes = int(delay_minutes)
            # Logic to update delay status
            # You can implement SMS notification here
            messages.success(request, f'Bus delay updated: {delay_status} ({delay_minutes} minutes)')
        except ValueError:
            messages.error(request, 'Invalid delay time')
    
    return render(request, 'conductor/conductor-bus-delay-update.html')


def conductor_boarding_status(request):
    """Display children currently boarded on the bus"""
    boarded_children = ChildModels.objects.filter(children_status1='Boarded')
    
    context = {
        'children': boarded_children,
        'status_type': 'boarding',
        'total_count': boarded_children.count(),
    }
    
    return render(request, 'conductor/conductor-boarding-status.html', context)


def conductor_drop_status(request):
    """Display children dropped by the bus"""
    dropped_children = ChildModels.objects.filter(children_status1='Dropped')
    
    context = {
        'children': dropped_children,
        'status_type': 'dropping',
        'total_count': dropped_children.count(),
    }
    
    return render(request, 'conductor/conductor-drop-status.html', context)


@require_http_methods(["GET"])
@require_http_methods(["GET"])
def api_bus_status(request):
    """API endpoint to get current bus status with per-bus counts and recent location history.

    Supports query parameters `bus_id` or `bus_number` to select a specific bus; otherwise uses
    the authenticated conductor's assigned bus or the first available bus.
    """
    try:
        bus = None
        # allow override via query params
        bus_id = request.GET.get('bus_id')
        bus_num = request.GET.get('bus_number')
        if bus_id:
            try:
                bus = BusModels.objects.get(bus_id=bus_id)
            except BusModels.DoesNotExist:
                return JsonResponse({'error': 'Bus not found'}, status=404)
        elif bus_num:
            try:
                bus = BusModels.objects.get(bus_number__iexact=bus_num)
            except BusModels.DoesNotExist:
                return JsonResponse({'error': 'Bus not found'}, status=404)
        else:
            # fall back to conductor's assignment
            if hasattr(request, 'user') and request.user.is_authenticated:
                try:
                    conductor = ConductorModels.objects.get(conductor_email=request.user.email)
                    bus = conductor.bus
                except ConductorModels.DoesNotExist:
                    pass

        # If still no bus, use first available
        if not bus:
            bus = BusModels.objects.first()

        if not bus:
            # No buses in system
            return JsonResponse({
                'bus_id': None,
                'bus_number': None,
                'status': 'none',
                'boarded_count': 0,
                'dropped_count': 0,
                'history': [],
                'latest_location': None,
            })

        # Latest location
        latest_location = bus.locations.first()

        # Compute boarded/dropped for this bus by checking each child's last event
        boarded_count = 0
        dropped_count = 0
        child_ids = PickupDropEvent.objects.filter(bus=bus).values_list('child', flat=True).distinct()
        for cid in child_ids:
            last_event = PickupDropEvent.objects.filter(child=cid).order_by('-event_time').first()
            if not last_event:
                continue
            if last_event.event_type == 'pickup' and last_event.bus_id == bus.bus_id:
                boarded_count += 1
            elif last_event.event_type == 'drop' and last_event.bus_id == bus.bus_id:
                dropped_count += 1

        # Recent history (last 20 points)
        history_qs = BusLocationModels.objects.filter(bus=bus).order_by('-timestamp')[:20]
        history = []
        for loc in reversed(history_qs):
            history.append({
                'latitude': loc.latitude,
                'longitude': loc.longitude,
                'speed': loc.speed,
                'timestamp': loc.timestamp.isoformat(),
            })

        data = {
            'bus_id': bus.bus_id,
            'bus_number': bus.bus_number,
            'status': bus.bus_status,
            'latest_location': {
                'latitude': latest_location.latitude if latest_location else None,
                'longitude': latest_location.longitude if latest_location else None,
                'speed': latest_location.speed if latest_location else 0,
                'timestamp': latest_location.timestamp.isoformat() if latest_location else None,
            } if latest_location else None,
            'boarded_count': boarded_count,
            'dropped_count': dropped_count,
            'history': history,
            'timestamp': timezone.now().isoformat(),
        }

        return JsonResponse(data)
    except ConductorModels.DoesNotExist:
        return JsonResponse({'error': 'Conductor not found'}, status=404)
    except Exception as e:
        logger.error(f"Error in api_bus_status: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["POST"])
def api_update_location(request):
    """API endpoint to update bus location (from GPS/Mobile)
    
    Broadcasts location to WebSocket clients in real-time.
    
    Expected JSON: {
        "latitude": float,
        "longitude": float,
        "speed": float (optional, default=0),
        "heading": float (optional, default=0)
    }
    """
    try:
        data = json.loads(request.body)
        
        conductor = ConductorModels.objects.get(conductor_email=request.user.email)
        bus = conductor.bus
        
        if not bus:
            return JsonResponse({'error': 'No bus assigned'}, status=404)
        
        # Create location entry
        location = BusLocationModels.objects.create(
            bus=bus,
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            speed=data.get('speed', 0),
            heading=data.get('heading')
        )
        
        # Prepare response with location serialized
        location_data = {
            'location_id': location.location_id,
            'latitude': location.latitude,
            'longitude': location.longitude,
            'speed': location.speed,
            'heading': location.heading,
            'timestamp': location.timestamp.isoformat(),
            'bus_id': bus.bus_id,
            'bus_number': bus.bus_number,
        }
        
        # Broadcast update to any connected websocket clients
        try:
            from asgiref.sync import async_to_sync
            from channels.layers import get_channel_layer
            
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'bus_{bus.bus_id}',
                {
                    'type': 'location_update',
                    'data': location_data
                }
            )
            logger.info(f"Broadcast location for bus {bus.bus_number} to WebSocket clients")
        except Exception as e:
            logger.warning(f"Failed to broadcast via WebSocket: {e}")
            # Continue anyway - response will still be sent
        
        return JsonResponse({
            'success': True,
            'location': location_data,
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except ConductorModels.DoesNotExist:
        return JsonResponse({'error': 'Conductor not found'}, status=404)
    except Exception as e:
        logger.error(f"Error in api_update_location: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


# Alias for backward compatibility
def update_location_api(request):
    """Update bus location via API"""
    return api_update_location(request)


def send_parent_notification(child, event_type, location=None):
    """
    Send notification to parent about child pickup/drop
    Implement SMS/Email notification here
    """
    try:
        # TODO: Implement SMS/Email notification
        # You can use Twilio for SMS or Django email backend
        
        message = f"{child.children_name} has been {'picked up' if event_type == 'pickup' else 'dropped off'}"
        
        if location:
            message += f" at {location.latitude:.4f}, {location.longitude:.4f}"
        
        logger.info(f"Parent notification: {message} to {child.children_contact}")
        
        # Mark as notified in database
        event = PickupDropEvent.objects.filter(
            child=child,
            event_type=event_type
        ).latest('event_time')
        event.parent_notified = True
        event.save()
        
    except Exception as e:
        logger.error(f"Error sending parent notification: {str(e)}")


@require_http_methods(["POST"])
def api_assign_bus(request):
    """Assign a bus to the logged-in conductor.

    Expected JSON body: {"bus_id": <id>}.
    """
    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    bus_id = data.get('bus_id')
    if not bus_id:
        return JsonResponse({'error': 'bus_id required'}, status=400)

    try:
        bus_obj = BusModels.objects.get(bus_id=bus_id)
    except BusModels.DoesNotExist:
        return JsonResponse({'error': 'bus not found'}, status=404)

    if not (hasattr(request, 'user') and request.user.is_authenticated):
        return JsonResponse({'error': 'authentication required'}, status=403)

    try:
        conductor = ConductorModels.objects.get(conductor_email=request.user.email)
        bus_obj.conductor = conductor
        bus_obj.save()
        return JsonResponse({'success': True, 'bus_id': bus_obj.bus_id, 'bus_number': bus_obj.bus_number})
    except ConductorModels.DoesNotExist:
        return JsonResponse({'error': 'conductor not found'}, status=404)


@require_http_methods(["POST"])
def api_scan_token(request):
    """API endpoint: accept signed token, verify it, and create pickup/drop event.

    Expected JSON body: {"token": "<token>", "event": "pickup"|"drop", "bus_number": "BUS001" (optional)}
    If the request is authenticated and the user is a conductor, their bus will be used.
    """
    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    token = data.get('token')
    event_type = data.get('event')
    bus_number = data.get('bus_number')

    if not token or event_type not in ('pickup', 'drop'):
        return JsonResponse({'error': 'Missing token or invalid event type'}, status=400)

    try:
        payload = verify_token(token)
    except TokenValidationError as e:
        return JsonResponse({'error': f'token invalid: {e}'}, status=400)

    obj_type = payload.get('t')
    obj_id = payload.get('id')

    # Handle bus tokens (assign bus to conductor) or student tokens
    if obj_type == 'bus':
        # find bus by bus_number string
        try:
            bus_obj = BusModels.objects.filter(bus_number__iexact=obj_id).first()
            if not bus_obj:
                return JsonResponse({'error': 'bus not found'}, status=404)
        except Exception:
            return JsonResponse({'error': 'bus not found'}, status=404)

        # If authenticated conductor, assign bus to them
        if hasattr(request, 'user') and request.user.is_authenticated:
            try:
                conductor = ConductorModels.objects.get(conductor_email=request.user.email)
                # assign bus to conductor
                bus_obj.conductor = conductor
                bus_obj.save()
                return JsonResponse({'success': True, 'bus_id': bus_obj.bus_id, 'bus_number': bus_obj.bus_number})
            except ConductorModels.DoesNotExist:
                pass

        # If not authenticated, just return bus info
        return JsonResponse({'bus_id': bus_obj.bus_id, 'bus_number': bus_obj.bus_number})

    # student token handling (existing)
    try:
        child = ChildModels.objects.get(pk=int(obj_id))
    except Exception:
        return JsonResponse({'error': 'child not found'}, status=404)

    # Resolve bus: prefer authenticated conductor's bus, else use provided bus_number
    bus = None
    if hasattr(request, 'user') and request.user.is_authenticated:
        try:
            conductor = ConductorModels.objects.get(conductor_email=request.user.email)
            bus = conductor.bus
        except ConductorModels.DoesNotExist:
            pass

    if not bus and bus_number:
        try:
            bus = BusModels.objects.get(bus_number=bus_number)
        except BusModels.DoesNotExist:
            return JsonResponse({'error': 'bus not found'}, status=404)

    # Get current location if available
    current_location = None
    if bus:
        current_location = bus.locations.first()

    # Update child status and create event
    try:
        if event_type == 'pickup':
            child.children_status1 = 'Boarded'
            child.children_status2 = 'In Transit'
            child.save(update_fields=['children_status1', 'children_status2'])
        else:
            child.children_status1 = 'Dropped'
            child.children_status2 = 'At Home'
            child.save(update_fields=['children_status1', 'children_status2'])

        event = PickupDropEvent.objects.create(
            child=child,
            bus=bus if bus else None,
            event_type='pickup' if event_type == 'pickup' else 'drop',
            location_latitude=current_location.latitude if current_location else None,
            location_longitude=current_location.longitude if current_location else None,
            parent_notified=False
        )

        # optionally send notification
        try:
            send_parent_notification(child, event.event_type, current_location)
        except Exception:
            pass

        return JsonResponse({'success': True, 'event_id': event.event_id})

    except Exception as e:
        logger.error(f"Error creating pickup/drop event: {e}")
        return JsonResponse({'error': str(e)}, status=500)
