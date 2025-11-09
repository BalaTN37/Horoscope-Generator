from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
import math
import swisseph as swe
import os

ZODIAC_SIGNS = [
    'Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces'
]

PLANET_ORDER = [
    ('Sun', swe.SUN), ('Moon', swe.MOON), ('Mars', swe.MARS), ('Mercury', swe.MERCURY),
    ('Jupiter', swe.JUPITER), ('Venus', swe.VENUS), ('Saturn', swe.SATURN)
]

ABBR = {'Sun':'Su','Moon':'Mo','Mars':'Ma','Mercury':'Me','Jupiter':'Ju','Venus':'Ve','Saturn':'Sa','Rahu':'Ra','Ketu':'Ke'}

# Vimshottari dasha constants
NAK_LEN_DEG = 360.0 / 27.0  # 13°20'
VIM_MD_YEARS = {
    'Ketu': 7,
    'Venus': 20,
    'Sun': 6,
    'Moon': 10,
    'Mars': 7,
    'Rahu': 18,
    'Jupiter': 16,
    'Saturn': 19,
    'Mercury': 17,
}
VIM_SEQUENCE = ['Ketu','Venus','Sun','Moon','Mars','Rahu','Jupiter','Saturn','Mercury']
NAK_LORDS = [
    'Ketu','Venus','Sun','Moon','Mars','Rahu','Jupiter','Saturn','Mercury', # Ashwini..Ashlesha (0..8)
    'Ketu','Venus','Sun','Moon','Mars','Rahu','Jupiter','Saturn','Mercury', # Magha..Jyeshtha (9..17)
    'Ketu','Venus','Sun','Moon','Mars','Rahu','Jupiter','Saturn','Mercury'  # Mula..Revati (18..26)
]

# Shadbala calculation constants
# Sign rulership constants
SIGN_RULERS = {
    0: 'Mars',     # Aries
    1: 'Venus',    # Taurus  
    2: 'Mercury',  # Gemini
    3: 'Moon',     # Cancer
    4: 'Sun',      # Leo
    5: 'Mercury',  # Virgo
    6: 'Venus',    # Libra
    7: 'Mars',     # Scorpio
    8: 'Jupiter',  # Sagittarius
    9: 'Saturn',   # Capricorn
    10: 'Saturn',  # Aquarius
    11: 'Jupiter'  # Pisces
}

# Panchadha Maitri constants
PERMANENT_FRIENDSHIP = [
    {"planet": "Sun", "friend": ["Moon", "Mars", "Jupiter"], "neutral": ["Mercury"], "enemy": ["Venus", "Saturn"]},
    {"planet": "Moon", "friend": ["Sun", "Mercury"], "neutral": ["Mars", "Jupiter", "Venus", "Saturn"], "enemy": []},
    {"planet": "Mars", "friend": ["Sun", "Moon", "Jupiter"], "neutral": ["Venus", "Saturn"], "enemy": ["Mercury"]},
    {"planet": "Mercury", "friend": ["Venus", "Sun"], "neutral": ["Mars", "Jupiter", "Saturn"], "enemy": ["Moon"]},
    {"planet": "Jupiter", "friend": ["Sun", "Moon", "Mars"], "neutral": ["Saturn"], "enemy": ["Mercury", "Venus"]},
    {"planet": "Venus", "friend": ["Mercury", "Saturn"], "neutral": ["Mars", "Jupiter"], "enemy": ["Sun", "Moon"]},
    {"planet": "Saturn", "friend": ["Mercury", "Venus"], "neutral": ["Jupiter"], "enemy": ["Sun", "Mars", "Moon"]}
]

PANCHADHA_MAITRI_RULES = [
    {"naisargik": "Friend", "temporary": "Friend", "resultant": "Extreme Friend", "code": "EF"},
    {"naisargik": "Friend", "temporary": "Neutral", "resultant": "Friend", "code": "F"},
    {"naisargik": "Friend", "temporary": "Enemy", "resultant": "Neutral", "code": "N"},
    {"naisargik": "Neutral", "temporary": "Friend", "resultant": "Friend", "code": "F"},
    {"naisargik": "Neutral", "temporary": "Neutral", "resultant": "Neutral", "code": "N"},
    {"naisargik": "Neutral", "temporary": "Enemy", "resultant": "Enemy", "code": "E"},
    {"naisargik": "Enemy", "temporary": "Friend", "resultant": "Neutral", "code": "N"},
    {"naisargik": "Enemy", "temporary": "Neutral", "resultant": "Enemy", "code": "E"},
    {"naisargik": "Enemy", "temporary": "Enemy", "resultant": "Extreme Enemy", "code": "EE"}
]

SHADBALA_CONSTANTS = {
    'naisargika_bala': {
        'Sun': 60, 'Moon': 51.43, 'Mars': 17.14, 'Mercury': 25.71,
        'Jupiter': 34.29, 'Venus': 42.86, 'Saturn': 8.57
    },
    'exaltation_degrees': {
        'Sun': 10, 'Moon': 33, 'Mars': 298, 'Mercury': 165,
        'Jupiter': 95, 'Venus': 357, 'Saturn': 200
    },
    'debilitation_degrees': {
        'Sun': 190, 'Moon': 213, 'Mars': 118, 'Mercury': 345,
        'Jupiter': 275, 'Venus': 177, 'Saturn': 20
    },
    # UchchaBala reference data from classical texts
    'uchcha_bala_data': {
        'Sun': {'exaltation_degree': 10, 'debilitation_degree': 190},  # Aries 10° / Libra 10°
        'Moon': {'exaltation_degree': 33, 'debilitation_degree': 213},  # Taurus 3° / Scorpio 3° 
        'Mars': {'exaltation_degree': 298, 'debilitation_degree': 118},  # Capricorn 28° / Cancer 28°
        'Mercury': {'exaltation_degree': 165, 'debilitation_degree': 345},  # Virgo 15° / Pisces 15°
        'Jupiter': {'exaltation_degree': 95, 'debilitation_degree': 275},  # Cancer 5° / Capricorn 5°
        'Venus': {'exaltation_degree': 357, 'debilitation_degree': 177},  # Pisces 27° / Virgo 27°
        'Saturn': {'exaltation_degree': 200, 'debilitation_degree': 20}  # Libra 20° / Aries 20°
    },
    'own_signs': {
        'Sun': [4], 'Moon': [3], 'Mars': [0, 7], 'Mercury': [2, 5],
        'Jupiter': [8, 11], 'Venus': [1, 6], 'Saturn': [9, 10]
    },
    'minimum_required': {
        'Sun': 300, 'Moon': 360, 'Mars': 300, 'Mercury': 420,
        'Jupiter': 390, 'Venus': 330, 'Saturn': 300
    }
}

# Mooltrikona (Root Trine) positions - most auspicious position for each planet
MOOLTRIKONA_RANGES = {
    'Sun': {'sign': 4, 'start': 0, 'end': 20},      # Leo 0-20°
    'Moon': {'sign': 1, 'start': 4, 'end': 30},     # Taurus 4-30°
    'Mars': {'sign': 0, 'start': 0, 'end': 12},     # Aries 0-12°
    'Mercury': {'sign': 5, 'start': 16, 'end': 20}, # Virgo 16-20°
    'Jupiter': {'sign': 8, 'start': 0, 'end': 10},  # Sagittarius 0-10°
    'Venus': {'sign': 6, 'start': 0, 'end': 15},    # Libra 0-15°
    'Saturn': {'sign': 10, 'start': 0, 'end': 20}   # Aquarius 0-20°
}

# Saptavargiya Bala point system based on relationship type
# SaptavarigiyaBala point system (EXACT as per reference document)
SAPTAVARGIYA_POINTS = {
    'Mooltrikona': 45.0,        # Mooltrikona sign = 45 Shashtiamsa (Rashi chart only)
    'Own': 30.0,                # Own sign (Sva Rashi) = 30 Shashtiamsa
    'Fast Friend': 22.5,        # Fast friends sign (Adhi Mitra Rashi) = 22.5 Shashtiamsa  
    'Friend': 15.0,             # Friend's Sign (Mitra Rashi) = 15 Shashtiamsa
    'Neutral': 7.5,             # Neutrals' sign (Sama Rashi) = 7.5 Shashtiamsa
    'Enemy': 3.75,              # Enemy's Sign (Shatru Rashi) = 3.75 Shashtiamsa
    'Bitter Enemy': 1.875       # Bitter Enemy's sign (Adhi Shatru Rashi) = 1.875 Shashtiamsa
}

# Kala Bala constants and data for classical calculation
WEEKDAY_LORDS = ['Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Sun']  # Monday=0, Sunday=6

HORA_LORDS = ['Saturn', 'Jupiter', 'Mars', 'Sun', 'Venus', 'Mercury', 'Moon']  # Sequence starting from Saturday

TRIBHAGA_RULERS = {
    'day': {1: 'Mercury', 2: 'Sun', 3: 'Saturn'},
    'night': {1: 'Moon', 2: 'Venus', 3: 'Mars'}
}

# Natural benefic/malefic classifications for Paksha Bala
NATURAL_BENEFICS = ['Jupiter', 'Venus', 'Mercury']  # Mercury when well-associated
NATURAL_MALEFICS = ['Sun', 'Mars', 'Saturn']

# Declination table for Ayana Bala (in arc minutes)
DECLINATION_TABLE = [
    (0, 0), (15, 362), (30, 703), (45, 1002), (60, 1238), (75, 1388), (90, 1440)
]

# Planetary disc diameters for Yuddha Bala (in arc seconds)
PLANETARY_DISC_DIAMETERS = {
    'Mars': 9.4, 'Mercury': 6.6, 'Jupiter': 190.4, 'Venus': 16.6, 'Saturn': 158.0
}


def _julday(dt_utc: datetime) -> float:
    ut = dt_utc.hour + dt_utc.minute/60.0 + dt_utc.second/3600.0 + dt_utc.microsecond/3_600_000_000
    return swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, ut)


def _calculate_sunrise_sunset(birth_dt_local: datetime, lat: float, lon: float) -> tuple:
    """Calculate sunrise and sunset times for the birth location and date."""
    try:
        # Convert to UTC for calculations
        birth_date = birth_dt_local.date()
        jd = swe.julday(birth_date.year, birth_date.month, birth_date.day, 0)
        
        # Calculate sunrise and sunset
        sunrise_info = swe.rise_trans(jd, swe.SUN, lon, lat, 0, 0, 0)
        sunset_info = swe.rise_trans(jd, swe.SUN, lon, lat, 0, 0, 1)
        
        if sunrise_info[0] and sunset_info[0]:
            # Convert Julian day back to hours
            sunrise_jd = sunrise_info[1]
            sunset_jd = sunset_info[1]
            
            # Extract time portions (fractional part of JD represents time)
            sunrise_frac = (sunrise_jd - int(sunrise_jd) + 0.5) % 1.0
            sunset_frac = (sunset_jd - int(sunset_jd) + 0.5) % 1.0
            
            sunrise_hours = sunrise_frac * 24
            sunset_hours = sunset_frac * 24
            
            return sunrise_hours, sunset_hours
        else:
            # Fallback to approximate values
            return 6.0, 18.0
    except:
        # Fallback to standard sunrise/sunset
        return 6.0, 18.0


def _get_ahargana(birth_dt: datetime) -> int:
    """Calculate Ahargana (days since epoch) for Abda and Masa Bala calculations."""
    # Using corrected epoch that matches classical calculations: January 31, 1951
    epoch = datetime(1951, 1, 31)
    delta = birth_dt.date() - epoch.date()
    return delta.days


def _interpolate_declination(bhuja_degrees: float) -> float:
    """Interpolate declination from Bhuja using classical table."""
    bhuja = abs(bhuja_degrees)
    
    # Find the appropriate range in the declination table
    for i in range(len(DECLINATION_TABLE) - 1):
        deg1, dec1 = DECLINATION_TABLE[i]
        deg2, dec2 = DECLINATION_TABLE[i + 1]
        
        if deg1 <= bhuja <= deg2:
            # Linear interpolation
            if deg2 == deg1:
                return dec1 / 60.0  # Convert arc minutes to degrees
            
            ratio = (bhuja - deg1) / (deg2 - deg1)
            interpolated_minutes = dec1 + ratio * (dec2 - dec1)
            return interpolated_minutes / 60.0  # Convert to degrees
    
    # If beyond 90 degrees, use maximum
    return DECLINATION_TABLE[-1][1] / 60.0


def _calculate_declination(sayana_longitude: float) -> float:
    """Calculate declination from sayana longitude using classical method."""
    
    # Ensure longitude is in 0-360 range
    sayana_lon = sayana_longitude % 360
    
    # Find Bhuja (distance from nearest equinoctical point)
    if 0 <= sayana_lon <= 90:
        bhuja = sayana_lon
    elif 90 < sayana_lon <= 180:
        bhuja = 180 - sayana_lon
    elif 180 < sayana_lon <= 270:
        bhuja = sayana_lon - 180
    else:  # 270 < sayana_lon < 360
        bhuja = 360 - sayana_lon
    
    # Declination calculation using classical table (interpolated)
    # Reference points: 0°=0', 15°=362', 30°=703', 45°=1002', 60°=1238', 75°=1388', 90°=1440'
    if bhuja <= 15:
        declin_minutes = 362 * bhuja / 15
    elif bhuja <= 30:
        declin_minutes = 362 + 341 * (bhuja - 15) / 15
    elif bhuja <= 45:
        declin_minutes = 703 + 299 * (bhuja - 30) / 15
    elif bhuja <= 60:
        declin_minutes = 1002 + 236 * (bhuja - 45) / 15
    elif bhuja <= 75:
        declin_minutes = 1238 + 150 * (bhuja - 60) / 15
    else:  # bhuja <= 90
        declin_minutes = 1388 + 52 * (bhuja - 75) / 15
    
    # Convert to degrees
    declination = declin_minutes / 60
    
    # Determine North/South
    if 0 <= sayana_lon <= 180:
        return declination  # North
    else:
        return -declination  # South


def _calculate_ayana_bala(planet_name: str, nirayana_longitude: float, ayanamsa: float = 24.0) -> float:
    """Calculate Ayana Bala using classical method."""
    
    # Convert to Sayana longitude
    sayana_longitude = (nirayana_longitude + ayanamsa) % 360
    
    # Get declination
    declination = _calculate_declination(sayana_longitude)
    abs_declination = abs(declination)
    is_north = declination >= 0
    
    # Apply planet-specific rules
    if planet_name in ['Sun', 'Venus', 'Mars', 'Jupiter']:
        # North declination is added to 24, South is subtracted from 24
        if is_north:
            ayana_strength = 24 + abs_declination
        else:
            ayana_strength = 24 - abs_declination
    elif planet_name in ['Saturn', 'Moon']:
        # South declination is added to 24, North is subtracted from 24
        if is_north:
            ayana_strength = 24 - abs_declination
        else:
            ayana_strength = 24 + abs_declination
    else:  # Mercury
        # Declination (whether N or S) is always additive to 24
        ayana_strength = 24 + abs_declination
    
    # Convert to Shashtiamsa: multiply by 60/48 = 5/4
    ayana_bala = ayana_strength * 5 / 4
    
    # Sun's Ayana Bala is always doubled
    if planet_name == 'Sun':
        ayana_bala *= 2
    
    return max(0, ayana_bala)


def _ayanamsa_mode(name: str) -> int:
    n = (name or '').lower()
    if n in ('lahiri','kp','krishnamurti'):
        return swe.SIDM_LAHIRI
    # default to Lahiri
    return swe.SIDM_LAHIRI


def _house_system_code(name: str) -> bytes:
    n = (name or '').lower()
    if n in ('equal','e'):
        return b'E'
    if n in ('placidus','p'):
        return b'P'
    if n in ('koch','k'):
        return b'K'
    if n in ('porphyry','o'):
        return b'O'
    if n in ('regiomontanus','r'):
        return b'R'
    if n in ('campanus','c'):
        return b'C'
    if n in ('whole','w','whole_sign','whole-sign','whole sign'):
        # we will simulate whole sign houses separately using equal cusps
        return b'E'
    return b'E'


def _degnorm(d: float) -> float:
    return d % 360.0


def _sign_index(lon: float) -> int:
    return int(math.floor(_degnorm(lon) / 30.0))


def _deg_in_sign(lon: float) -> float:
    return _degnorm(lon) % 30.0


def _choose_iflag(ephe_dir: Optional[str]) -> int:
    """Choose Swiss Ephemeris flags based on availability of ephemeris files."""
    # Prefer SWIEPH if ephemeris files exist in ephe_dir; otherwise use MOSEPH
    if ephe_dir and os.path.isdir(ephe_dir):
        try:
            swe.set_ephe_path(ephe_dir)
            return swe.FLG_SIDEREAL | swe.FLG_SWIEPH
        except Exception:
            pass
    return swe.FLG_SIDEREAL | swe.FLG_MOSEPH


class DivisionalChartCalculator:
    """Calculate Divisional Charts (Vargas) using traditional BPHS rules."""
    
    def __init__(self):
        self.divisional_names = {
            2: "Hora (D2)",
            3: "Drekkana (D3)", 
            7: "Saptamsa (D7)",
            9: "Navamsa (D9)",
            12: "Dwadasamsa (D12)",
            30: "Trimsamsa (D30)"
        }
    
    def division_index(self, degree: float, n: int) -> int:
        """Calculate division index for given degree and division number."""
        return int(math.ceil(degree * n / 30.0))
    
    def get_sign_name_and_ruler(self, sign_index: int) -> tuple:
        """Get sign name and ruling planet for given sign index (0-11)."""
        sign_name = ZODIAC_SIGNS[sign_index % 12]
        ruler = SIGN_RULERS[sign_index % 12]
        return sign_name, ruler
    
    def calculate_hora_d2(self, sign_index: int, degree: float) -> tuple:
        """Calculate Hora (D2) position."""
        division_num = self.division_index(degree, 2)
        
        if (sign_index + 1) % 2 == 1:  # Odd signs (1,3,5,7,9,11)
            if division_num == 1:
                result_sign = 4  # Leo (Sun)
            else:
                result_sign = 3  # Cancer (Moon)
        else:  # Even signs (2,4,6,8,10,12)
            if division_num == 1:
                result_sign = 3  # Cancer (Moon)
            else:
                result_sign = 4  # Leo (Sun)
        
        # Return (sign_index, degree_in_sign) format
        result_degree = 15.0  # Default middle degree for divisional charts
        return result_sign, result_degree
    
    def calculate_drekkana_d3(self, sign_index: int, degree: float) -> tuple:
        """Calculate Drekkana (D3) position."""
        division_num = self.division_index(degree, 3)
        
        # First drekkana: same sign
        # Second drekkana: 5th sign from current
        # Third drekkana: 9th sign from current
        if division_num == 1:
            result_sign = sign_index
        elif division_num == 2:
            result_sign = (sign_index + 4) % 12  # 5th sign (0-indexed)
        else:  # division_num == 3
            result_sign = (sign_index + 8) % 12  # 9th sign (0-indexed)
        
        # Return (sign_index, degree_in_sign) format
        result_degree = 15.0  # Default middle degree for divisional charts
        return result_sign, result_degree
    
    def calculate_saptamsa_d7(self, sign_index: int, degree: float) -> tuple:
        """Calculate Saptamsa (D7) position."""
        division_num = self.division_index(degree, 7)
        
        if (sign_index + 1) % 2 == 1:  # Odd signs
            # Start from same sign
            result_sign = (sign_index + division_num - 1) % 12
        else:  # Even signs  
            # Start from 7th sign
            result_sign = (sign_index + 6 + division_num - 1) % 12
        
        return result_sign, 15.0  # Return (sign_index, degree_in_sign) format
    
    def calculate_navamsa_d9(self, sign_index: int, degree: float) -> tuple:
        """Calculate Navamsa (D9) position using traditional BPHS method."""
        
        # Each navamsa is 3° 20' (3.333... degrees)
        navamsa_in_sign = int(degree / (30.0 / 9))  # 0-8
        
        # Fire signs (Aries, Leo, Sagittarius): start from Aries (0)
        # Earth signs (Taurus, Virgo, Capricorn): start from Capricorn (9)
        # Air signs (Gemini, Libra, Aquarius): start from Libra (6)  
        # Water signs (Cancer, Scorpio, Pisces): start from Cancer (3)
        
        element = sign_index % 4
        
        if element == 0:  # Fire signs (0, 4, 8) - Aries, Leo, Sagittarius
            start_sign = 0  # Start from Aries
        elif element == 1:  # Earth signs (1, 5, 9) - Taurus, Virgo, Capricorn
            start_sign = 9  # Start from Capricorn
        elif element == 2:  # Air signs (2, 6, 10) - Gemini, Libra, Aquarius
            start_sign = 6  # Start from Libra
        else:  # Water signs (3, 7, 11) - Cancer, Scorpio, Pisces
            start_sign = 3  # Start from Cancer
        
        result_sign = (start_sign + navamsa_in_sign) % 12
        return result_sign, 15.0  # Return (sign_index, degree_in_sign) format
    
    def calculate_dwadasamsa_d12(self, sign_index: int, degree: float) -> tuple:
        """Calculate Dwadasamsa (D12) position."""
        division_num = self.division_index(degree, 12)
        
        # Count signs forward from same sign
        result_sign = (sign_index + division_num - 1) % 12
        
        return result_sign, 15.0  # Return (sign_index, degree_in_sign) format
    
    def calculate_trimsamsa_d30(self, sign_index: int, degree: float) -> tuple:
        """Calculate Trimsamsa (D30) position using traditional BPHS method."""
        
        # Each trimsamsa is 1 degree (30 divisions per sign)
        trimsamsa_in_sign = int(degree)  # 0-29
        
        # Traditional D30 rulership pattern within each sign
        if (sign_index + 1) % 2 == 1:  # Odd signs (1,3,5,7,9,11)
            # Pattern: Mars(0-4°), Saturn(5-9°), Jupiter(10-17°), Mercury(18-24°), Venus(25-29°)
            if 0 <= trimsamsa_in_sign <= 4:
                ruler = 'Mars'
                start_sign = 0  # Aries
            elif 5 <= trimsamsa_in_sign <= 9:
                ruler = 'Saturn'  
                start_sign = 10  # Aquarius
            elif 10 <= trimsamsa_in_sign <= 17:
                ruler = 'Jupiter'
                start_sign = 8  # Sagittarius
            elif 18 <= trimsamsa_in_sign <= 24:
                ruler = 'Mercury'
                start_sign = 2  # Gemini
            else:  # 25-29
                ruler = 'Venus'
                start_sign = 1  # Taurus
        else:  # Even signs (2,4,6,8,10,12)
            # Reverse pattern: Venus(0-4°), Mercury(5-11°), Jupiter(12-19°), Saturn(20-24°), Mars(25-29°)
            if 0 <= trimsamsa_in_sign <= 4:
                ruler = 'Venus'
                start_sign = 6  # Libra
            elif 5 <= trimsamsa_in_sign <= 11:
                ruler = 'Mercury'
                start_sign = 5  # Virgo
            elif 12 <= trimsamsa_in_sign <= 19:
                ruler = 'Jupiter'
                start_sign = 11  # Pisces
            elif 20 <= trimsamsa_in_sign <= 24:
                ruler = 'Saturn'
                start_sign = 9  # Capricorn
            else:  # 25-29
                ruler = 'Mars'
                start_sign = 7  # Scorpio
        
        # Calculate the exact longitude within the D30 chart
        # The position depends on the trimsamsa within its rulership range
        if (sign_index + 1) % 2 == 1:  # Odd signs
            if 0 <= trimsamsa_in_sign <= 4:
                pos_in_range = trimsamsa_in_sign  # 0-4
                total_range = 5
            elif 5 <= trimsamsa_in_sign <= 9:
                pos_in_range = trimsamsa_in_sign - 5  # 0-4
                total_range = 5
            elif 10 <= trimsamsa_in_sign <= 17:
                pos_in_range = trimsamsa_in_sign - 10  # 0-7
                total_range = 8
            elif 18 <= trimsamsa_in_sign <= 24:
                pos_in_range = trimsamsa_in_sign - 18  # 0-6
                total_range = 7
            else:  # 25-29
                pos_in_range = trimsamsa_in_sign - 25  # 0-4
                total_range = 5
        else:  # Even signs
            if 0 <= trimsamsa_in_sign <= 4:
                pos_in_range = trimsamsa_in_sign  # 0-4
                total_range = 5
            elif 5 <= trimsamsa_in_sign <= 11:
                pos_in_range = trimsamsa_in_sign - 5  # 0-6
                total_range = 7
            elif 12 <= trimsamsa_in_sign <= 19:
                pos_in_range = trimsamsa_in_sign - 12  # 0-7
                total_range = 8
            elif 20 <= trimsamsa_in_sign <= 24:
                pos_in_range = trimsamsa_in_sign - 20  # 0-4
                total_range = 5
            else:  # 25-29
                pos_in_range = trimsamsa_in_sign - 25  # 0-4
                total_range = 5
        
        # Map to the appropriate sign based on ruler and calculate final position
        result_sign = start_sign
        return result_sign, 15.0  # Return (sign_index, degree_in_sign) format
    
    def get_divisional_chart(self, base_positions: Dict[str, tuple], division_type: int) -> Dict[str, Dict]:
        """
        Calculate single divisional chart.
        
        Args:
            base_positions: Dict of body -> (sign_index [0-11], degree_in_sign [0-30])
            division_type: 2, 3, 7, 9, 12, or 30
        
        Returns:
            Dict of body -> {'sign': str, 'ruler': str}
        """
        chart_data = {}
        
        for body, (sign_index, degree) in base_positions.items():
            if division_type == 2:
                sign_name, ruler = self.calculate_hora_d2(sign_index, degree)
            elif division_type == 3:
                sign_name, ruler = self.calculate_drekkana_d3(sign_index, degree)
            elif division_type == 7:
                sign_name, ruler = self.calculate_saptamsa_d7(sign_index, degree)
            elif division_type == 9:
                sign_name, ruler = self.calculate_navamsa_d9(sign_index, degree)
            elif division_type == 12:
                sign_name, ruler = self.calculate_dwadasamsa_d12(sign_index, degree)
            elif division_type == 30:
                sign_name, ruler = self.calculate_trimsamsa_d30(sign_index, degree)
            else:
                raise ValueError(f"Unsupported division type: {division_type}")
            
            chart_data[body] = {
                'sign': sign_name,
                'ruler': ruler,
                'division_index': self.division_index(degree, division_type)
            }
        
        return chart_data
    
    def get_all_charts(self, base_positions: Dict[str, tuple]) -> Dict[str, Dict]:
        """
        Calculate all divisional charts.
        
        Args:
            base_positions: Dict of body -> (sign_index [0-11], degree_in_sign [0-30])
        
        Returns:
            Dict mapping chart name -> chart data
        """
        all_charts = {}
        
        for div_type in [2, 3, 7, 9, 12, 30]:
            chart_name = f"D{div_type}"
            chart_full_name = self.divisional_names[div_type]
            
            try:
                chart_data = self.get_divisional_chart(base_positions, div_type)
                all_charts[chart_name] = {
                    'name': chart_full_name,
                    'division': div_type,
                    'positions': chart_data
                }
            except Exception as e:
                all_charts[chart_name] = {
                    'name': chart_full_name,
                    'division': div_type,
                    'error': f"Calculation failed: {str(e)}",
                    'positions': {}
                }
        
        return all_charts


class PanchadhaMaitriCalculator:
    """Calculate Panchadha Maitri (Five-fold Friendship) tables."""
    
    def __init__(self):
        self.planets = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']
        self.friend_houses = [2, 3, 4, 10, 11, 12]  # II, III, IV, X, XI, XII
        self.enemy_houses = [1, 5, 6, 7, 8, 9]      # I, V, VI, VII, VIII, IX
    
    def build_naisargika_maitri_table(self) -> Dict[str, Dict[str, str]]:
        """Module 1: Build Naisargika (Natural/Permanent) Friendship table."""
        
        naisargika_table = {}
        
        for planet_data in PERMANENT_FRIENDSHIP:
            planet = planet_data["planet"]
            naisargika_table[planet] = {}
            
            for other_planet in self.planets:
                if planet == other_planet:
                    naisargika_table[planet][other_planet] = "Self"
                elif other_planet in planet_data["friend"]:
                    naisargika_table[planet][other_planet] = "Friend"
                elif other_planet in planet_data["neutral"]:
                    naisargika_table[planet][other_planet] = "Neutral"
                elif other_planet in planet_data["enemy"]:
                    naisargika_table[planet][other_planet] = "Enemy"
                else:
                    # Default to neutral if not explicitly listed
                    naisargika_table[planet][other_planet] = "Neutral"
        
        return naisargika_table
    
    def build_tatkaala_maitri_table(self, planets_sidereal: Dict[str, float]) -> Dict[str, Dict[str, str]]:
        """Module 2: Build Tatkaala (Temporary) Friendship table based on house positions."""
        
        tatkaala_table = {}
        
        # Convert longitudes to sign numbers (1-12)
        planet_signs = {}
        for planet, longitude in planets_sidereal.items():
            if planet in self.planets:
                planet_signs[planet] = int(longitude // 30) + 1
        
        for planet_a in self.planets:
            if planet_a not in planet_signs:
                continue
                
            tatkaala_table[planet_a] = {}
            sign_a = planet_signs[planet_a]
            
            for planet_b in self.planets:
                if planet_b not in planet_signs:
                    continue
                    
                if planet_a == planet_b:
                    tatkaala_table[planet_a][planet_b] = "Self"
                    continue
                
                sign_b = planet_signs[planet_b]
                
                # Calculate house position from planet_a's perspective
                # Planet_A is always in house 1 from its own perspective
                # Other planets are in houses based on sign difference
                house_position = (sign_b - sign_a) % 12
                if house_position <= 0:
                    house_position += 12
                # Convert to 1-indexed (planet_a itself would be house 1, next sign is house 2, etc.)
                house_position += 1
                if house_position > 12:
                    house_position -= 12
                
                # Determine temporary relationship based on house position
                # Friend Houses: 2, 3, 4, 10, 11, 12
                # Enemy Houses: 1, 5, 6, 7, 8, 9
                if house_position in self.friend_houses:
                    tatkaala_table[planet_a][planet_b] = "Friend"
                elif house_position in self.enemy_houses:
                    tatkaala_table[planet_a][planet_b] = "Enemy"
                else:
                    tatkaala_table[planet_a][planet_b] = "Neutral"
        
        return tatkaala_table
    
    def build_panchadha_maitri_table(self, naisargika_table: Dict[str, Dict[str, str]], 
                                   tatkaala_table: Dict[str, Dict[str, str]]) -> Dict[str, Dict[str, Dict[str, str]]]:
        """Module 3: Build Panchadha (Integrated) Maitri table."""
        
        panchadha_table = {}
        
        for planet_a in self.planets:
            if planet_a not in naisargika_table or planet_a not in tatkaala_table:
                continue
                
            panchadha_table[planet_a] = {}
            
            for planet_b in self.planets:
                if planet_b not in naisargika_table[planet_a] or planet_b not in tatkaala_table[planet_a]:
                    continue
                
                if planet_a == planet_b:
                    panchadha_table[planet_a][planet_b] = {
                        "resultant": "Self",
                        "code": "S",
                        "naisargik": "Self",
                        "temporary": "Self"
                    }
                    continue
                
                naisargik = naisargika_table[planet_a][planet_b]
                temporary = tatkaala_table[planet_a][planet_b]
                
                # Find matching rule in PANCHADHA_MAITRI_RULES
                resultant = "Neutral"  # Default
                code = "N"
                
                for rule in PANCHADHA_MAITRI_RULES:
                    if rule["naisargik"] == naisargik and rule["temporary"] == temporary:
                        resultant = rule["resultant"]
                        code = rule["code"]
                        break
                
                panchadha_table[planet_a][planet_b] = {
                    "resultant": resultant,
                    "code": code,
                    "naisargik": naisargik,
                    "temporary": temporary
                }
        
        return panchadha_table
    
    def calculate_all_maitri_tables(self, planets_sidereal: Dict[str, float]) -> Dict[str, Any]:
        """Calculate all three Maitri tables and return comprehensive data."""
        
        # Module 1: Naisargika Maitri
        naisargika_table = self.build_naisargika_maitri_table()
        
        # Module 2: Tatkaala Maitri  
        tatkaala_table = self.build_tatkaala_maitri_table(planets_sidereal)
        
        # Module 3: Panchadha Maitri
        panchadha_table = self.build_panchadha_maitri_table(naisargika_table, tatkaala_table)
        
        return {
            "naisargika_maitri": naisargika_table,
            "tatkaala_maitri": tatkaala_table,
            "panchadha_maitri": panchadha_table,
            "planet_signs": {planet: int(longitude // 30) + 1 
                           for planet, longitude in planets_sidereal.items() 
                           if planet in self.planets},
            "rules_applied": PANCHADHA_MAITRI_RULES
        }


class SaptavarigiyaBalaCalculator:
    """Calculate Saptavargiya Bala exactly as per reference document with lookup table methodology."""
    
    def __init__(self):
        self.divisional_calculator = DivisionalChartCalculator()
        self.maitri_calculator = PanchadhaMaitriCalculator()
        self.planets = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']
        
        # Seven divisional charts for Saptavargiya Bala
        self.seven_charts = [1, 2, 3, 7, 9, 12, 30]  # Rashi, Hora, Drekkana, Saptamsa, Navamsa, Dwadasamsa, Trimsamsa
        
        self.chart_names = {
            1: "Rashi Chart",
            2: "Hora", 
            3: "Dreshkon",
            7: "Saptamsa",
            9: "Navamsa",
            12: "Dwadasamsa", 
            30: "Treisamsa"
        }
        

    
    def is_in_mooltrikona(self, planet: str, sign_index: int, degree_in_sign: float) -> bool:
        """Check if planet is in its Mooltrikona range."""
        if planet not in MOOLTRIKONA_RANGES:
            return False
        
        mooltrikona = MOOLTRIKONA_RANGES[planet]
        return (sign_index == mooltrikona['sign'] and 
                mooltrikona['start'] <= degree_in_sign <= mooltrikona['end'])
    
    def is_own_sign(self, planet: str, sign_index: int) -> bool:
        """Check if planet is in its own sign."""
        own_signs = SHADBALA_CONSTANTS['own_signs'].get(planet, [])
        return sign_index in own_signs
    
    def is_exalted(self, planet: str, sign_index: int) -> bool:
        """Check if planet is in its exaltation sign."""
        if planet in SHADBALA_CONSTANTS['uchcha_bala_data']:
            exalt_degree = SHADBALA_CONSTANTS['uchcha_bala_data'][planet]['exaltation_degree']
            exalt_sign = int(exalt_degree // 30)
            return sign_index == exalt_sign
        return False
    
    def get_panchadha_relationship(self, planet: str, other_planet: str, panchadha_maitri: Dict) -> str:
        """Get relationship using dynamic Panchadha Maitri calculation."""
        if planet in panchadha_maitri and other_planet in panchadha_maitri[planet]:
            relationship_data = panchadha_maitri[planet][other_planet]
            resultant = relationship_data.get('resultant', 'Neutral')
            
            # Map Panchadha Maitri results to SaptavarigiyaBala categories
            if resultant == 'Extreme Friend':
                return "Fast Friend"
            elif resultant == 'Friend':
                return "Friend"
            elif resultant == 'Neutral':
                return "Neutral"
            elif resultant == 'Enemy':
                return "Enemy"
            elif resultant == 'Extreme Enemy':
                return "Bitter Enemy"
        
        return "Neutral"  # Default
    
    def get_sign_relationship(self, planet: str, sign_index: int, degree_in_sign: float, panchadha_maitri: Dict, division: int = 1) -> str:
        """Determine relationship between planet and sign ruler using dynamic calculation."""
        
        # First priority: Check for Mooltrikona (ONLY in Rashi chart - division 1)
        if division == 1 and self.is_in_mooltrikona(planet, sign_index, degree_in_sign):
            return "Mooltrikona"
        
        # Second priority: Check for own sign
        if self.is_own_sign(planet, sign_index):
            return "Own"
        
        # Third priority: Use dynamic Panchadha Maitri relationship
        sign_ruler = SIGN_RULERS[sign_index]
        return self.get_panchadha_relationship(planet, sign_ruler, panchadha_maitri)
    
    def get_relationship_from_points(self, points: float) -> str:
        """Reverse lookup to determine relationship type from points value."""
        point_to_relationship = {
            45.0: "Mooltrikona",
            30.0: "Own", 
            22.5: "Fast Friend",
            15.0: "Friend",
            7.5: "Neutral", 
            3.75: "Enemy",
            1.875: "Bitter Enemy"
        }
        return point_to_relationship.get(points, "Unknown")
    
    def calculate_saptavargiya_bala(self, planets_sidereal: Dict[str, float]) -> Dict[str, Any]:
        """Calculate SaptavarigiyaBala by determining actual relationships in each divisional chart."""
        
        # Get Panchadha Maitri relationships from Rashi chart (D1)
        maitri_data = self.maitri_calculator.calculate_all_maitri_tables(planets_sidereal)
        panchadha_maitri = maitri_data["panchadha_maitri"]
        
        # Calculate all divisional charts
        divisional_charts = {}
        for division in self.seven_charts:
            if division == 1:
                # Rashi chart - use original positions
                chart_data = {}
                for planet, longitude in planets_sidereal.items():
                    if planet in self.planets:
                        sign_index = _sign_index(longitude)
                        degree_in_sign = _deg_in_sign(longitude)
                        sign_name, ruler = self.divisional_calculator.get_sign_name_and_ruler(sign_index)
                        chart_data[planet] = {
                            'sign_index': sign_index,
                            'sign_name': sign_name,
                            'degree_in_sign': degree_in_sign,
                            'ruler': ruler
                        }
                divisional_charts[division] = chart_data
            else:
                # Calculate divisional chart positions
                chart_data = {}
                for planet, longitude in planets_sidereal.items():
                    if planet in self.planets:
                        sign_index = _sign_index(longitude)
                        degree_in_sign = _deg_in_sign(longitude)
                        
                        try:
                            if division == 2:
                                div_sign_index, div_degree = self.divisional_calculator.calculate_hora_d2(sign_index, degree_in_sign)
                            elif division == 3:
                                div_sign_index, div_degree = self.divisional_calculator.calculate_drekkana_d3(sign_index, degree_in_sign)
                            elif division == 7:
                                div_sign_index, div_degree = self.divisional_calculator.calculate_saptamsa_d7(sign_index, degree_in_sign)
                            elif division == 9:
                                div_sign_index, div_degree = self.divisional_calculator.calculate_navamsa_d9(sign_index, degree_in_sign)
                            elif division == 12:
                                div_sign_index, div_degree = self.divisional_calculator.calculate_dwadasamsa_d12(sign_index, degree_in_sign)
                            elif division == 30:
                                div_sign_index, div_degree = self.divisional_calculator.calculate_trimsamsa_d30(sign_index, degree_in_sign)
                            
                            sign_name, ruler = self.divisional_calculator.get_sign_name_and_ruler(div_sign_index)
                            chart_data[planet] = {
                                'sign_index': div_sign_index,
                                'sign_name': sign_name,
                                'degree_in_sign': div_degree,
                                'ruler': ruler
                            }
                        except Exception as e:
                            chart_data[planet] = {
                                'error': f"Calculation failed: {str(e)}",
                                'sign_index': None,
                                'sign_name': None,
                                'degree_in_sign': None,
                                'ruler': None
                            }
                
                divisional_charts[division] = chart_data
        
        # Calculate actual relationships and assign points for each planet in each chart
        planet_chart_scores = {}
        for planet in self.planets:
            if planet not in planets_sidereal:
                continue
                
            planet_chart_scores[planet] = {}
            
            for division in self.seven_charts:
                chart_data = divisional_charts[division]
                if planet in chart_data and chart_data[planet].get('sign_index') is not None:
                    planet_data = chart_data[planet]
                    sign_index = planet_data['sign_index']
                    degree_in_sign = planet_data.get('degree_in_sign', 0)
                    
                    # Determine relationship type based on actual chart position
                    relationship = self.get_sign_relationship(planet, sign_index, degree_in_sign, panchadha_maitri, division)
                    
                    # Get points based on relationship
                    points = SAPTAVARGIYA_POINTS.get(relationship, 0)
                    
                    planet_chart_scores[planet][division] = {
                        'chart_name': self.chart_names[division],
                        'sign_name': planet_data['sign_name'],
                        'ruler': planet_data['ruler'],
                        'relationship': relationship,
                        'points': points
                    }
                else:
                    planet_chart_scores[planet][division] = {
                        'chart_name': self.chart_names[division],
                        'sign_name': 'Error',
                        'ruler': 'Unknown',
                        'relationship': 'Error',
                        'points': 0
                    }
        
        # Calculate total scores by summing actual calculated points
        planet_totals = {}
        for planet in self.planets:
            if planet in planet_chart_scores:
                total_points = sum(score_data['points'] for score_data in planet_chart_scores[planet].values())
                planet_totals[planet] = round(total_points, 3)
        
        return {
            'planet_chart_scores': planet_chart_scores,
            'planet_totals': planet_totals,
            'chart_names': self.chart_names,
            'panchadha_maitri_used': panchadha_maitri,
            'point_system': SAPTAVARGIYA_POINTS,
            'mooltrikona_ranges': MOOLTRIKONA_RANGES
        }


class YugmayugmaBalaCalculator:
    """Calculator for YugmayugmaBala (Odd/Even Sign Strength)."""
    
    def __init__(self):
        self.planets = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']
        # Planets that get strength in even signs
        self.even_sign_planets = ['Moon', 'Venus']
        # Planets that get strength in odd signs  
        self.odd_sign_planets = ['Sun', 'Mars', 'Mercury', 'Jupiter', 'Saturn']
        self.max_points_per_chart = 15  # Maximum 15 Shashtiamsa per chart
        
    def is_odd_sign(self, sign_index: int) -> bool:
        """Check if a sign is odd. Aries(0), Gemini(2), Leo(4), etc. are odd signs."""
        # Note: In traditional Vedic astrology, Aries is 1st sign (odd)
        # But in our 0-indexed system: Aries=0, Taurus=1, Gemini=2, etc.
        # So odd signs are at even indices: 0, 2, 4, 6, 8, 10
        return (sign_index % 2) == 0
        
    def is_even_sign(self, sign_index: int) -> bool:
        """Check if a sign is even. Taurus(1), Cancer(3), Virgo(5), etc. are even signs."""
        # Even signs are at odd indices: 1, 3, 5, 7, 9, 11
        return (sign_index % 2) == 1
    
    def calculate_yugmayugma_bala(self, planets_sidereal: Dict[str, float]) -> Dict[str, Any]:
        """Calculate YugmayugmaBala for all planets in Rashi and Navamsha charts."""
        
        # Initialize divisional calculator for Navamsha positions
        divisional_calculator = DivisionalChartCalculator()
        
        # Calculate results for each planet
        planet_scores = {}
        planet_details = {}
        
        for planet in self.planets:
            if planet not in planets_sidereal:
                continue
                
            planet_lon = planets_sidereal[planet]
            
            # Get Rashi chart position
            rashi_sign_index = _sign_index(planet_lon)
            rashi_degree = _deg_in_sign(planet_lon)
            
            # Get Navamsha chart position (D9)
            navamsha_sign_index, navamsha_degree = divisional_calculator.calculate_navamsa_d9(rashi_sign_index, rashi_degree)
            
            # Determine if planet gets strength in odd or even signs
            prefers_odd = planet in self.odd_sign_planets
            prefers_even = planet in self.even_sign_planets
            
            # Calculate points for Rashi chart
            rashi_is_odd = self.is_odd_sign(rashi_sign_index)
            rashi_points = 0
            if prefers_odd and rashi_is_odd:
                rashi_points = self.max_points_per_chart
            elif prefers_even and not rashi_is_odd:  # Even sign
                rashi_points = self.max_points_per_chart
            
            # Calculate points for Navamsha chart
            navamsha_is_odd = self.is_odd_sign(navamsha_sign_index)
            navamsha_points = 0
            if prefers_odd and navamsha_is_odd:
                navamsha_points = self.max_points_per_chart
            elif prefers_even and not navamsha_is_odd:  # Even sign
                navamsha_points = self.max_points_per_chart
            
            # Total YugmayugmaBala
            total_points = rashi_points + navamsha_points
            
            # Store detailed breakdown
            planet_details[planet] = {
                'rashi_chart': {
                    'sign_index': rashi_sign_index,
                    'sign_name': ZODIAC_SIGNS[rashi_sign_index],
                    'sign_type': 'Odd' if rashi_is_odd else 'Even',
                    'points': rashi_points,
                    'gets_strength': (prefers_odd and rashi_is_odd) or (prefers_even and not rashi_is_odd)
                },
                'navamsha_chart': {
                    'sign_index': navamsha_sign_index, 
                    'sign_name': ZODIAC_SIGNS[navamsha_sign_index],
                    'sign_type': 'Odd' if navamsha_is_odd else 'Even',
                    'points': navamsha_points,
                    'gets_strength': (prefers_odd and navamsha_is_odd) or (prefers_even and not navamsha_is_odd)
                },
                'planet_preference': 'Odd Signs' if prefers_odd else 'Even Signs',
                'total_points': total_points
            }
            
            planet_scores[planet] = total_points
        
        return {
            'planet_scores': planet_scores,
            'planet_details': planet_details,
            'calculation_rules': {
                'odd_sign_planets': self.odd_sign_planets,
                'even_sign_planets': self.even_sign_planets,
                'max_points_per_chart': self.max_points_per_chart,
                'total_max_points': self.max_points_per_chart * 2
            }
        }


class KendraBalaCalculator:
    """Calculator for KendraBala (Angular House Strength)."""
    
    def __init__(self):
        self.planets = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']
        # KendraBala point system according to reference document
        self.kendra_points = 60      # Houses 1, 4, 7, 10 (Angular)
        self.panapara_points = 30    # Houses 2, 5, 8, 11 (Succedent)
        self.apoklima_points = 15    # Houses 3, 6, 9, 12 (Cadent)
        
        # House classifications
        self.kendra_houses = [1, 4, 7, 10]      # Angular
        self.panapara_houses = [2, 5, 8, 11]    # Succedent (next to Kendras)
        self.apoklima_houses = [3, 6, 9, 12]    # Cadent (behind Kendras)
    
    def get_house_for_longitude(self, planet_lon: float, cusps_map: Dict[int, float]) -> int:
        """Determine which house a planet occupies based on its longitude."""
        
        def in_arc(longitude, start_cusp, end_cusp):
            """Check if longitude is within the arc from start_cusp to end_cusp."""
            start = _degnorm(start_cusp)
            end = _degnorm(end_cusp)
            lon = _degnorm(longitude)
            
            if start <= end:
                return start <= lon < end
            else:  # Arc crosses 0 degrees
                return lon >= start or lon < end
        
        # Check each house
        for house_num in range(1, 13):
            start_cusp = cusps_map[house_num]
            next_house = house_num + 1 if house_num < 12 else 1
            end_cusp = cusps_map[next_house]
            
            if in_arc(planet_lon, start_cusp, end_cusp):
                return house_num
        
        # Fallback - shouldn't happen in normal circumstances
        return 1
    
    def get_house_classification(self, house_number: int) -> tuple[str, int]:
        """Get the classification and points for a house number."""
        if house_number in self.kendra_houses:
            return "Kendra", self.kendra_points
        elif house_number in self.panapara_houses:
            return "Panapara", self.panapara_points
        elif house_number in self.apoklima_houses:
            return "Apoklima", self.apoklima_points
        else:
            # Should not happen for houses 1-12
            return "Unknown", 0
    
    def calculate_kendra_bala(self, planets_sidereal: Dict[str, float], cusps_map: Dict[int, float]) -> Dict[str, Any]:
        """Calculate KendraBala for all planets based on their house positions in Rashi chart."""
        
        planet_scores = {}
        planet_details = {}
        
        for planet in self.planets:
            if planet not in planets_sidereal:
                continue
                
            planet_lon = planets_sidereal[planet]
            
            # Determine house position
            house_number = self.get_house_for_longitude(planet_lon, cusps_map)
            
            # Get house classification and points
            house_type, points = self.get_house_classification(house_number)
            
            # Store detailed information
            planet_details[planet] = {
                'longitude': planet_lon,
                'house_number': house_number,
                'house_type': house_type,
                'points': points,
                'house_classification': {
                    'kendra': house_number in self.kendra_houses,
                    'panapara': house_number in self.panapara_houses,
                    'apoklima': house_number in self.apoklima_houses
                }
            }
            
            planet_scores[planet] = points
        
        return {
            'planet_scores': planet_scores,
            'planet_details': planet_details,
            'house_classifications': {
                'kendra_houses': self.kendra_houses,
                'panapara_houses': self.panapara_houses,
                'apoklima_houses': self.apoklima_houses
            },
            'point_system': {
                'kendra_points': self.kendra_points,
                'panapara_points': self.panapara_points,
                'apoklima_points': self.apoklima_points
            }
        }


class DreshkonBalaCalculator:
    """Calculator for DreshkonBala (Decanate Strength based on planetary gender)."""
    
    def __init__(self):
        self.planets = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']
        self.max_points = 15  # 15 Shashtiamsa for correct Dreshkon
        
        # Planet gender classifications according to reference document
        self.male_planets = ['Sun', 'Mars', 'Jupiter']
        self.hermaphrodite_planets = ['Mercury', 'Saturn']
        self.female_planets = ['Moon', 'Venus']
        
        # Dreshkon ranges (each sign has 3 Dreshkons of 10° each)
        self.dreshkon_ranges = {
            1: (0.0, 10.0),    # First Dreshkon: 0°-10°
            2: (10.0, 20.0),   # Second Dreshkon: 10°-20°
            3: (20.0, 30.0)    # Third Dreshkon: 20°-30°
        }
    
    def get_planet_gender(self, planet: str) -> str:
        """Get the gender classification of a planet."""
        if planet in self.male_planets:
            return "Male"
        elif planet in self.hermaphrodite_planets:
            return "Hermaphrodite"
        elif planet in self.female_planets:
            return "Female"
        else:
            return "Unknown"
    
    def get_dreshkon_number(self, degree_in_sign: float) -> int:
        """Determine which Dreshkon (1, 2, or 3) a planet occupies within its sign."""
        # Normalize degree to 0-30 range
        degree = degree_in_sign % 30.0
        
        if 0.0 <= degree < 10.0:
            return 1  # First Dreshkon
        elif 10.0 <= degree < 20.0:
            return 2  # Second Dreshkon  
        elif 20.0 <= degree < 30.0:
            return 3  # Third Dreshkon
        else:
            # Edge case, default to first
            return 1
    
    def gets_dreshkon_strength(self, planet: str, dreshkon_number: int) -> bool:
        """Check if a planet gets strength in the given Dreshkon based on its gender."""
        gender = self.get_planet_gender(planet)
        
        if gender == "Male" and dreshkon_number == 1:
            return True  # Male planets get strength in 1st Dreshkon
        elif gender == "Hermaphrodite" and dreshkon_number == 2:
            return True  # Hermaphrodite planets get strength in 2nd Dreshkon
        elif gender == "Female" and dreshkon_number == 3:
            return True  # Female planets get strength in 3rd Dreshkon
        else:
            return False
    
    def calculate_dreshkon_bala(self, planets_sidereal: Dict[str, float]) -> Dict[str, Any]:
        """Calculate DreshkonBala for all planets based on their position within their signs."""
        
        planet_scores = {}
        planet_details = {}
        
        for planet in self.planets:
            if planet not in planets_sidereal:
                continue
                
            planet_lon = planets_sidereal[planet]
            
            # Get sign and degree within sign
            sign_index = _sign_index(planet_lon)
            degree_in_sign = _deg_in_sign(planet_lon)
            
            # Determine which Dreshkon the planet is in
            dreshkon_number = self.get_dreshkon_number(degree_in_sign)
            
            # Get planet gender
            gender = self.get_planet_gender(planet)
            
            # Check if planet gets strength in this Dreshkon
            gets_strength = self.gets_dreshkon_strength(planet, dreshkon_number)
            
            # Calculate points
            points = self.max_points if gets_strength else 0
            
            # Get Dreshkon name
            dreshkon_names = {1: "First", 2: "Second", 3: "Third"}
            dreshkon_name = dreshkon_names[dreshkon_number]
            
            # Store detailed information
            planet_details[planet] = {
                'sign_index': sign_index,
                'sign_name': ZODIAC_SIGNS[sign_index],
                'degree_in_sign': round(degree_in_sign, 2),
                'dreshkon_number': dreshkon_number,
                'dreshkon_name': dreshkon_name,
                'dreshkon_range': self.dreshkon_ranges[dreshkon_number],
                'planet_gender': gender,
                'gets_strength': gets_strength,
                'points': points,
                'explanation': f"{gender} planet in {dreshkon_name} Dreshkon ({'✓' if gets_strength else '✗'} gets strength)"
            }
            
            planet_scores[planet] = points
        
        return {
            'planet_scores': planet_scores,
            'planet_details': planet_details,
            'gender_classifications': {
                'male_planets': self.male_planets,
                'hermaphrodite_planets': self.hermaphrodite_planets,  
                'female_planets': self.female_planets
            },
            'strength_rules': {
                'male_planets_get_strength_in': "First Dreshkon (0°-10°)",
                'hermaphrodite_planets_get_strength_in': "Second Dreshkon (10°-20°)",
                'female_planets_get_strength_in': "Third Dreshkon (20°-30°)",
                'max_points': self.max_points
            },
            'dreshkon_ranges': self.dreshkon_ranges
        }


def compute_chart(birth_dt_local: datetime, lat: float, lon: float, tz_offset_hours: float, ayanamsa: str, house_system: str,
                  ephe_dir: Optional[str] = None, node_type: str = 'mean') -> Dict[str, Any]:
    # Convert local time by provided offset to UTC
    birth_dt_utc = birth_dt_local - timedelta(hours=tz_offset_hours)
    birth_dt_utc = birth_dt_utc.replace(tzinfo=timezone.utc)
    jd_ut = _julday(birth_dt_utc)

    # Configure Swiss Ephemeris for sidereal zodiac; choose SWIEPH if ephemeris files are present
    swe.set_sid_mode(_ayanamsa_mode(ayanamsa))
    iflag = _choose_iflag(ephe_dir)

    # Planets
    planets_sidereal: Dict[str, float] = {}
    for name, ipl in PLANET_ORDER:
        xx, ret = swe.calc_ut(jd_ut, ipl, iflag)
        planet_lon = xx[0]  # Fixed: use different variable name to avoid collision
        planets_sidereal[name] = _degnorm(planet_lon)
    # Nodes
    node_code = swe.MEAN_NODE if (node_type.lower() in ('mean','m')) else swe.TRUE_NODE
    xxn, ret = swe.calc_ut(jd_ut, node_code, iflag)
    node_lon = xxn[0]
    planets_sidereal['Rahu'] = _degnorm(node_lon)
    planets_sidereal['Ketu'] = _degnorm(node_lon + 180.0)

    # Houses and Ascendant - calculate correctly using tropical then convert to sidereal
    hsys = _house_system_code(house_system)
    
    # Calculate houses in tropical mode (without sidereal flag)
    tropical_iflag = swe.FLG_SWIEPH if os.path.exists('sedelx18.se1') else swe.FLG_MOSEPH
    houses_res = swe.houses_ex(jd_ut, lat, lon, hsys, tropical_iflag)
    cusps, ascmc = houses_res
    asc_tropical = ascmc[0]  # Ascendant in tropical coordinates
    
    # Get ayanamsa and convert to sidereal
    ayanamsa_value = swe.get_ayanamsa_ut(jd_ut)
    asc_sid = _degnorm(asc_tropical - ayanamsa_value)

    # If user asked for whole-sign, rebuild cusps from asc sidereal at 0 deg of asc sign
    if house_system.lower() in ('whole','w','whole-sign','wholesign','whole sign'):
        asc_sign_start = 30.0 * _sign_index(asc_sid)
        cusps_map = {i: _degnorm(asc_sign_start + (i-1)*30.0) for i in range(1,13)}
    else:
        # cusps tuple is 12 elements, index 0..11 - convert from tropical to sidereal
        cusps_map = {i+1: _degnorm(cusps[i] - ayanamsa_value) for i in range(12)}

    # Transit now (sidereal)
    now_utc = datetime.utcnow().replace(tzinfo=timezone.utc)
    jd_now = _julday(now_utc)
    swe.set_sid_mode(_ayanamsa_mode(ayanamsa))
    trans_sid: Dict[str, float] = {}
    for name, ipl in PLANET_ORDER:
        xx_now, _ = swe.calc_ut(jd_now, ipl, iflag)
        planet_lon = xx_now[0]  # Fixed: use different variable name
        trans_sid[name] = _degnorm(planet_lon)
    xxn_now, _ = swe.calc_ut(jd_now, node_code, iflag)
    node_lon_now = xxn_now[0]
    trans_sid['Rahu'] = _degnorm(node_lon_now)
    trans_sid['Ketu'] = _degnorm(node_lon_now + 180.0)

    # Prepare outputs
    def sign_name(lon):
        return ZODIAC_SIGNS[_sign_index(lon)]

    planets_out = {}
    for name, lonv in planets_sidereal.items():
        planets_out[name] = {
            'longitude': round(lonv, 6),
            'sign': sign_name(lonv),
            'degInSign': round(_deg_in_sign(lonv), 2),
        }

    trans_out = {}
    for name, lonv in trans_sid.items():
        trans_out[name] = {
            'longitude': round(lonv, 6),
            'sign': sign_name(lonv),
            'degInSign': round(_deg_in_sign(lonv), 2),
        }

    # House assignment using cusp boundaries: a planet is in house i if it lies between cusp[i] and cusp[i+1] along zodiac
    cusp_list = [cusps_map[i] for i in range(1,13)]
    def in_arc(a, start, end):
        start = _degnorm(start); end = _degnorm(end); a = _degnorm(a)
        if start <= end:
            return start <= a < end
        else:
            return a >= start or a < end
    def house_index_for(lonv: float) -> int:
        for i in range(12):
            start = cusp_list[i]
            end = cusp_list[(i+1) % 12]
            if in_arc(lonv, start, end):
                return i+1
        return 12

    planets_by_house: Dict[str, List[Dict[str, Any]]] = {str(i): [] for i in range(1,13)}
    for name, lonv in planets_sidereal.items():
        hi = house_index_for(lonv)
        planets_by_house[str(((hi - 1) % 12) + 1)].append({
            'name': name,
            'abbr': ABBR.get(name, name[:2]),
            'sign': sign_name(lonv),
            'degInSign': round(_deg_in_sign(lonv), 2),
        })

    # Vimshottari Mahadasha/Antardasha/Pratyantardasha based on birth Moon nakshatra
    def _vim_mds(birth_local: datetime, moon_lon_sidereal: float):
        # Determine nakshatra and its lord
        nak_index = int(math.floor(_degnorm(moon_lon_sidereal) / NAK_LEN_DEG))  # 0..26
        nak_offset_deg = _degnorm(moon_lon_sidereal) - nak_index * NAK_LEN_DEG
        lord = NAK_LORDS[nak_index]
        total_years = VIM_MD_YEARS[lord]
        # Remaining proportion in current nakshatra
        frac_remaining = 1.0 - (nak_offset_deg / NAK_LEN_DEG)
        remaining_years_current = total_years * frac_remaining

        # Compute the start of current MD by subtracting elapsed from birth
        elapsed_years_current = total_years - remaining_years_current

        def add_years_calendar(dt: datetime, years: int) -> datetime:
            try:
                return dt.replace(year=dt.year + years)
            except ValueError:
                # handle Feb 29 -> Feb 28 fallback
                return dt.replace(month=2, day=28, year=dt.year + years)

        def add_years_fractional(dt: datetime, years_fraction: float, sign: int = +1) -> datetime:
            days = years_fraction * 365.2425
            return dt + timedelta(days=sign * days)

        # Start of current MD
        start_current = birth_local
        # Subtract integer years then fractional portion to get the MD start
        int_elapsed = int(math.floor(elapsed_years_current))
        frac_elapsed = elapsed_years_current - int_elapsed
        if int_elapsed:
            start_current = add_years_calendar(start_current, -int_elapsed)
        if abs(frac_elapsed) > 1e-9:
            start_current = add_years_fractional(start_current, frac_elapsed, sign=-1)

        # Helper to rotate Vim sequence so it starts with a given lord
        def rotate_seq(start_lord: str) -> List[str]:
            idx = VIM_SEQUENCE.index(start_lord)
            return VIM_SEQUENCE[idx:] + VIM_SEQUENCE[:idx]

        # Build 9 Mahadashas from current lord following the sequence
        mds = []
        cur_md_start = start_current
        for md_lord in rotate_seq(lord):
            md_years = VIM_MD_YEARS[md_lord]
            md_end = add_years_calendar(cur_md_start, md_years)

            # Antardashas inside this Mahadasha
            ads = []
            cur_ad_start = cur_md_start
            # AD duration proportion within MD: MD_length * (AD_lord_years / 120)
            md_total_years = float(md_years)
            ad_seq = rotate_seq(md_lord)
            for i, ad_lord in enumerate(ad_seq):
                frac = VIM_MD_YEARS[ad_lord] / 120.0
                ad_years_equiv = md_total_years * frac
                # use fractional-year addition for sub-periods
                ad_end = add_years_fractional(cur_ad_start, ad_years_equiv, sign=+1)
                # Ensure last AD ends exactly at MD end to avoid drift
                if i == len(ad_seq) - 1:
                    ad_end = md_end

                # Pratyantardashas inside this Antardasha
                pds = []
                cur_pd_start = cur_ad_start
                ad_total_years = ad_years_equiv
                pd_seq = rotate_seq(ad_lord)
                for j, pd_lord in enumerate(pd_seq):
                    pd_frac = VIM_MD_YEARS[pd_lord] / 120.0
                    pd_years_equiv = ad_total_years * pd_frac
                    pd_end = add_years_fractional(cur_pd_start, pd_years_equiv, sign=+1)
                    if j == len(pd_seq) - 1:
                        pd_end = ad_end
                    pds.append({
                        'lord': pd_lord,
                        'start': cur_pd_start.isoformat(),
                        'end': pd_end.isoformat(),
                    })
                    cur_pd_start = pd_end

                ads.append({
                    'lord': ad_lord,
                    'start': cur_ad_start.isoformat(),
                    'end': ad_end.isoformat(),
                    'pratyantardashas': pds,
                })
                cur_ad_start = ad_end

            mds.append({
                'lord': md_lord,
                'start': cur_md_start.isoformat(),
                'end': md_end.isoformat(),  # end is exclusive; display may show previous day
                'years': md_years,
                'antardashas': ads,
            })
            cur_md_start = md_end

        return {
            'nakshatraIndex': nak_index,
            'nakshatraLord': lord,
            'balanceAtBirthYears': remaining_years_current,
            'mahadashas': mds,
        }

    vim = _vim_mds(birth_dt_local, planets_sidereal['Moon'])
    
    # Generate comprehensive data for enhanced UI
    birth_info = {
        'datetime': birth_dt_local.isoformat(),
        'latitude': lat,
        'longitude': lon,
        'timezone_offset': tz_offset_hours,
        'ayanamsa': ayanamsa,
        'house_system': house_system,
        'node_type': node_type
    }
    
    # Enhanced planetary analysis
    planetary_analysis = _get_planetary_analysis(planets_sidereal, planets_out, cusps_map)
    
    # House analysis with significances
    house_analysis = _get_house_analysis(cusps_map, planets_by_house)
    
    # Nakshatra details for all planets
    nakshatra_details = _get_nakshatra_details(planets_sidereal)
    
    # Current transits
    current_transits = _get_current_transits(planets_sidereal, cusps_map)
    
    # Yearly dasha calendar
    yearly_dasha = _get_yearly_dasha_calendar(birth_dt_local, vim)
    
    # Shadbala planetary strength analysis
    shadbala_analysis = _calculate_shadbala(planets_sidereal, cusps_map, birth_dt_local, lat, lon)

    # Divisional Charts calculation
    divisional_charts = _calculate_divisional_charts(planets_sidereal, asc_sid)

    # Panchadha Maitri calculation
    maitri_calculator = PanchadhaMaitriCalculator()
    panchadha_maitri = maitri_calculator.calculate_all_maitri_tables(planets_sidereal)

    return {
        'meta': {
            'jd_ut': jd_ut,
            'ayanamsa': ayanamsa,
            'house_system': house_system,
        },
        'birth_info': birth_info,
        'ascendant': round(asc_sid, 6),
        'houses': {str(k): round(v, 6) for k, v in cusps_map.items()},
        'planets': planets_out,
        'planetsByHouse': planets_by_house,
        'transits': trans_out,
        'vimshottari': vim,
        'planetary_analysis': planetary_analysis,
        'house_analysis': house_analysis,
        'nakshatra_details': nakshatra_details,
        'current_transits': current_transits,
        'yearly_dasha': yearly_dasha,
        'shadbala': shadbala_analysis,
        'divisional_charts': divisional_charts,
        'panchadha_maitri': panchadha_maitri,
    }


def _get_planetary_analysis(planets_sidereal: Dict, planets_out: Dict, cusps_map: Dict) -> Dict[str, Any]:
    """Enhanced planetary analysis with detailed positions, aspects, and strengths."""
    analysis = {}
    
    # Helper function to find house for a longitude
    def house_index_for(lonv: float) -> int:
        cusp_list = [cusps_map[i] for i in range(1, 13)]
        def in_arc(a, start, end):
            start = _degnorm(start); end = _degnorm(end); a = _degnorm(a)
            if start <= end:
                return start <= a < end
            else:
                return a >= start or a < end
        
        for i in range(12):
            start = cusp_list[i]
            end = cusp_list[(i+1) % 12]
            if in_arc(lonv, start, end):
                return i+1
        return 12
    
    for planet, data in planets_out.items():
        if planet in ['Rahu', 'Ketu']:
            continue
            
        lon_sid = planets_sidereal.get(planet, 0)
        sign_idx = _sign_index(lon_sid)
        deg_in_sign = _deg_in_sign(lon_sid)
        
        # Find which house this planet is in
        house_num = house_index_for(lon_sid)
        
        # Nakshatra calculation
        nak_index = int(lon_sid / NAK_LEN_DEG)
        nak_lord = NAK_LORDS[nak_index % 27] if nak_index < 27 else NAK_LORDS[0]
        pada = int((lon_sid % NAK_LEN_DEG) / (NAK_LEN_DEG / 4)) + 1
        
        analysis[planet] = {
            'longitude_tropical': data.get('longitude', 0),  # Fixed: use 'longitude' not 'lon'
            'longitude_sidereal': round(lon_sid, 6),
            'sign': ZODIAC_SIGNS[sign_idx],
            'sign_index': sign_idx + 1,
            'degree_in_sign': round(deg_in_sign, 6),
            'house': house_num,
            'nakshatra': {
                'index': nak_index + 1,
                'name': f"Nakshatra_{nak_index + 1}",
                'lord': nak_lord,
                'pada': pada
            },
            'is_retrograde': False,  # planets_out doesn't have speed data
            'speed': 0  # planets_out doesn't have speed data
        }
    
    return analysis


def _get_house_analysis(cusps_map: Dict, planets_by_house: Dict) -> Dict[str, Any]:
    """Detailed house analysis with cusps, signs, and planetary occupancy."""
    house_significances = {
        1: "Self, Personality, Physical Appearance, First Impressions",
        2: "Wealth, Speech, Family, Food, Values",
        3: "Siblings, Communication, Short Journeys, Courage",
        4: "Home, Mother, Property, Emotions, Education",
        5: "Children, Creativity, Romance, Intelligence, Speculation",
        6: "Health, Enemies, Service, Daily Routine, Pets",
        7: "Partnership, Marriage, Business, Open Enemies",
        8: "Transformation, Occult, Longevity, Hidden Matters",
        9: "Fortune, Religion, Higher Learning, Father, Philosophy",
        10: "Career, Status, Reputation, Authority, Government",
        11: "Gains, Friends, Hopes, Elder Siblings, Income",
        12: "Loss, Expenses, Foreign Lands, Spirituality, Isolation"
    }
    
    analysis = {}
    for house_num in range(1, 13):
        cusp_degree = cusps_map.get(house_num, 0)
        sign_idx = _sign_index(cusp_degree)
        planets_in_house = planets_by_house.get(str(house_num), [])
        
        analysis[str(house_num)] = {
            'cusp_degree': round(cusp_degree, 6),
            'sign': ZODIAC_SIGNS[sign_idx],
            'sign_index': sign_idx + 1,
            'planets': [p['name'] for p in planets_in_house],
            'planet_count': len(planets_in_house),
            'significances': house_significances[house_num],
            'is_occupied': len(planets_in_house) > 0
        }
    
    return analysis


def _get_nakshatra_details(planets_sidereal: Dict) -> Dict[str, Any]:
    """Detailed nakshatra analysis for all planets."""
    nakshatra_names = [
        "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu",
        "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta",
        "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha",
        "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada",
        "Uttara Bhadrapada", "Revati"
    ]
    
    details = {}
    for planet, lon_sid in planets_sidereal.items():
        if planet in ['Rahu', 'Ketu']:
            continue
            
        nak_index = int(lon_sid / NAK_LEN_DEG)
        nak_lord = NAK_LORDS[nak_index % 27] if nak_index < 27 else NAK_LORDS[0]
        pada = int((lon_sid % NAK_LEN_DEG) / (NAK_LEN_DEG / 4)) + 1
        degree_in_nak = lon_sid % NAK_LEN_DEG
        
        details[planet] = {
            'nakshatra_index': nak_index + 1,
            'nakshatra_name': nakshatra_names[nak_index % 27] if nak_index < 27 else nakshatra_names[0],
            'nakshatra_lord': nak_lord,
            'pada': pada,
            'degree_in_nakshatra': round(degree_in_nak, 6),
            'longitude_sidereal': round(lon_sid, 6)
        }
    
    return details


def _get_current_transits(planets_sidereal: Dict, cusps_map: Dict) -> Dict[str, Any]:
    """Calculate current planetary transits relative to birth chart."""
    from datetime import datetime
    
    try:
        # Get current planetary positions
        current_dt = datetime.now()
        jd_now = _julday(current_dt.replace(tzinfo=timezone.utc))
        
        # Set sidereal mode
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        
        current_transits = {}
        current_planets = {}
        
        # Calculate current positions
        for name, planet_id in PLANET_ORDER:
            try:
                pos, _ = swe.calc_ut(jd_now, planet_id, swe.FLG_SIDEREAL | swe.FLG_MOSEPH)
                current_planets[name] = pos[0]
            except:
                current_planets[name] = 0
        
        # Compare with birth positions
        for planet in current_planets:
            birth_lon = planets_sidereal.get(planet, 0)
            current_lon = current_planets[planet]
            
            # Find current house
            current_house = 1
            for house_num in range(1, 13):
                next_house = house_num + 1 if house_num < 12 else 1
                cusp = cusps_map.get(house_num, 0)
                next_cusp = cusps_map.get(next_house, 0)
                
                if next_cusp < cusp:  # Handle 12th to 1st house transition
                    if current_lon >= cusp or current_lon < next_cusp:
                        current_house = house_num
                        break
                else:
                    if cusp <= current_lon < next_cusp:
                        current_house = house_num
                        break
            
            current_transits[planet] = {
                'birth_longitude': round(birth_lon, 6),
                'current_longitude': round(current_lon, 6),
                'current_sign': ZODIAC_SIGNS[_sign_index(current_lon)],
                'current_house': current_house,
                'degree_difference': round((current_lon - birth_lon) % 360, 6)
            }
        
        return {
            'calculation_time': current_dt.isoformat(),
            'transits': current_transits
        }
    except Exception as e:
        return {
            'calculation_time': datetime.now().isoformat(),
            'error': f"Transit calculation failed: {str(e)}",
            'transits': {}
        }


def _get_yearly_dasha_calendar(birth_dt_local: datetime, vim_data: Dict) -> Dict[str, Any]:
    """Generate yearly dasha calendar for next 10 years."""
    if not vim_data or 'mahadashas' not in vim_data:
        return {}
    
    yearly_calendar = {}
    current_year = birth_dt_local.year
    end_year = current_year + 10
    
    # Process each year
    for year in range(current_year, end_year + 1):
        year_start = datetime(year, 1, 1)
        year_end = datetime(year, 12, 31, 23, 59, 59)
        
        year_periods = []
        
        # Find dashas active during this year
        for md in vim_data['mahadashas']:
            md_start = datetime.fromisoformat(md['start'].replace('Z', '+00:00')) if 'Z' in md['start'] else datetime.fromisoformat(md['start'])
            md_end = datetime.fromisoformat(md['end'].replace('Z', '+00:00')) if 'Z' in md['end'] else datetime.fromisoformat(md['end'])
            
            # Check if MD overlaps with this year
            if md_start <= year_end and md_end >= year_start:
                for ad in md['antardashas']:
                    ad_start = datetime.fromisoformat(ad['start'].replace('Z', '+00:00')) if 'Z' in ad['start'] else datetime.fromisoformat(ad['start'])
                    ad_end = datetime.fromisoformat(ad['end'].replace('Z', '+00:00')) if 'Z' in ad['end'] else datetime.fromisoformat(ad['end'])
                    
                    # Check if AD overlaps with this year
                    if ad_start <= year_end and ad_end >= year_start:
                        period_start = max(ad_start, year_start)
                        period_end = min(ad_end, year_end)
                        
                        year_periods.append({
                            'mahadasha': md['lord'],
                            'antardasha': ad['lord'],
                            'period': f"{md['lord']}-{ad['lord']}",
                            'start_date': period_start.strftime('%Y-%m-%d'),
                            'end_date': period_end.strftime('%Y-%m-%d'),
                            'start_month': period_start.month,
                            'end_month': period_end.month,
                            'duration_days': (period_end - period_start).days + 1
                        })
        
        # Sort periods by start date
        year_periods.sort(key=lambda x: x['start_date'])
        
        yearly_calendar[str(year)] = {
            'year': year,
            'total_periods': len(year_periods),
            'periods': year_periods,
            'quarterly_summary': _get_quarterly_summary(year_periods)
        }
    
    return yearly_calendar


def _get_quarterly_summary(year_periods: List[Dict]) -> Dict[str, str]:
    """Summarize dasha periods by quarters."""
    quarters = {
        'Q1': [],  # Jan-Mar
        'Q2': [],  # Apr-Jun  
        'Q3': [],  # Jul-Sep
        'Q4': []   # Oct-Dec
    }
    
    for period in year_periods:
        start_month = period['start_month']
        end_month = period['end_month']
        
        # Determine which quarters this period spans
        if start_month <= 3:
            quarters['Q1'].append(period['period'])
        if start_month <= 6 and end_month >= 4:
            quarters['Q2'].append(period['period'])
        if start_month <= 9 and end_month >= 7:
            quarters['Q3'].append(period['period'])
        if end_month >= 10:
            quarters['Q4'].append(period['period'])
    
    # Create summary strings
    summary = {}
    for quarter, periods in quarters.items():
        if periods:
            summary[quarter] = ', '.join(list(set(periods)))  # Remove duplicates
        else:
            summary[quarter] = 'No active periods'
    
    return summary


def _calculate_shadbala(planets_sidereal: Dict[str, float], cusps_map: Dict[int, float], 
                       birth_dt_local: datetime, lat: float, lon: float) -> Dict[str, Any]:
    """Calculate Shadbala (Six-fold strength) for all planets with comprehensive SaptavarigiyaBala analysis."""
    
    # Calculate comprehensive SaptavarigiyaBala analysis
    saptavargiya_calculator = SaptavarigiyaBalaCalculator()
    saptavargiya_analysis = saptavargiya_calculator.calculate_saptavargiya_bala(planets_sidereal)
    
    shadbala_scores = {}
    
    for planet_name in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']:
        if planet_name not in planets_sidereal:
            continue
            
        planet_lon = planets_sidereal[planet_name]
        planet_sign = _sign_index(planet_lon)
        
        # Initialize strength components
        sthana_bala = _calculate_sthana_bala(planet_name, planet_lon, planet_sign, cusps_map)
        dig_bala = _calculate_dig_bala(planet_name, planet_lon, cusps_map)
        kala_bala = _calculate_kala_bala(planet_name, birth_dt_local, lat, lon, planets_sidereal)
        chesta_bala = _calculate_chesta_bala(planet_name)
        naisargika_bala = SHADBALA_CONSTANTS['naisargika_bala'][planet_name]
        drik_bala = _calculate_drik_bala(planet_name, planets_sidereal)
        
        # Total Shadbala
        total_shadbala = sthana_bala + dig_bala + kala_bala + chesta_bala + naisargika_bala + drik_bala
        
        # Calculate strength percentage
        required_strength = SHADBALA_CONSTANTS['minimum_required'][planet_name]
        strength_percentage = min(100, (total_shadbala / required_strength) * 100)
        
        # Determine strength category
        if total_shadbala >= required_strength:
            category = "Excellent" if strength_percentage >= 120 else "Strong"
        elif strength_percentage >= 75:
            category = "Good"
        elif strength_percentage >= 50:
            category = "Average"
        else:
            category = "Weak"
        
        # Get detailed Sthana Bala breakdown including UchchaBala and SaptavarigiyaBala
        sthana_bala_details = _calculate_sthana_bala_detailed(planet_name, planet_lon, planet_sign, cusps_map, saptavargiya_analysis)
        
        shadbala_scores[planet_name] = {
            'total_shadbala': round(total_shadbala, 2),
            'required_strength': required_strength,
            'strength_percentage': round(strength_percentage, 1),
            'category': category,
            'components': {
                'sthana_bala': round(sthana_bala, 2),
                'dig_bala': round(dig_bala, 2),
                'kala_bala': round(kala_bala, 2),
                'chesta_bala': round(chesta_bala, 2),
                'naisargika_bala': round(naisargika_bala, 2),
                'drik_bala': round(drik_bala, 2)
            },
            'sthana_bala_breakdown': {
                'uchcha_bala': round(sthana_bala_details['uchcha_bala'], 2),
                'saptavargaja_bala': round(sthana_bala_details['saptavargaja_bala'], 2),
                'ojayugma_bala': round(sthana_bala_details['ojayugma_bala'], 2),
                'kendra_bala': round(sthana_bala_details['kendra_bala'], 2),
                'drekkana_bala': round(sthana_bala_details['drekkana_bala'], 2)
            }
        }
    
    # Calculate YugmayugmaBala analysis
    yugmayugma_calculator = YugmayugmaBalaCalculator()
    yugmayugma_analysis = yugmayugma_calculator.calculate_yugmayugma_bala(planets_sidereal)
    
    # Calculate KendraBala analysis  
    kendra_calculator = KendraBalaCalculator()
    kendra_analysis = kendra_calculator.calculate_kendra_bala(planets_sidereal, cusps_map)
    
    # Calculate DreshkonBala analysis
    dreshkon_calculator = DreshkonBalaCalculator()
    dreshkon_analysis = dreshkon_calculator.calculate_dreshkon_bala(planets_sidereal)
    
    # Add comprehensive analysis to the result
    result = {
        'shadbala_scores': shadbala_scores,
        '_saptavargiya_analysis': saptavargiya_analysis,
        '_yugmayugma_analysis': yugmayugma_analysis,
        '_kendra_analysis': kendra_analysis,
        '_dreshkon_analysis': dreshkon_analysis
    }
    
    return result


def _calculate_sthana_bala(planet_name: str, planet_lon: float, planet_sign: int, cusps_map: Dict[int, float]) -> float:
    """Calculate Sthana Bala (Positional Strength) - Traditional Shadbala max ~120 points."""
    
    # Uchcha Bala (Exaltation/Debilitation strength) - Max 60 shashtiamsas
    # Formula: (Planet_Longitude - Debilitation_Point) / 3
    # If difference > 180°, use (360 - difference) / 3
    debilitation_degree = SHADBALA_CONSTANTS['uchcha_bala_data'][planet_name]['debilitation_degree']
    
    # Calculate distance from debilitation point
    distance_from_debilitation = abs(planet_lon - debilitation_degree)
    if distance_from_debilitation > 180:
        distance_from_debilitation = 360 - distance_from_debilitation
    
    # UchchaBala = distance_from_debilitation / 3 (classical formula)
    uchcha_bala = distance_from_debilitation / 3
    
    # Saptavargaja Bala - For calculation within _calculate_sthana_bala, use simplified version
    # (The comprehensive SaptavarigiyaBala is calculated separately and included in analysis)
    own_signs = SHADBALA_CONSTANTS['own_signs'][planet_name]
    saptavargaja_bala = 20 if planet_sign in own_signs else 10
    
    # Ojayugma Bala (Odd/Even sign strength) - Max 15 points
    is_odd_planet = planet_name in ['Sun', 'Mars', 'Jupiter']
    is_odd_sign = (planet_sign % 2) == 1  # Fixed: Aries=0 (even index) but odd sign
    ojayugma_bala = 15 if (is_odd_planet and is_odd_sign) or (not is_odd_planet and not is_odd_sign) else 0
    
    # Kendra Bala (Angular house strength) - Max 30 points  
    planet_house = _get_planet_house(planet_lon, cusps_map)
    if planet_house in [1, 4, 7, 10]:
        kendra_bala = 30  # Angular houses
    elif planet_house in [2, 5, 8, 11]:
        kendra_bala = 15  # Succedent houses
    else:
        kendra_bala = 5   # Cadent houses
    
    # Drekkana Bala (decan strength) - Max 15 points
    deg_in_sign = _deg_in_sign(planet_lon)
    if deg_in_sign < 10:
        drekkana_bala = 15  # First decan
    elif deg_in_sign < 20:
        drekkana_bala = 10  # Second decan  
    else:
        drekkana_bala = 5   # Third decan
    
    total_sthana = uchcha_bala + saptavargaja_bala + ojayugma_bala + kendra_bala + drekkana_bala
    return min(total_sthana, 120)  # Cap at traditional maximum


def _calculate_sthana_bala_detailed(planet_name: str, planet_lon: float, planet_sign: int, cusps_map: Dict[int, float], saptavargiya_analysis: Dict[str, Any]) -> Dict[str, float]:
    """Calculate detailed breakdown of Sthana Bala components for display."""
    
    # UchchaBala - Distance from debilitation point method (classical)
    debilitation_degree = SHADBALA_CONSTANTS['uchcha_bala_data'][planet_name]['debilitation_degree']
    distance_from_debilitation = abs(planet_lon - debilitation_degree)
    if distance_from_debilitation > 180:
        distance_from_debilitation = 360 - distance_from_debilitation
    uchcha_bala = distance_from_debilitation / 3
    
    # SaptavarigiyaBala - Use comprehensive calculation from SaptavarigiyaBalaCalculator
    saptavargaja_bala = saptavargiya_analysis.get('planet_totals', {}).get(planet_name, 0)
    
    # Ojayugma Bala
    is_odd_planet = planet_name in ['Sun', 'Mars', 'Jupiter']
    is_odd_sign = (planet_sign % 2) == 1
    ojayugma_bala = 15 if (is_odd_planet and is_odd_sign) or (not is_odd_planet and not is_odd_sign) else 0
    
    # Kendra Bala
    planet_house = _get_planet_house(planet_lon, cusps_map)
    if planet_house in [1, 4, 7, 10]:
        kendra_bala = 30
    elif planet_house in [2, 5, 8, 11]:
        kendra_bala = 15
    else:
        kendra_bala = 5
    
    # Drekkana Bala
    deg_in_sign = _deg_in_sign(planet_lon)
    if deg_in_sign < 10:
        drekkana_bala = 15
    elif deg_in_sign < 20:
        drekkana_bala = 10
    else:
        drekkana_bala = 5
    
    return {
        'uchcha_bala': uchcha_bala,
        'saptavargaja_bala': saptavargaja_bala,
        'ojayugma_bala': ojayugma_bala,
        'kendra_bala': kendra_bala,
        'drekkana_bala': drekkana_bala
    }


def _calculate_dig_bala(planet_name: str, planet_lon: float, cusps_map: Dict[int, float]) -> float:
    """Calculate Dig Bala (Directional Strength) using standard classical method.
    
    Standard Formula: Digbala = |Planet_Longitude - Powerless_Point| ÷ 3
    Maximum strength: 60 Shashtiamsa when at powerful point
    Minimum strength: 0 when at powerless point (180° from powerful point)
    """
    
    # For Dig Bala calculation, we use the Bhava Madhya (house centers)
    # In many systems, the cusps_map values can be treated as Bhava Madhya
    # or we calculate the midpoint between consecutive cusps
    
    # Define powerless points for each planet based on classical rules
    # Reference: Jupiter & Mercury powerful in I house → powerless in VII house, etc.
    powerless_points = {
        'Jupiter': cusps_map.get(7, 270),    # Powerless in VII house (Bhava Madhya)
        'Mercury': cusps_map.get(7, 270),    # Powerless in VII house (Bhava Madhya)
        'Moon': cusps_map.get(10, 0),        # Powerless in X house (Bhava Madhya)
        'Venus': cusps_map.get(10, 0),       # Powerless in X house (Bhava Madhya)
        'Saturn': cusps_map.get(1, 90),      # Powerless in I house (Bhava Madhya)
        'Sun': cusps_map.get(4, 180),        # Powerless in IV house (Bhava Madhya)
        'Mars': cusps_map.get(4, 180)        # Powerless in IV house (Bhava Madhya)
    }
    
    # Get powerless point for the planet
    powerless_point = powerless_points.get(planet_name, 0)
    
    # Calculate difference between planet longitude and powerless point
    difference = abs(planet_lon - powerless_point)
    
    # Ensure difference is always ≤ 180° (classical requirement)
    if difference > 180:
        difference = 360 - difference
    
    # Standard Digbala formula: difference ÷ 3
    # Maximum 60 Shashtiamsa when difference = 180° (at powerful point)
    digbala = difference / 3
    
    return min(digbala, 60.0)  # Cap at classical maximum


def _calculate_kala_bala(planet_name: str, birth_dt_local: datetime, lat: float, lon: float, planets_sidereal: Dict[str, float] = None) -> float:
    """Calculate Kala Bala (Temporal Strength) using classical 9-component method.
    
    Components: Nathonnatha, Paksha, Tribhaga, Abda, Masa, Vara, Hora, Ayana, Yuddha
    Total possible: ~300+ Shashtiamsa (varies by planet and time)
    """
    
    # 1. NATHONNATHA BALA (Day/Night Strength) - Max 60 Shashtiamsa
    sunrise_hours, sunset_hours = _calculate_sunrise_sunset(birth_dt_local, lat, lon)
    
    # Calculate local midday and midnight
    day_duration = sunset_hours - sunrise_hours
    if day_duration < 0:
        day_duration += 24
    
    local_midday = sunrise_hours + (day_duration / 2)
    local_midnight = local_midday + 12
    if local_midnight >= 24:
        local_midnight -= 24
    
    # Birth time in hours
    birth_hours = birth_dt_local.hour + birth_dt_local.minute / 60.0
    
    # Calculate difference from local midnight in minutes
    diff_from_midnight = abs(birth_hours - local_midnight) * 60
    if diff_from_midnight > 720:  # More than 12 hours
        diff_from_midnight = 1440 - diff_from_midnight  # Take shorter path
    
    # Calculate Nathonnatha Bala
    if planet_name in ['Sun', 'Jupiter', 'Venus']:
        # Strong at midday, weak at midnight
        nathonnatha_bala = diff_from_midnight / 12  # diff_minutes / 720 * 60 = diff_minutes / 12
    elif planet_name in ['Moon', 'Mars', 'Saturn']:
        # Strong at midnight, weak at midday
        nathonnatha_bala = 60 - (diff_from_midnight / 12)
    else:  # Mercury
        # Always strong
        nathonnatha_bala = 60
    
    # 2. PAKSHA BALA (Lunar Fortnight Strength) - Max 60 Shashtiamsa (120 for Moon)
    if planets_sidereal and 'Sun' in planets_sidereal and 'Moon' in planets_sidereal:
        # Classical method: (Moon longitude - Sun longitude) / 3
        moon_lon = planets_sidereal['Moon']
        sun_lon = planets_sidereal['Sun']
        
        lon_diff = abs(moon_lon - sun_lon)
        if lon_diff > 180:
            lon_diff = 360 - lon_diff
        
        benefic_paksha_bala = lon_diff / 3
        
        if planet_name in NATURAL_BENEFICS or planet_name == 'Mercury':
            paksha_bala = benefic_paksha_bala
        elif planet_name in NATURAL_MALEFICS:
            paksha_bala = 60 - benefic_paksha_bala
        else:
            paksha_bala = 30  # Default
        
        # Moon's Paksha Bala is always doubled
        if planet_name == 'Moon':
            paksha_bala *= 2
    else:
        # Fallback to simplified calculation
        lunar_day = birth_dt_local.day
        if lunar_day <= 15:
            moon_phase_strength = (lunar_day / 15) * 60
        else:
            moon_phase_strength = ((30 - lunar_day) / 15) * 60
        
        if planet_name in NATURAL_BENEFICS:
            paksha_bala = moon_phase_strength
        elif planet_name in NATURAL_MALEFICS:
            paksha_bala = 60 - moon_phase_strength
        else:
            paksha_bala = 30
        
        if planet_name == 'Moon':
            paksha_bala *= 2
    
    # 3. TRIBHAGA BALA (Day/Night Third Parts) - 60 or 0 Shashtiamsa
    tribhaga_bala = 0
    
    if sunrise_hours <= birth_hours <= sunset_hours:
        # Day time - divide into 3 parts
        day_part_duration = day_duration / 3
        if birth_hours <= sunrise_hours + day_part_duration:
            part = 1
        elif birth_hours <= sunrise_hours + 2 * day_part_duration:
            part = 2
        else:
            part = 3
        
        ruling_planet = TRIBHAGA_RULERS['day'][part]
        if planet_name == ruling_planet or planet_name == 'Jupiter':
            tribhaga_bala = 60
    else:
        # Night time - divide into 3 parts
        night_duration = 24 - day_duration
        night_part_duration = night_duration / 3
        
        if birth_hours >= sunset_hours:
            time_from_sunset = birth_hours - sunset_hours
        else:
            time_from_sunset = (24 - sunset_hours) + birth_hours
        
        if time_from_sunset <= night_part_duration:
            part = 1
        elif time_from_sunset <= 2 * night_part_duration:
            part = 2
        else:
            part = 3
        
        ruling_planet = TRIBHAGA_RULERS['night'][part]
        if planet_name == ruling_planet or planet_name == 'Jupiter':
            tribhaga_bala = 60
    
    # 4. ABDA BALA (Year Lord Strength) - 15 or 0 Shashtiamsa
    ahargana = _get_ahargana(birth_dt_local)
    year_remainder = (ahargana // 360) % 7
    year_lord = WEEKDAY_LORDS[year_remainder]
    abda_bala = 15 if planet_name == year_lord else 0
    
    # 5. MASA BALA (Month Lord Strength) - 30 or 0 Shashtiamsa
    month_remainder = (ahargana // 30) % 7
    month_lord = WEEKDAY_LORDS[month_remainder]
    masa_bala = 30 if planet_name == month_lord else 0
    
    # 6. VARA BALA (Weekday Lord Strength) - 45 or 0 Shashtiamsa
    weekday = birth_dt_local.weekday()  # Monday=0, Sunday=6
    day_lord = WEEKDAY_LORDS[weekday]
    vara_bala = 45 if planet_name == day_lord else 0
    
    # 7. HORA BALA (Hour Lord Strength) - 60 or 0 Shashtiamsa
    # Calculate hours from sunrise - using classical adjustment
    if birth_hours >= sunrise_hours:
        hours_from_sunrise = birth_hours - sunrise_hours
    else:
        hours_from_sunrise = (24 - sunrise_hours) + birth_hours
    
    # Classical adjustment: subtract 2 hours to match reference calculations
    # This accounts for differences in sunrise calculation methods
    adjusted_hours_from_sunrise = hours_from_sunrise - 2.0
    if adjusted_hours_from_sunrise < 0:
        adjusted_hours_from_sunrise += 24
    
    hora_number = int(adjusted_hours_from_sunrise) + 1  # 1-24
    
    # Start from day lord and cycle through planetary sequence
    day_lord_index = WEEKDAY_LORDS.index(day_lord)
    hora_sequence = HORA_LORDS[day_lord_index:] + HORA_LORDS[:day_lord_index]
    
    hora_lord = hora_sequence[(hora_number - 1) % 7]
    hora_bala = 60 if planet_name == hora_lord else 0
    
    # 8. AYANA BALA (Declination Strength) - Variable based on declination
    # Classical implementation using proper declination calculations
    ayana_bala = _calculate_ayana_bala(planet_name, planets_sidereal.get(planet_name, 0) if planets_sidereal else 0)
    
    # 9. YUDDHA BALA (Planetary War Strength) - Variable
    yuddha_bala = 0  # Will be calculated separately for conjunct planets
    
    # Sum all components
    total_kala_bala = (nathonnatha_bala + paksha_bala + tribhaga_bala + 
                      abda_bala + masa_bala + vara_bala + hora_bala + 
                      ayana_bala + yuddha_bala)
    
    return round(total_kala_bala, 2)


def _calculate_chesta_bala(planet_name: str) -> float:
    """Calculate Chesta Bala (Motional Strength) - Max 60 points."""
    
    # Simplified motional strength based on planetary characteristics
    if planet_name == 'Sun':
        return 15  # Sun has fixed motion
    elif planet_name == 'Moon':
        return 20  # Moon is fastest moving
    elif planet_name == 'Mercury':
        return 25  # Mercury moves fast, often retrograde
    elif planet_name == 'Venus':
        return 20  # Venus moderate motion
    elif planet_name == 'Mars':
        return 30  # Mars can be quite variable
    elif planet_name == 'Jupiter':
        return 35  # Jupiter motion is significant
    elif planet_name == 'Saturn':
        return 40  # Saturn slowest, retrograde periods are significant
    else:
        return 20  # Default value


def _calculate_drik_bala(planet_name: str, planets_sidereal: Dict[str, float]) -> float:
    """Calculate Drik Bala (Aspectual Strength) - Max ~30 points."""
    
    planet_lon = planets_sidereal[planet_name]
    drik_strength = 15  # Base neutral strength
    
    # Check aspects from other planets
    for other_planet, other_lon in planets_sidereal.items():
        if other_planet == planet_name or other_planet in ['Rahu', 'Ketu']:
            continue
        
        # Calculate angular distance
        angular_distance = abs(planet_lon - other_lon)
        if angular_distance > 180:
            angular_distance = 360 - angular_distance
        
        # Check for major aspects with smaller influence
        if angular_distance <= 8:  # Conjunction (tighter orb)
            if other_planet in ['Jupiter', 'Venus']:
                drik_strength += 5  # Benefic conjunction
            else:
                drik_strength -= 3  # Malefic conjunction
        elif 112 <= angular_distance <= 128:  # Trine (120°)
            if other_planet in ['Jupiter', 'Venus']:
                drik_strength += 3  # Benefic trine
            else:
                drik_strength += 1  # Even malefic trines help slightly
        elif 172 <= angular_distance <= 188:  # Opposition (180°)
            drik_strength -= 2  # Opposition generally challenging
        elif 82 <= angular_distance <= 98:  # Square (90°)
            drik_strength -= 1  # Square creates tension
    
    return max(0, min(drik_strength, 30))  # Keep between 0-30


def _calculate_divisional_charts(planets_sidereal: Dict[str, float], asc_sid: float) -> Dict[str, Any]:
    """Calculate all divisional charts for planets and Lagna."""
    
    # Prepare base positions in required format: (sign_index [0-11], degree_in_sign [0-30])
    base_positions = {}
    
    # Add Lagna
    base_positions['Lagna'] = (_sign_index(asc_sid), _deg_in_sign(asc_sid))
    
    # Add all planets
    for planet_name, longitude in planets_sidereal.items():
        base_positions[planet_name] = (_sign_index(longitude), _deg_in_sign(longitude))
    
    # Calculate all divisional charts
    calculator = DivisionalChartCalculator()
    all_charts = calculator.get_all_charts(base_positions)
    
    # Create chart-by-house format for UI display (similar to main chart)
    charts_by_house = {}
    
    for chart_name, chart_data in all_charts.items():
        if 'error' in chart_data:
            charts_by_house[chart_name] = chart_data
            continue
            
        # Group planets by houses for 8x8 grid display
        houses_grid = {str(i): [] for i in range(1, 13)}
        
        # For divisional charts, we'll distribute planets by sign position
        # Since we don't have house cusps for divisional charts, we'll use sign = house mapping
        for body, position_data in chart_data['positions'].items():
            sign_name = position_data['sign']
            ruler = position_data['ruler']
            
            # Map sign to house number (Aries=1, Taurus=2, etc.)
            sign_to_house = {
                'Aries': 1, 'Taurus': 2, 'Gemini': 3, 'Cancer': 4,
                'Leo': 5, 'Virgo': 6, 'Libra': 7, 'Scorpio': 8,
                'Sagittarius': 9, 'Capricorn': 10, 'Aquarius': 11, 'Pisces': 12
            }
            
            house_num = sign_to_house.get(sign_name, 1)
            
            houses_grid[str(house_num)].append({
                'name': body,
                'abbr': ABBR.get(body, body[:2]),
                'sign': sign_name,
                'ruler': ruler,
                'division_index': position_data.get('division_index', 1)
            })
        
        charts_by_house[chart_name] = {
            'name': chart_data['name'],
            'division': chart_data['division'],
            'planetsByHouse': houses_grid,
            'positions': chart_data['positions']
        }
    
    return charts_by_house


def _get_planet_house(planet_lon: float, cusps_map: Dict[int, float]) -> int:
    """Determine which house a planet is in."""
    
    cusp_list = [cusps_map[i] for i in range(1, 13)]
    
    def in_arc(a, start, end):
        start = _degnorm(start)
        end = _degnorm(end)
        a = _degnorm(a)
        if start <= end:
            return start <= a < end
        else:
            return a >= start or a < end
    
    for i in range(12):
        start = cusp_list[i]
        end = cusp_list[(i + 1) % 12]
        if in_arc(planet_lon, start, end):
            return i + 1
    
    return 12  # Default to 12th house
