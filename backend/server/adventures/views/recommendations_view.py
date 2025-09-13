# AdventureLog/backend/server/adventures/views/recommendations_view.py

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.conf import settings
import requests
from geopy.distance import geodesic
from adventures.geocoding import _preferred_lang  # <-- reuse the helper

# Soft transliteration: if unidecode is installed, use it; otherwise no-op
try:
    from unidecode import unidecode as _unidecode
except Exception:
    def _unidecode(s): return s

def _is_latin(s: str) -> bool:
    """Heuristic: treat as non-Latin if any letter is outside basic Latin."""
    try:
        for ch in s:
            o = ord(ch)
            if ('A' <= ch <= 'Z') or ('a' <= ch <= 'z') or ch in " -_.,'’&()/":
                continue
            if o <= 127:
                continue
            # non-ASCII letter/symbol
            return False
        return True
    except Exception:
        return True

class RecommendationsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    BASE_URL = "https://overpass-api.de/api/interpreter"
    HEADERS = {'User-Agent': 'AdventureLog Server'}

    def parse_google_places(self, places, origin):
        locations = []
        for place in places:
            location = place.get('location', {})
            types = place.get('types', [])

            # New API fields
            formatted_address = place.get("formattedAddress") or place.get("shortFormattedAddress")
            display_name = place.get("displayName", {})
            name = display_name.get("text") if isinstance(display_name, dict) else display_name

            lat = location.get('latitude')
            lon = location.get('longitude')
            if not name or not lat or not lon:
                continue

            # dedupe: don't echo name as address
            if formatted_address and isinstance(formatted_address, str) and name and formatted_address.strip() == name.strip():
                formatted_address = None

            distance_km = geodesic(origin, (lat, lon)).km
            adventure = {
                "id": place.get('id'),
                "type": 'place',
                "name": name,
                "description": place.get('businessStatus', None),
                "latitude": lat,
                "longitude": lon,
                "address": formatted_address,
                "tag": types[0] if types else None,
                "distance_km": round(distance_km, 2),
            }
            locations.append(adventure)

        locations.sort(key=lambda x: x["distance_km"])  # nearest first
        return locations

    def parse_overpass_response(self, data, request):
        def _dedupe_address(n, a):
            if not a or not n:
                return a
            return None if a.strip().lower() == n.strip().lower() else a

        nodes = data.get('elements', [])
        locations = []
        all = request.query_params.get('all', False)

        origin = None
        try:
            origin = (
                float(request.query_params.get('lat')),
                float(request.query_params.get('lon'))
            )
        except (ValueError, TypeError):
            origin = None

        # language: allow ?lang= override; else helper
        req_lang = request.query_params.get('lang')
        raw_lang = req_lang or _preferred_lang(getattr(request, "user", None)) or "en"
        lang = str(raw_lang).strip()
        base_lang = lang.split('-')[0] if lang else None
        lang_key = f"name:{lang}" if lang else None
        alt_key = f"name:{base_lang}" if base_lang and base_lang != lang else None

        for node in nodes:
            if node.get('type') not in ['node', 'way', 'relation']:
                continue

            tags = node.get('tags', {}) or {}
            lat = node.get('lat')
            lon = node.get('lon')

            # Prefer localized name, then international/official, then generic
            name = (
                (tags.get(lang_key) if lang_key else None) or
                (tags.get(alt_key) if alt_key else None) or
                tags.get('int_name') or
                tags.get('official_name') or
                tags.get('name', '')
            )

            # If user/UI language is English and OSM lacks an English tag,
            # transliterate to Latin as a last-resort display (doesn't modify data).
            if name and base_lang == 'en' and not _is_latin(name):
                name = _unidecode(name)

            if (not name or lat is None or lon is None) and not all:
                continue

            # Build a simple address string from OSM addr:* tags (may be local language)
            addr_keys = ['housenumber', 'street', 'suburb', 'city', 'state', 'postcode', 'country']
            address_parts = [tags.get(f'addr:{k}') for k in addr_keys]
            formatted_address = ", ".join(filter(None, address_parts)) or None

            # For English UI, transliterate address too if fully non-Latin
            if formatted_address and base_lang == 'en' and not _is_latin(formatted_address):
                formatted_address = _unidecode(formatted_address)

            formatted_address = _dedupe_address(name, formatted_address)

            distance_km = None
            if origin:
                distance_km = round(geodesic(origin, (lat, lon)).km, 2)

            adventure = {
                "id": f"osm:{node.get('id')}",
                "type": "place",
                "name": name,
                "description": tags.get('description'),
                "latitude": lat,
                "longitude": lon,
                "address": formatted_address,
                "tag": next((tags.get(key) for key in ['leisure', 'tourism', 'natural', 'historic', 'amenity'] if key in tags), None),
                "distance_km": distance_km,
                "powered_by": "osm"
            }
            locations.append(adventure)

        if origin:
            locations.sort(key=lambda x: x.get("distance_km") or float("inf"))
        return locations

    def query_overpass(self, lat, lon, radius, category, request):
        if category == 'tourism':
            query = f"""
                [out:json];
                (
                  node(around:{radius},{lat},{lon})["tourism"];
                  node(around:{radius},{lat},{lon})["leisure"];
                  node(around:{radius},{lat},{lon})["historic"];
                  node(around:{radius},{lat},{lon})["sport"];
                  node(around:{radius},{lat},{lon})["natural"];
                  node(around:{radius},{lat},{lon})["attraction"];
                  node(around:{radius},{lat},{lon})["museum"];
                  node(around:{radius},{lat},{lon})["zoo"];
                  node(around:{radius},{lat},{lon})["aquarium"];
                );
                out;
            """
        elif category == 'lodging':
            query = f"""
                [out:json];
                (
                  node(around:{radius},{lat},{lon})["tourism"="hotel"];
                  node(around:{radius},{lat},{lon})["tourism"="motel"];
                  node(around:{radius},{lat},{lon})["tourism"="guest_house"];
                  node(around:{radius},{lat},{lon})["tourism"="hostel"];
                  node(around:{radius},{lat},{lon})["tourism"="camp_site"];
                  node(around:{radius},{lat},{lon})["tourism"="caravan_site"];
                  node(around:{radius},{lat},{lon})["tourism"="chalet"];
                  node(around:{radius},{lat},{lon})["tourism"="alpine_hut"];
                  node(around:{radius},{lat},{lon})["tourism"="apartment"];
                );
                out;
            """
        elif category == 'food':
            query = f"""
                [out:json];
                (
                  node(around:{radius},{lat},{lon})["amenity"="restaurant"];
                  node(around:{radius},{lat},{lon})["amenity"="cafe"];
                  node(around:{radius},{lat},{lon})["amenity"="fast_food"];
                  node(around:{radius},{lat},{lon})["amenity"="pub"];
                  node(around:{radius},{lat},{lon})["amenity"="bar"];
                  node(around:{radius},{lat},{lon})["amenity"="food_court"];
                  node(around:{radius},{lat},{lon})["amenity"="ice_cream"];
                  node(around:{radius},{lat},{lon})["amenity"="bakery"];
                  node(around:{radius},{lat},{lon})["amenity"="confectionery"];
                );
                out;
            """
        else:
            return Response({"error": "Invalid category."}, status=400)

        overpass_url = f"{self.BASE_URL}?data={query}"
        try:
            # Overpass doesn't localize output; we localize in parse_overpass_response
            response = requests.get(overpass_url, headers=self.HEADERS, timeout=10)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print("Overpass API error:", e)
            return Response({"error": "Failed to retrieve data from Overpass API."}, status=500)

        locations = self.parse_overpass_response(data, request)
        return Response(locations)

    def query_google_nearby(self, lat, lon, radius, category, request):
        """Query Google Places API (New) for nearby places, honoring language"""
        api_key = settings.GOOGLE_MAPS_API_KEY
        url = "https://places.googleapis.com/v1/places:searchNearby"

        headers = {
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': api_key,
            'X-Goog-FieldMask': 'places.displayName.text,places.formattedAddress,places.location,places.types,places.rating,places.userRatingCount,places.businessStatus,places.id'
        }

        type_mapping = {
            'lodging': 'lodging',
            'food': 'restaurant',
            'tourism': 'tourist_attraction',
        }

        lang = _preferred_lang(getattr(request, "user", None))
        payload = {
            "includedTypes": [type_mapping[category]],
            "maxResultCount": 20,
            "locationRestriction": {
                "circle": {
                    "center": {"latitude": float(lat), "longitude": float(lon)},
                    "radius": float(radius)
                }
            },
            "languageCode": lang,  # Google honors this
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            places = data.get('places', [])
            origin = (float(lat), float(lon))
            # (Google rarely needs transliteration, it returns English when asked.)
            locations = self.parse_google_places(places, origin)
            return Response(locations)
        except requests.exceptions.RequestException as e:
            print(f"Google Places API error: {e}")
            return self.query_overpass(lat, lon, radius, category, request)
        except Exception as e:
            print(f"Unexpected error with Google Places API: {e}")
            return self.query_overpass(lat, lon, radius, category, request)

    @action(detail=False, methods=['get'])
    def query(self, request):
        lat = request.query_params.get('lat')
        lon = request.query_params.get('lon')
        radius = request.query_params.get('radius', '1000')
        category = request.query_params.get('category', 'all')

        if not lat or not lon:
            return Response({"error": "Latitude and longitude parameters are required."}, status=400)

        valid_categories = {'lodging': 'lodging', 'food': 'restaurant', 'tourism': 'tourist_attraction'}
        if category not in valid_categories:
            return Response({"error": f"Invalid category. Valid categories: {', '.join(valid_categories)}"}, status=400)

        api_key = getattr(settings, 'GOOGLE_MAPS_API_KEY', None)
        if not api_key:
            return self.query_overpass(lat, lon, radius, category, request)

        return self.query_google_nearby(lat, lon, radius, category, request)
