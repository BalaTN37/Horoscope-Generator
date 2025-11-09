#!/usr/bin/env python3
"""Test script to verify complete Shadbala calculation with enhanced Kala Bala."""

from datetime import datetime
from vedic.core import _calculate_shadbala

# Test data
birth_dt = datetime(1990, 6, 15, 14, 30, 0)  # 2:30 PM on June 15, 1990
lat = 28.6139  # Delhi latitude
lon = 77.2090  # Delhi longitude

# Sample planetary longitudes (sidereal)
planets_sidereal = {
    'Sun': 61.5,      # Gemini 1°30'
    'Moon': 215.8,    # Scorpio 5°48'
    'Mars': 89.3,     # Cancer 29°18'
    'Mercury': 45.2,  # Taurus 15°12'
    'Jupiter': 150.7, # Virgo 0°42'
    'Venus': 72.1,    # Gemini 12°06'
    'Saturn': 279.4   # Capricorn 9°24'
}

# Sample house cusps (would be calculated by Swiss Ephemeris)
cusps_map = {
    1: 30,    # Taurus Ascendant
    2: 60,    # Gemini 2nd house
    3: 90,    # Cancer 3rd house
    4: 120,   # Leo 4th house
    5: 150,   # Virgo 5th house
    6: 180,   # Libra 6th house
    7: 210,   # Scorpio 7th house
    8: 240,   # Sagittarius 8th house
    9: 270,   # Capricorn 9th house
    10: 300,  # Aquarius 10th house
    11: 330,  # Pisces 11th house
    12: 0     # Aries 12th house
}

print("Testing Complete Shadbala Calculation with Enhanced Kala Bala")
print("=" * 60)
print(f"Birth: {birth_dt}")
print(f"Location: {lat}°N, {lon}°E")
print()

try:
    shadbala_analysis = _calculate_shadbala(planets_sidereal, cusps_map, birth_dt, lat, lon)
    
    print("SHADBALA ANALYSIS:")
    print("-" * 40)
    
    for planet, data in shadbala_analysis.items():
        if isinstance(data, dict) and 'total_shadbala' in data:
            print(f"\n{planet.upper()}:")
            print(f"  Total Shadbala: {data['total_shadbala']:6.2f} | Required: {data['required_strength']:6.2f}")
            print(f"  Strength: {data['strength_percentage']:5.1f}% | Category: {data['category']}")
            print(f"  Components:")
            for comp, value in data['components'].items():
                comp_name = comp.replace('_', ' ').title()
                print(f"    {comp_name:15}: {value:6.2f}")
            
            if 'sthana_bala_breakdown' in data:
                print(f"  Sthana Bala Details:")
                for comp, value in data['sthana_bala_breakdown'].items():
                    comp_name = comp.replace('_', ' ').title()
                    print(f"    {comp_name:15}: {value:6.2f}")

except Exception as e:
    print(f"Error in Shadbala calculation: {e}")
    import traceback
    traceback.print_exc()