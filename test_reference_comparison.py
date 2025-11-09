#!/usr/bin/env python3
"""Test script to compare our Kala Bala implementation with reference test data."""

import sys
sys.path.append('.')

from datetime import datetime
from vedic.core import _calculate_kala_bala

# Test data from the reference (August 22, 1996, 12:23 PM IST, Coimbatore)
birth_dt = datetime(1996, 8, 22, 12, 23, 0)
lat = 10.59/60 + 10  # 10°59'N = 10.9833
lon = 76 + 57/60     # 76°57'E = 76.95

# Planetary longitudes from test data (sidereal)
planets_sidereal = {
    'Sun': 125.63,     # 125° 38' = 5° 38' Leo
    'Moon': 217.35,    # 217° 21' = 7° 21' Scorpio  
    'Mars': 84.37,     # 84° 22' = 24° 22' Gemini
    'Mercury': 152.95, # 152° 57' = 2° 57' Virgo
    'Jupiter': 254.23, # 254° 14' = 14° 14' Sagittarius
    'Venus': 79.9,     # 79° 54' = 19° 54' Gemini
    'Saturn': 342.62   # 342° 37' = 12° 37' Pisces
}

# Reference Kala Bala values from test data
reference_kala_bala = {
    'Moon': 117.35,
    'Sun': 239.0,
    'Mercury': 121.05,
    'Venus': 164.41,
    'Mars': 117.85,
    'Jupiter': 195.99,
    'Saturn': 116.36
}

# Individual Kala Bala components from test data
reference_components = {
    'Moon': {
        'Nathonnatha Bala': 0.17,
        'Paksha Bala': 61.14,
        'Tribhaga Bala': 0,
        'Varsha Bala': 0,
        'Masa Bala': 0,
        'Dina Bala': 0,
        'Hora Bala': 0,
        'Ayana Bala': 56.04,
        'Yudhdha Bala': 0
    },
    'Sun': {
        'Nathonnatha Bala': 59.83,
        'Paksha Bala': 29.43,
        'Tribhaga Bala': 60,
        'Varsha Bala': 0,
        'Masa Bala': 0,
        'Dina Bala': 0,
        'Hora Bala': 0,
        'Ayana Bala': 89.74,
        'Yudhdha Bala': 0
    },
    'Mercury': {
        'Nathonnatha Bala': 60,
        'Paksha Bala': 29.43,
        'Tribhaga Bala': 0,
        'Varsha Bala': 0,
        'Masa Bala': 0,
        'Dina Bala': 0,
        'Hora Bala': 0,
        'Ayana Bala': 31.62,
        'Yudhdha Bala': 0
    },
    'Venus': {
        'Nathonnatha Bala': 59.83,
        'Paksha Bala': 30.57,
        'Tribhaga Bala': 0,
        'Varsha Bala': 15,
        'Masa Bala': 0,
        'Dina Bala': 0,
        'Hora Bala': 0,
        'Ayana Bala': 59.01,
        'Yudhdha Bala': 0
    },
    'Mars': {
        'Nathonnatha Bala': 0.17,
        'Paksha Bala': 29.43,
        'Tribhaga Bala': 0,
        'Varsha Bala': 0,
        'Masa Bala': 30,
        'Dina Bala': 0,
        'Hora Bala': 0,
        'Ayana Bala': 58.25,
        'Yudhdha Bala': 0
    },
    'Jupiter': {
        'Nathonnatha Bala': 59.83,
        'Paksha Bala': 30.57,
        'Tribhaga Bala': 60,
        'Varsha Bala': 0,
        'Masa Bala': 0,
        'Dina Bala': 45,
        'Hora Bala': 0,
        'Ayana Bala': 0.58,
        'Yudhdha Bala': 0
    },
    'Saturn': {
        'Nathonnatha Bala': 0.17,
        'Paksha Bala': 29.43,
        'Tribhaga Bala': 0,
        'Varsha Bala': 0,
        'Masa Bala': 0,
        'Dina Bala': 0,
        'Hora Bala': 60,
        'Ayana Bala': 26.76,
        'Yudhdha Bala': 0
    }
}

print("KALA BALA COMPARISON - Reference vs Our Implementation")
print("=" * 70)
print(f"Birth: {birth_dt} IST")
print(f"Location: {lat}°N, {lon}°E (Coimbatore)")
print()

total_deviation = 0
planet_count = 0

for planet in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']:
    if planet in planets_sidereal and planet in reference_kala_bala:
        our_kala_bala = _calculate_kala_bala(planet, birth_dt, lat, lon, planets_sidereal)
        ref_kala_bala = reference_kala_bala[planet]
        deviation = our_kala_bala - ref_kala_bala
        
        print(f"{planet:8} | Our: {our_kala_bala:6.2f} | Ref: {ref_kala_bala:6.2f} | Dev: {deviation:+7.2f}")
        
        total_deviation += abs(deviation)
        planet_count += 1

print("-" * 70)
print(f"Average Deviation: {total_deviation/planet_count:.2f} Shashtiamsa")
print()

# Test specific components for Sun (largest deviation expected)
print("DETAILED COMPONENT ANALYSIS FOR SUN:")
print("-" * 50)

# We need to create a detailed version of our function to get component breakdown
# For now, let's analyze what might be causing deviations

print("Reference Sun components:")
for comp, value in reference_components['Sun'].items():
    print(f"  {comp:20}: {value:6.2f}")

print(f"\nTotal from components: {sum(reference_components['Sun'].values()):.2f}")
print(f"Reference total:       {reference_kala_bala['Sun']:.2f}")