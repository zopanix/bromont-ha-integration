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

    def match_trail(self, trail_name: str, trail_number: Optional[str] = None,
                   difficulty: Optional[str] = None) -> Optional[Dict]:
        """
        Match a Bromont trail to OSM data using enhanced fuzzy matching.
        
        Args:
            trail_name: Name of the trail from Bromont
            trail_number: Trail number/reference from Bromont
            difficulty: Trail difficulty level (optional, used for secondary matching)
            
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
        
        # Try fuzzy matching with confidence scoring
        best_match = None
        best_score = 0.0
        
        for osm_key, osm_trail in self.trails.items():
            if not osm_key.startswith("ref_"):
                osm_difficulty = osm_trail.get("difficulty")
                
                # Check if names are similar (includes confidence scoring internally)
                if self._names_similar(normalized_name, osm_trail["name"], difficulty, osm_difficulty):
                    # Calculate detailed score for ranking multiple matches
                    score = self._calculate_similarity_score(
                        self._normalize_for_comparison(normalized_name),
                        self._normalize_for_comparison(osm_trail["name"]),
                        difficulty,
                        osm_difficulty
                    )
                    
                    if score > best_score:
                        best_score = score
                        best_match = osm_trail
        
        if best_match:
            _LOGGER.info(f"Fuzzy match found for '{trail_name}' -> OSM trail '{best_match['name']}' (confidence: {best_score:.2%})")
            return best_match
        
        _LOGGER.debug(f"No OSM match found for trail '{trail_name}' (#{trail_number})")
        return None

    def _normalize_trail_name(self, name: str) -> str:
        """
        Normalize trail name by removing area suffix and common variations.
        
        Bromont trail names often include area info like "Miami | Versant du Midi"
        but OSM names are usually just "Miami". This method strips the area suffix
        and handles various French naming conventions.
        """
        # Split on pipe character and take the first part
        if "|" in name:
            name = name.split("|")[0].strip()
        else:
            name = name.strip()
        
        # Remove common French prefixes (case-insensitive)
        prefixes_to_remove = [
            "piste ", "piste de ", "piste du ", "piste des ",
            "trail ", "la ", "le ", "les ", "l'",
            "sentier ", "sentier de ", "sentier du ", "sentier des "
        ]
        
        name_lower = name.lower()
        for prefix in prefixes_to_remove:
            if name_lower.startswith(prefix):
                # Preserve original case for the remaining part
                name = name[len(prefix):]
                break
        
        # Remove numeric suffixes (e.g., "Miami 2" -> "Miami")
        # But preserve trail numbers at the start (e.g., "47 Cowansville")
        import re
        # Match patterns like " 2", " II", " bis" at the end
        name = re.sub(r'\s+\d+$', '', name)  # Remove trailing numbers
        name = re.sub(r'\s+[IVX]+$', '', name)  # Remove Roman numerals
        name = re.sub(r'\s+(bis|ter)$', '', name, flags=re.IGNORECASE)  # Remove bis/ter
        
        return name.strip()
    
    def _names_similar(self, name1: str, name2: str, difficulty1: str = None, difficulty2: str = None) -> bool:
        """
        Check if two trail names are similar enough to be considered a match.
        
        Uses multiple matching strategies with confidence scoring:
        - Exact match after normalization
        - Substring matching
        - Levenshtein distance for typo tolerance
        - Phonetic matching for French names
        - Difficulty as secondary factor
        """
        # Normalize names - remove accents, convert to lowercase, normalize punctuation
        n1 = self._normalize_for_comparison(name1)
        n2 = self._normalize_for_comparison(name2)
        
        # Exact match after normalization (100% confidence)
        if n1 == n2:
            _LOGGER.debug(f"Exact match: '{name1}' == '{name2}'")
            return True
        
        # Check if one contains the other (90% confidence)
        if n1 in n2 or n2 in n1:
            _LOGGER.debug(f"Substring match: '{name1}' ~ '{name2}'")
            return True
        
        # Check with common variations removed (85% confidence)
        n1_clean = self._remove_common_suffixes(n1)
        n2_clean = self._remove_common_suffixes(n2)
        
        if n1_clean == n2_clean:
            _LOGGER.debug(f"Clean match: '{name1}' ~ '{name2}'")
            return True
        
        # Calculate similarity score using multiple methods
        similarity_score = self._calculate_similarity_score(n1, n2, difficulty1, difficulty2)
        
        # Match if similarity score is above threshold (75%)
        if similarity_score >= 0.75:
            _LOGGER.debug(f"Fuzzy match: '{name1}' ~ '{name2}' (score: {similarity_score:.2f})")
            return True
        
        return False
    
    def _calculate_similarity_score(self, name1: str, name2: str,
                                    difficulty1: str = None, difficulty2: str = None) -> float:
        """
        Calculate overall similarity score using multiple methods.
        
        Returns a score between 0.0 and 1.0, where 1.0 is a perfect match.
        """
        scores = []
        weights = []
        
        # 1. Levenshtein distance (weight: 0.4)
        lev_score = self._levenshtein_similarity(name1, name2)
        scores.append(lev_score)
        weights.append(0.4)
        
        # 2. Token-based matching (weight: 0.3)
        token_score = self._token_similarity(name1, name2)
        scores.append(token_score)
        weights.append(0.3)
        
        # 3. Phonetic matching for French names (weight: 0.2)
        phonetic_score = self._phonetic_similarity(name1, name2)
        scores.append(phonetic_score)
        weights.append(0.2)
        
        # 4. Difficulty matching as secondary factor (weight: 0.1)
        if difficulty1 and difficulty2:
            difficulty_score = 1.0 if self._difficulties_match(difficulty1, difficulty2) else 0.0
            scores.append(difficulty_score)
            weights.append(0.1)
        
        # Calculate weighted average
        total_weight = sum(weights)
        weighted_score = sum(s * w for s, w in zip(scores, weights)) / total_weight
        
        return weighted_score
    
    def _levenshtein_similarity(self, s1: str, s2: str) -> float:
        """
        Calculate similarity using Levenshtein distance.
        
        Returns a score between 0.0 and 1.0, where 1.0 means identical strings.
        """
        if not s1 or not s2:
            return 0.0
        
        # Calculate Levenshtein distance
        len1, len2 = len(s1), len(s2)
        if len1 < len2:
            s1, s2 = s2, s1
            len1, len2 = len2, len1
        
        # Create distance matrix
        current_row = range(len2 + 1)
        for i in range(1, len1 + 1):
            previous_row = current_row
            current_row = [i] + [0] * len2
            for j in range(1, len2 + 1):
                add = previous_row[j] + 1
                delete = current_row[j - 1] + 1
                change = previous_row[j - 1]
                if s1[i - 1] != s2[j - 1]:
                    change += 1
                current_row[j] = min(add, delete, change)
        
        distance = current_row[len2]
        max_len = max(len1, len2)
        
        # Convert distance to similarity (0.0 to 1.0)
        similarity = 1.0 - (distance / max_len)
        return similarity
    
    def _token_similarity(self, name1: str, name2: str) -> float:
        """
        Calculate similarity based on matching tokens (words).
        
        Returns the ratio of matching tokens to total tokens.
        """
        tokens1 = set(name1.split())
        tokens2 = set(name2.split())
        
        if not tokens1 or not tokens2:
            return 0.0
        
        # Calculate Jaccard similarity
        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _phonetic_similarity(self, name1: str, name2: str) -> float:
        """
        Calculate phonetic similarity for French names.
        
        Uses simplified French phonetic rules to handle common variations.
        """
        # Apply French phonetic transformations
        p1 = self._french_phonetic(name1)
        p2 = self._french_phonetic(name2)
        
        # Use Levenshtein on phonetic versions
        return self._levenshtein_similarity(p1, p2)
    
    def _french_phonetic(self, text: str) -> str:
        """
        Apply simplified French phonetic rules.
        
        Handles common French pronunciation patterns.
        """
        import re
        
        # Convert to lowercase
        text = text.lower()
        
        # French phonetic rules (simplified)
        rules = [
            (r'ph', 'f'),           # philosophie -> filosofie
            (r'qu', 'k'),           # quebec -> kebec
            (r'ch', 'sh'),          # chalet -> shalet
            (r'eau', 'o'),          # chateau -> shato
            (r'au', 'o'),           # auto -> oto
            (r'oi', 'wa'),          # roi -> rwa
            (r'ou', 'u'),           # rouge -> ruge
            (r'ain', 'in'),         #omain -> domin
            (r'ein', 'in'),         # plein -> plin
            (r'tion', 'sion'),      # station -> stasion
            (r'x$', 's'),           # deux -> deus
            (r'[sz]$', ''),         # paris -> pari
            (r'e$', ''),            # piste -> pist
            (r'ent$', ''),          # parent -> par
        ]
        
        for pattern, replacement in rules:
            text = re.sub(pattern, replacement, text)
        
        # Remove silent letters
        text = re.sub(r'h', '', text)  # Remove h
        
        return text
    
    def _difficulties_match(self, diff1: str, diff2: str) -> bool:
        """
        Check if two difficulty levels match or are compatible.
        
        Handles various difficulty naming conventions.
        """
        if not diff1 or not diff2:
            return False
        
        # Normalize difficulty names
        difficulty_map = {
            'facile': ['easy', 'green', 'beginner', 'facile', 'vert'],
            'intermed': ['intermediate', 'blue', 'intermed', 'intermediaire', 'bleu'],
            'difficile': ['difficult', 'black', 'difficile', 'noir', 'advanced'],
            'tdifficile': ['expert', 'double-black', 'tdifficile', 'tres-difficile', 'expert'],
        }
        
        d1_norm = diff1.lower().strip()
        d2_norm = diff2.lower().strip()
        
        # Direct match
        if d1_norm == d2_norm:
            return True
        
        # Check if both belong to same category
        for category, variants in difficulty_map.items():
            if d1_norm in variants and d2_norm in variants:
                return True
        
        return False
    
    def _normalize_for_comparison(self, name: str) -> str:
        """
        Normalize a trail name for comparison by removing accents, punctuation, etc.
        
        Handles French-specific characters and common variations to improve matching.
        """
        import unicodedata
        import re
        
        # Convert to lowercase
        name = name.lower().strip()
        
        # Handle French ligatures and special characters before accent removal
        french_replacements = {
            'œ': 'oe',
            'æ': 'ae',
            'ç': 'c',
            'ñ': 'n',
        }
        for old, new in french_replacements.items():
            name = name.replace(old, new)
        
        # Remove accents (é -> e, à -> a, etc.)
        name = ''.join(
            c for c in unicodedata.normalize('NFD', name)
            if unicodedata.category(c) != 'Mn'
        )
        
        # Normalize apostrophes and quotes
        name = name.replace("'", " ").replace("'", " ").replace("`", " ").replace("'", " ")
        
        # Normalize hyphens and dashes to spaces
        name = name.replace("-", " ").replace("–", " ").replace("—", " ").replace("_", " ")
        
        # Remove common French articles and prepositions
        articles = ['le ', 'la ', 'les ', 'l ', 'de ', 'du ', 'des ', 'd ']
        for article in articles:
            # Remove at start
            if name.startswith(article):
                name = name[len(article):]
            # Remove in middle (with spaces around)
            name = name.replace(' ' + article, ' ')
        
        # Remove punctuation except spaces
        name = re.sub(r'[^\w\s]', '', name)
        
        # Remove numeric suffixes (e.g., "miami 2" -> "miami")
        name = re.sub(r'\s+\d+$', '', name)
        name = re.sub(r'\s+[ivx]+$', '', name)  # Roman numerals
        
        # Remove multiple spaces and trim
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