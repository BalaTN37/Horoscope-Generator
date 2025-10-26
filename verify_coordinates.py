"""
Coordinate Verification Utility
Helps verify the accuracy of coordinates returned by the local geocoder.
"""

import math
from local_geocoder import LocalGeocoder

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two coordinates using Haversine formula."""
    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371  # Radius of earth in kilometers
    return c * r

def verify_coordinates(city_name, expected_lat=None, expected_lon=None, show_alternatives=True):
    """
    Verify coordinates for a given city name.
    
    Args:
        city_name (str): Name of the city to search
        expected_lat (float, optional): Expected latitude for comparison
        expected_lon (float, optional): Expected longitude for comparison  
        show_alternatives (bool): Whether to show alternative matches
    
    Returns:
        dict: Results with coordinates and accuracy info
    """
    geocoder = LocalGeocoder()
    results = geocoder.search_cities(city_name, limit=5)
    
    print(f"\nSearching for: '{city_name}'")
    print("=" * 50)
    
    if not results:
        print("ERROR: No results found")
        return {"found": False, "results": []}
    
    # Show primary result
    primary = results[0]
    print(f"Primary result: {primary['name']}")
    print(f"   Coordinates: ({primary['lat']}, {primary['lon']})")
    
    # Calculate distance if expected coordinates provided
    distance_info = None
    if expected_lat is not None and expected_lon is not None:
        distance = calculate_distance(expected_lat, expected_lon, primary['lat'], primary['lon'])
        distance_info = {
            "distance_km": distance,
            "accurate": distance <= 50
        }
        
        status = "ACCURATE" if distance <= 50 else "INACCURATE"
        print(f"   Distance from expected: {distance:.2f} km [{status}]")
        print(f"   Expected: ({expected_lat}, {expected_lon})")
    
    # Google Maps link for verification
    gmaps_url = f"https://www.google.com/maps?q={primary['lat']},{primary['lon']}"
    print(f"   Verify on Google Maps: {gmaps_url}")
    
    # Show alternatives
    if show_alternatives and len(results) > 1:
        print(f"\nAlternative matches:")
        for i, result in enumerate(results[1:4], 2):
            alt_distance_info = None
            if expected_lat is not None and expected_lon is not None:
                alt_distance = calculate_distance(expected_lat, expected_lon, result['lat'], result['lon'])
                alt_status = "ACCURATE" if alt_distance <= 50 else "INACCURATE"
                alt_distance_info = {"distance_km": alt_distance, "accurate": alt_distance <= 50}
                print(f"   {i}. {result['name']} ({result['lat']}, {result['lon']}) - {alt_distance:.2f}km [{alt_status}]")
            else:
                print(f"   {i}. {result['name']} ({result['lat']}, {result['lon']})")
    
    return {
        "found": True,
        "primary": primary,
        "distance_info": distance_info,
        "alternatives": results[1:] if len(results) > 1 else [],
        "gmaps_url": gmaps_url
    }

def batch_verify(city_list):
    """
    Verify multiple cities at once.
    
    Args:
        city_list (list): List of city names or dicts with expected coordinates
    """
    print("BATCH COORDINATE VERIFICATION")
    print("=" * 60)
    
    results = []
    accurate_count = 0
    
    for i, city in enumerate(city_list, 1):
        if isinstance(city, str):
            # Simple city name
            result = verify_coordinates(city, show_alternatives=False)
        else:
            # Dict with expected coordinates
            result = verify_coordinates(
                city['name'], 
                city.get('lat'), 
                city.get('lon'),
                show_alternatives=False
            )
            if result['distance_info'] and result['distance_info']['accurate']:
                accurate_count += 1
        
        results.append(result)
        
        if i < len(city_list):
            print()  # Add spacing between results
    
    # Summary
    if any(isinstance(city, dict) for city in city_list):
        total_with_expected = sum(1 for city in city_list if isinstance(city, dict))
        if total_with_expected > 0:
            accuracy_rate = (accurate_count / total_with_expected) * 100
            print(f"\nSUMMARY: {accurate_count}/{total_with_expected} accurate ({accuracy_rate:.1f}%)")
    
    return results

def quick_test():
    """Quick test with some common cities."""
    test_cities = [
        {"name": "New York", "lat": 40.7128, "lon": -74.0060},
        {"name": "London England", "lat": 51.5074, "lon": -0.1278},
        {"name": "Tokyo", "lat": 35.6762, "lon": 139.6503},
        {"name": "Mumbai", "lat": 19.0760, "lon": 72.8777},
        {"name": "Sydney", "lat": -33.8688, "lon": 151.2093},
    ]
    
    return batch_verify(test_cities)

if __name__ == "__main__":
    print("Coordinate Verification Utility")
    print("Type 'help' for commands, 'quit' to exit")
    
    while True:
        user_input = input("\n> ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            break
        elif user_input.lower() in ['help', 'h']:
            print("""
Available commands:
- Enter a city name to search (e.g., 'Paris France')
- 'test' - Run quick accuracy test
- 'help' - Show this help
- 'quit' - Exit program
            """)
        elif user_input.lower() == 'test':
            quick_test()
        elif user_input:
            verify_coordinates(user_input)
        else:
            print("Please enter a city name or command.")