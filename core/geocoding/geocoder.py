from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

geolocator = Nominatim(user_agent="ai_logistics_optimizer")

# rate limiter (safe + faster handling)
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=0.5)

# simple in-memory cache
cache = {}

def geocode_address(address):

    if address in cache:
        return cache[address]

    try:
        location = geocode(address)

        if location:
            lat, lon = location.latitude, location.longitude
            cache[address] = (lat, lon)
            return lat, lon

        return None, None

    except Exception:
        return None, None