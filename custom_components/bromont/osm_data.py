"""OpenStreetMap data integration for Bromont trails."""

from __future__ import annotations

import asyncio
import logging
from typing import Dict, List, Optional
import aiohttp
import async_timeout

_LOGGER = logging.getLogger(__name__)

# Bromont coordinates (approximate center)
BROMONT_LAT = 45.3167
BROMONT_LON = -72.6500
SEARCH_RADIUS = 5000  # meters - increased to capture all trails


class OSMTrailData:
    """Fetch and manage OpenStreetMap trail data for Bromont."""

    def __init__(self):
        """Initialize OSM data manager."""
        self.trails: Dict[str, Dict] = {}
        self._overpass_url = "https://overpass-api.de/api/interpreter"

    async def fetch_trails(self) -> Dict[str, Dict]:
        """Fetch trail data from OpenStreetMap with retry logic."""
        # Query for trails using multiple tag combinations
        query = f"""
        [out:json][timeout:60];
        (
          way["piste:type"](around:{SEARCH_RADIUS},{BROMONT_LAT},{BROMONT_LON});
          way["piste:name"](around:{SEARCH_RADIUS},{BROMONT_LAT},{BROMONT_LON});
          relation["piste:type"](around:{SEARCH_RADIUS},{BROMONT_LAT},{BROMONT_LON});
        );
        out geom;
        """

        # Retry logic for API reliability
        max_retries = 2
        for attempt in range(max_retries):
            try:
                response = await self._query_overpass(query)
                if response:
                    self.trails = self._parse_trails(response)
                    _LOGGER.info(f"Fetched {len(self.trails)} trails from OpenStreetMap")
                    return self.trails
                elif attempt < max_retries - 1:
                    _LOGGER.warning(f"OSM query attempt {attempt + 1} returned no data, retrying in 3 seconds...")
                    await asyncio.sleep(3)
                    continue
            except Exception as e:
                if attempt < max_retries - 1:
                    _LOGGER.warning(f"Error fetching OSM data (attempt {attempt + 1}): {e}, retrying in 3 seconds...")
                    await asyncio.sleep(3)
                    continue
                else:
                    _LOGGER.error(f"Error fetching OSM data after {max_retries} attempts: {e}")
                    return {}

        return {}

    async def _query_overpass(self, query: str) -> Optional[Dict]:
        """Query the Overpass API with extended timeout."""
        try:
            async with async_timeout.timeout(90):
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        self._overpass_url,
                        data={"data": query}
                    ) as response:
                        response.raise_for_status()
                        return await response.json()
        except aiohttp.ClientError as e:
            _LOGGER.error(f"Overpass API request failed: {e}")
            return None
        except Exception as e:
            _LOGGER.error(f"Unexpected error querying Overpass API: {e}")
            return None

    async def fetch_trail_geometry(self, osm_id: int) -> Optional[Dict]:
        """
        Fetch detailed geometry for a specific trail.
        
        Returns a dict with:
        - coordinates: List of [lat, lon] points
        - center: [lat, lon] of trail center
        - geojson: GeoJSON LineString representation
        """
        query = f"""
        [out:json];
        way({osm_id});
        out geom;
        """
        
        try:
            response = await self._query_overpass(query)
            if response and response.get("elements"):
                way = response["elements"][0]
                geometry = way.get("geometry", [])
                
                if not geometry:
                    return None
                
                # Extract coordinates as [lat, lon] pairs
                coordinates = [[node["lat"], node["lon"]] for node in geometry]
                
                # Calculate center point (simple average)
                center_lat = sum(coord[0] for coord in coordinates) / len(coordinates)
                center_lon = sum(coord[1] for coord in coordinates) / len(coordinates)
                
                # Create GeoJSON LineString
                geojson = {
                    "type": "LineString",
                    "coordinates": [[coord[1], coord[0]] for coord in coordinates]  # GeoJSON uses [lon, lat]
                }
                
                return {
                    "coordinates": coordinates,  # [lat, lon] format for HA
                    "center": [center_lat, center_lon],
                    "geojson": geojson,
                    "bounds": {
                        "min_lat": min(coord[0] for coord in coordinates),
                        "max_lat": max(coord[0] for coord in coordinates),
                        "min_lon": min(coord[1] for coord in coordinates),
                        "max_lon": max(coord[1] for coord in coordinates),
                    }
                }
        except Exception as e:
            _LOGGER.error(f"Error fetching geometry for OSM way {osm_id}: {e}")
            return None
        
        return None

    def _parse_trails(self, data: Dict) -> Dict[str, Dict]:
        """Parse trail data from Overpass API response."""
        trails = {}
        nodes = {}
        
        elements = data.get("elements", [])
        _LOGGER.debug(f"Processing {len(elements)} elements from Overpass API")
        
        # First pass: collect all nodes
        for element in elements:
            if element.get("type") == "node":
                node_id = element.get("id")
                nodes[node_id] = {
                    "lat": element.get("lat"),
                    "lon": element.get("lon")
                }
        
        # Second pass: process ways with geometry
        for element in elements:
            if element.get("type") == "way":
                tags = element.get("tags", {})
                
                # Process ski pistes - check multiple tag combinations
                piste_type = tags.get("piste:type", "")
                if piste_type in ["downhill", "nordic", "skitour", "sled", "hike"]:
                    # Try multiple name tags
                    trail_name = (
                        tags.get("name") or
                        tags.get("piste:name") or
                        tags.get("ref") or
                        ""
                    ).strip()
                    trail_ref = tags.get("ref", "").strip()
                    
                    # Extract geometry if available
                    geometry = element.get("geometry", [])
                    coordinates = None
                    center = None
                    geojson = None
                    
                    if geometry:
                        # Geometry is already included in the response
                        coordinates = [[node["lat"], node["lon"]] for node in geometry]
                        
                        # Calculate center point
                        if coordinates:
                            center_lat = sum(coord[0] for coord in coordinates) / len(coordinates)
                            center_lon = sum(coord[1] for coord in coordinates) / len(coordinates)
                            center = [center_lat, center_lon]
                            
                            # Create GeoJSON LineString
                            geojson = {
                                "type": "LineString",
                                "coordinates": [[coord[1], coord[0]] for coord in coordinates]  # GeoJSON uses [lon, lat]
                            }
                    
                    # Create a unique key for matching
                    if trail_name:
                        trail_info = {
                            "osm_id": element.get("id"),
                            "name": trail_name,
                            "ref": trail_ref,
                            "piste_type": tags.get("piste:type"),
                            "difficulty": tags.get("piste:difficulty"),
                            "grooming": tags.get("piste:grooming"),
                            "lit": tags.get("lit"),
                            "oneway": tags.get("piste:oneway"),
                            "tags": tags,
                            "coordinates": coordinates,
                            "center": center,
                            "geojson": geojson,
                        }
                        
                        # Use name as primary key, with ref as fallback
                        key = trail_name.lower()
                        trails[key] = trail_info
                        
                        # Also index by ref if available
                        if trail_ref:
                            trails[f"ref_{trail_ref}"] = trail_info
                        
                        _LOGGER.debug(f"Added OSM trail: '{trail_name}' (ref: {trail_ref or 'none'}, id: {element.get('id')}, coords: {len(coordinates) if coordinates else 0})")

        _LOGGER.info(f"Parsed {len(trails)} trail entries from {len([e for e in elements if e.get('type') == 'way'])} ways")
        return trails

    def match_trail(self, trail_name: str, trail_number: Optional[str] = None) -> Optional[Dict]:
        """
        Match a Bromont trail to OSM data.
        
        Args:
            trail_name: Name of the trail from Bromont
            trail_number: Trail number/reference from Bromont
            
        Returns:
            OSM trail data if found, None otherwise
        """
        # Normalize the trail name by removing area suffix (e.g., "| Versant du Midi")
        normalized_name = self._normalize_trail_name(trail_name)
        
        # Try exact name match first
        key = normalized_name.lower().strip()
        if key in self.trails:
            _LOGGER.debug(f"Exact match found for '{trail_name}' -> OSM trail '{self.trails[key]['name']}'")
            return self.trails[key]
        
        # Try matching by trail number/ref
        if trail_number:
            ref_key = f"ref_{trail_number}"
            if ref_key in self.trails:
                _LOGGER.debug(f"Ref match found for '{trail_name}' (#{trail_number}) -> OSM trail '{self.trails[ref_key]['name']}'")
                return self.trails[ref_key]
        
        # Try fuzzy matching (remove common suffixes/prefixes)
        for osm_key, osm_trail in self.trails.items():
            if not osm_key.startswith("ref_"):
                # Simple fuzzy match - check if names are similar
                if self._names_similar(normalized_name, osm_trail["name"]):
                    _LOGGER.debug(f"Fuzzy match found for '{trail_name}' -> OSM trail '{osm_trail['name']}'")
                    return osm_trail
        
        _LOGGER.debug(f"No OSM match found for trail '{trail_name}' (#{trail_number})")
        return None

    def _normalize_trail_name(self, name: str) -> str:
        """
        Normalize trail name by removing area suffix.
        
        Bromont trail names often include area info like "Miami | Versant du Midi"
        but OSM names are usually just "Miami". This method strips the area suffix.
        """
        # Split on pipe character and take the first part
        if "|" in name:
            return name.split("|")[0].strip()
        return name.strip()
    
    def _names_similar(self, name1: str, name2: str) -> bool:
        """Check if two trail names are similar enough to be considered a match."""
        # Normalize names - remove accents, convert to lowercase, normalize punctuation
        n1 = self._normalize_for_comparison(name1)
        n2 = self._normalize_for_comparison(name2)
        
        # Exact match after normalization
        if n1 == n2:
            return True
        
        # Check if one contains the other (for cases like "Miami" vs "Miami | Versant du Midi")
        if n1 in n2 or n2 in n1:
            return True
        
        # Check with common variations removed
        n1_clean = self._remove_common_suffixes(n1)
        n2_clean = self._remove_common_suffixes(n2)
        
        if n1_clean == n2_clean:
            return True
        
        return False
    
    def _normalize_for_comparison(self, name: str) -> str:
        """Normalize a trail name for comparison by removing accents, punctuation, etc."""
        import unicodedata
        
        # Convert to lowercase
        name = name.lower().strip()
        
        # Remove accents (é -> e, à -> a, etc.)
        name = ''.join(
            c for c in unicodedata.normalize('NFD', name)
            if unicodedata.category(c) != 'Mn'
        )
        
        # Normalize apostrophes and quotes
        name = name.replace("'", " ").replace("'", " ").replace("`", " ")
        
        # Normalize hyphens and dashes
        name = name.replace("-", " ").replace("–", " ").replace("—", " ")
        
        # Remove multiple spaces
        name = " ".join(name.split())
        
        return name
    
    def _remove_common_suffixes(self, name: str) -> str:
        """Remove common trail suffixes like 'prk', 'park', etc."""
        # Remove common suffixes
        suffixes = [" prk", " park", " trail", " piste"]
        for suffix in suffixes:
            if name.endswith(suffix):
                name = name[:-len(suffix)].strip()
        return name

    def get_osm_url(self, osm_id: int) -> str:
        """Get the OpenStreetMap URL for a trail."""
        return f"https://www.openstreetmap.org/way/{osm_id}"