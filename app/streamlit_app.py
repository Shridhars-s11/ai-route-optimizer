# import sys
# import os
# import requests
# import streamlit as st
# import pandas as pd
# import matplotlib.pyplot as plt
# import time
# import folium
# import streamlit.components.v1 as components

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# from visualization.map_visualizer import create_route_map
# from core.geocoding.geocoder import geocode_dataframe, geocode_address

# st.title("🚚 AI Route Optimization System")
# st.write("Optimize delivery routes and predict ETA using AI.")
# st.markdown(
#     """
#     <div style="
#         background-color:#2c3e50;
#         padding:18px;
#         border-radius:12px;
#         color:white;
#         font-size:18px;
#         text-align:center;
#     ">
#         📂 Please upload your delivery dataset to begin route optimization
#     </div>
#     """,
#     unsafe_allow_html=True
# )

# # ---------------------------
# # INPUT
# # ---------------------------

# st.sidebar.header("Data Input")

# input_mode = st.sidebar.radio(
#     "Input Method",
#     ["Upload CSV", "Enter Addresses"]
# )

# data = None

# # -------- ADDRESS INPUT --------

# if input_mode == "Enter Addresses":

#     warehouse = st.sidebar.text_input("Warehouse Address")
#     stops = st.sidebar.text_area("Delivery Stops (one per line)")

#     if st.sidebar.button("Prepare Data"):

#         stop_list = [s.strip() for s in stops.split("\n") if s.strip() != ""]
#         addresses = [warehouse] + stop_list

#         coords = []
#         for addr in addresses:
#             lat, lon = geocode_address(addr)
#             coords.append({"latitude": lat, "longitude": lon})

#         data = pd.DataFrame(coords)

# # -------- CSV INPUT --------

# elif input_mode == "Upload CSV":

#     uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])

#     if uploaded_file:
#         data = pd.read_csv(uploaded_file)

# # ---------------------------
# # VEHICLES
# # ---------------------------

# num_vehicles = st.sidebar.slider("Vehicles", 1, 10, 3)

# # ---------------------------
# # DATA CHECK
# # ---------------------------

# if data is None:
#     st.stop()

# if "latitude" not in data.columns or "longitude" not in data.columns:

#     if "address" in data.columns:
#         st.info("Geocoding...")
#         data = geocode_dataframe(data)
#     else:
#         st.error("Need lat/lon or address column")
#         st.stop()

# st.write("### Locations")
# st.dataframe(data)

# # ---------------------------
# # 🚀 CALL BACKEND
# # ---------------------------

# if st.button("🚀 Optimize Routes"):

#     try:
#         payload = {
#             "vehicles": int(num_vehicles),
#             "locations": data.to_dict(orient="records")
#         }

#         response = requests.post(
#             "http://127.0.0.1:8000/optimize-routes",
#             json=payload,
#             timeout=30
#         )

#         if response.status_code == 200:

#             result = response.json()

#             # ✅ STORE IN SESSION
#             st.session_state["result"] = result
#             st.session_state["data"] = data

#             st.success("✅ Optimization Completed Successfully!")

#         else:
#             st.error(f"❌ API Failed: {response.status_code}")

#     except requests.exceptions.ConnectionError:
#         st.error("🚨 Backend not running. Start FastAPI server.")

#     except requests.exceptions.Timeout:
#         st.error("⏳ Request timed out. Try again.")

#     except Exception as e:
#         st.error(f"Unexpected Error: {str(e)}")


# # ---------------------------
# # 📊 DISPLAY RESULTS (PERSIST)
# # ---------------------------

# if "result" in st.session_state:

#     result = st.session_state["result"]
#     data = st.session_state["data"]

#     fleet_routes = result.get("fleet_routes", [])

#     if not fleet_routes:
#         st.warning("⚠️ No routes generated.")
#     else:
#         # ---------------------------
#         # 📊 KPI DASHBOARD
#         # ---------------------------

#         st.write("## 📊 Logistics Dashboard")

#         total_vehicles = len(fleet_routes)

#         total_deliveries = sum(len(v["stops"]) for v in fleet_routes)

#         avg_eta = round(
#             sum(
#                 stop["eta_minutes"]
#                 for v in fleet_routes
#                 for stop in v["stops"]
#             ) / max(total_deliveries, 1),
#             2
#         )

#         col1, col2, col3 = st.columns(3)

#         col1.metric("🚚 Vehicles", total_vehicles)
#         col2.metric("📦 Deliveries", total_deliveries)
#         col3.metric("⏱ Avg ETA", f"{avg_eta} min")

#         st.write("## 🚚 Optimized Routes")

#         for vehicle in fleet_routes:

#             route_text = " → ".join(
#                 [f"Stop {s['stop_id']}" for s in vehicle["stops"]]
#             )

#             st.write(f"**Vehicle {vehicle['vehicle_id']}**: {route_text}")
#             st.write(f"⏱ Total Time: {vehicle['total_route_time']} min")

#         # ---------------------------
#         # 🗺 MAP
#         # ---------------------------

#         st.write("## 🗺 Route Map")

#         try:
#             routes_only = [v["route"] for v in fleet_routes]

#             create_route_map(data, routes_only)

#             st.components.v1.html(
#                 open("optimized_routes.html", "r").read(),
#                 height=500
#             )

#         except Exception as e:
#             st.error(f"Map rendering failed: {str(e)}")

#         # ---------------------------
#         # 📦 DELIVERY STATUS (INITIAL)
#         # ---------------------------

#         st.write("## 📦 Delivery Status")

#         status_placeholder = st.empty()
#         chart_placeholder = st.empty()

#         progress_data = []

#         status_data = []

#         for vehicle in fleet_routes:
#             for stop in vehicle["stops"]:
#                 status_data.append({
#                     "Vehicle": vehicle["vehicle_id"],
#                     "Stop": stop["stop_id"],
#                     "ETA": stop["eta_minutes"],
#                     "Status": "🟡 Pending"
#                 })

#         status_df = pd.DataFrame(status_data)
#         status_placeholder.dataframe(status_df)

#         # ---------------------------
#         # 🚚 LIVE SIMULATION
#         # ---------------------------

#         st.write("## 🚚 Live Vehicle Simulation")

#         fig, ax = plt.subplots()
#         line, = ax.plot([], [])
#         ax.set_title("Deliveries Completed Over Time")
#         ax.set_xlabel("Time Step")
#         ax.set_ylabel("Delivered Count")

#         if st.button("▶️ Start Simulation"):

#             map_placeholder = st.empty()

#             # ✅ Prepare all vehicle paths
#             vehicle_paths = []

#             for vehicle in fleet_routes:

#                 geometry = vehicle.get("geometry") or []

#                 geometry = [
#                     point for point in geometry
#                     if point and len(point) == 2 and None not in point
#                 ]

#                 if len(geometry) >= 2:
#                     vehicle_paths.append({
#                         "vehicle_id": vehicle["vehicle_id"],
#                         "geometry": geometry,
#                         "current_index": 0
#                     })

#             # ✅ Find max steps
#             max_steps = max(len(v["geometry"]) for v in vehicle_paths)

#             def interpolate_points(p1, p2, steps=10):
#                 lat1, lon1 = p1
#                 lat2, lon2 = p2

#                 points = []
#                 for i in range(steps):
#                     lat = lat1 + (lat2 - lat1) * (i / steps)
#                     lon = lon1 + (lon2 - lon1) * (i / steps)
#                     points.append((lat, lon))

#                 return points
            
#             for v in fleet_routes:
#                 for stop in v["stops"]:
#                     stop["status"] = "pending"

#             # 🚀 SIMULATION LOOP (ALL VEHICLES MOVE TOGETHER)
#             for step in range(max_steps):


#                 try:
#                     m = folium.Map(location=vehicle_paths[0]["geometry"][min(step, len(vehicle_paths[0]["geometry"]) - 1)], zoom_start=13)

#                     # ---------------- DRAW ALL VEHICLES ----------------
#                     for v in vehicle_paths:

#                         geom = v["geometry"]

#                         if step < len(geom):

#                             path = []

#                             # 🔥 SMOOTH INTERPOLATION
#                             for i in range(max(1, min(step, len(geom) - 1))):
#                                 segment = interpolate_points(geom[i], geom[i+1], steps=5)
#                                 path.extend(segment)
                            
#                             if not path:
#                                 continue

#                             # route line
#                             folium.PolyLine(geom).add_to(m)  # full route (static)

#                             # moving marker
#                             folium.Marker(
#                                 path[-1],
#                                 tooltip=f"Vehicle {v['vehicle_id']}"
#                             ).add_to(m)

#                     m.save("simulation_map.html")

#                     with map_placeholder:
#                         with open("simulation_map.html", "r") as f:
#                             html_data = f.read()

#                         components.html(html_data, height=400)

#                     # ---------------- STATUS UPDATE ----------------
#                     for v in vehicle_paths:

#                         vehicle_id = v["vehicle_id"]
#                         current_step = step

#                         for vehicle in fleet_routes:
#                             if vehicle["vehicle_id"] == vehicle_id:

#                                 stops = vehicle["stops"]

#                                 if current_step < len(stops) and step % 2 == 0:
#                                     if stops[current_step]["status"] == "pending":
#                                         stops[current_step]["status"] = "delivered"

#                     # rebuild status table
#                     status_data = []

#                     for v in fleet_routes:
#                         for stop in v["stops"]:
#                             status_icon = "🟡 Pending"
#                             if stop["status"] == "delivered":
#                                 status_icon = "✅ Delivered"

#                             status_data.append({
#                                 "Vehicle": v["vehicle_id"],
#                                 "Stop": stop["stop_id"],
#                                 "ETA": stop["eta_minutes"],
#                                 "Status": status_icon
#                             })

#                     status_df = pd.DataFrame(status_data)
#                     status_placeholder.dataframe(status_df)

#                     # ---------------- CHART UPDATE ----------------
#                     delivered_count = sum(
#                         1 for v in fleet_routes
#                         for stop in v["stops"]
#                         if stop["status"] == "delivered"
#                     )

#                     progress_data.append(delivered_count)

#                     line.set_xdata(range(len(progress_data)))
#                     line.set_ydata(progress_data)

#                     ax.relim()
#                     ax.autoscale_view()

#                     chart_placeholder.pyplot(fig)


#                     # 🔥 LIVE KPI UPDATE

#                     delivered_count = sum(
#                         1 for v in fleet_routes
#                         for stop in v["stops"]
#                         if stop["status"] == "delivered"
#                     )

#                     kpi_placeholder = st.empty()
#                     kpi_placeholder.info(f"✅ Delivered: {delivered_count} / {total_deliveries}")

#                     time.sleep(0.8)

#                     delivered_count = sum(
#                         1 for v in fleet_routes
#                         for stop in v["stops"]
#                         if stop["status"] == "delivered"
#                     )

#                     if delivered_count == total_deliveries:
#                         st.success("🎉 All deliveries completed!")
#                         break

#                 except Exception as e:
#                     st.error(f"Simulation error: {str(e)}")
#                     break

import sys
import os
import requests
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import time
import folium
import streamlit.components.v1 as components

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from visualization.map_visualizer import create_route_map
from core.geocoding.geocoder import geocode_address

st.title("🚚 AI Route Optimization System")
st.write("Optimize delivery routes and predict ETA using AI.")

# ---------------------------
# 📦 ADD ORDER
# ---------------------------

st.write("## 📦 Add New Order")

with st.form("order_form"):

    address = st.text_input("Address")
    weight = st.number_input("Package Weight", value=1.0)
    priority = st.selectbox("Priority", ["low", "normal", "high"])

    submit = st.form_submit_button("Add Order")

    if submit:
        try:
            # convert address → coordinates
            latitude, longitude = geocode_address(address)

            payload = {
                "address": address,
                "latitude": latitude,
                "longitude": longitude,
                "package_weight": weight,
                "priority": priority
            }

            res = requests.post(
                "https://ai-logistics-backend.onrender.com/add-order",
                json=payload
            )

            if res.status_code == 200:
                st.success("✅ Order Added Successfully")
            else:
                st.error("❌ Failed to add order")

        except Exception as e:
            st.error(f"Error: {str(e)}")    

st.markdown("""
<div style="background-color:#2c3e50;padding:18px;border-radius:12px;color:white;text-align:center;">
📂 Please upload your delivery dataset or manually enter the addresses of the locations to begin route optimization
</div>
""", unsafe_allow_html=True)

# ---------------- INPUT ----------------
st.sidebar.header("Data Input")

# ---------------------------
# 📂 DATA INPUT (NEW)
# ---------------------------

st.sidebar.header("Data Input")

input_mode = st.sidebar.radio(
    "Choose Input Type",
    ["Upload Dataset", "Enter Addresses"]
)

data = None

# -------- OPTION 1: UPLOAD --------

if input_mode == "Upload Dataset":

    uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])

    if uploaded_file:
        data = pd.read_csv(uploaded_file)

        # handle address OR coordinates
        if "address" in data.columns:
            st.info("Geocoding addresses...")

            coords = []
            for addr in data["address"]:
                lat, lon = geocode_address(addr)
                coords.append((lat, lon))

            data["latitude"] = [c[0] for c in coords]
            data["longitude"] = [c[1] for c in coords]

# -------- OPTION 2: ENTER ADDRESSES --------

elif input_mode == "Enter Addresses":

    warehouse = st.sidebar.text_input("Warehouse Address")
    stops = st.sidebar.text_area("Delivery Stops (one per line)")

    if st.sidebar.button("Generate Data"):

        if not warehouse:
            st.error("❌ Warehouse address is required")
            st.stop()

        stop_list = [s.strip() for s in stops.split("\n") if s.strip()]

        if len(stop_list) == 0:
            st.error("❌ Enter at least one delivery stop")
            st.stop()

        all_addresses = [warehouse] + stop_list

        coords = []
        failed = []

        with st.spinner("🌍 Geocoding addresses..."):

            for addr in all_addresses:

                lat, lon = geocode_address(addr)

                if lat is None or lon is None:
                    failed.append(addr)
                else:
                    coords.append({
                        "address": addr,
                        "latitude": float(lat),
                        "longitude": float(lon)
                    })

        # 🚨 Handle failures
        if failed:
            st.warning("⚠️ Some addresses could not be located:")
            for f in failed:
                st.write(f"❌ {f}")

        if len(coords) < 2:
            st.error("❌ Need at least 2 valid locations")
            st.stop()

        data = pd.DataFrame(coords)

        st.success(f"✅ {len(coords)} locations ready for optimization")

num_vehicles = st.sidebar.slider("Vehicles", 1, 10, 3)

if data is None:
    st.stop()

st.write("### Locations")
st.dataframe(data)
st.map(data[["latitude", "longitude"]])

# ---------------- API CALL ----------------
if st.button("🚀 Optimize Routes"):
    payload = {"vehicles": int(num_vehicles), "locations": data.to_dict("records")}

    response = requests.post("https://ai-logistics-backend.onrender.com/optimize-routes", json=payload)

    if response.status_code == 200:
        st.session_state["result"] = response.json()
        st.session_state["data"] = data
        st.success("✅ Optimization Completed!")
    else:
        st.error("❌ API failed")

# ---------------- RESULTS ----------------
if "result" in st.session_state:

    result = st.session_state["result"]
    data = st.session_state["data"]
    fleet_routes = result.get("fleet_routes", [])
    # ---------------------------
    # 🗺 SHOW OPTIMIZED ROUTES MAP
    # ---------------------------

    st.write("## 🗺 Optimized Routes Map")

    try:
        routes_only = [v["route"] for v in fleet_routes]

        create_route_map(data, routes_only)

        with open("optimized_routes.html", "r", encoding="utf-8") as f:
            html_data = f.read()

        st.components.v1.html(html_data, height=500)

        st.success("🗺 Routes visualized successfully!")

    except FileNotFoundError:
        st.error("❌ Map file not found")

    except Exception as e:
        st.error(f"❌ Map rendering failed: {str(e)}")

    st.write("## 📦 Delivery Status")

    status_placeholder = st.empty()
    chart_placeholder = st.empty()

    progress_data = []

    # initialize statuses
    for v in fleet_routes:
        for stop in v["stops"]:
            stop["status"] = "pending"

    def build_status():
        rows = []
        for v in fleet_routes:
            for stop in v["stops"]:
                rows.append({
                    "Vehicle": v["vehicle_id"],
                    "Stop": stop["stop_id"],
                    "ETA": stop["eta_minutes"],
                    "Status": "✅ Delivered" if stop["status"] == "delivered" else "🟡 Pending"
                })
        return pd.DataFrame(rows)

    status_placeholder.dataframe(build_status())

    st.write("## 🚚 Live Simulation")

    fig, ax = plt.subplots()
    line, = ax.plot([], [])
    ax.set_title("Deliveries Completed Over Time")

    if st.button("▶️ Start Simulation"):

        if not fleet_routes:
            st.error("❌ No routes available for simulation")
            st.stop()

        map_placeholder = st.empty()

        vehicle_paths = []

        for v in fleet_routes:
            geom = v.get("geometry") or []

            # 🛡 clean invalid points
            geom = [
                point for point in geom
                if point and len(point) == 2 and None not in point
            ]

            if len(geom) >= 2:
                vehicle_paths.append({
                    "vehicle_id": v["vehicle_id"],
                    "geometry": geom
                })

        if not vehicle_paths:
            st.error("❌ No valid vehicle paths found")
            st.stop()

        max_steps = max(len(v["geometry"]) for v in vehicle_paths)

        for step in range(max_steps):

            try:
                base = vehicle_paths[0]["geometry"]
                m = folium.Map(location=base[min(step, len(base)-1)], zoom_start=13)

                for v in vehicle_paths:
                    geom = v["geometry"]

                    if step >= len(geom):
                        continue

                    current_position = geom[step]

                    # full route
                    folium.PolyLine(geom).add_to(m)

                    # moving vehicle
                    folium.Marker(
                        current_position,
                        tooltip=f"Vehicle {v['vehicle_id']}"
                    ).add_to(m)

                m.save("simulation_map.html")

                with map_placeholder:
                    with open("simulation_map.html", "r", encoding="utf-8") as f:
                        html_data = f.read()

                    components.html(html_data, height=400)

                # update delivery
                for v in fleet_routes:
                    stops = v["stops"]

                    if step < len(stops):
                        stops[step]["status"] = "delivered"

                status_placeholder.dataframe(build_status())

                delivered = sum(
                    1 for v in fleet_routes for s in v["stops"]
                    if s["status"] == "delivered"
                )

                progress_data.append(delivered)

                line.set_xdata(range(len(progress_data)))
                line.set_ydata(progress_data)
                ax.relim()
                ax.autoscale_view()

                chart_placeholder.pyplot(fig)

                time.sleep(0.7)

            except Exception as e:
                st.error(str(e))
                break


# ---------------------------
# 📥 DOWNLOAD CSV (SAFE)
# ---------------------------

try:
    response = requests.get(
        "https://ai-logistics-backend.onrender.com/download-routes",
        timeout=10
    )

    if response.status_code == 200 and response.content:

        st.download_button(
            label="📥 Download Routes CSV",
            data=response.content,
            file_name="optimized_routes.csv",
            mime="text/csv"
        )

    else:
        st.warning("⚠️ No data available to download. Run optimization first.")

except requests.exceptions.ConnectionError:
    st.warning("⚠️ Backend not running (CSV unavailable).")

except Exception as e:
    st.warning(f"Download error: {str(e)}")