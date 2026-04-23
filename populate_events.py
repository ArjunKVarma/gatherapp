import os
import django
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.gis.geos import Point

# Setup django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gathertravel.settings')
django.setup()

from gather.models import Event

def populate():
    # Base location (New Delhi)
    base_lat = 28.63576000
    base_lng = 77.22445000
    today = timezone.now().date()
    
    events_data = [
        {
            'name': 'Delhi Tech Meetup',
            'description': 'A gathering for developers and tech enthusiasts in Delhi.',
            'place_name': 'Connaught Place',
            'lat': 28.6304,
            'lng': 77.2177, # very close to base
            'category': 'Technology',
            'date': today
        },
        {
            'name': 'Cultural Heritage Walk',
            'description': 'Guided tour through the historic streets of Old Delhi.',
            'place_name': 'Red Fort',
            'lat': 28.6562,
            'lng': 77.2410, # within 5-10km
            'category': 'Culture',
            'date': today
        },
        {
            'name': 'Weekend Flea Market',
            'description': 'Local vendors selling arts, crafts, and food.',
            'place_name': 'Hauz Khas Village',
            'lat': 28.5540,
            'lng': 77.1940, # within 15km
            'category': 'Market',
            'date': today
        },
        {
            'name': 'Mumbai Music Fest',
            'description': 'Annual music festival featuring local artists.',
            'place_name': 'Bandra Kurla Complex',
            'lat': 19.0658,
            'lng': 72.8654, # Mumbai
            'category': 'Music',
            'date': today
        }
    ]

    for data in events_data:
        event, created = Event.objects.get_or_create(
            name=data['name'],
            defaults={
                'description': data['description'],
                'place_name': data['place_name'],
                'date': data['date'],
                'time': timezone.now().time(),
                'lat': data['lat'],
                'lng': data['lng'],
                'position': Point(data['lng'], data['lat'], srid=4326),
                'category': data['category']
            }
        )
        if created:
            print(f"Created event: {event.name}")
        else:
            print(f"Event already exists: {event.name}")

if __name__ == '__main__':
    populate()
