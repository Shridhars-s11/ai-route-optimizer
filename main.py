from src.distance_matrix import load_locations,compute_distance_matrix

data = load_locations("data/deliveries.csv")

matrix = compute_distance_matrix(data)

print("Distance Matrix:")
for row in matrix:
    print(row) 