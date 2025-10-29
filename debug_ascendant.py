#!/usr/bin/env python3
"""
Debug script to check ayanamsa and ascendant calculation
"""

import swisseph as swe
from datetime import datetime, timezone, timedelta

# Test data
birth_dt_local = datetime(1996, 8, 22, 12, 23)
lat, lon = 11.0055, 76.9661
tz_offset_hours = 5.5

# Convert to UTC
birth_dt_utc = birth_dt_local - timedelta(hours=tz_offset_hours)
birth_dt_utc = birth_dt_utc.replace(tzinfo=timezone.utc)

def _julday(dt_utc: datetime) -> float:
    ut = dt_utc.hour + dt_utc.minute/60.0 + dt_utc.second/3600.0 + dt_utc.microsecond/3_600_000_000
    return swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, ut)

jd_ut = _julday(birth_dt_utc)

print(f"Birth time local: {birth_dt_local}")
print(f"Birth time UTC: {birth_dt_utc}")
print(f"Julian Day: {jd_ut}")

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

# Expected
print(f"Expected ascendant: 215.42°")
print(f"Difference: {abs(asc_sidereal - 215.42):.2f}°")

# Check what happens with sidereal flag directly
sidereal_iflag = swe.FLG_MOSEPH | swe.FLG_SIDEREAL
houses_res_sid = swe.houses_ex(jd_ut, lat, lon, b'E', sidereal_iflag)
cusps_sid, ascmc_sid = houses_res_sid
asc_direct_sidereal = ascmc_sid[0]
print(f"Direct sidereal calculation: {asc_direct_sidereal:.6f}°")