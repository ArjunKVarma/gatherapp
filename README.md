# Gather: Travel & Event Discovery Platform

Gather is a professional SaaS application designed to help travelers discover local events, celebrations, and attractions anywhere in the world. Built with Django and GeoDjango, it leverages spatial data to provide a location-aware experience.

## 🚀 Exact Working & Workflow

### 1. User Roles & Permissions
Gather implements a multi-tier user system to ensure content quality and security:
- **Explorers (Regular Users)**: Can discover events, view nearby attractions, and filter by date/distance.
- **Creators (Editors)**: Verified users who can publish new events. 
- **Administrators**: Manage the platform and approve Creator applications.

#### Admin Approval Logic
When a user registers as a **Creator**, their account is placed in a "Pending Review" state. 
- They cannot log in until an **Administrator** approves their profile via the Django Admin panel (`/admin`).
- Once approved, the "Post Event" feature becomes accessible in their navigation menu.

### 2. Location-Based Discovery
The platform uses high-precision geographic tools:
- **OpenStreetMap (OSM) Integration**: Uses Nominatim for geocoding (converting addresses to coordinates) and finding nearby places of interest.
- **Reverse Geocoding**: Automatically identifies the user's current city/area based on coordinates.
- **Interactive Maps**: Uses Leaflet.js to display event locations and nearby attractions dynamically.

### 3. Spatial Filtering
- **PostGIS Integration**: The app uses the PostGIS extension for PostgreSQL to perform complex spatial queries.
- **Distance Queries**: Users can filter events within a specific radius (e.g., 20km) from their selected location.
- **Temporal Filtering**: Events can be filtered by date to see what's happening today or in the future.

### 4. Event Management
- **Creators** can upload event details including name, description, category, date, time, and multiple images.
- The app automatically geocodes the event address to store its exact `Point` coordinates for spatial searching.

## 🛠 Tech Stack
- **Backend**: Django (Python)
- **Database**: PostgreSQL with **PostGIS** extension
- **Mapping**: Leaflet.js, OpenStreetMap (Nominatim API)
- **Frontend**: Bootstrap 5, Vanilla JS, AOS (Animations), FontAwesome 6
- **Geocoding**: `geocoder` library and OSM utilities

## ⚙️ Local Setup

### Prerequisites
- **PostGIS**: Must be installed on your local machine.
- **GDAL**: Required for GeoDjango functionalities.

### Installation
```sh
# Create and activate virtual environment
python -m venv gathervenv
gathervenv/Scripts/activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Database Setup
python manage.py makemigrations
python manage.py migrate

# Create Admin
python manage.py createsuperuser

# Run Server
python manage.py runvserver
```

## 🖼 Preview
<img src="https://github.com/ArjunKVarma/ruby-travelmanager/blob/main/images/home.png" alt="Home image" width="500"/>
<img src="https://github.com/ArjunKVarma/ruby-travelmanager/blob/main/images/fetd.png" alt="Featured" width="500"/>

---
*Front-End Design inspired by modern Material Design principles with sharp, professional aesthetics.*

## License
MIT
