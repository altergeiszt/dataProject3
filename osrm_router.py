import requests

OSRM_URL = 'http://localhost:5000/route/v1/driving/'

def get_driving_distance(start_lat, start_lon, end_lat, end_lon):
    """Returns the driving distance in meters and trip duration in seconds
        between two points using the OSRM container
    """
    # 
    coordinates = f"{start_lon},{start_lat};{end_lon},{end_lat}"

    url = f"{OSRM_URL}{coordinates}?overview=false"

    try:
        response = requests.get(url)
        data = response.json()

        if data['code'] == 'Ok':
            route = data['routes'][0]
            distance_meters = route['distance']
            duration_seconds = route['duration']
            return distance_meters, duration_seconds
        else:
            print(f"Error finding route: {data['code']}")
            return None, None
    
    except requests.exceptions.RequestException as e:
        print(f"Connection failed: {e}")
        return None, None
    

if __name__ == "__main__":
    dist, dur = get_driving_distance(50.4503, -104.6094, 50.4155, -104.5878)

    if dist is not None and dur is not None:
        print(f"Driving Distance: {dist/1000:.2f} km")
        print(f"Driving Time: {dur/60:.1f} minutes")
    else:
        print("Route calculation failed. Ensure the OSRM server is running at localhost:5000")