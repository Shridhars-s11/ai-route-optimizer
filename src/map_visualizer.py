import folium

def create_route_map(df, route):
    # center map at first location (warehouse)
    center_lat = df.iloc[0]["latitude"]
    center_lon = df.iloc[0]["longitude"]

    m = folium.Map(location=[center_lat, center_lon], zoom_start=12)

    # add markers
    for order, stop in enumerate(route):

        lat = df.iloc[stop]["latitude"]
        lon = df.iloc[stop]["longitude"]

        if order == 0:
            folium.Marker(
                location=[lat, lon],
                popup="Warehouse",
                icon=folium.Icon(color="red", icon="home")
            ).add_to(m)

        else:
            folium.Marker(
                location=[lat, lon],
                popup=f"Stop {order}",
                icon=folium.DivIcon(
                    html=f"""
                    <div style="
                    font-size:14px;
                    color:white;
                    background:blue;
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

    # draw route
    route_coords = []

    for stop in route:
        lat = df.iloc[stop]["latitude"]
        lon = df.iloc[stop]["longitude"]
        route_coords.append((lat, lon))

    folium.PolyLine(route_coords, color="green", weight=5).add_to(m)

    m.save("optimized_route.html")