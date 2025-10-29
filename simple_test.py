#!/usr/bin/env python3
"""
Simple manual test to get planet positions for the test case
DOB: 22/08/1996 - 12:23 PM, Coimbatore, IN
"""

import requests
import json
from datetime import datetime

# Test data
test_data = {
    'datetime': '1996-08-22T12:23:00',
    'place': 'Coimbatore, India', 
    'lat': 11.0055,
    'lon': 76.9661,
    'tz_offset': 5.5,
    'ayanamsa': 'lahiri',
    'house_system': 'equal',
    'node_type': 'mean'
}

print("Testing Astrology App with:")
print(f"Date: 22/08/1996 - 12:23 PM")
print(f"Place: Coimbatore, India")
print(f"Coordinates: {test_data['lat']}°N, {test_data['lon']}°E")
print(f"Timezone: UTC+{test_data['tz_offset']}")
print("=" * 60)

try:
    # Make API call
    response = requests.post('http://localhost:5000/api/chart', json=test_data)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('ok'):
            chart_data = data['data']
            
            print("\n🎯 ASCENDANT:")
            if 'ascendant' in chart_data:
                asc = chart_data['ascendant']
                print(f"Ascendant: {asc:.2f}° ({asc//30 + 1} sign)")
            
            print("\n🪐 PLANET POSITIONS:")
            if 'planets' in chart_data:
                for planet, info in chart_data['planets'].items():
                    longitude = info.get('longitude', info.get('degree', 0))
                    sign = info.get('sign', 'Unknown')
                    deg_in_sign = info.get('degInSign', longitude % 30)
                    
                    print(f"{planet:10}: {longitude:7.2f}° | {deg_in_sign:5.2f}° in {sign}")
                    
                    if 'nakshatra' in info and isinstance(info['nakshatra'], dict):
                        nak_name = info['nakshatra'].get('name', 'Unknown')
                        print(f"           Nakshatra: {nak_name}")
            
            # Save full output for debugging
            with open('test_output.json', 'w') as f:
                json.dump(chart_data, f, indent=2)
            print(f"\n📁 Full output saved to: test_output.json")
            
        else:
            print(f"API Error: {data.get('error', 'Unknown error')}")
    else:
        print(f"HTTP Error: {response.status_code}")
        print(response.text)
        
except requests.exceptions.ConnectionError:
    print("❌ Cannot connect to Flask app. Please start it with: python app.py")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)
print("EXPECTED VALUES (from test data):")
print("Ascendant: 215.42° (5.42° in Scorpio)")
print("Sun      : 125.63° (5.63° in Leo)")
print("Moon     : 217.35° (7.35° in Scorpio)") 
print("Mercury  : 152.95° (2.95° in Virgo)")
print("Venus    : 79.90°  (19.90° in Gemini)")
print("Mars     : 84.37°  (24.37° in Gemini)")
print("Jupiter  : 254.23° (14.23° in Sagittarius)")
print("Saturn   : 342.62° (12.62° in Pisces)")
print("Rahu     : 166.22° (16.22° in Virgo)")
print("Ketu     : 346.22° (16.22° in Pisces)")
print("=" * 60)