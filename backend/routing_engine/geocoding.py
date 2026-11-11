import requests

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"


def geocode(place_name: str) -> tuple[float, float] | None:
    """Returns (lon, lat) for a place name, or None if not found."""
    resp = requests.get(
        NOMINATIM_URL,
        params={'q': place_name, 'format': 'json', 'limit': 1},
        headers={'User-Agent': 'RoadtripPlanner/1.0'},  # Nominatim requires a User-Agent
    )
    resp.raise_for_status()
    results = resp.json()
    if not results:
        return None
    lat = float(results[0]['lat'])
    lon = float(results[0]['lon'])
    return (lon, lat)