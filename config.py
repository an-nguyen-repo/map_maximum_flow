from helper import get_locations_centroids

# app configurations
KEY_LOCATIONS = {
    "hang_xanh": {
        "name": "Hang Xanh Intersection",
        "coords": (10.801184600518491, 106.7112997434957),
    },
    "tan_son_nhat": {
        "name": "Tan Son Nhat International Airport",
        "coords": (10.8125471, 106.66566368265137),
    },
    "bay_hien": {
        "name": "Bay Hien Intersection",
        "coords": (10.7928977, 106.653385),
    },
}

LOCATION_CENTROID = get_locations_centroids(KEY_LOCATIONS)
MAP_RADIUS = 4500

# ui configurations
INACTIVE_COLOR = "#A9A9A9"
ACTIVE_COLOR = "#FF5733"
