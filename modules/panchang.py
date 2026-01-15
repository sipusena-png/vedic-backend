import swisseph as swe
import datetime

def get_panchang(jd):
    """
    Calculates Tithi, Nakshatra, Yoga, and Karana using Swiss Ephemeris.
    """
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL

    # 1. Calculate Sun and Moon positions
    res_sun, _ = swe.calc_ut(jd, swe.SUN, flags)
    res_moon, _ = swe.calc_ut(jd, swe.MOON, flags)
    
    sun_lon = res_sun[0]
    moon_lon = res_moon[0]

    # 2. Tithi Formula: (Moon_Long - Sun_Long) / 12
    # Result 0-15 = Shukla Paksha, 15-30 = Krishna Paksha
    diff = (moon_lon - sun_lon + 360) % 360
    tithi_val = diff / 12.0
    tithi_no = int(tithi_val) + 1
    
    tithis = [
        "Prathama", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashti", "Saptami", "Ashtami",
        "Navami", "Dashami", "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima/Amavasya"
    ]
    tithi_name = tithis[(tithi_no - 1) % 15]
    paksha = "Shukla" if tithi_no <= 15 else "Krishna"

    # 3. Nakshatra (Moon distance)
    # Each Nakshatra is 13° 20' (13.333 degrees). 27 Nakshatras total.
    nak_no = int(moon_lon / (360/27.0)) + 1
    nak_list = [
        "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu", "Pushya", "Ashlesha",
        "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
        "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
    ]
    nak_name = nak_list[min(nak_no - 1, 26)]

    # 4. Yoga Formula: (Moon_Long + Sun_Long) / 13.20 (Note: 13.20 refers to 13° 20' or 13.333°)
    yoga_sum = (sun_lon + moon_lon) % 360
    yoga_no = int(yoga_sum / (360/27.0)) + 1
    yoga_list = [
        "Vishkumbha", "Priti", "Ayushman", "Saubhagya", "Sobhana", "Atiganda", "Sukarma", "Dhriti", "Shula",
        "Ganda", "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra", "Siddhi", "Vyatipata", "Variyan", "Parigha",
        "Shiva", "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma", "Indra", "Vaidhriti"
    ]
    yoga_name = yoga_list[min(yoga_no - 1, 26)]

    # 5. Karana (Half of Tithi)
    # Each Karana is 6 degrees.
    karana_no = int(diff / 6) + 1
    # Note: Simplified Karana list
    return {
        "tithi": tithi_name,
        "paksha": paksha,
        "nakshatra": nak_name,
        "yoga": yoga_name,
        "tithi_number": tithi_no,
        "jd": jd
    }
