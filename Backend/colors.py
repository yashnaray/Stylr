COLOR_KEYWORDS = [
    'Navy Blue', 'Off White', 'Coffee Brown', 'Grey Melange',
    'Lime Green', 'Sea Green', 'Turquoise Blue', 'Mushroom Brown',
    'Fluorescent Green', 'Blue', 'Silver', 'Black', 'Grey', 'Green',
    'Purple', 'Beige', 'Brown', 'White', 'Bronze', 'Teal', 'Copper',
    'Pink', 'Maroon', 'Red', 'Khaki', 'Orange', 'Yellow', 'Gold',
    'Tan', 'Magenta', 'Lavender', 'Cream', 'Peach', 'Olive', 'Burgundy',
    'Rust', 'Rose', 'Mauve', 'Metallic', 'Mustard', 'Taupe', 'Nude',
    'Charcoal', 'Steel', 'Skin'
]

def extract_color_from_name(name):
    name_lower = name.lower()
    for color in COLOR_KEYWORDS:
        if color.lower() in name_lower:
            return color
    return ""
