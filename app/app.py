import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import streamlit as st
import pandas as pd

from src.distance_matrix import compute_distance_matrix
from src.route_optimizer import solve_vrp
from src.utils import calculate_route_distance, create_naive_route
from src.map_visualizer import create_route_map
from src.ml.predict_eta import load_model, predict_stop_eta


st.title("🚚 AI Route Optimization System")

st.write("Optimize delivery routes and predict ETA using AI.")


# -------------------------
# DATA INPUT
# -------------------------

st.sidebar.header("Data Input")



# -------------------------
# LOAD DATA
# -------------------------
uploaded_file = st.sidebar.file_uploader(
    "Upload Delivery Dataset (CSV)",
    type=["csv"]
)

if uploaded_file is None:
    st.warning("Please upload a delivery dataset to continue.")
    st.stop()

data = pd.read_csv(uploaded_file)

st.write("### Delivery Locations")
st.dataframe(data)


required_cols = ["latitude", "longitude"]

for col in required_cols:
    if col not in data.columns:
        st.error(f"Dataset must contain column: {col}")
        st.stop()


# -------------------------
# ROUTE OPTIMIZATION
# -------------------------

distance_matrix = compute_distance_matrix(data)

optimized_route = solve_vrp(distance_matrix)

naive_route = create_naive_route(len(distance_matrix))

optimized_distance = calculate_route_distance(optimized_route, distance_matrix)

naive_distance = calculate_route_distance(naive_route, distance_matrix)

savings = ((naive_distance - optimized_distance) / naive_distance) * 100


# -------------------------
# ETA PREDICTION
# -------------------------

model, feature_columns = load_model()

eta_results = []

total_time = 0

import random

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

    eta = predict_stop_eta(model, feature_columns, features)

    total_time += eta

    eta_results.append((stop, eta))

st.write("## Delivery Timeline")

current_time = 0

for stop, eta in eta_results:

    current_time += eta

    st.write(f"Stop {stop} → ETA {eta} min | Arrival Time: {round(current_time,2)} min")

st.write("## AI Delivery Insights")

etas = [eta for _, eta in eta_results]

avg_time = sum(etas) / len(etas)

max_stop = max(eta_results, key=lambda x: x[1])

fuel_cost_per_km = 10  # estimated

fuel_savings = (naive_distance - optimized_distance) * fuel_cost_per_km


st.write(f"Most Time-Consuming Stop: Stop {max_stop[0]} ({round(max_stop[1],2)} min)")

st.write(f"Average Delivery Time per Stop: {round(avg_time,2)} minutes")

st.write(f"Estimated Fuel Cost Savings: ₹{round(fuel_savings,2)}")


# -------------------------
# RESULTS
# -------------------------

st.write("## Optimized Route")

st.write(optimized_route)

route_text = " → ".join(
    ["Warehouse" if stop == 0 else f"Delivery {stop}" for stop in optimized_route]
)

st.write(route_text)


st.write("## Distance Comparison")

st.write(f"Naive Distance: {naive_distance} km")
st.write(f"Optimized Distance: {optimized_distance} km")
st.write(f"Distance Savings: {round(savings,2)} %")


st.write("## ETA Predictions")

for stop, eta in eta_results:

    st.write(f"Stop {stop} → {eta} minutes")


st.write("### Total Route Time")

st.success(f"{round(total_time,2)} minutes")


# -------------------------
# MAP
# -------------------------

create_route_map(data, optimized_route)

st.write("### Route Map")

st.components.v1.html(open("optimized_route.html",'r').read(), height=500)

st.write("## Route Analytics")

col1, col2, col3 = st.columns(3)

col1.metric("Naive Distance", f"{naive_distance} km")
col2.metric("Optimized Distance", f"{optimized_distance} km")
col3.metric("Savings", f"{round(savings,2)} %")