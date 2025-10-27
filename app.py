from flask import Flask, render_template, request, jsonify, send_file, Response
from datetime import datetime
from vedic.core import compute_chart
from timezonefinder import TimezoneFinder
from zoneinfo import ZoneInfo
from local_geocoder import LocalGeocoder
import os
import time
import json
from io import StringIO

tf = TimezoneFinder()
local_geocoder = LocalGeocoder()  # Initialize local geocoder

app = Flask(__name__)

# Simple in-memory cache for place queries: { query_lower: (timestamp, [ {name,lat,lon}, ... ]) }
PLACES_CACHE = {}
PLACES_CACHE_TTL = 60 * 60  # 1 hour

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chart', methods=['POST'])
def api_chart():
    print("DEBUG: api_chart called")
    data = request.get_json() or {}
    print(f"DEBUG: Received data: {data}")
    
    try:
        print("DEBUG: Parsing datetime...")
        birth_dt = datetime.fromisoformat(data['datetime'])
        print(f"DEBUG: birth_dt parsed: {birth_dt}")

        # Defaults as per reference: Lahiri, Equal houses, Mean node
        ayanamsa = (data.get('ayanamsa') or 'lahiri')
        system = (data.get('house_system') or 'equal')
        node_type = (data.get('node_type') or 'mean')

        # If place provided, geocode to lat/lon using multi-source geocoder
        place = data.get('place')
        lat = data.get('lat')
        lon = data.get('lon')
        
        if place and (lat is None or lon is None or lat == '' or lon == ''):
            results = geocode_query(place)
            if not results:
                return jsonify({'ok': False, 'error': 'Place not found'}), 400
            lat = float(results[0]['lat'])
            lon = float(results[0]['lon'])
        else:
            # Validate lat/lon are provided and not empty
            if not lat or lat == '':
                return jsonify({'ok': False, 'error': 'Latitude is required'}), 400
            if not lon or lon == '':
                return jsonify({'ok': False, 'error': 'Longitude is required'}), 400
            
            try:
                lat = float(lat)
                lon = float(lon)
            except ValueError:
                return jsonify({'ok': False, 'error': 'Invalid latitude or longitude format'}), 400

        # Timezone offset: auto if not supplied
        raw_tz = data.get('tz_offset', None)
        if raw_tz in (None, '', []):
            tz_offset = compute_tz_offset_hours(birth_dt, lat, lon)
        else:
            tz_offset = float(raw_tz)

        print(f"DEBUG: About to call compute_chart with:")
        print(f"  birth_dt: {birth_dt}")
        print(f"  lat: {lat}, lon: {lon}")
        print(f"  tz_offset: {tz_offset}")
        print(f"  ayanamsa: {ayanamsa}, system: {system}")
        
        result = compute_chart(birth_dt, lat, lon, tz_offset, ayanamsa, system, node_type=node_type)
        
        print(f"DEBUG: compute_chart returned successfully")
        print(f"DEBUG: Result keys: {list(result.keys())}")
        
        # Store data for download functionality
        global last_chart_data
        last_chart_data = result
        
        return jsonify({ 'ok': True, 'data': result })
    except Exception as e:
        print(f"DEBUG: Exception in api_chart: {str(e)}")
        print(f"DEBUG: Exception type: {type(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({ 'ok': False, 'error': str(e) }), 400

def local_search_cities(query: str):
    """Local city search using offline database."""
    return local_geocoder.search_cities(query, limit=7)


def geocode_query(query: str):
    """Geocode using local database with caching."""
    # Serve from cache if fresh
    key = (query or '').strip().lower()
    now = time.time()
    if key in PLACES_CACHE:
        ts, data = PLACES_CACHE[key]
        if now - ts < PLACES_CACHE_TTL:
            return data

    # Use local geocoder (no internet required)
    try:
        data = local_search_cities(query)
        PLACES_CACHE[key] = (now, data)
        return data
    except Exception:
        PLACES_CACHE[key] = (now, [])
        return []


@app.route('/api/places')
def api_places():
    q = request.args.get('q', '')
    if len(q) < 3:
        return jsonify({ 'ok': True, 'data': [] })
    try:
        data = geocode_query(q)
        return jsonify({ 'ok': True, 'data': data })
    except Exception as e:
        # On provider errors, return empty list quickly instead of 500 to keep UI snappy
        return jsonify({ 'ok': True, 'data': [] })


def compute_tz_offset_hours(dt_local: datetime, lat: float, lon: float) -> float:
    tzname = TimezoneFinder().timezone_at(lng=lon, lat=lat)
    if not tzname:
        return 0.0
    try:
        tz = ZoneInfo(tzname)
        localized = dt_local.replace(tzinfo=tz)
        offset = localized.utcoffset()
        return (offset.total_seconds() / 3600.0) if offset else 0.0
    except Exception:
        return 0.0


@app.route('/api/tz')
def api_tz():
    try:
        dt = datetime.fromisoformat(request.args['datetime'])
        lat = float(request.args['lat'])
        lon = float(request.args['lon'])
        off = compute_tz_offset_hours(dt, lat, lon)
        return jsonify({ 'ok': True, 'data': { 'tz_offset': off }})
    except Exception as e:
        return jsonify({ 'ok': False, 'error': str(e) }), 400

@app.route('/api/health')
def health():
    return jsonify({'ok': True})

# Store the last chart data for downloads
last_chart_data = {}

@app.route('/api/download/<section>')
def download_section(section):
    """Download specific section data as formatted JSON."""
    global last_chart_data
    
    if not last_chart_data:
        return jsonify({'ok': False, 'error': 'No chart data available. Generate a chart first.'}), 400
    
    try:
        # Define section mappings
        section_data = {}
        
        if section == 'birth_info':
            section_data = {
                'birth_info': last_chart_data.get('birth_info', {}),
                'meta': last_chart_data.get('meta', {}),
                'ascendant': last_chart_data.get('ascendant', 0)
            }
        elif section == 'planets':
            section_data = {
                'planetary_analysis': last_chart_data.get('planetary_analysis', {}),
                'planets': last_chart_data.get('planets', {}),
                'planetsByHouse': last_chart_data.get('planetsByHouse', {})
            }
        elif section == 'houses':
            section_data = {
                'house_analysis': last_chart_data.get('house_analysis', {}),
                'houses': last_chart_data.get('houses', {})
            }
        elif section == 'nakshatras':
            section_data = {
                'nakshatra_details': last_chart_data.get('nakshatra_details', {}),
                'planetary_nakshatras': {
                    planet: data.get('nakshatra', {}) 
                    for planet, data in last_chart_data.get('planetary_analysis', {}).items()
                }
            }
        elif section == 'transits':
            section_data = {
                'current_transits': last_chart_data.get('current_transits', {}),
                'birth_positions': {
                    planet: {
                        'longitude': data.get('longitude_sidereal', 0),
                        'sign': data.get('sign', ''),
                        'house': data.get('house', 1)
                    }
                    for planet, data in last_chart_data.get('planetary_analysis', {}).items()
                }
            }
        elif section == 'mahadasha':
            section_data = {
                'vimshottari': last_chart_data.get('vimshottari', {}),
                'current_period_analysis': _analyze_current_period(last_chart_data.get('vimshottari', {}))
            }
        elif section == 'yearly_dasha':
            section_data = {
                'yearly_dasha': last_chart_data.get('yearly_dasha', {}),
                'dasha_summary': _get_dasha_summary(last_chart_data.get('yearly_dasha', {}))
            }
        elif section == 'complete':
            section_data = last_chart_data
        else:
            return jsonify({'ok': False, 'error': f'Unknown section: {section}'}), 400
        
        # Create formatted JSON with AI-friendly structure
        formatted_data = {
            'section': section,
            'generated_at': datetime.now().isoformat(),
            'data_type': 'vedic_astrology_chart',
            'ai_readable_format': True,
            'content': section_data
        }
        
        # Create response
        json_str = json.dumps(formatted_data, indent=2, ensure_ascii=False)
        
        return Response(
            json_str,
            mimetype='application/json',
            headers={'Content-Disposition': f'attachment; filename="astrology_{section}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json"'}
        )
        
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 400

def _analyze_current_period(vim_data):
    """Analyze current dasha period."""
    if not vim_data or 'mahadashas' not in vim_data:
        return {}
    
    current_date = datetime.now()
    
    for md in vim_data['mahadashas']:
        md_start = datetime.fromisoformat(md['start'].replace('Z', '+00:00')) if 'Z' in md['start'] else datetime.fromisoformat(md['start'])
        md_end = datetime.fromisoformat(md['end'].replace('Z', '+00:00')) if 'Z' in md['end'] else datetime.fromisoformat(md['end'])
        
        if md_start <= current_date <= md_end:
            # Find current antardasha
            for ad in md['antardashas']:
                ad_start = datetime.fromisoformat(ad['start'].replace('Z', '+00:00')) if 'Z' in ad['start'] else datetime.fromisoformat(ad['start'])
                ad_end = datetime.fromisoformat(ad['end'].replace('Z', '+00:00')) if 'Z' in ad['end'] else datetime.fromisoformat(ad['end'])
                
                if ad_start <= current_date <= ad_end:
                    # Find current pratyantardasha
                    current_pd = None
                    for pd in ad.get('pratyantardashas', []):
                        pd_start = datetime.fromisoformat(pd['start'].replace('Z', '+00:00')) if 'Z' in pd['start'] else datetime.fromisoformat(pd['start'])
                        pd_end = datetime.fromisoformat(pd['end'].replace('Z', '+00:00')) if 'Z' in pd['end'] else datetime.fromisoformat(pd['end'])
                        
                        if pd_start <= current_date <= pd_end:
                            current_pd = pd
                            break
                    
                    return {
                        'current_mahadasha': md['lord'],
                        'current_antardasha': ad['lord'],
                        'current_pratyantardasha': current_pd['lord'] if current_pd else 'Unknown',
                        'md_start': md['start'],
                        'md_end': md['end'],
                        'ad_start': ad['start'],
                        'ad_end': ad['end'],
                        'pd_start': current_pd['start'] if current_pd else None,
                        'pd_end': current_pd['end'] if current_pd else None,
                        'current_period': f"{md['lord']}-{ad['lord']}-{current_pd['lord'] if current_pd else 'Unknown'}"
                    }
    
    return {'status': 'No current period found'}

def _get_dasha_summary(yearly_data):
    """Generate summary of yearly dasha patterns."""
    if not yearly_data:
        return {}
    
    summary = {
        'total_years': len(yearly_data),
        'years_covered': list(yearly_data.keys()),
        'dominant_mahadashas': {},
        'dominant_antardashas': {}
    }
    
    # Count frequency of each dasha lord
    md_count = {}
    ad_count = {}
    
    for year_data in yearly_data.values():
        for period in year_data.get('periods', []):
            md_lord = period['mahadasha']
            ad_lord = period['antardasha']
            
            md_count[md_lord] = md_count.get(md_lord, 0) + 1
            ad_count[ad_lord] = ad_count.get(ad_lord, 0) + 1
    
    summary['dominant_mahadashas'] = dict(sorted(md_count.items(), key=lambda x: x[1], reverse=True))
    summary['dominant_antardashas'] = dict(sorted(ad_count.items(), key=lambda x: x[1], reverse=True))
    
    return summary

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
