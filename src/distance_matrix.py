import pandas as pd
from geopy.distance import geodesic

def load_locations(file_path):
    """
    Load the delivery locations from csv file
    """
    df = pd.read_csv(file_path)
    return df

def compute_distance_matrix(df):
    """
    compute NxN distance matrix between delivery locations
    """

    locations = list(zip(df["latitude"],df["longitude"]))
    
    matrix = []

    for i in range(len(locations)):
        row = []
        for j in range(len(locations)):
            if i == j:
                row.append(0)
            else:
                distance = geodesic(locations[i],locations[j]).km
                row.append(round(distance,2))
        matrix.append(row)
    
    return matrix
