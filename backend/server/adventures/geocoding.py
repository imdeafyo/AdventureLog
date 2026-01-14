import requests
import time
import socket
import re
import unicodedata
from worldtravel.models import Region, City, VisitedRegion, VisitedCity
from django.conf import settings

# -----------------
# SEARCHING
def search_google(query):
    try:
        api_key = settings.GOOGLE_MAPS_API_KEY
        if not api_key:
            return {"error": "Geocoding service unavailable. Please check configuration."}

        # Updated to use the new Places API (New) endpoint
        url = "https://places.googleapis.com/v1/places:searchText"
        
        headers = {
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': api_key,
            'X-Goog-FieldMask': 'places.displayName.text,places.formattedAddress,places.location,places.types,places.rating,places.userRatingCount'
        }
        
        payload = {
            "textQuery": query,
            "maxResultCount": 20  # Adjust as needed
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=(2, 5))
        response.raise_for_status()

        data = response.json()
        
        # Check if we have places in the response
        places = data.get("places", [])
        if not places:
            return {"error": "No locations found for the given query."}

        results = []
        for place in places:
            location = place.get("location", {})
            types = place.get("types", [])
            primary_type = types[0] if types else None
            category = _extract_google_category(types)
            addresstype = _infer_addresstype(primary_type)

            importance = None
            rating = place.get("rating")
            ratings_total = place.get("userRatingCount")
            if rating is not None and ratings_total:
                importance = round(float(rating) * ratings_total / 100, 2)

            # Extract display name from the new API structure
            display_name_obj = place.get("displayName", {})
            name = display_name_obj.get("text") if display_name_obj else None

            results.append({
                "lat": location.get("latitude"),
                "lon": location.get("longitude"),
                "name": name,
                "display_name": place.get("formattedAddress"),
                "type": primary_type,
                "category": category,
                "importance": importance,
                "addresstype": addresstype,
                "powered_by": "google",
            })

        if results:
            results.sort(key=lambda r: r["importance"] if r["importance"] is not None else 0, reverse=True)

        return results

    except requests.exceptions.Timeout:
        return {"error": "Request timed out while contacting Google Maps. Please try again."}
    except requests.exceptions.ConnectionError:
        return {"error": "Unable to connect to Google Maps service. Please check your internet connection."}
    except requests.exceptions.HTTPError as e:
        if response.status_code == 400:
            return {"error": "Invalid request to Google Maps. Please check your query."}
        elif response.status_code == 401:
            return {"error": "Authentication failed with Google Maps. Please check API configuration."}
        elif response.status_code == 403:
            return {"error": "Access forbidden to Google Maps. Please check API permissions."}
        elif response.status_code == 429:
            return {"error": "Too many requests to Google Maps. Please try again later."}
        else:
            return {"error": "Google Maps service error. Please try again later."}
    except requests.exceptions.RequestException:
        return {"error": "Network error while contacting Google Maps. Please try again."}
    except Exception:
        return {"error": "An unexpected error occurred during Google search. Please try again."}

def _extract_google_category(types):
    # Basic category inference based on common place types
    if not types:
        return None
    if "restaurant" in types:
        return "food"
    if "lodging" in types:
        return "accommodation"
    if "park" in types or "natural_feature" in types:
        return "nature"
    if "museum" in types or "tourist_attraction" in types:
        return "attraction"
    if "locality" in types or "administrative_area_level_1" in types:
        return "region"
    return types[0]  # fallback to first type


def _infer_addresstype(type_):
    # Rough mapping of Google place types to OSM-style addresstypes
    mapping = {
        "locality": "city",
        "sublocality": "neighborhood",
        "administrative_area_level_1": "region",
        "administrative_area_level_2": "county",
        "country": "country",
        "premise": "building",
        "point_of_interest": "poi",
        "route": "road",
        "street_address": "address",
    }
    return mapping.get(type_, None)


def search_osm(query):
    try:
        url = f"https://nominatim.openstreetmap.org/search?q={query}&format=jsonv2"
        headers = {'User-Agent': 'AdventureLog Server'}
        response = requests.get(url, headers=headers, timeout=(2, 5))
        response.raise_for_status()
        data = response.json()

        return [{
            "lat": item.get("lat"),
            "lon": item.get("lon"),
            "name": item.get("name"),
            "display_name": item.get("display_name"),
            "type": item.get("type"),
            "category": item.get("category"),
            "importance": item.get("importance"),
            "addresstype": item.get("addresstype"),
            "powered_by": "nominatim",
        } for item in data]
    except requests.exceptions.Timeout:
        return {"error": "Request timed out while contacting OpenStreetMap. Please try again."}
    except requests.exceptions.ConnectionError:
        return {"error": "Unable to connect to OpenStreetMap service. Please check your internet connection."}
    except requests.exceptions.HTTPError as e:
        if response.status_code == 400:
            return {"error": "Invalid request to OpenStreetMap. Please check your query."}
        elif response.status_code == 429:
            return {"error": "Too many requests to OpenStreetMap. Please try again later."}
        else:
            return {"error": "OpenStreetMap service error. Please try again later."}
    except requests.exceptions.RequestException:
        return {"error": "Network error while contacting OpenStreetMap. Please try again."}
    except Exception:
        return {"error": "An unexpected error occurred during OpenStreetMap search. Please try again."}

def search(query):
    """
    Unified search function that tries Google Maps first, then falls back to OpenStreetMap.
    """
    if getattr(settings, 'GOOGLE_MAPS_API_KEY', None):
        google_result = search_google(query)
        if "error" not in google_result:
            return google_result
        # If Google fails, fallback to OSM
    return search_osm(query)

# -----------------
# REVERSE GEOCODING
# -----------------

def extractIsoCode(user, data):
    """
    Extract the ISO code from the response data.
    Returns a dictionary containing the region name, country name, and ISO code if found.
    """
    iso_code = None
    display_name = None
    country_code = None
    city = None
    visited_city = None
    location_name = None

    if 'name' in data.keys():
        location_name = data['name']

    address = data.get('address', {}) or {}

    # Capture country code early for ISO selection and name fallback.
    country_code = address.get("ISO3166-1")
    state_name = address.get("state")

    # Prefer the most specific ISO 3166-2 code available before falling back to country-level.
    # France gets lvl4 (regions) first for city matching, then lvl6 (departments) as a fallback.
    preferred_iso_keys = (
        [
            "ISO3166-2-lvl10",
            "ISO3166-2-lvl9",
            "ISO3166-2-lvl8",
            "ISO3166-2-lvl4",
            "ISO3166-2-lvl6",
            "ISO3166-2-lvl7",
            "ISO3166-2-lvl5",
            "ISO3166-2-lvl3",
            "ISO3166-2-lvl2",
            "ISO3166-2-lvl1",
            "ISO3166-2",
        ]
        if country_code == "FR"
        else [
            "ISO3166-2-lvl10",
            "ISO3166-2-lvl9",
            "ISO3166-2-lvl8",
            "ISO3166-2-lvl4",
            "ISO3166-2-lvl7",
            "ISO3166-2-lvl6",
            "ISO3166-2-lvl5",
            "ISO3166-2-lvl3",
            "ISO3166-2-lvl2",
            "ISO3166-2-lvl1",
            "ISO3166-2",
        ]
    )

    iso_candidates = []
    for key in preferred_iso_keys:
        value = address.get(key)
        if value and value not in iso_candidates:
            iso_candidates.append(value)

    # If no region-level code, fall back to country code only as a last resort.
    if not iso_candidates and "ISO3166-1" in address:
        iso_candidates.append(address.get("ISO3166-1"))

    iso_code = iso_candidates[0] if iso_candidates else None

    region_candidates = []
    for candidate in iso_candidates:
        if len(str(candidate)) <= 2:
            continue
        match = Region.objects.filter(id=candidate).first()
        if match and match not in region_candidates:
            region_candidates.append(match)

    region = region_candidates[0] if region_candidates else None

    # Fallback: attempt to resolve region by name and country code when no ISO match.
    if not region and state_name:
        region_queryset = Region.objects.filter(name__iexact=state_name)
        if country_code:
            region_queryset = region_queryset.filter(country__country_code=country_code)
        region = region_queryset.first()
        if region:
            iso_code = region.id
            if not country_code:
                country_code = region.country.country_code
            if region not in region_candidates:
                region_candidates.insert(0, region)

    if not region:
        return {"error": "No region found"}

    if not country_code:
        country_code = region.country.country_code

    region_visited = False
    city_visited = False

    # ordered preference for best-effort locality matching
    locality_keys = [
        'suburb',
        'neighbourhood',
        'neighborhood',  # alternate spelling
        'city',
        'city_district',
        'town',
        'village',
        'hamlet',
        'locality',
        'municipality',
        'county',
    ]

    def _normalize_name(value):
        normalized = unicodedata.normalize("NFKD", value)
        ascii_only = normalized.encode("ascii", "ignore").decode("ascii")
        return re.sub(r"[^a-z0-9]", "", ascii_only.lower())

    def match_locality(key_name, target_region):
        value = address.get(key_name)
        if not value:
            return None
        qs = City.objects.filter(region=target_region)

        # Use exact matches first to avoid broad county/name collisions (e.g. Troms vs Tromsø).
        exact_match = qs.filter(name__iexact=value).first()
        if exact_match:
            return exact_match

        normalized_value = _normalize_name(value)
        for candidate in qs.values_list('id', 'name'):
            candidate_id, candidate_name = candidate
            if _normalize_name(candidate_name) == normalized_value:
                return qs.filter(id=candidate_id).first()

        # Allow partial matching for most locality fields but keep county strict.
        if key_name == 'county':
            return None

        return qs.filter(name__icontains=value).first()

    chosen_region = region
    for candidate_region in region_candidates or [region]:
        for key_name in locality_keys:
            city = match_locality(key_name, candidate_region)
            if city:
                chosen_region = candidate_region
                iso_code = chosen_region.id
                break
        if city:
            break

    region = chosen_region
    iso_code = region.id
    visited_region = VisitedRegion.objects.filter(region=region, user=user).first()
    region_visited = bool(visited_region)

    if city:
        display_name = f"{city.name}, {region.name}, {country_code or region.country.country_code}"
        visited_city = VisitedCity.objects.filter(city=city, user=user).first()
        city_visited = bool(visited_city)
    else:
        display_name = f"{region.name}, {country_code or region.country.country_code}"

    return {
        "region_id": iso_code,
        "region": region.name,
        "country": region.country.name,
        "country_id": region.country.country_code,
        "region_visited": region_visited,
        "display_name": display_name,
        "city": city.name if city else None,
        "city_id": city.id if city else None,
        "city_visited": city_visited,
        'location_name': location_name,
    }

def is_host_resolvable(hostname: str) -> bool:
    try:
        socket.gethostbyname(hostname)
        return True
    except socket.error:
        return False

def reverse_geocode(lat, lon, user):
    if getattr(settings, 'GOOGLE_MAPS_API_KEY', None):
        google_result = reverse_geocode_google(lat, lon, user)
        if "error" not in google_result:
            return google_result
        # If Google fails, fallback to OSM
        return reverse_geocode_osm(lat, lon, user)
    return reverse_geocode_osm(lat, lon, user)

def reverse_geocode_osm(lat, lon, user):
    url = f"https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat={lat}&lon={lon}"
    headers = {'User-Agent': 'AdventureLog Server'}
    connect_timeout = 1
    read_timeout = 5

    if not is_host_resolvable("nominatim.openstreetmap.org"):
        return {"error": "Unable to resolve OpenStreetMap service. Please check your internet connection."}

    try:
        response = requests.get(url, headers=headers, timeout=(connect_timeout, read_timeout))
        response.raise_for_status()
        data = response.json()
        return extractIsoCode(user, data)
    except requests.exceptions.Timeout:
        return {"error": "Request timed out while contacting OpenStreetMap. Please try again."}
    except requests.exceptions.ConnectionError:
        return {"error": "Unable to connect to OpenStreetMap service. Please check your internet connection."}
    except requests.exceptions.HTTPError as e:
        if response.status_code == 400:
            return {"error": "Invalid request to OpenStreetMap. Please check coordinates."}
        elif response.status_code == 429:
            return {"error": "Too many requests to OpenStreetMap. Please try again later."}
        else:
            return {"error": "OpenStreetMap service error. Please try again later."}
    except requests.exceptions.RequestException:
        return {"error": "Network error while contacting OpenStreetMap. Please try again."}
    except Exception:
        return {"error": "An unexpected error occurred during OpenStreetMap geocoding. Please try again."}

def reverse_geocode_google(lat, lon, user):
    api_key = settings.GOOGLE_MAPS_API_KEY
    
    # Updated to use the new Geocoding API endpoint (this one is still supported)
    # The Geocoding API is separate from Places API and still uses the old format
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"latlng": f"{lat},{lon}", "key": api_key}

    try:
        response = requests.get(url, params=params, timeout=(2, 5))
        response.raise_for_status()
        data = response.json()

        status = data.get("status")
        if status != "OK":
            if status == "ZERO_RESULTS":
                return {"error": "No location found for the given coordinates."}
            elif status == "OVER_QUERY_LIMIT":
                return {"error": "Query limit exceeded for Google Maps. Please try again later."}
            elif status == "REQUEST_DENIED":
                return {"error": "Request denied by Google Maps. Please check API configuration."}
            elif status == "INVALID_REQUEST":
                return {"error": "Invalid request to Google Maps. Please check coordinates."}
            else:
                return {"error": "Geocoding failed. Please try again."}

        # Convert Google schema to Nominatim-style for extractIsoCode
        first_result = data.get("results", [])[0]
        result_data = {
            "name": first_result.get("formatted_address"),
            "address": _parse_google_address_components(first_result.get("address_components", []))
        }
        return extractIsoCode(user, result_data)
    except requests.exceptions.Timeout:
        return {"error": "Request timed out while contacting Google Maps. Please try again."}
    except requests.exceptions.ConnectionError:
        return {"error": "Unable to connect to Google Maps service. Please check your internet connection."}
    except requests.exceptions.HTTPError as e:
        if response.status_code == 400:
            return {"error": "Invalid request to Google Maps. Please check coordinates."}
        elif response.status_code == 401:
            return {"error": "Authentication failed with Google Maps. Please check API configuration."}
        elif response.status_code == 403:
            return {"error": "Access forbidden to Google Maps. Please check API permissions."}
        elif response.status_code == 429:
            return {"error": "Too many requests to Google Maps. Please try again later."}
        else:
            return {"error": "Google Maps service error. Please try again later."}
    except requests.exceptions.RequestException:
        return {"error": "Network error while contacting Google Maps. Please try again."}
    except Exception:
        return {"error": "An unexpected error occurred during Google geocoding. Please try again."}

def _parse_google_address_components(components):
    parsed = {}
    country_code = None
    state_code = None

    for comp in components:
        types = comp.get("types", [])
        long_name = comp.get("long_name")
        short_name = comp.get("short_name")

        if "country" in types:
            parsed["country"] = long_name
            country_code = short_name
            parsed["ISO3166-1"] = short_name
        if "administrative_area_level_1" in types:
            parsed["state"] = long_name
            state_code = short_name
        if "administrative_area_level_2" in types:
            parsed["county"] = long_name
        if "administrative_area_level_3" in types:
            parsed["municipality"] = long_name
        if "locality" in types:
            parsed["city"] = long_name
        if "postal_town" in types:
            parsed.setdefault("city", long_name)
        if "sublocality" in types or any(t.startswith("sublocality_level_") for t in types):
            parsed["suburb"] = long_name
        if "neighborhood" in types:
            parsed["neighbourhood"] = long_name
        if "route" in types:
            parsed["road"] = long_name
        if "street_address" in types:
            parsed["address"] = long_name

    # Build composite ISO 3166-2 code like US-ME (matches Region.id in DB)
    if country_code and state_code:
        parsed["ISO3166-2-lvl1"] = f"{country_code}-{state_code}"

    return parsed
