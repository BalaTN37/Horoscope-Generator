#!/usr/bin/env python3
"""
Quick test runner that can start the Flask app and run tests
"""

import subprocess
import time
import sys
import os
import signal
from test_planet_positions import test_astrology_api

def run_test_with_app():
    """Start Flask app, run test, then stop app"""
    
    print("🚀 Starting Astrology App Test Suite...")
    print("=" * 50)
    
    flask_process = None
    
    try:
        # Start Flask app
        print("Starting Flask application...")
        flask_process = subprocess.Popen(
            [sys.executable, 'app.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for Flask to start
        print("Waiting for Flask app to initialize...")
        time.sleep(3)
        
        # Check if Flask is still running
        if flask_process.poll() is not None:
            stdout, stderr = flask_process.communicate()
            print("Flask app failed to start!")
            print("STDOUT:", stdout.decode())
            print("STDERR:", stderr.decode())
            return False
        
        print("Flask app started successfully!")
        print("Running planet position validation test...\n")
        
        # Run the test
        success = test_astrology_api()
        
        return success
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        return False
        
    except Exception as e:
        print(f"Error during test: {e}")
        return False
        
    finally:
        # Clean up Flask process
        if flask_process and flask_process.poll() is None:
            print("\nStopping Flask application...")
            flask_process.terminate()
            try:
                flask_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                flask_process.kill()
                flask_process.wait()
            print("Flask application stopped.")

if __name__ == "__main__":
    success = run_test_with_app()
    
    if success:
        print("\n🎉 All tests passed! Your astrology app is working correctly.")
    else:
        print("\n❌ Tests failed. Please check the output above for details.")
    
    sys.exit(0 if success else 1)