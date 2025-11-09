#!/usr/bin/env python3
"""Test Sthana Bala component specifically."""

import sys
sys.path.append('.')

from datetime import datetime
from vedic.core import _calculate_sthana_bala, _sign_index

planets_sidereal = {
    'Sun': 61.5,
    'Moon': 215.8,
    'Mars': 89.3,
}

cusps_map = {
    1: 30, 2: 60, 3: 90, 4: 120, 5: 150, 6: 180,
    7: 210, 8: 240, 9: 270, 10: 300, 11: 330, 12: 0
}

try:
    planet_name = 'Sun'
    planet_lon = planets_sidereal[planet_name]
    planet_sign = _sign_index(planet_lon)
    
    print(f"Testing Sthana Bala for {planet_name}:")
    print(f"Longitude: {planet_lon}, Sign: {planet_sign}")
    
    sthana_bala = _calculate_sthana_bala(planet_name, planet_lon, planet_sign, cusps_map)
    print(f"Sthana Bala: {sthana_bala}")
    
    print("Sthana Bala calculated successfully!")

except Exception as e:
    print(f"Error in Sthana Bala: {e}")
    import traceback
    traceback.print_exc()