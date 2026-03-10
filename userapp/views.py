from django.shortcuts import render,redirect
from userapp.models import *
from adminapp.models import *
from textblob import TextBlob
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
from userapp.routing_utils import get_route_coordinates, calculate_distance, get_route_eta



# Create your views here.

def user_index(request):
    return render(request,'user/user-index.html')


def user_about(request):    
    return render(request,'user/user-about.html')

def user_feedback(request):
    user_id = request.session.get('c_id')
    if not user_id:
        return redirect('user_index')
    user = ChildModels.objects.get(c_id=user_id)

    # user=ChildModels.objects.get(user_id=c_id)
    # c_id=request.session['c_id']
    if request.method == "POST":
        rating=request.POST.get("rating")
        text=request.POST.get("text")
        
        analysis = TextBlob(text)

        sentiment = ''
        if analysis.polarity >= 0.5:
            sentiment = 'Very Positive'
        elif analysis.polarity > 0 and analysis.polarity < 0.5:
            sentiment = 'Positive'
        elif analysis.polarity < 0 and analysis.polarity > -0.5:
            sentiment = 'Negative'
        elif analysis.polarity <= -0.5:
            sentiment = 'Very Negative'
        else:
            sentiment = 'Neutral'

        print(sentiment)
        user_feedback = UserFeedbackModel.objects.create(rating=rating,text=text,userfeedback=user,sentiment=sentiment)
        user_feedback.save()


        messages.success(request,"Successfully Sent")   
    return render(request,'user/user-feedback.html')


def user_myprofile(request):
    user_id = request.session.get('c_id')
    if not user_id:
        return redirect('user_index')
    user = ChildModels.objects.get(c_id=user_id)

    print(user)
    

    if request.method =="POST"and request.FILES['image']:
        name=request.POST.get('name')
        childclass=request.POST.get('class')
        mothername=request.POST.get('mothername')
        fathername=request.POST.get('fathername')
        email=request.POST.get('email')
        contact=request.POST.get('contact')
        address=request.POST.get('address')
        childid=request.POST.get('childid')
        password=request.POST.get('password')
        image=request.FILES['image']
        print(image)
       
      
        if len(request.FILES)!=0:
            image=request.FILES['image']
            user.children_rollnum=childid
            user.children_name=name
            user.children_email=email
            user.children_password=password
            user.children_mothername=mothername
            user.children_fathername=fathername
            user.children_contact=contact
            user.children_class=childclass
            user.children_image=image
            user.children_address=address
            user.save()
        
        else:
            user.children_name=name
            user.children_rollnum=childid
            user.children_email=email
            user.children_password=password
            user.children_mothername=mothername
            user.children_fathername=fathername
            user.children_contact=contact
            user.children_class=childclass
            user.children_image=image
            user.children_address=address
            user.save()
    print(user.children_image,'ggg')
    return render(request,'user/user-myprofile.html',{'user':user})


def user_view_status(request):
    """
    Real-time bus tracking view for parents/users.
    Shows live bus location, speed, and allows searching by bus number or destination.
    """
    user_id = request.session.get('c_id')
    if not user_id:
        return redirect('user_index')
    
    bus_id = None
    initial_lat = 20.0
    initial_lng = 78.0
    
    try:
        child = ChildModels.objects.get(c_id=user_id)
        # Try to get the bus from the child's last event
        last_event = child.pickup_drop_events.order_by('-event_time').first()
        if last_event:
            bus_id = last_event.bus.bus_id
            if last_event.location_latitude and last_event.location_longitude:
                initial_lat = last_event.location_latitude
                initial_lng = last_event.location_longitude
    except ChildModels.DoesNotExist:
        pass
    
    context = {
        'bus_id': bus_id,
        'lat': initial_lat,
        'lng': initial_lng,
        'user_id': user_id,
    }
    
    return render(request, 'user/user-tracking-realtime.html', context)


def user_changepassword(request):
    
    user_id = request.session.get('c_id')
    if not user_id:
        return redirect('user_index')
    user = ChildModels.objects.get(c_id=user_id)
    if request.method=="POST":
        oldpassword=request.POST.get('oldpassword')
        newpassword=request.POST.get('newpassword')
        confirmpassword=request.POST.get('confirmpassword')
        print(oldpassword,newpassword,confirmpassword)

        print(user)
        user.children_password=newpassword
        user.save()

    return render(request,'user/user-changepassword.html')


@csrf_exempt
@require_http_methods(["POST"])
def api_calculate_route(request):
    """
    API endpoint for calculating route between source and destination.
    Uses free OSRM (Open Source Routing Machine) API.
    
    Request body: {
        "source_lat": float,
        "source_lng": float,
        "dest_lat": float,
        "dest_lng": float
    }
    
    Response: {
        "success": boolean,
        "route": [[lat, lng], ...],  # Array of route waypoints
        "distance_km": float,         # Total distance in kilometers
        "distance_miles": float,      # Total distance in miles
        "eta_seconds": int,           # Estimated time in seconds at 40km/h
        "eta_human": "string"         # Human readable ETA (e.g., "15 mins 30 secs")
    }
    """
    try:
        data = json.loads(request.body)
        
        source_lat = float(data.get('source_lat'))
        source_lng = float(data.get('source_lng'))
        dest_lat = float(data.get('dest_lat'))
        dest_lng = float(data.get('dest_lng'))
        
        # Validate coordinates
        if not (-90 <= source_lat <= 90 and -180 <= source_lng <= 180):
            return JsonResponse({
                'success': False,
                'error': 'Invalid source coordinates'
            }, status=400)
        
        if not (-90 <= dest_lat <= 90 and -180 <= dest_lng <= 180):
            return JsonResponse({
                'success': False,
                'error': 'Invalid destination coordinates'
            }, status=400)
        
        # Get route from OSRM
        route_coords = get_route_coordinates(source_lat, source_lng, dest_lat, dest_lng)
        
        if not route_coords or len(route_coords) == 0:
            return JsonResponse({
                'success': False,
                'error': 'Could not calculate route'
            }, status=500)
        
        # Calculate distance and ETA
        distance_km = calculate_distance(route_coords)
        distance_miles = distance_km * 0.621371
        eta_dict = get_route_eta(distance_km)
        
        # Extract ETA values from returned dictionary
        eta_seconds = eta_dict['total_seconds']
        hours = eta_dict['hours']
        minutes = eta_dict['minutes']
        
        # Human readable ETA
        if hours > 0:
            eta_human = f"{hours}h {minutes}m"
        elif minutes > 0:
            eta_human = f"{minutes}m"
        else:
            eta_human = f"{eta_seconds}s"
        
        return JsonResponse({
            'success': True,
            'route': route_coords,
            'distance_km': round(distance_km, 2),
            'distance_miles': round(distance_miles, 2),
            'eta_seconds': int(eta_seconds),
            'eta_human': eta_human
        })
    
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON in request body'
        }, status=400)
    except (ValueError, TypeError) as e:
        return JsonResponse({
            'success': False,
            'error': f'Invalid coordinate values: {str(e)}'
        }, status=400)
    except Exception as e:
        print(f'[ROUTING ERROR] {str(e)}')
        return JsonResponse({
            'success': False,
            'error': 'Server error calculating route'
        }, status=500)

def boarding_status(request):
    user_id = request.session.get('c_id')
    if not user_id:
        return redirect('user_index')
    card = ChildModels.objects.filter(children_status1='Boarded').filter(c_id=user_id)
    
    return render(request,'user/user-boarding-status.html',{
            'card':card})


    return render(request,'user/user-boarding-status.html')


def dropping_status(request):
       user_id = request.session.get('c_id')
       if not user_id:
           return redirect('user_index')
       card = ChildModels.objects.filter(children_status1='Dropped').filter(c_id=user_id)

       return render(request,'user/user-dropping-status.html',{
            'card':card})

    # return render(request,'user/user-dropping-status.html')



def notification_status(request):
    user_id = request.session.get('c_id')
    if not user_id:
        return redirect('user_index')
    data=DelayModel.objects.all().order_by('-pk')[0:1]
    print(data)

    return render(request,'user/user-notification.html',{'data':data})