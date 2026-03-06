from src.distance_matrix import load_locations,compute_distance_matrix
from src.route_optimizer import solve_vrp
from src.utils import  calculate_route_distance,create_naive_route

data = load_locations("data/deliveries.csv")

distance_matrix = compute_distance_matrix(data)

optimized_route = solve_vrp(distance_matrix)

naive_route = create_naive_route(len(distance_matrix))

optimized_distance = calculate_route_distance(optimized_route,distance_matrix)

naive_distance = calculate_route_distance(naive_route,distance_matrix)

savings = ((naive_distance-optimized_distance)/naive_distance)*100

print("\nNaive Route:", naive_route)
print("Naive Distance:", naive_distance, "km")

print("\nOptimized Route:", optimized_route)
print("Optimized Distance:", optimized_distance, "km")

print("\nDistance Savings:", round(savings, 2), "%")