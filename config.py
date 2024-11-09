import numpy as np 

def get_locations_centroids(locations, key = 'coords'):
    lats = []
    longs = []
    for k, v in locations.items():
        lats.append(v[key][0])
        longs.append(v[key][1])
    return (np.mean(lats), np.mean(longs))

KEY_LOCATIONS = {
    'hang_xanh': {
        'name': 'Hang Xanh Intersection',
        'coords': (10.801184600518491, 106.7112997434957)
    },
    'tan_son_nhat': {
        'name': 'Tan Son Nhat International Airport',
        'coords': (10.8125471,106.66566368265137),
    },
    'bay_hien': {
        'name': 'Bay Hien Intersection',
        'coords': (10.7928977, 106.653385)
    },
}

LOCATION_CENTROID = get_locations_centroids(KEY_LOCATIONS)