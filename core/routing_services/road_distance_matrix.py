import requests


def compute_osrm_distance_matrix(df):

    locations = list(zip(df["longitude"], df["latitude"]))

    # format coordinates for OSRM
    coords = ";".join([f"{lon},{lat}" for lon, lat in locations])

    url = f"http://router.project-osrm.org/table/v1/driving/{coords}?annotations=distance"

    response = requests.get(url)

    if response.status_code != 200:
        raise Exception("OSRM request failed")

    data = response.json()

    distances = data["distances"]

    matrix = []

    for row in distances:
        matrix.append([round(d / 1000, 2) for d in row])  # meters → km

    return matrix