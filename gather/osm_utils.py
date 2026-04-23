import requests
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import folium

def geocode_address(address):
    """Convert address to coordinates using OpenStreetMap Nominatim"""
    geolocator = Nominatim(user_agent="gather_travel_app")
    try:
        location = geolocator.geocode(address)
        if location:
            return location.latitude, location.longitude
    except:
        pass
    return None, None

def reverse_geocode(lat, lng):
    """Convert coordinates to address using OpenStreetMap Nominatim"""
    geolocator = Nominatim(user_agent="gather_travel_app")
    try:
        location = geolocator.reverse((lat, lng))
        if location:
            return location.address
    except:
        pass
    return "Unknown Location"

def find_nearby_places(lat, lng, radius_km=5):
    """Find nearby places using Overpass API (OpenStreetMap)"""
    overpass_url = "https://overpass-api.de/api/interpreter"
    
    # Map OSM tags to UI categories
    # Key is OSM value, Value is (UI Label, CSS Class)
    CATEGORY_MAP = {
        # Dining
        'cafe': ('Cafe', 'Dining'),
        'restaurant': ('Restaurant', 'Dining'),
        'bar': ('Bar', 'Dining'),
        'pub': ('Pub', 'Dining'),
        'fast_food': ('Fast Food', 'Dining'),
        'food_court': ('Food Court', 'Dining'),
        
        # Entertainment
        'cinema': ('Movies', 'Movies'),
        'theatre': ('Theatre', 'Movies'),
        'arts_centre': ('Arts Centre', 'Movies'),
        
        # Gym & Sports
        'gym': ('GYM', 'gym'),
        'fitness_centre': ('Fitness Centre', 'gym'),
        'fitness_station': ('Fitness Station', 'gym'),
        'sports_centre': ('Sports Centre', 'gym'),
        
        # Attractions
        'attraction': ('Attraction', 'tourist_attraction'),
        'museum': ('Museum', 'tourist_attraction'),
        'viewpoint': ('Viewpoint', 'tourist_attraction'),
        'zoo': ('Zoo', 'tourist_attraction'),
        'theme_park': ('Theme Park', 'tourist_attraction'),
        'gallery': ('Gallery', 'tourist_attraction'),
        'artwork': ('Artwork', 'tourist_attraction'),
        'historic': ('Historic Site', 'tourist_attraction'),
        'park': ('Park', 'tourist_attraction'),
        
        # Worship
        'hindu_temple': ('Temple', 'worship'),
        'temple': ('Temple', 'worship'),
        'place_of_worship': ('Place of Worship', 'worship'),
        'mosque': ('Mosque', 'worship'),
        'church': ('Church', 'worship')
    }

    # Cap radius to 5km to prevent Overpass API timeouts in dense areas
    actual_radius = min(radius_km, 5)
    
    # Build a single optimized query
    # We look for nodes, ways, and relations with relevant tags
    overpass_query = f"""
    [out:json][timeout:25];
    (
      node["amenity"~"cafe|restaurant|bar|pub|fast_food|food_court|cinema|theatre|arts_centre|place_of_worship"](around:{actual_radius*1000},{lat},{lng});
      node["tourism"~"attraction|museum|viewpoint|zoo|theme_park|gallery|artwork"](around:{actual_radius*1000},{lat},{lng});
      node["leisure"~"gym|fitness_centre|fitness_station|sports_centre|park"](around:{actual_radius*1000},{lat},{lng});
      node["historic"](around:{actual_radius*1000},{lat},{lng});
      
      way["amenity"~"cafe|restaurant|bar|pub|fast_food|food_court|cinema|theatre|arts_centre|place_of_worship"](around:{actual_radius*1000},{lat},{lng});
      way["tourism"~"attraction|museum|viewpoint|zoo|theme_park|gallery|artwork"](around:{actual_radius*1000},{lat},{lng});
      way["leisure"~"gym|fitness_centre|fitness_station|sports_centre|park"](around:{actual_radius*1000},{lat},{lng});
      way["historic"](around:{actual_radius*1000},{lat},{lng});
    );
    out center;
    """
    
    places = []
    try:
        headers = {'User-Agent': 'GatherTravelApp/1.0 (Contact: arjun@example.com)'}
        response = requests.get(overpass_url, params={'data': overpass_query}, headers=headers, timeout=25)
        data = response.json()
        
        for element in data.get('elements', []):
            if element.get('tags'):
                tags = element['tags']
                name = tags.get('name', 'Unnamed Place')
                
                # Determine category and class
                osm_val = tags.get('amenity') or tags.get('tourism') or tags.get('leisure') or tags.get('shop') or tags.get('sport')
                if tags.get('religion') == 'hindu':
                    osm_val = 'hindu_temple'
                
                cat_info = CATEGORY_MAP.get(osm_val, ('Other', 'other'))
                
                # Get coordinates
                if element['type'] == 'node':
                    place_lat = element['lat']
                    place_lng = element['lon']
                elif 'center' in element:
                    place_lat = element['center']['lat']
                    place_lng = element['center']['lon']
                else:
                    continue
                
                # Calculate distance
                distance = geodesic((lat, lng), (place_lat, place_lng)).kilometers
                
                places.append({
                    'name': name,
                    'category': cat_info[0],
                    'category_class': cat_info[1],
                    'lat': place_lat,
                    'lng': place_lng,
                    'distance': round(distance, 2),
                })
    except Exception as e:
        print(f"Error fetching nearby places: {e}")
    
    # Sort by distance and limit results
    places.sort(key=lambda x: x['distance'])
    return places[:20]

def create_map(lat, lng, places=None, zoom_level=13):
    """Create an interactive map using Folium"""
    # Create map centered at the given coordinates with more robust tile provider
    m = folium.Map(location=[lat, lng], zoom_start=zoom_level, tiles="CartoDB voyager")
    
    # Add marker for user location
    folium.Marker(
        [lat, lng],
        popup="Your Location",
        icon=folium.Icon(color='red', icon='info-sign')
    ).add_to(m)
    
    # Add markers for nearby places
    if places:
        for place in places:
            folium.Marker(
                [place['lat'], place['lng']],
                popup=f"{place['name']}<br>{place['category']}<br>{place['distance']} km",
                icon=folium.Icon(color='blue', icon='info-sign')
            ).add_to(m)
    
    return m._repr_html_()
