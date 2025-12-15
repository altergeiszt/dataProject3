# logic_solver_osrm.py

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from osrm_router import OSRMRouter  # Ensure this is correctly imported
from sqlalchemy import create_engine, text
import pandas as pd
import numpy as np

class VRPSolver:
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.engine = None
        self.osrm_router = OSRMRouter()  # Instantiate OSRMRouter
    
    def _get_engine(self):
        if self.engine is None:
            self.engine = create_engine(self.db_url)
        return self.engine
    
    def extract_orders(self) -> pd.DataFrame:
        engine = self._get_engine()
        query = text("SELECT id, latitude, longitude, time_window_start, time_window_end, demand FROM deliveries")
        orders_df = pd.read_sql(query, engine)
        return orders_df
    
    def solve_vrp(self, orders_df: pd.DataFrame):
        # Create the data model
        data = self.create_data_model(orders_df)

        # Create the routing index manager
        manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']), data['num_vehicles'], data['depot'])

        # Create Routing Model
        routing = pywrapcp.RoutingModel(manager)

        # Create and register a transit callback.
        def distance_callback(from_index, to_index):
            """Returns the distance between the two nodes."""
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return data['distance_matrix'][from_node][to_node]

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)

        # Define cost of each arc.
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        # Add Time Windows constraint
        time = 'Time'
        routing.AddDimension(
            transit_callback_index,
            slack_max=30,  # allow waiting time
            capacity=2880,  # maximum time per vehicle
            fix_start_cumul_to_zero=True,
            name=time)
        time_dimension = routing.GetDimensionOrDie(time)
        
        for location_idx, time_window in enumerate(data['time_windows']):
            if location_idx == data['depot']:
                continue

            index = manager.NodeToIndex(location_idx)
            time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])

        # Add Capacity constraint
        demand_callback_index = routing.RegisterUnaryTransitCallback(
            lambda from_index: data['demands'][manager.IndexToNode(from_index)])
        routing.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            slack_max=0,  # null capacity slack
            vehicle_capacities=data['vehicle_capacities'],  # vehicle maximum capacities
            fix_start_cumul_to_zero=True,
            name='Capacity')

        # Setting first solution heuristic (cheapest addition).
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

        # Solve the problem.
        solution = routing.SolveWithParameters(search_parameters)

        # Print solution on console.
        if solution:
            self.print_solution(manager, routing, solution)
        else:
            print('No solution found !')
    
    def create_data_model(self, orders_df: pd.DataFrame):
        data = {}
        
        num_vehicles = 5
        depot = 0

        # Distance matrix
        distance_matrix = self.compute_distance_matrix(orders_df)
        data['distance_matrix'] = distance_matrix

        # Time windows
        time_windows = [(0, 2880) for _ in range(len(orders_df) + 1)]  # depot + orders
        for i, row in enumerate(orders_df.itertuples(index=False)):
            location_idx = i + 1  # Depot is at index 0
            time_windows[location_idx] = (row.time_window_start, row.time_window_end)
        
        data['time_windows'] = time_windows

        # Demands and capacities
        demands = [0] + list(orders_df['demand'].values)
        data['demands'] = demands
        vehicle_capacities = [15 for _ in range(num_vehicles)]
        data['vehicle_capacities'] = vehicle_capacities

        data['num_vehicles'] = num_vehicles
        data['depot'] = depot

        return data

    
    def compute_distance_matrix(self, orders_df: pd.DataFrame):
        num_locations = len(orders_df) + 1  # +1 for the depot
        distance_matrix = np.zeros((num_locations, num_locations))
        
        # Assuming depot is at index 0 with coordinates (0, 0)
        depot_coords = (0, 0)
        
        # Compute distances from depot to each location and between locations
        for i in range(num_locations):
            if i == 0:
                coord1 = depot_coords
            else:
                coord1 = (orders_df.iloc[i-1]['longitude'], orders_df.iloc[i-1]['latitude'])
            
            for j in range(num_locations):
                if j == 0:
                    coord2 = depot_coords
                else:
                    coord2 = (orders_df.iloc[j-1]['longitude'], orders_df.iloc[j-1]['latitude'])
                
                distance_meters, _ = self.osrm_router.get_driving_distance(coord1[1], coord1[0], coord2[1], coord2[0])
                if distance_meters is None:
                    raise Exception(f"Failed to get driving distance between {coord1} and {coord2}")
                
                distance_matrix[i][j] = distance_meters
        
        return distance_matrix.tolist()
    
    def print_solution(self, manager, routing, solution):
        """Prints solution on console."""
        time_dimension = routing.GetDimensionOrDie('Time')
        total_distance = 0
        total_time = 0
        for vehicle_id in range(routing.vehicles()):
            index = routing.Start(vehicle_id)
            plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
            distance = 0
            while not routing.IsEnd(index):
                time_var = time_dimension.CumulVar(index)
                plan_output += '{0} Time({1},{2}) -> '.format(
                    manager.IndexToNode(index), solution.Min(time_var),
                    solution.Max(time_var))
                previous_index = index
                index = solution.Value(routing.NextVar(index))
                distance += routing.GetArcCostForVehicle(previous_index, index,
                                                        vehicle_id)
            time_var = time_dimension.CumulVar(index)
            plan_output += '{0} Time({1},{2})\n'.format(
                manager.IndexToNode(index), solution.Min(time_var),
                solution.Max(time_var))
            plan_output += 'Distance of the route: {}m\n'.format(distance)
            plan_output += 'Time of the route: {}min\n'.format(
                solution.Min(time_var))
            print(plan_output)
            total_distance += distance
            total_time += solution.Min(time_var)
        print('Total distance of all routes: {}m'.format(total_distance))
        print('Total time of all routes: {}min'.format(total_time))
