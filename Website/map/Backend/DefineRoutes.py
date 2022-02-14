from __future__ import division
from __future__ import print_function
from calendar import c
import json
import urllib.request
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp


def create_data():
    """Creates the data."""
    data = {}
    data['API_key'] = 'AIzaSyA6T3-uxZ2AZ--uYDRzMuAtzW9KK71geis'
    data['addresses'] = ['41.7160449,-8.8438683',  # Viana do Castelo
                         '41.70154,-8.8373567',  # Santa Luzia
                         '41.6900904,-8.8324579',  # gil eanes
                         '41.6905816,-8.8301721'  # cerqueiras
                         ]
    data['time_windows'] = [
        (0, 500),  # depot
        (0, 540),
        (700, 2000),
        (800, 2000),
    ]
    data['num_vehicles'] = 2
    data['depot'] = 0

    return data


def print_solution(data, manager, routing, solution):
    """Prints solution on console."""
    time_dimension = routing.GetDimensionOrDie('Time')
    json_output = []
    
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        coordenadasRoute = []
        hexadecimalColors = ['#00ff00', '#ffff00']
            
        while not routing.IsEnd(index):
            time_var = time_dimension.CumulVar(index)
            coordenadasRoute.append(data['addresses'][manager.IndexToNode(index)])
            index = solution.Value(routing.NextVar(index))

        time_var = time_dimension.CumulVar(index)
        coordenadasRoute.append(data['addresses'][manager.IndexToNode(index)])
        coordenadasRoute.append(solution.Min(time_var))
        coordenadasRoute.append(hexadecimalColors[vehicle_id])
        json_output.append(coordenadasRoute)
        
    print('Rotas enviadas para ficheiro JSON')

    with open('route.json', '+w') as f:
        json.dump(json_output, f, indent=4, sort_keys=True)
        

def create_distance_matrix(data):
    addresses = data["addresses"]
    API_key = data["API_key"]
    # Distance Matrix API only accepts 100 elements per request, so get rows in multiple requests.
    max_elements = 100
    num_addresses = len(addresses)  # 16 in this example.
    # Maximum number of rows that can be computed per request (6 in this example).
    max_rows = max_elements // num_addresses
    # num_addresses = q * max_rows + r (q = 2 and r = 4 in this example).
    q, r = divmod(num_addresses, max_rows)
    dest_addresses = addresses
    distance_matrix = []
    # Send q requests, returning max_rows rows per request.
    for i in range(q):
        origin_addresses = addresses[i * max_rows: (i + 1) * max_rows]
        response = send_request(origin_addresses, dest_addresses, API_key)
        distance_matrix += build_distance_matrix(response)

    # Get the remaining remaining r rows, if necessary.
    if r > 0:
        origin_addresses = addresses[q * max_rows: q * max_rows + r]
        response = send_request(origin_addresses, dest_addresses, API_key)
        distance_matrix += build_distance_matrix(response)
    return distance_matrix


def send_request(origin_addresses, dest_addresses, API_key):
    """ Build and send request for the given origin and destination addresses."""

    def build_address_str(addresses):
        # Build a pipe-separated string of addresses
        address_str = ''
        for i in range(len(addresses) - 1):
            address_str += addresses[i] + '|'
        address_str += addresses[-1]
        return address_str

    request = 'https://maps.googleapis.com/maps/api/distancematrix/json?units=metric'
    origin_address_str = build_address_str(origin_addresses)
    dest_address_str = build_address_str(dest_addresses)
    request = request + '&origins=' + origin_address_str + '&destinations=' + \
              dest_address_str + '&key=' + API_key
    jsonResult = urllib.request.urlopen(request).read()
    response = json.loads(jsonResult)
    return response


def build_distance_matrix(response):
    distance_matrix = []
    for row in response['rows']:
        row_list = [row['elements'][j]['duration']['value'] for j in range(len(row['elements']))]
        distance_matrix.append(row_list)
    return distance_matrix


########
# Main #
########

output = []


def main():
    """Entry point of the program"""
    # Create the data.
    data = create_data()
    addresses = data['addresses']
    API_key = data['API_key']
    distance_matrix = create_distance_matrix(data)
    #print(distance_matrix)

    """Solve the VRP with time windows."""
    # Instantiate the data problem.
    data = create_data()

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(len(distance_matrix), data['num_vehicles'], data['depot'])

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    # Create and register a transit callback.
    def time_callback(from_index, to_index):
        """Returns the travel time between the two nodes."""
        # Convert from routing variable Index to time matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['time_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(time_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add Time Windows constraint.
    time = 'Time'
    routing.AddDimension(
        transit_callback_index,
        300,  # allow waiting time
        1500,  # maximum time per vehicle
        False,  # Don't force start cumul to zero.
        time)
    time_dimension = routing.GetDimensionOrDie(time)
    # Add time window constraints for each location except depot.
    for location_idx, time_window in enumerate(data['time_windows']):
        if location_idx == data['depot']:
            continue
        index = manager.NodeToIndex(location_idx)
        time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])
    # Add time window constraints for each vehicle start node.
    depot_idx = data['depot']
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        time_dimension.CumulVar(index).SetRange(
            data['time_windows'][depot_idx][0],
            data['time_windows'][depot_idx][1])

    # Instantiate route start and end times to produce feasible times.
    for i in range(data['num_vehicles']):
        routing.AddVariableMinimizedByFinalizer(
            time_dimension.CumulVar(routing.Start(i)))
        routing.AddVariableMinimizedByFinalizer(
            time_dimension.CumulVar(routing.End(i)))

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    output.append(manager)
    output.append(routing)
    output.append(solution)

    # Print solution on console.
    if solution:
        print_solution(data, manager, routing, solution)

    return output


if __name__ == '__main__':
    main()
