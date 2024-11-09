import numpy as np 

def get_locations_centroids(locations, key = 'coords'):
    # locs = []
    # for loc, loc_data in locations.items():
    #     coords = loc_data.get(key)
    #     locs.extend(coords)
    #return find_circumcenter(*locs)
    #

    lats = []
    longs = []
    for loc, loc_data in locations.items():
        coords = loc_data.get(key)
        lats.append(coords[0])
        longs.append(coords[1])
    return np.mean(lats), np.mean(longs)

def find_circumcenter(x1, y1, x2, y2, x3, y3):
    """
    Calculate the circumcenter of a triangle given by three points.

    Args:
        x1, y1: Coordinates of the first point.
        x2, y2: Coordinates of the second point.
        x3, y3: Coordinates of the third point.

    Returns:
        A tuple (U, V) representing the circumcenter coordinates.
        Returns None if the points are collinear.
    """
    # Calculate the determinant
    D = 2 * (x1*(y2 - y3) + x2*(y3 - y1) + x3*(y1 - y2))
    
    if D == 0:
        print("The three points are collinear; circumcircle is undefined.")
        return None
    
    # Calculate circumcenter coordinates
    U_numerator = ((x1**2 + y1**2)*(y2 - y3) +
                   (x2**2 + y2**2)*(y3 - y1) +
                   (x3**2 + y3**2)*(y1 - y2))
    V_numerator = ((x1**2 + y1**2)*(x3 - x2) +
                   (x2**2 + y2**2)*(x1 - x3) +
                   (x3**2 + y3**2)*(x2 - x1))
    
    U = U_numerator / D
    V = V_numerator / D
    
    return (U, V)

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