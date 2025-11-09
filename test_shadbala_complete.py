#!/usr/bin/env python3
"""Test the complete _calculate_shadbala function with debug output."""

import sys
sys.path.append('.')

from datetime import datetime
from vedic.core import _calculate_shadbala

# Test data
birth_dt = datetime(1990, 6, 15, 14, 30, 0)
lat = 28.6139
lon = 77.2090

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
    print("Starting _calculate_shadbala function...")
    shadbala_analysis = _calculate_shadbala(planets_sidereal, cusps_map, birth_dt, lat, lon)
    print("Function completed successfully!")
    
    print(f"\nResult keys: {list(shadbala_analysis.keys())}")
    
    if 'shadbala_scores' in shadbala_analysis:
        scores = shadbala_analysis['shadbala_scores']
        print(f"Planet scores available for: {list(scores.keys())}")
        
        if 'Sun' in scores:
            sun_data = scores['Sun']
            print(f"\nSun Shadbala: {sun_data['total_shadbala']}")
            print(f"Components: {sun_data['components']}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()