"""
Local geocoding module using offline world cities database.
No internet connection required.
"""

import json
import os
from rapidfuzz import fuzz, process
from typing import List, Dict, Optional

class LocalGeocoder:
    def __init__(self, cities_file_path: str = "world_cities.json"):
        """Initialize the local geocoder with cities database."""
        self.cities_file_path = cities_file_path
        self.cities = []
        self.city_names = []
        self._load_cities()
    
    def _load_cities(self):
        """Load cities from the JSON file."""
        try:
            if os.path.exists(self.cities_file_path):
                with open(self.cities_file_path, 'r', encoding='utf-8') as f:
                    self.cities = json.load(f)
                
                # Create a searchable list of city names with full display names
                self.city_names = []
                for city in self.cities:
                    # Create display name: City, State, Country
                    display_name_parts = [city['name']]
                    
                    # Add state if available (especially for US cities)
                    if 'state' in city and city['state']:
                        display_name_parts.append(city['state'])
                    
                    # Add country name or code
                    if 'country' in city:
                        display_name_parts.append(city['country'])
                    
                    display_name = ', '.join(display_name_parts)
                    
                    self.city_names.append({
                        'name': display_name,
                        'search_name': city['name'].lower(),
                        'lat': float(city['lat']),
                        'lon': float(city['lng']),
                        'original': city
                    })
                
                print(f"Loaded {len(self.cities)} cities from local database")
            else:
                print(f"Cities file not found: {self.cities_file_path}")
                self.cities = []
                self.city_names = []
        except Exception as e:
            print(f"Error loading cities: {e}")
            self.cities = []
            self.city_names = []
    
    def search_cities(self, query: str, limit: int = 7) -> List[Dict]:
        """
        Search for cities matching the query string.
        Returns a list of dictionaries with name, lat, lon.
        """
        if not query or len(query.strip()) < 2:
            return []
        
        query = query.strip().lower()
        results = []
        
        # First, find exact matches and prefix matches
        exact_matches = []
        prefix_matches = []
        fuzzy_candidates = []
        
        for city_data in self.city_names:
            city_name_lower = city_data['search_name']
            display_name = city_data['name']
            
            # Exact match (highest priority)
            if city_name_lower == query:
                exact_matches.append(city_data)
            # Prefix match (high priority)
            elif city_name_lower.startswith(query):
                prefix_matches.append(city_data)
            # Contains query (medium priority)
            elif query in city_name_lower or query in display_name.lower():
                fuzzy_candidates.append(city_data)
        
        # Combine results in order of priority
        combined_results = exact_matches + prefix_matches + fuzzy_candidates
        
        # If we have enough results, return them
        if len(combined_results) >= limit:
            results = combined_results[:limit]
        else:
            # Use fuzzy matching for additional results
            all_city_names = [city['name'] for city in self.city_names]
            fuzzy_matches = process.extract(query, all_city_names, limit=limit*2, scorer=fuzz.partial_ratio)
            
            # Add fuzzy matches that aren't already in results
            existing_names = {city['name'] for city in combined_results}
            for match_name, score, _ in fuzzy_matches:  # rapidfuzz returns (match, score, index)
                if score > 60 and match_name not in existing_names:  # Minimum similarity threshold
                    # Find the city data for this match
                    for city_data in self.city_names:
                        if city_data['name'] == match_name:
                            combined_results.append(city_data)
                            break
                if len(combined_results) >= limit:
                    break
            
            results = combined_results[:limit]
        
        # Format results for API response
        formatted_results = []
        for city_data in results:
            formatted_results.append({
                'name': city_data['name'],
                'lat': city_data['lat'],
                'lon': city_data['lon']
            })
        
        return formatted_results

    def geocode_single(self, query: str) -> Optional[Dict]:
        """
        Geocode a single location and return the best match.
        Returns None if no good match is found.
        """
        results = self.search_cities(query, limit=1)
        return results[0] if results else None


def test_geocoder():
    """Test function for the local geocoder."""
    geocoder = LocalGeocoder()
    
    test_queries = ["New York", "London", "Delhi", "Mumbai", "Paris", "Tokyo"]
    
    for query in test_queries:
        print(f"\nSearching for '{query}':")
        results = geocoder.search_cities(query, limit=3)
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result['name']} ({result['lat']}, {result['lon']})")


if __name__ == "__main__":
    test_geocoder()