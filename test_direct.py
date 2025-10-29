#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
from vedic.core import compute_chart

# Test data
birth_dt = datetime.fromisoformat("1996-08-22T12:23:00")
lat = 11.0118
lon = 76.9628
tz_offset = 5.5
ayanamsa = "lahiri"
house_system = "equal"
node_type = "mean"

print("Testing compute_chart function directly...")
print(f"Parameters:")
print(f"  birth_dt: {birth_dt}")
print(f"  lat: {lat}, lon: {lon}")
print(f"  tz_offset: {tz_offset}")
print(f"  ayanamsa: '{ayanamsa}' (type: {type(ayanamsa)})")
print(f"  house_system: '{house_system}' (type: {type(house_system)})")
print(f"  node_type: '{node_type}' (type: {type(node_type)})")

try:
    result = compute_chart(birth_dt, lat, lon, tz_offset, ayanamsa, house_system, node_type=node_type)
    print("\nSuccess! Chart computed.")
    print(f"Ascendant longitude: {result['ascendant']}")
    
    print("\nPlanet positions:")
    for planet, info in result.get('planets', {}).items():
        if isinstance(info, dict):
            lon = info.get('longitude', 'N/A')
            sign = info.get('sign', 'N/A')
            print(f"{planet}: {lon}° in {sign}")
    
except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()