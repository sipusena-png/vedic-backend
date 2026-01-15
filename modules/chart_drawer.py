import svgwrite
import io

# Sign positions for South Indian Style Chart
SIGN_POSITIONS = {
    0: (100, 0),    # Aries (Top Row, 2nd Box)
    1: (200, 0),    # Taurus
    2: (300, 0),    # Gemini (Top Right)
    3: (300, 100),  # Cancer (Right Col, 2nd Box)
    4: (300, 200),  # Leo
    5: (300, 300),  # Virgo (Bottom Right)
    6: (200, 300),  # Libra
    7: (100, 300),  # Scorpio
    8: (0, 300),    # Sagittarius (Bottom Left)
    9: (0, 200),    # Capricorn
    10: (0, 100),   # Aquarius
    11: (0, 0)      # Pisces (Top Left)
}

def create_south_indian_chart(planets_data):
    """Generates a South Indian Style Chart as an SVG string."""
    dwg = svgwrite.Drawing(size=('400px', '400px'), profile='tiny')
    
    stroke_color = "black"
    box_size = 100
    width = 400
    height = 400

    # Draw Grid
    dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill='white', stroke=stroke_color, stroke_width=2))
    dwg.add(dwg.line(start=(0, box_size), end=(width, box_size), stroke=stroke_color))
    dwg.add(dwg.line(start=(0, height - box_size), end=(width, height - box_size), stroke=stroke_color))
    dwg.add(dwg.line(start=(box_size, 0), end=(box_size, height), stroke=stroke_color))
    dwg.add(dwg.line(start=(width - box_size, 0), end=(width - box_size, height), stroke=stroke_color))

    occupants = {i: 0 for i in range(12)}
    for planet_name, sign_index in planets_data.items():
        base_x, base_y = SIGN_POSITIONS[sign_index]
        count = occupants[sign_index]
        text_x = base_x + 10
        text_y = base_y + 25 + (count * 20)
        dwg.add(dwg.text(planet_name, insert=(text_x, text_y), fill='red', font_size='14px', font_family='Arial'))
        occupants[sign_index] += 1

    return dwg.tostring()

def create_north_indian_chart(house_data, sign_starting_h1):
    """Generates a North Indian Style Chart as an SVG string."""
    size = 400
    center = size / 2
    dwg = svgwrite.Drawing(size=(f'{size}px', f'{size}px'), profile='tiny')
    
    stroke = "black"
    stroke_width = 2

    # Draw the Grid (The "Diamond" Pattern)
    dwg.add(dwg.rect(insert=(0, 0), size=(size, size), fill='white', stroke=stroke, stroke_width=stroke_width))
    dwg.add(dwg.line(start=(0, 0), end=(size, size), stroke=stroke, stroke_width=stroke_width))
    dwg.add(dwg.line(start=(size, 0), end=(0, size), stroke=stroke, stroke_width=stroke_width))
    dwg.add(dwg.line(start=(center, 0), end=(0, center), stroke=stroke, stroke_width=stroke_width))
    dwg.add(dwg.line(start=(0, center), end=(center, size), stroke=stroke, stroke_width=stroke_width))
    dwg.add(dwg.line(start=(center, size), end=(size, center), stroke=stroke, stroke_width=stroke_width))
    dwg.add(dwg.line(start=(size, center), end=(center, 0), stroke=stroke, stroke_width=stroke_width))

    house_anchors = {
        1: (200, 70), 2: (70, 50), 3: (40, 140), 4: (70, 200),
        5: (40, 260), 6: (70, 350), 7: (200, 330), 8: (330, 350),
        9: (360, 260), 10: (330, 200), 11: (360, 140), 12: (330, 50),
    }

    # Place Sign Numbers
    current_sign = sign_starting_h1
    for house_num in range(1, 13):
        bx, by = house_anchors[house_num]
        sign_x, sign_y = bx - 20, by - 15 
        if house_num in [1, 7]: sign_x += 20; sign_y -= 10
        if house_num in [4, 10]: sign_x -= 25; sign_y += 15
        dwg.add(dwg.text(str(current_sign), insert=(sign_x, sign_y), fill='grey', font_size='10px', font_family='Arial', font_weight='bold'))
        current_sign = (current_sign % 12) + 1

    # Place Planets
    occupants = {i: 0 for i in range(1, 13)}
    for planet, house_num in house_data.items():
        base_x, base_y = house_anchors[house_num]
        count = occupants[house_num]
        text_x, text_y = base_x, base_y + (count * 15)
        txt = dwg.text(planet, insert=(text_x, text_y), fill='red', font_size='14px', font_family='Arial')
        txt['text-anchor'] = 'middle'
        dwg.add(txt)
        occupants[house_num] += 1

    return dwg.tostring()
