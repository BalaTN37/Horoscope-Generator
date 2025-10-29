#!/usr/bin/env python3
"""
Compare debug_ascendant.py calculation vs core.py calculation
"""

import swisseph as swe
from datetime import datetime, timezone, timedelta

# Test data - EXACT same as core.py receives
birth_dt_local = datetime(1996, 8, 22, 12, 23)
lat, lon = 11.0055, 76.9661
tz_offset_hours = 5.5

print("=== WORKING DEBUG SCRIPT CALCULATION ===")

# Convert to UTC - EXACT same as core.py
birth_dt_utc = birth_dt_local - timedelta(hours=tz_offset_hours)
birth_dt_utc = birth_dt_utc.replace(tzinfo=timezone.utc)

def _julday(dt_utc: datetime) -> float:
    ut = dt_utc.hour + dt_utc.minute/60.0 + dt_utc.second/3600.0 + dt_utc.microsecond/3_600_000_000
    return swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, ut)

jd_ut = _julday(birth_dt_utc)

print(f"Birth time local: {birth_dt_local}")
print(f"Birth time UTC: {birth_dt_utc}")
print(f"Julian Day: {jd_ut}")
print(f"Lat: {lat}, Lon: {lon}")

# Set Lahiri ayanamsa
swe.set_sid_mode(swe.SIDM_LAHIRI)

# Get ayanamsa
ayanamsa = swe.get_ayanamsa_ut(jd_ut)
print(f"Ayanamsa (Lahiri): {ayanamsa:.6f}°")

# Calculate houses in tropical
tropical_iflag = swe.FLG_MOSEPH
houses_res = swe.houses_ex(jd_ut, lat, lon, b'E', tropical_iflag)
cusps, ascmc = houses_res
asc_tropical = ascmc[0]
print(f"Ascendant (tropical): {asc_tropical:.6f}°")

# Convert to sidereal
asc_sidereal = (asc_tropical - ayanamsa) % 360
print(f"Ascendant (sidereal): {asc_sidereal:.6f}°")
print(f"Expected ascendant: 215.42°")
print(f"Match: {abs(asc_sidereal - 215.42) < 1.0}")

print("\n=== CORE.PY EQUIVALENT ===")
# Now import core.py and see what it gives
from vedic.core import compute_chart

try:
    result = compute_chart(birth_dt_local, lat, lon, tz_offset_hours, 'lahiri', 'equal')
    print(f"Core.py result: {result.get('ascendant', 'ERROR')}")
except Exception as e:
    print(f"Error in core.py: {e}")