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
# Create your views here.


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        # Ensure password matches confirmation
        password = request.POST["password"]

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, password)
            user.save()
        except IntegrityError:
            return render(request, "registration/register.html", {
                "message": "Username already taken."
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
            login(request, user)
            return HttpResponseRedirect(reverse("home"))
        else:
            return render(request, "registration/login.html", {
                "message": "Invalid username and/or password."
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

    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{lng}",
        "radius": int(km) * 1000,

        "rating": 2,
        "key": f"{settings.GOOGLE_API_KEY}"
    }
    types = ["amusement_park", "movie_theater", "bowling_alley", "cafe", "casino", "hindu_temple", "library", "mosque",
             "museum", "night_club", "park", "restaurant", "spa", "shopping_mall", "stadium", "tourist_attraction", "zoo"]

    response = requests.get(url, params=params)
    data = response.json()

    places = []

    for type in types:
        params["types"] = type
        response = requests.get(url, params=params)
        data = response.json()
        for result in data['results']:
            if 'photos' in result:
                place = {
                    'name': result['name'],
                    'image_url': result['photos'][0]['photo_reference'],
                    'types': result['types'],
                    'rating': result.get('rating', 0),
                    'tot_ratings': result.get('user_ratings_total', 0),
                    'place_id': result['place_id']
                }
                places.append(place)
    places.sort(key=lambda x: x['tot_ratings'], reverse=True)
    g = geocoder.google([lat, lng], method='reverse')
    place_name = g.city

    pnt = Point(request.session.get('lat'),
                request.session.get('lng'), srid=4326)
    nearest_point = Event.objects.filter(Q(position__distance_lte=(pnt, D(km=km))) & Q(
        date=datetime.strptime(tdate, '%Y-%m-%d').date()))  # (km=no of kilometers)

    return render(request, "ruby/home.html", {
        "lat": request.session['lat'],
        "lng": request.session['lng'],
        "loc": place_name,
        "date": tdate,
        "dist": km,
        "events": nearest_point,
        "API_KEY": settings.GOOGLE_API_KEY,
        "attractions": places,

    })


@login_required(login_url='/login')
@login_required(login_url='/login')
def regevent(request):
    if request.method == 'POST':
        new_evt = Event()
        new_evt.name = request.POST['event_name']
        new_evt.place_name = request.POST['address']
        new_evt.description = request.POST['description']
        new_evt.date = request.POST['event_date']
        new_evt.time = request.POST['event_time']
        new_evt.category = request.POST['category']
        images = request.FILES.getlist('images')
        g = geocoder.google(new_evt.place_name)
        new_evt.lat = g.lat
        new_evt.lng = g.lng
        print(images)
        new_evt.position = "POINT({} {})".format(g.lat, g.lng)

        new_evt.save()

        for image in images:
            image = Image(image=image)
            image.save()
            new_evt.images.add(image)
        return HttpResponseRedirect(reverse('home'))
    return render(request, "ruby/register_event.html", {
        "API_KEY": settings.GOOGLE_API_KEY
    })


@login_required(login_url='/login')
def update_loc(request):
    address = request.POST['gaddress']
    km = request.POST['distance']
    date = request.POST['date']
    g = geocoder.google(address)
    request.session['lat'] = g.lat
    request.session['lng'] = g.lng
    request.session['km'] = km
    request.session['date'] = date
    return HttpResponseRedirect(reverse('home'))


def ev_details(request, id):
    event = Event.objects.get(id=id)

    return render(request, "ruby/event.html", {
        "event": event,

    })
