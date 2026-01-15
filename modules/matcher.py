import json
import os

# Load Nakshatra properties
data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'nakshatras.json')
with open(data_path, 'r') as f:
    NAKSHATRA_DATA = json.load(f)

def calculate_nakshatra_index(longitude):
    """Step A: Convert Longitude (0-360°) to Nakshatra Index (0-26)."""
    # Formula: Index = int(Longitude / 13.333...)
    return int((longitude % 360) / (360/27))

def guna_milan(boy_moon_lon, girl_moon_lon):
    """
    Ashta Koota (36 Points) Matching Logic.
    """
    b_idx = str(calculate_nakshatra_index(boy_moon_lon))
    g_idx = str(calculate_nakshatra_index(girl_moon_lon))
    
    b_props = NAKSHATRA_DATA[b_idx]
    g_props = NAKSHATRA_DATA[g_idx]
    
    score = 0.0
    details = {}

    # 1. Varna (1 pt)
    varna_weights = {"Brahmin": 4, "Kshatriya": 3, "Vaishya": 2, "Shudra": 1}
    if varna_weights[b_props['varna']] >= varna_weights[g_props['varna']]:
        curr = 1
    else:
        curr = 0
    score += curr
    details['Varna'] = curr

    # 2. Vashya (2 pts)
    if b_props['vashya'] == g_props['vashya']:
        curr = 2
    else:
        # Simplified: mid score for partially compatible vashyas can be added here
        curr = 0
    score += curr
    details['Vashya'] = curr

    # 3. Tara (3 pts)
    # Distance between Nakshatras mod 9
    dist = (int(g_idx) - int(b_idx) + 27) % 27
    if (dist % 9) in [0, 1, 2, 4, 6, 8]: # Simplified auspicious Tara counts
        curr = 3.0
    else:
        curr = 1.5 # Neutral
    score += curr
    details['Tara'] = curr

    # 4. Yoni (4 pts)
    yoni_compatibility = {
        # Simplified: 4 for same, 0 for enemy animals
        b_props['yoni']: {g_props['yoni']: 4 if b_props['yoni'] == g_props['yoni'] else 2}
    }
    # For a full implementation, a matrix of animal compatibility is required.
    # Placeholder Logic:
    if b_props['yoni'] == g_props['yoni']:
        curr = 4
    else:
        curr = 2
    score += curr
    details['Yoni'] = curr

    # 5. Maitri (5 pts - Planetary Friendship)
    if b_props['lord'] == g_props['lord']:
        curr = 5
    else:
        curr = 3 # Placeholder for friend/neutral/enemy matrix
    score += curr
    details['Maitri'] = curr

    # 6. Gana (6 pts)
    if b_props['gana'] == g_props['gana']:
        curr = 6
    elif (b_props['gana'] == "Deva" and g_props['gana'] == "Manushya") or (b_props['gana'] == "Manushya" and g_props['gana'] == "Deva"):
        curr = 5
    else:
        curr = 0
    score += curr
    details['Gana'] = curr

    # 7. Bhakoot (7 pts)
    # Moon Sign distance
    b_sign = int(boy_moon_lon / 30)
    g_sign = int(girl_moon_lon / 30)
    sign_dist = (g_sign - b_sign + 12) % 12 + 1
    
    # 2/12, 5/9, 6/8 are problematic sign relationships
    if sign_dist in [2, 12, 6, 8]:
        # Bhakoot Dosha Cancellation: If Rashi Lords are friends or same
        # Simplified Check for cancellation
        lords = {0: "Mars", 1: "Ven", 2: "Merc", 3: "Moon", 4: "Sun", 5: "Merc", 6: "Ven", 7: "Mars", 8: "Jup", 9: "Sat", 10: "Sat", 11: "Jup"}
        if lords[b_sign] == lords[g_sign]:
            curr = 7 # Cancellation!
        else:
            curr = 0
    else:
        curr = 7
    score += curr
    details['Bhakoot'] = curr

    # 8. Nadi (8 pts)
    if b_props['nadi'] == g_props['nadi']:
        # Nadi Dosha Exceptions:
        # Same Rashi but different Nakshatras, or Same Nakshatra but different Rashis
        if b_sign == g_sign and b_idx != g_idx:
            curr = 8 # Cancellation!
        elif b_idx == g_idx and b_sign != g_sign:
            curr = 8 # Cancellation!
        else:
            curr = 0 # Dosha!
    else:
        curr = 8
    score += curr
    details['Nadi'] = curr

    return {
        "total_score": score,
        "max_score": 36,
        "verdict": "Compatible" if score >= 18 else "Not Compatible (Dosha)",
        "details": details,
        "boy": {"nakshatra": b_props['name'], "sign": b_sign + 1},
        "girl": {"nakshatra": g_props['name'], "sign": g_sign + 1}
    }
