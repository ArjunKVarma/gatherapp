from datetime import datetime
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.urls import reverse
import geocoder
from django.conf import settings
from psycopg2 import IntegrityError
from .models import Event, Image
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
import requests
from django.contrib.auth.models import User
from .osm_utils import find_nearby_places, create_map, reverse_geocode, geocode_address
# Create your views here.


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        role = request.POST.get("role", "user")

        # Attempt to create new user
        try:
            user = User.objects.create_user(username=username, password=password)
            user.save()

            # Profile is automatically created by signal, now update it
            user.profile.role = role
            if role == 'editor':
                user.profile.is_approved = False
            user.profile.save()

        except IntegrityError:
            return render(request, "registration/register.html", {
                "message": "Username already taken."
            })

        if role == 'editor':
            return render(request, "registration/login.html", {
                "message": "Registration successful! Your editor account is now under review. We will notify you once approved.",
                "msg_class": "m3-alert-info"
            })

        login(request, user)
        return HttpResponseRedirect(reverse("home"))
    else:
        return render(request, 'registration/register.html')



def sign_in(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            # Check editor approval status
            if hasattr(user, 'profile') and user.profile.role == 'editor' and not user.profile.is_approved:
                return render(request, "registration/login.html", {
                    "message": "Your editor account is currently under review. We will notify you once it's approved.",
                    "msg_class": "m3-alert"
                })

            login(request, user)
            return HttpResponseRedirect(reverse("home"))
        else:
            return render(request, "registration/login.html", {
                "message": "Invalid username and/or password.",
                "msg_class": "m3-alert"
            })
    else:
        return render(request, "registration/login.html")



def signout(request):
    logout(request)
    return HttpResponseRedirect(reverse("home"))


def home(request):

    if 'lat' not in request.session or 'lng' not in request.session or 'km' not in request.session or 'date' not in request.session:
        request.session['lat'] = 28.63576000
        request.session['lng'] = 77.22445000
        request.session['km'] = 20
        request.session['date'] = datetime.now().strftime('%Y-%m-%d')

    lat = request.session.get('lat')
    lng = request.session.get('lng')
    km = request.session.get('km')
    tdate = request.session.get('date')

    # Find nearby places using OpenStreetMap
    places = find_nearby_places(float(lat), float(lng), int(km))
    
    # Get place name using OpenStreetMap reverse geocoding
    place_name = reverse_geocode(float(lat), float(lng))
    pnt = Point(float(request.session.get('lng')),
                float(request.session.get('lat')), srid=4326)
    nearest_point = Event.objects.filter(Q(position__distance_lte=(pnt, D(km=float(km)))) & Q(
        date=datetime.strptime(tdate, '%Y-%m-%d').date()))  # (km=no of kilometers)

    # Create interactive map
    map_html = create_map(float(lat), float(lng), places)

    return render(request, "gather/home.html", {
        "lat": request.session['lat'],
        "lng": request.session['lng'],
        "loc": place_name,
        "date": tdate,
        "dist": km,
        "events": nearest_point,
        "attractions": places,
        "map": map_html,
    })


@login_required(login_url='/login')
def regevent(request):
    # Check if user is an approved editor or admin
    if not (request.user.is_staff or (hasattr(request.user, 'profile') and request.user.profile.role == 'editor' and request.user.profile.is_approved)):
        return HttpResponseRedirect(reverse('home'))

    if request.method == 'POST':

        new_evt = Event()
        new_evt.name = request.POST['event_name']
        new_evt.place_name = request.POST['address']
        new_evt.description = request.POST['description']
        new_evt.date = request.POST['event_date']
        new_evt.time = request.POST['event_time']
        new_evt.category = request.POST['category']
        images = request.FILES.getlist('images')
        # Use OpenStreetMap Nominatim for geocoding
        lat, lng = geocode_address(new_evt.place_name)
        if lat and lng:
            new_evt.lat = lat
            new_evt.lng = lng
            new_evt.position = f"POINT({lng} {lat})"
        else:
            # Default coordinates if geocoding fails
            new_evt.lat = 28.63576000
            new_evt.lng = 77.22445000
            new_evt.position = "POINT(77.22445000 28.63576000)"

        new_evt.save()

        for image in images:
            image = Image(image=image)
            image.save()
            new_evt.images.add(image)
        return HttpResponseRedirect(reverse('home'))
    return render(request, "gather/register_event.html")


def update_loc(request):
    # Use gaddress (picked from autocomplete) or fall back to raw typed address
    address = request.POST.get('gaddress') or request.POST.get('address') or ''
    
    raw_km = request.POST.get('distance')
    km = raw_km if raw_km and str(raw_km).strip() else 20
    
    raw_date = request.POST.get('date')
    date = raw_date if raw_date and str(raw_date).strip() else datetime.now().strftime('%Y-%m-%d')

    if address.strip():
        # Use OpenStreetMap Nominatim for geocoding
        lat, lng = geocode_address(address)
        if lat and lng:
            request.session['lat'] = lat
            request.session['lng'] = lng
    request.session['km'] = km
    request.session['date'] = date
    return HttpResponseRedirect(reverse('home'))


def ev_details(request, id):
    event = Event.objects.get(id=id)

    return render(request, "gather/event.html", {
        "event": event,

    })
