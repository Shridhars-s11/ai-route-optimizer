from fastapi import FastAPI
import pandas as pd
from pydantic import BaseModel
import random
from fastapi.responses import StreamingResponse
import io
from datetime import datetime
import os

from backend.schemas import RouteRequest
from database.db import engine, SessionLocal
from database.models import Base, Route ,Delivery, Order

from core.routing_services.road_distance_matrix import compute_osrm_distance_matrix
from core.optimization.multi_vehicle_optimizer import solve_multi_vehicle_vrp
from core.geocoding.geocoder import geocode_address
from core.ml.predict_eta import load_model, predict_stop_eta
from core.routing_services.osrm_route_geometry import get_osrm_route_geometry

Base.metadata.create_all(bind=engine)

# load ETA model once
eta_model, feature_columns = load_model()

app = FastAPI(title="AI Logistics Optimization API")


@app.get("/")
def home():
    return {"message": "AI Logistics API Running"}

@app.post("/add-order")
def add_order(order: dict):

    db = SessionLocal()

    # ✅ geocode address
    lat, lon = geocode_address(order["address"])

    new_order = Order(
        address=order.get("address"),
        latitude=float(lat),
        longitude=float(lon),
        package_weight=float(order.get("package_weight", 1.0)),
        priority=order.get("priority", "normal")
    )

    db.add(new_order)
    db.commit()
    db.close()

    return {"message": "Order added successfully"}


@app.post("/optimize-routes")
def optimize_routes(request: RouteRequest):

    print("🔥 optimize_routes API HIT")
    db = SessionLocal()

    df = pd.DataFrame([loc.model_dump() for loc in request.locations])
    vehicles = request.vehicles

    # geocode addresses if provided
    if "address" in df.columns:
        df = geocode_dataframe(df)

    # compute road distance matrix
    distance_matrix = compute_osrm_distance_matrix(df)

    # solve VRP
    routes = solve_multi_vehicle_vrp(distance_matrix, vehicles)
    print("ROUTES OUTPUT:", routes)
    results = []

    for vehicle_id, route in enumerate(routes):
        print("Processing route:", route)
        # if len(route) <= 2:
        #     continue

        route_coords = [
            (df.iloc[i]["latitude"], df.iloc[i]["longitude"])
            for i in route
        ]

        geometry = get_osrm_route_geometry(route_coords)

        vehicle_data = {
            "vehicle_id": vehicle_id + 1,
            "route": route,
            "stops": [],
            "geometry": geometry
        }

        total_time = 0

        # ✅ FIXED LOOP (only ONE loop)
        for order_idx, stop in enumerate(route[1:-1]):

            # get real distance from matrix
            prev_stop = route[order_idx]   # previous node
            curr_stop = stop               # current node

            distance_km = distance_matrix[prev_stop][curr_stop]

            features = {
                "Delivery_person_Age": 30,
                "Delivery_person_Ratings": 4.5,
                "Vehicle_condition": 3,
                "multiple_deliveries": order_idx,
                "distance_km": distance_km,
                "order_hour": datetime.now().hour,
                "prep_time": 10
            }

            eta = predict_stop_eta(eta_model, feature_columns, features)

            total_time += eta

            lat = float(df.iloc[stop]["latitude"])
            lon = float(df.iloc[stop]["longitude"])
            address = (
                        str(df.iloc[stop]["address"])
                        if "address" in df.columns
                        else f"{lat}, {lon}"
                    )

            # ✅ STORE DELIVERY
            delivery = Delivery(
                    latitude=float(lat),
                    longitude=float(lon),
                    address=str(address),
                    vehicle_id=int(vehicle_id + 1),
                    stop_order=int(order_idx),
                    eta_minutes=float(round(total_time, 2))
                )

            db.add(delivery)

            vehicle_data["stops"].append({
                "stop_id": stop,
                "eta_minutes": float(round(total_time, 2)),
                "status": "pending"
            })
            

        vehicle_data["total_route_time"] = round(total_time, 2)

        # store route
        route_record = Route(
            vehicle_id=vehicle_id + 1,
            stop_sequence=str(route),
            total_time=float(total_time)
        )

        db.add(route_record)
        
        results.append(vehicle_data)

    # ✅ SINGLE COMMIT (VERY IMPORTANT)
    print("COMMITTING TO DB")
    db.commit()
    db.close()

    return {"fleet_routes": results}


@app.get("/routes")
def get_routes():

    db = SessionLocal()

    routes = db.query(Route).all()

    results = []

    for r in routes:
        results.append({
            "id": r.id,
            "vehicle_id": r.vehicle_id,
            "stop_sequence": r.stop_sequence,
            "total_time": r.total_time
        })

    db.close()

    return {"routes": results}

def generate_routes_csv_from_db(db):

    deliveries = db.query(Delivery).all()

    rows = []

    for d in deliveries:
        rows.append({
            "vehicle_id": d.vehicle_id,
            "stop_order": d.stop_order,
            "latitude": d.latitude,
            "longitude": d.longitude,
            "address": d.address,
            "eta_minutes": d.eta_minutes
        })

    df = pd.DataFrame(rows)

    stream = io.StringIO()
    df.to_csv(stream, index=False)
    stream.seek(0)

    return stream

@app.get("/download-routes")
def download_routes():

    db = SessionLocal()

    csv_stream = generate_routes_csv_from_db(db)

    db.close()

    return StreamingResponse(
        csv_stream,
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=optimized_routes.csv"
        }
    )