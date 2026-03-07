import folium

def create_route_map(df, route):
    # center map at first location (warehouse)
    center_lat = df.iloc[0]["latitude"]
    center_lon = df.iloc[0]["longitude"]

    m = folium.Map(location=[center_lat, center_lon], zoom_start=12)

    # add markers
    for idx, row in df.iterrows():

        if idx == 0:
            folium.Marker(
                location=[row["latitude"], row["longitude"]],
                popup="Warehouse",
                icon=folium.Icon(color="red", icon="home")
            ).add_to(m)
        else:
            folium.Marker(
                location=[row["latitude"], row["longitude"]],
                popup=f"Stop {idx}",
                icon=folium.DivIcon(
                    html=f"""
                    <div style="font-size: 12pt; color: white;
                    background-color: blue; border-radius: 50%;
                    width: 25px; height: 25px; text-align:center;">
                    {idx}
                    </div>
                    """
                )
            ).add_to(m)

    # draw route
    route_coords = []

    for stop in route:
        lat = df.iloc[stop]["latitude"]
        lon = df.iloc[stop]["longitude"]
        route_coords.append((lat, lon))

    folium.PolyLine(route_coords, color="green", weight=5).add_to(m)

    m.save("optimized_route.html")