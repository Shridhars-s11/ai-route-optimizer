from ortools.constraint_solver import pywrapcp, routing_enums_pb2
import math


def create_data_model(distance_matrix, num_vehicles=3):

    data = {}
    data["distance_matrix"] = distance_matrix
    data["num_vehicles"] = num_vehicles
    data["depot"] = 0

    return data


def solve_multi_vehicle_vrp(distance_matrix, num_vehicles=3):

    data = create_data_model(distance_matrix, num_vehicles)

    manager = pywrapcp.RoutingIndexManager(
        len(data["distance_matrix"]),
        data["num_vehicles"],
        data["depot"],
    )

    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):

        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)

        return int(data["distance_matrix"][from_node][to_node] * 1000)

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # -------- BALANCE ROUTES --------

    routing.AddDimension(
        transit_callback_index,
        0,
        100000,
        True,
        "Distance"
    )

    distance_dimension = routing.GetDimensionOrDie("Distance")

    distance_dimension.SetGlobalSpanCostCoefficient(10000)

    # --------------------------------

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()

    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )

    solution = routing.SolveWithParameters(search_parameters)

    if not solution:
        return None

    routes = []

    for vehicle_id in range(data["num_vehicles"]):

        index = routing.Start(vehicle_id)

        route = []

        while not routing.IsEnd(index):

            node = manager.IndexToNode(index)

            route.append(node)

            index = solution.Value(routing.NextVar(index))

        route.append(manager.IndexToNode(index))

        routes.append(route)

    return routes