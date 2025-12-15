import requests
from typing import Optional 

class OSRMRouter:
    def __init__(self, base_url: str = 'https://localhost:5000'):
        '''
        Initialize the OSRM client.
        '''
        self.base_url = base_url.rstrip('/')
        self.service_url = f"{self.base_url}/route/v1/driving"

    def get_driving_distance(self, start_lat: float, start_lon: float, end_lat: float, end_lon: float) -> tuple[Optional[float],Optional[float]]:
        '''
        Returns the driving distance in meters and trip duration in seconds
        between two points using the OSRM container.

        Returns:
            (distance_meters, duration_seconds) or (None, None) if the request fails.
        '''
        # OSRM expects coordinates in "lon,lat" format
        coordinates = f"{start_lon},{start_lat};{end_lon},{end_lat}"

        # overview-false skips returning the geometry points to save bandwidth
        url = f"{self.service_url}/{coordinates}?overview=false"

        try: 
            response = requests.get(url)
            response.raise_for_status()

            data = response.json()

            if data['code'] == 'Ok':
                route = data['routes'][0]
                distance_meters = route['distance']
                duration_seconds = route['duration']
                return distance_meters, duration_seconds
            else:
                print(f"OSRM Logic Error: {data['code']}")
                return None, None
        except requests.exceptions.RequestException as e:
            print(f"Connection to OSRM failed: {e}")
            return None, None


    