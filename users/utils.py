from decouple import config
import requests
from geopy.distance import geodesic  # Import geodesic for "crow-flies" distance calculation
import math


GOOGLE_API_KEY = config('GOOGLE_API_KEY')

def get_coordinates_from_zip(zip_code):
    """
    Get latitude and longitude from zip code using Google Geocoding API.
    """
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={zip_code}&key={GOOGLE_API_KEY}"
    response = requests.get(url)
    data = response.json()
    
    if data['status'] == 'OK':
        # Extract latitude and longitude
        location = data['results'][0]['geometry']['location']
        return location['lat'], location['lng']
    else:
        raise ValueError(f"Geocoding failed for {zip_code} with status {data['status']}")

def haversine(coord1, coord2):
    """
    Calculate the great-circle distance between two points (specified in decimal degrees) using the Haversine formula.
    """
    lat1, lon1 = coord1
    lat2, lon2 = coord2

    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))

    # Radius of earth in miles is 3958.8 (use 6371 for kilometers)
    r = 3958.8
    return c * r  # Returns distance in miles

def calculate_straight_line_distance(coord1, coord2):
    """
    Calculate the straight-line distance between two coordinates using geopy.
    coord1 and coord2 are tuples (latitude, longitude).
    """
    return haversine(coord1, coord2)  # Returns distance in miles

def calculate_real_distance(customer_coords, mechanic_coords, max_distance):
    """
    Calculate the real distance between two zip codes using Google Distance Matrix API
    only if the straight-line distance is within max_distance.
    """
    # Step 1: Calculate the straight-line distance (crow-flies)
    crow_flies_distance = calculate_straight_line_distance(customer_coords, mechanic_coords)

    # Step 2: If the crow-flies distance is greater than max_distance, no need for Google API
    if crow_flies_distance > max_distance:
        return {
            "distance": f"{crow_flies_distance:.2f} miles (crow-flies)",
            "real_distance_not_calculated": True
        }

    # Step 3: Otherwise, call Google Distance Matrix API to get real driving distance
    distance_matrix_url = (
        f"https://maps.googleapis.com/maps/api/distancematrix/json?"
        f"origins={customer_coords[0]},{customer_coords[1]}&"
        f"destinations={mechanic_coords[0]},{mechanic_coords[1]}&"
        f"key={GOOGLE_API_KEY}&units=imperial"
    )

    response = requests.get(distance_matrix_url)
    data = response.json()

    # Step 4: Check if the request was successful and return only the distance
    if data['status'] == 'OK':
        distance_text = data['rows'][0]['elements'][0]['distance']['text']  # Get distance
        return {
            "distance": distance_text,
            "real_distance_not_calculated": False
        }
    else:
        raise ValueError(f"Distance calculation failed with status {data['status']}")