#!/usr/bin/env python3
"""
Direct test of compute_chart function to see if changes are applied
"""

from datetime import datetime
from vedic.core import compute_chart

# Test data
birth_dt = datetime(1996, 8, 22, 12, 23)
lat, lon = 11.0055, 76.9661
tz_offset = 5.5

print("Testing compute_chart directly...")

result = compute_chart(birth_dt, lat, lon, tz_offset, 'lahiri', 'equal')

print(f"Ascendant: {result['ascendant']}")
print(f"Expected: 215.42")
print(f"Match: {abs(result['ascendant'] - 215.42) < 1.0}")