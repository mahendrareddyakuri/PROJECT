# zone_config.py
# Define restricted zones as polygons (x, y) pixel coordinates
# These coordinates should match your actual camera resolution

RESTRICTED_ZONES = [
    {
        "name": "Server Room",
        "polygon": [(100, 100), (300, 100), (300, 300), (100, 300)],
        "color": (0, 0, 255)  # Red in BGR
    },
    {
        "name": "Cash Register",
        "polygon": [(500, 200), (700, 200), (700, 400), (500, 400)],
        "color": (0, 0, 200)
    }
]

# Loitering threshold in seconds
LOITERING_THRESHOLD = 10  # Alert if person stays > 10 seconds in one area
