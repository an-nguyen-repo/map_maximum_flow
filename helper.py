import numpy as np


def get_locations_centroids(locations, key="coords"):
    lats = []
    longs = []
    for _, loc_data in locations.items():
        coords = loc_data.get(key)
        lats.append(coords[0])
        longs.append(coords[1])
    return np.mean(lats), np.mean(longs)
