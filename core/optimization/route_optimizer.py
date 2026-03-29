from ortools.constraint_solver import pywrapcp, routing_enums_pb2

def create_data_model(distance_matrix):
    """Stores the data for the problem"""
    data ={}
    data["distance_matrix"] = distance_matrix
    data["num_vehicles"] = 1
    data['depot'] = 0
    return data

def solve_vrp(distance_matrix):
    data = create_data_model(distance_matrix)
    manager = pywrapcp.RoutingIndexManager(
        len(data["distance_matrix"]),
        data['num_vehicles'],
        data["depot"],
    )

    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index,to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return int(data["distance_matrix"][from_node][to_node]*1000)
    
    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()

    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )

    solution = routing.SolveWithParameters(search_parameters)

    if solution:
        index = routing.Start(0)

        route = []

        while not routing.IsEnd(index):

            node = manager.IndexToNode(index)

            route.append(node)

            index = solution.Value(routing.NextVar(index))

        route.append(manager.IndexToNode(index))

        return route

    return None