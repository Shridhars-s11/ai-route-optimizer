import requests

def get_osrm_route_geometry(coordinates):

    try:
        coords = ";".join([f"{lon},{lat}" for lat, lon in coordinates])

        url = f"http://router.project-osrm.org/route/v1/driving/{coords}?overview=full&geometries=geojson"

        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return coordinates  # fallback

        data = response.json()

        if "routes" not in data or len(data["routes"]) == 0:
            return coordinates  # fallback

        geometry = data["routes"][0]["geometry"]["coordinates"]

        return [[lat, lon] for lon, lat in geometry]

    except Exception:
        return coordinates  # fallback ALWAYS