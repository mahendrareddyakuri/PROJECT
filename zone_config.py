# zone_config.py
RESTRICTED_ZONES = [
    {
        "name": "Server Room",
        "polygon": [(100, 100), (300, 100), (300, 300), (100, 300)],
        "color": (0, 0, 255)
    },
    {
        "name": "Cash Register",
        "polygon": [(500, 200), (700, 200), (700, 400), (500, 400)],
        "color": (0, 0, 200)
    }
]

LOITERING_THRESHOLD = 10
