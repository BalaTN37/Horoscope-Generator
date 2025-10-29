#!/usr/bin/env python3
import requests
import json

# Test data
test_data = {
    "datetime": "1996-08-22T12:23:00",
    "lat": 11.0118,
    "lon": 76.9628,
    "tz_offset": 5.5,
    "place": "Coimbatore"
}

# Make API request
try:
    response = requests.post('http://localhost:5000/api/chart', 
                           json=test_data, 
                           headers={'Content-Type': 'application/json'})
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Text: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get('ok'):
            result = data['data']
            print("\nSuccess! Planet positions:")
            for planet, info in result.get('planets', {}).items():
                if isinstance(info, dict):
                    lon = info.get('longitude', 'N/A')
                    sign = info.get('sign', 'N/A')
                    print(f"{planet}: {lon}° in {sign}")
            
            ascendant = result.get('ascendant', {})
            print(f"\nAscendant: {ascendant.get('longitude', 'N/A')}°")
        else:
            print(f"API Error: {data.get('error', 'Unknown error')}")
    else:
        print(f"HTTP Error: {response.status_code}")
        print(f"Response: {response.text}")

except Exception as e:
    print(f"Exception: {e}")