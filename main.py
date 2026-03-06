from src.distance_matrix import load_locations,compute_distance_matrix
from src.route_optimizer import solve_vrp

data = load_locations("data/deliveries.csv")

distance_matrix = compute_distance_matrix(data)

route = solve_vrp(distance_matrix)

print(f"Optimized Route order is: {route}")