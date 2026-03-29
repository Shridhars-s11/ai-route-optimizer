from core.routing_services.road_distance_matrix import compute_osrm_distance_matrix
from core.optimization.distance_matrix import load_locations
from core.optimization.multi_vehicle_optimizer import solve_multi_vehicle_vrp
from core.utils import calculate_route_distance, create_naive_route
from visualization.map_visualizer import create_route_map
from core.ml.train_eta_model import train_model
from core.ml.predict_eta import load_model, predict_stop_eta
from core.geocoding.geocoder import geocode_dataframe

import random


# Train model
train_model("data/cleaned_delivery_dataset.csv")

# Load model
eta_model, feature_columns = load_model()

# Load delivery dataset
data = load_locations("data/delivery_test_dataset.csv")

# convert addresses to coordinates
if "address" in data.columns:
    data = geocode_dataframe(data)

# Compute distance matrix
distance_matrix = compute_osrm_distance_matrix(data)

# Solve VRP with multiple vehicles
optimized_routes = solve_multi_vehicle_vrp(distance_matrix, num_vehicles=3)

# Naive route (still single just for comparison)
naive_route = create_naive_route(len(distance_matrix))
naive_distance = calculate_route_distance(naive_route, distance_matrix)

print("\nNaive Route:", naive_route)
print("Naive Distance:", naive_distance, "km")


print("\nOptimized Fleet Routes")

if optimized_routes is None:
    print("No feasible route found")
else:
    total_fleet_distance = 0
    for i, route in enumerate(optimized_routes):

        if len(route) <= 2:
            continue

        optimized_distance = calculate_route_distance(route, distance_matrix)
        total_fleet_distance += optimized_distance

        print(f"\nVehicle {i+1} Route:", route)
        print("Route Distance:", optimized_distance, "km")

        total_time = 0

        print("\nETA Predictions:")

        for stop in route[1:-1]:

            features = {
                "Delivery_person_Age": random.randint(20, 40),
                "Delivery_person_Ratings": round(random.uniform(3.5, 5), 1),
                "Vehicle_condition": random.randint(1, 5),
                "multiple_deliveries": random.randint(0, 3),
                "distance_km": random.uniform(1, 10),
                "order_hour": random.randint(8, 22),
                "prep_time": random.randint(5, 20)
            }

            eta = predict_stop_eta(eta_model, feature_columns, features)

            total_time += eta

            print(f"Stop {stop} → ETA {round(eta,2)} minutes")

        print("Total Route Time:", round(total_time, 2), "minutes")

        # Temporary map generation per vehicle
        create_route_map(data, optimized_routes)
    print("\nTotal Fleet Distance:", round(total_fleet_distance,2), "km")