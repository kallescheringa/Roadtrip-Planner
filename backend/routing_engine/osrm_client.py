import requests

OSRM_URL = "https://router.project-osrm.org" 


def get_route(coordinates: list[tuple[float, float]]) -> dict:
    """
    coordinates: list of (lon, lat) tuples in order (start, ...stops, end)
    Returns dict with 'geometry' (GeoJSON LineString) and 'distance'/'duration'.
    """
    coord_str = ';'.join(f"{lon},{lat}" for lon, lat in coordinates)
    url = f"{OSRM_URL}/route/v1/driving/{coord_str}"
    params = {'overview': 'full', 'geometries': 'geojson'}

    resp = requests.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()

    if data.get('code') != 'Ok' or not data.get('routes'):
        raise ValueError(f"OSRM could not find a route: {data.get('message', 'unknown error')}")

    route = data['routes'][0]
    return {
        'geometry': route['geometry'],  # GeoJSON LineString
        'distance': route['distance'],  # meters
        'duration': route['duration'],  # seconds
    }