"""Emergency resource query service supporting local SQLite resources and

graceful OpenStreetMap Overpass API lookups.
"""

import math
import logging
from typing import List, Dict, Any, Optional
import requests
from models import EmergencyResource

logger = logging.getLogger(__name__)


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great circle distance between two points in kilometers."""
    R = 6371.0  # Earth radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)


def get_nearby_database_resources(
    lat: float, lon: float, radius_km: float = 15.0, resource_type: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Query local pre-seeded/registered database emergency facilities sorted by proximity."""
    query = EmergencyResource.query.filter_by(is_active=True)
    if resource_type and resource_type.lower() != "all":
        query = query.filter_by(resource_type=resource_type)

    all_resources = query.all()
    results = []

    for res in all_resources:
        distance = haversine_distance(lat, lon, res.latitude, res.longitude)
        if distance <= radius_km:
            item = res.to_dict()
            item["distance_km"] = distance
            item["source"] = "Registered System Facility"
            results.append(item)

    # Sort by closest distance first
    results.sort(key=lambda x: x["distance_km"])
    return results


def fetch_osm_emergency_resources(
    lat: float, lon: float, radius_meters: int = 5000
) -> List[Dict[str, Any]]:
    """Query OpenStreetMap Overpass API for real-world emergency infrastructure.

    Gracefully falls back on timeout or network error without throwing exceptions.
    """
    try:
        from flask import current_app
        if current_app and current_app.config.get("TESTING"):
            return []
    except Exception:
        pass

    overpass_url = "https://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json][timeout:4];
    (
      node["amenity"="hospital"](around:{radius_meters},{lat},{lon});
      node["amenity"="fire_station"](around:{radius_meters},{lat},{lon});
      node["amenity"="police"](around:{radius_meters},{lat},{lon});
    );
    out body 15;
    """

    try:
        response = requests.post(
            overpass_url, data={"data": overpass_query}, timeout=3.5
        )
        if response.status_code == 200:
            data = response.json()
            elements = data.get("elements", [])
            resources = []

            type_mapping = {
                "hospital": "Hospital",
                "fire_station": "Fire Station",
                "police": "Police Station",
            }

            for el in elements:
                tags = el.get("tags", {})
                amenity = tags.get("amenity", "emergency")
                name = tags.get("name", f"Local {type_mapping.get(amenity, 'Emergency Resource')}")
                el_lat = el.get("lat")
                el_lon = el.get("lon")

                if el_lat and el_lon:
                    dist = haversine_distance(lat, lon, el_lat, el_lon)
                    resources.append(
                        {
                            "id": f"osm-{el.get('id')}",
                            "name": name,
                            "resource_type": type_mapping.get(amenity, "Emergency Facility"),
                            "address": tags.get("addr:street", tags.get("addr:full", "Location via OpenStreetMap")),
                            "phone": tags.get("phone", tags.get("contact:phone", "N/A")),
                            "latitude": el_lat,
                            "longitude": el_lon,
                            "capacity": "Real-world facility",
                            "distance_km": dist,
                            "source": "OpenStreetMap Live",
                        }
                    )

            resources.sort(key=lambda x: x["distance_km"])
            return resources
    except Exception as e:
        logger.info(f"OSM Overpass lookup skipped or timed out: {e}")

    # Fallback to empty list when offline or Overpass is unavailable
    return []


def get_combined_nearby_resources(
    lat: float, lon: float, radius_km: float = 15.0
) -> Dict[str, Any]:
    """Retrieve emergency resources combining database records with optional OSM data."""
    db_resources = get_nearby_database_resources(lat, lon, radius_km=radius_km)
    osm_resources = fetch_osm_emergency_resources(lat, lon, radius_meters=int(radius_km * 1000))

    combined = db_resources + osm_resources
    # Sort combined results by distance
    combined.sort(key=lambda x: x["distance_km"])

    return {
        "count": len(combined),
        "database_count": len(db_resources),
        "osm_count": len(osm_resources),
        "resources": combined,
    }
