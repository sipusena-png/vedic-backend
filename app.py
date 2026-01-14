from flask import Flask, jsonify, request
import swisseph as swe
from modules.calculator import get_common_data, resolve_location, decimal_to_vedic_format
from modules.chart_drawer import create_south_indian_chart, create_north_indian_chart
import datetime

from modules.panchang import get_panchang
from modules.matcher import guna_milan
from modules.dasha import get_vimshottari_dasha
import json
import os
import datetime

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "message": "Astrology API is running",
        "version": "1.6.0",
        "structure": "Professional Modular"
    })

@app.route('/panchang')
def panchang():
    """Returns Panchang details (Tithi, Nakshatra, Yoga) for a specific time."""
    try:
        year = request.args.get('year', type=int)
        month = request.args.get('month', default=1, type=int)
        day = request.args.get('day', default=1, type=int)
        hour = request.args.get('hour', default=12.0, type=float)
        
        jd, _, _ = get_common_data(year, month, day, hour)
        data = get_panchang(jd)
        return jsonify(data)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/match')
def match():
    """Calculates Guna Milan score between two birth moments (Moon longitudes)."""
    try:
        # For simplicity, we directly take moon longitudes as input
        # In a full app, you'd calculate these from birth details
        boy_moon_lon = float(request.args.get('boy_moon_lon', 0.0))
        girl_moon_lon = float(request.args.get('girl_moon_lon', 0.0))
        
        result = guna_milan(boy_moon_lon, girl_moon_lon)
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/dasha')
def dasha():
    """Calculates Vimshottari Dasha for a specific birth time and Moon longitude."""
    try:
        moon_lon = float(request.args.get('moon_lon', 0.0))
        year = request.args.get('year', type=int)
        month = request.args.get('month', default=1, type=int)
        day = request.args.get('day', default=1, type=int)
        hour = request.args.get('hour', default=12, type=int)
        minute = request.args.get('minute', default=0, type=int)
        
        if year is None:
            return jsonify({"error": "Birth year is required"}), 400
            
        birth_dt = datetime.datetime(year, month, day, hour, minute)
        dasha_data = get_vimshottari_dasha(moon_lon, birth_dt)
        
        return jsonify({
            "system": "Vimshottari Dasha",
            "cycle_years": 120,
            "dashas": dasha_data
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/data/<file_name>')
def get_data(file_name):
    """Returns data from predictions.json or festivals.json."""
    if file_name not in ['predictions', 'festivals']:
        return jsonify({"error": "Invalid data file"}), 400
        
    file_path = f"data/{file_name}.json"
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404
        
    with open(file_path, 'r') as f:
        data = json.load(f)
    return jsonify(data)

@app.route('/lookup')
def lookup():
    """Endpoint to look up city coordinates and timezone with optional date for DST."""
    city = request.args.get('city')
    if not city:
        return jsonify({"error": "Please provide a city parameter"}), 400
    
    # Optional date params for DST check
    year = request.args.get('year', type=int)
    month = request.args.get('month', default=1, type=int)
    day = request.args.get('day', default=1, type=int)
    hour = request.args.get('hour', default=12, type=int)
    minute = request.args.get('minute', default=0, type=int)
        
    data = resolve_location(city, year, month, day, hour, minute)
    if not data:
        return jsonify({"error": "City not found or timezone lookup failed"}), 404
        
    return jsonify(data)

@app.route('/test_swisseph')
def test_swisseph():
    """Test endpoint for Lahiri (Sidereal) Sun position."""
    try:
        jd, planets_lon, _ = get_common_data()
        sun_longitude = planets_lon["Sun"]
        return jsonify({
            "service": "Swiss Ephemeris (Vedic/Lahiri)",
            "julian_day": jd,
            "sun_longitude": sun_longitude,
            "formatted": decimal_to_vedic_format(sun_longitude),
            "status": "success"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/vedic_sun')
def vedic_sun():
    """Returns the current Sun position in Vedic format."""
    try:
        _, planets_lon, _ = get_common_data()
        longitude = planets_lon["Sun"]
        return jsonify({
            "planet": "Sun",
            "longitude": longitude,
            "vedic_format": decimal_to_vedic_format(longitude)
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/chart')
def get_chart():
    """Generates and returns the current South Indian Vedic chart."""
    try:
        # Check if historical date is provided
        year = request.args.get('year', type=int)
        month = request.args.get('month', type=int)
        day = request.args.get('day', type=int)
        hour = request.args.get('hour', type=float) # Decimal hour

        jd, planets_lon, _ = get_common_data(year, month, day, hour)
        planets_data = {name: int(lon / 30) for name, lon in planets_lon.items()}
        svg_content = create_south_indian_chart(planets_data)
        return svg_content, 200, {'Content-Type': 'image/svg+xml'}
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/chart_north')
def get_chart_north():
    """Generates and returns a North Indian Vedic chart (DST-aware)."""
    try:
        # Get date/time parameters
        year = request.args.get('year', type=int)
        month = request.args.get('month', default=1, type=int)
        day = request.args.get('day', default=1, type=int)
        hour = request.args.get('hour', default=12.0, type=float)
        minute = request.args.get('minute', default=0, type=int)

        # Check if city is provided
        city = request.args.get('city')
        if city:
            loc_data = resolve_location(city, year, month, day, int(hour), minute)
            if not loc_data:
                return jsonify({"error": "City not found"}), 404
            lat = loc_data["lat"]
            lon = loc_data["lon"]
        else:
            # Default coordinates for Delhi
            lat = float(request.args.get('lat', 28.6139))
            lon = float(request.args.get('lon', 77.2090))
        
        # Calculate decimal hour if minute provided separately
        full_hour = hour + minute/60.0 if year is not None else None
        
        jd, planets_lon, flags = get_common_data(year, month, day, full_hour)
        
        # Calculate Houses (Whole Sign b'W')
        res, ascmc = swe.houses_ex(jd, flags, lat, lon, b'W')
        asc_lon = ascmc[0]
        asc_sign = int(asc_lon / 30) + 1 # 1-indexed (1=Aries, etc.)
        
        house_data = {}
        for name, p_lon in planets_lon.items():
            p_sign = int(p_lon / 30) + 1
            house = (p_sign - asc_sign + 12) % 12 + 1
            house_data[name] = house
            
        # Add Lagna to house 1
        house_data["Lagna"] = 1

        svg_content = create_north_indian_chart(house_data, asc_sign)
        return svg_content, 200, {'Content-Type': 'image/svg+xml'}
    except Exception as e:
        import traceback
        return jsonify({"status": "error", "message": str(e), "trace": traceback.format_exc()}), 500

if __name__ == '__main__':
    app.run(debug=True, port=8080)
