import swisseph as swe
import datetime
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import pytz

tf = TimezoneFinder()
geolocator = Nominatim(user_agent="astrology_api")

RASIS = [
    "Mesha (Aries)", "Vrishabha (Taurus)", "Mithuna (Gemini)", "Karka (Cancer)",
    "Simha (Leo)", "Kanya (Virgo)", "Tula (Libra)", "Vrishchika (Scorpio)",
    "Dhanu (Sagittarius)", "Makara (Capricorn)", "Kumbha (Aquarius)", "Meena (Pisces)"
]

def decimal_to_vedic_format(total_degrees):
    """Converts absolute longitude (0-360) into Vedic Sign + DMS format."""
    total_degrees = total_degrees % 360
    sign_index = int(total_degrees / 30)
    sign_name = RASIS[sign_index]
    degrees_in_sign_float = total_degrees % 30
    d = int(degrees_in_sign_float)
    minutes_float = (degrees_in_sign_float - d) * 60
    m = int(minutes_float)
    s = int((minutes_float - m) * 60)
    return f"{sign_name} {d}° {m}' {s}\""

def get_common_data(year=None, month=None, day=None, hour=12.0):
    """Helper to get JD and planets longitude for a specific time or now."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    if year is None:
        now = datetime.datetime.utcnow()
        year, month, day = now.year, now.month, now.day
        hour = now.hour + now.minute/60.0
        
    jd = swe.julday(year, month, day, hour)
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED | swe.FLG_SIDEREAL
    
    planets = {
        "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS, "Merc": swe.MERCURY,
        "Jup": swe.JUPITER, "Ven": swe.VENUS, "Sat": swe.SATURN, "Rahu": swe.MEAN_NODE
    }
    
    planets_lon = {}
    for name, id in planets.items():
        res, _ = swe.calc_ut(jd, id, flags)
        planets_lon[name] = res[0]
        
    # Add Ketu
    res_rahu, _ = swe.calc_ut(jd, swe.MEAN_NODE, flags)
    planets_lon["Ketu"] = (res_rahu[0] + 180) % 360
    
    return jd, planets_lon, flags

def resolve_location(city_name, year=None, month=1, day=1, hour=12, minute=0):
    """Converts a city name to coordinates, timezone name, and DST-accurate offset."""
    try:
        location = geolocator.geocode(city_name)
        if not location:
            return None
        
        lat, lon = location.latitude, location.longitude
        timezone_str = tf.timezone_at(lng=lon, lat=lat)
        
        if not timezone_str:
            return None
            
        tz = pytz.timezone(timezone_str)
        
        # DST-Aware calculation
        if year is not None:
            # Calculate offset for a specific historical date
            dt = datetime.datetime(year, month, day, hour, minute)
            localized_time = tz.localize(dt)
        else:
            # Use current time if no date provided
            localized_time = datetime.datetime.now(tz)
            
        # Calculate GMT Offset
        offset_seconds = localized_time.utcoffset().total_seconds()
        offset_hours = offset_seconds / 3600.0
        
        # Format offset string (e.g., +05:30)
        offset_string = localized_time.strftime('%z')
        formatted_offset = f"{offset_string[:-2]}:{offset_string[-2:]}"
        
        return {
            "name": location.address,
            "lat": lat,
            "lon": lon,
            "timezone": timezone_str,
            "gmt_offset_str": formatted_offset,
            "gmt_offset_decimal": offset_hours
        }
    except Exception:
        return None
