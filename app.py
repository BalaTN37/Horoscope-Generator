from flask import Flask, render_template, request, jsonify
from datetime import datetime
from vedic.core import compute_chart
from timezonefinder import TimezoneFinder
from zoneinfo import ZoneInfo
from local_geocoder import LocalGeocoder
import os
import time

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
    data = request.get_json() or {}
    try:
        birth_dt = datetime.fromisoformat(data['datetime'])

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
            lat = float(lat)
            lon = float(lon)

        # Timezone offset: auto if not supplied
        raw_tz = data.get('tz_offset', None)
        if raw_tz in (None, '', []):
            tz_offset = compute_tz_offset_hours(birth_dt, lat, lon)
        else:
            tz_offset = float(raw_tz)

        result = compute_chart(birth_dt, lat, lon, tz_offset, ayanamsa, system, node_type=node_type)
        return jsonify({ 'ok': True, 'data': result })
    except Exception as e:
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

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
