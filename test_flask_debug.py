#!/usr/bin/env python3
import subprocess
import time
import sys
import os

print("Starting Flask app...")
flask_proc = subprocess.Popen([sys.executable, 'app.py'], 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.STDOUT,
                              text=True,
                              bufsize=1,
                              universal_newlines=True)

# Wait for Flask to start and capture output
time.sleep(3)

print("Testing API...")
import requests
import json

try:
    test_data = {
        "datetime": "1996-08-22T12:23:00",
        "lat": 11.0118,
        "lon": 76.9628,
        "tz_offset": 5.5,
        "place": "Coimbatore"
    }

    response = requests.post('http://localhost:5000/api/chart', 
                           json=test_data, 
                           headers={'Content-Type': 'application/json'})
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
finally:
    print("Stopping Flask...")
    flask_proc.terminate()
    flask_proc.wait()
    
    # Get Flask output
    output, _ = flask_proc.communicate()
    if output:
        print("\nFlask Output:")
        print(output)