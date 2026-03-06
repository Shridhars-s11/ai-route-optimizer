def calculate_route_distance(route,distance_matrix):
    total_distance = 0

    for i in range(len(route)-1):
        from_node = route[i]
        to_node = route[i+1]
        total_distance += distance_matrix[from_node][to_node]
        
    return round(total_distance,2)

def create_naive_route(num_locations):
    route = list(range(num_locations))
    route.append(0)

    return route