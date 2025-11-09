#!/usr/bin/env python3
"""Test SaptavarigiyaBalaCalculator specifically."""

import sys
sys.path.append('.')

from vedic.core import SaptavarigiyaBalaCalculator

planets_sidereal = {
    'Sun': 61.5,
    'Moon': 215.8,
    'Mars': 89.3,
}

try:
    print("Testing SaptavarigiyaBalaCalculator...")
    
    saptavargiya_calculator = SaptavarigiyaBalaCalculator()
    print("Calculator instantiated")
    
    saptavargiya_analysis = saptavargiya_calculator.calculate_saptavargiya_bala(planets_sidereal)
    print("Analysis completed")
    
    print(f"Analysis keys: {list(saptavargiya_analysis.keys())}")
    
    if 'Sun' in saptavargiya_analysis:
        print(f"Sun data: {saptavargiya_analysis['Sun']}")

except Exception as e:
    print(f"Error in SaptavarigiyaBala: {e}")
    import traceback
    traceback.print_exc()