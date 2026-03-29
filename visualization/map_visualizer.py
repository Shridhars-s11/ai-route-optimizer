import folium
import time
from core.routing_services.osrm_route_geometry import get_osrm_route_geometry


def create_route_map(df, routes):

    # center map at warehouse
    center_lat = df.iloc[0]["latitude"]
    center_lon = df.iloc[0]["longitude"]

    m = folium.Map(location=[center_lat, center_lon], zoom_start=12)

    colors = [
            "red","blue","green","purple","orange",
            "darkred","cadetblue","darkgreen","black","pink"
            ]

    # add warehouse marker
    folium.Marker(
    location=[center_lat, center_lon],
    popup="🏭 Warehouse",
    icon=folium.Icon(color="black", icon="home")
    ).add_to(m)

    for vehicle_id, route in enumerate(routes):

        color = colors[vehicle_id % len(colors)]

        route_coords = []

        for order, stop in enumerate(route):

            if stop >= len(df):
                continue

            lat = df.iloc[stop]["latitude"]
            lon = df.iloc[stop]["longitude"]

            route_coords.append((lat, lon))

            if stop != 0:  # skip warehouse numbering

                folium.Marker(
                    location=[lat, lon],
                    popup=f"Vehicle {vehicle_id+1} Stop {order}",
                    icon=folium.DivIcon(
                        html=f"""
                        <div style="
                        font-size:14px;
                        color:white;
                        background:{color};
                        border-radius:50%;
                        width:28px;
                        height:28px;
                        text-align:center;
                        line-height:28px;">
                        {order}
                        </div>
                        """
                    )
                ).add_to(m)

        # get real road geometry
        road_path = get_osrm_route_geometry(route_coords)

        # 🛡 fallback if geometry fails
        if not road_path or len(road_path) < 2:
            road_path = route_coords

        folium.PolyLine(
            road_path,
            color=color,
            weight=5,
            opacity=0.8
        ).add_to(m)

        # simulate vehicle movement
        # show single truck at start of route
        if road_path:

            folium.Marker(
                location=road_path[0],
                icon=folium.Icon(color=color, icon="truck", prefix="fa"),
                popup=f"Vehicle {vehicle_id+1}"
            ).add_to(m)


    m.save("optimized_routes.html")