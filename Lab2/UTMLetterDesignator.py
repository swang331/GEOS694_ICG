def get_range_string_dict(lat):
    lat_ranges = {
        range(72, 84): "X",
        range(64, 71): "W",
        range(56, 63): "V", 
        range(48, 55): "U", 
        range(40, 47): "T",
        range(32, 39): "S",
        range(24, 31): "R", 
        range(16, 23): "Q", 
        range(8, 17): "P", 
        range(0, 7): "N", 
        range(-8, -1): "M", 
        range(-16, -9): "L", 
        range(-24, -17): "K", 
        range(-32, -25): "J", 
        range(-40, -33): "H", 
        range(-48, -41): "G", 
        range(-56, -49): "F", 
        range(-64, -57): "E", 
        range(-72, -65): "D", 
        range(-80, -73): "C"
    }

    for lat_range, UTM_letter in lat_ranges.items():
        if lat in lat_range:
            return UTM_letter
    return "Out of range"

print(get_range_string_dict(6))