from src.distance_matrix import load_locations,compute_distance_matrix
from src.route_optimizer import solve_vrp
from src.utils import  calculate_route_distance,create_naive_route
from src.map_visualizer import create_route_map
from src.ml.train_model import train_model
from src.ml.predict_eta import load_model,predict_stop_eta
import random

# loding the training model
train_model("data/cleaned_delivery_dataset.csv")

#loading our model
eta_model , feature_columns = load_model()

#loading the dataset
data = load_locations("data/deliveries.csv")

# computing the distance matrix
distance_matrix = compute_distance_matrix(data)

# solving the vehicel routing problem
optimized_route = solve_vrp(distance_matrix)

# calulating the naive route
naive_route = create_naive_route(len(distance_matrix))

# finalizing the shortest distances between each points
optimized_distance = calculate_route_distance(optimized_route,distance_matrix)

naive_distance = calculate_route_distance(naive_route,distance_matrix)

savings = ((naive_distance-optimized_distance)/naive_distance)*100

# for predict_stop_eta
total_time = 0

print("\nETA Predictions:")

for stop in optimized_route[1:-1]:

    features = {
        "Delivery_person_Age": random.randint(20,40),
        "Delivery_person_Ratings": round(random.uniform(3.5,5),1),
        "Vehicle_condition": random.randint(1,5),
        "multiple_deliveries": random.randint(0,3),
        "distance_km": random.uniform(1,10),
        "order_hour": random.randint(8,22),
        "prep_time": random.randint(5,20)
    }

    eta = predict_stop_eta(eta_model,feature_columns, features)

    total_time += eta

    print(f"Stop {stop} → ETA {eta} minutes")

print("\nTotal Route Time:", round(total_time,2), "minutes")

print("\nNaive Route:", naive_route)
print("Naive Distance:", naive_distance, "km")

print("\nOptimized Route:", optimized_route)
print("Optimized Distance:", optimized_distance, "km")

print("\nDistance Savings:", round(savings, 2), "%")

create_route_map(data, optimized_route)