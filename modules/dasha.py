import datetime

# Vimshottari Dasha period in years
DASHA_PERIODS = {
    "Ketu": 7,
    "Ven": 20,
    "Sun": 6,
    "Moon": 10,
    "Mars": 7,
    "Rahu": 18,
    "Jup": 16,
    "Sat": 19,
    "Merc": 17
}

DASHA_ORDER = ["Ketu", "Ven", "Sun", "Moon", "Mars", "Rahu", "Jup", "Sat", "Merc"]

def get_vimshottari_dasha(moon_lon, birth_dt):
    """
    Calculates Vimshottari Dasha periods for 120 years starting from birth.
    moon_lon: Sidereal longitude of Moon
    birth_dt: datetime object of birth
    """
    # 1. Find Nakshatra and its progress
    # Each Nakshatra is 13° 20' (13.333... degrees)
    nak_size = 360 / 27
    nak_index = int(moon_lon / nak_size)
    
    # 2. Find starting Dasha
    # Nakshatra 0 (Ashwini) is ruled by Ketu, 1 by Venus, etc.
    start_lord_index = nak_index % 9
    start_lord = DASHA_ORDER[start_lord_index]
    
    # 3. Calculate balance of first Dasha
    # Degrees already traversed in current Nakshatra
    traversed_in_nak = moon_lon % nak_size
    remaining_in_nak = nak_size - traversed_in_nak
    
    # Proportion of Dasha remaining
    total_period = DASHA_PERIODS[start_lord]
    remaining_years = (remaining_in_nak / nak_size) * total_period
    
    dashas = []
    current_start_date = birth_dt
    
    # Current (First) Dasha
    end_date = current_start_date + datetime.timedelta(days=int(remaining_years * 365.25))
    dashas.append({
        "planet": start_lord,
        "start": current_start_date.strftime("%Y-%m-%d"),
        "end": end_date.strftime("%Y-%m-%d"),
        "total_years": total_period,
        "is_balance": True
    })
    
    # Subsequent Dashas for the rest of the 120-year cycle
    current_start_date = end_date
    lord_ptr = (start_lord_index + 1) % 9
    
    for _ in range(8): # Add the rest of the sequence
        planet = DASHA_ORDER[lord_ptr]
        period = DASHA_PERIODS[planet]
        end_date = current_start_date + datetime.timedelta(days=int(period * 365.25))
        
        dashas.append({
            "planet": planet,
            "start": current_start_date.strftime("%Y-%m-%d"),
            "end": end_date.strftime("%Y-%m-%d"),
            "total_years": period,
            "is_balance": False
        })
        
        current_start_date = end_date
        lord_ptr = (lord_ptr + 1) % 9
        
    return dashas
