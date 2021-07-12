import math

problem_instance = ""  # Name of the problem
node_list = []  # List of nodes with id and x and y coordinates, a node include [id:int, x:double, y:double]
cust_demand = []  # List with id and customer demands
charging_station = []
distances = [[]]  # Distance matrix
problem_size = 0  # Problem dimension read
energy_consumption = 0.0

DEPOT = 0  # Depot index (usually 0)
NUM_OF_CUSTOMERS = 0  # Number of customers (excluding depot)
ACTUAL_PROBLEM_SIZE = 0  # Total number of customers, charging stations and depot
OPTIMUM = 0  # Problem's optimal solution
NUM_OF_STATIONS = 0  # Number of charging sations
BATTERY_CAPACITY = 0  # Maximum energy of vehicles
MAX_CAPACITY = 0  # Capacity of vehicles
MIN_VEHICLES = 0  # The minimal vehicles to solve this problem

evals = 0.0  # Total number of evaluation
current_best = float('inf')  # The total distance traveled, the smaller the better
best_routes = []  # Current best routes

TERMINATION = 25000 * ACTUAL_PROBLEM_SIZE  # Will terminate if the total evaluation exceeds this number

'''
/****************************************************************/
/*Compute and return the euclidean distance of two objects      */
/****************************************************************/
'''


def euclidean_distance(i: int, j: int):
    xd = node_list[i][1] - node_list[j][1]
    yd = node_list[i][2] - node_list[j][2]
    r = math.sqrt(xd * xd + yd * yd)
    return r


'''
/****************************************************************/
/*Compute the distance matrix of the problem instance           */
/****************************************************************/
'''


def compute_distances():
    global distances

    for i in range(ACTUAL_PROBLEM_SIZE):
        for j in range(ACTUAL_PROBLEM_SIZE):
            distances[i][j] = euclidean_distance(i, j)


'''
/****************************************************************/
/*Generate and return a two-dimension array of type double      */
/****************************************************************/
'''


def generate_2D_matrix_double(n: int, m: int):
    matrix = [[0.0 for i in range(n)] for j in range(m)]
    return matrix


'''
/****************************************************************/
/* Read the problem instance and generate the initial object    */
/* vector.                                                      */
/****************************************************************/
'''


def read_problem(filename: str):
    global problem_size
    global MAX_CAPACITY
    global MIN_VEHICLES
    global BATTERY_CAPACITY
    global energy_consumption
    global NUM_OF_STATIONS
    global OPTIMUM
    global NUM_OF_CUSTOMERS
    global node_list
    global ACTUAL_PROBLEM_SIZE
    global TERMINATION
    global distances
    global cust_demand
    global charging_station
    global DEPOT

    keywords = ""

    with open(filename, mode='r', encoding='UTF-8') as file:
        contents = file.readlines()
        for line in contents:
            word = line.split()

            if word[0] == "DIMENSION:":
                problem_size = int(word[1])
            elif word[0] == "CAPACITY:":
                MAX_CAPACITY = int(word[1])
            elif word[0] == "VEHICLES:":
                MIN_VEHICLES = int(word[1])
            elif word[0] == "ENERGY_CAPACITY:":
                BATTERY_CAPACITY = int(word[1])
            elif word[0] == "ENERGY_CONSUMPTION:":
                energy_consumption = float(word[1])
            elif word[0] == "STATIONS:":
                NUM_OF_STATIONS = int(word[1])
                NUM_OF_CUSTOMERS = problem_size - 1
                ACTUAL_PROBLEM_SIZE = problem_size + NUM_OF_STATIONS
            elif word[0] == "OPTIMAL_VALUE:":
                OPTIMUM = float(word[1])
            elif word[0] == "NODE_COORD_SECTION":
                keywords = "NODE_COORD_SECTION"
                distances = generate_2D_matrix_double(ACTUAL_PROBLEM_SIZE, ACTUAL_PROBLEM_SIZE)
                continue
            elif word[0] == "DEMAND_SECTION":
                keywords = "DEMAND_SECTION"
                cust_demand = [-1] * ACTUAL_PROBLEM_SIZE
                charging_station = [False] * ACTUAL_PROBLEM_SIZE
                continue
            elif word[0] == "STATIONS_COORD_SECTION":
                keywords = "STATIONS_COORD_SECTION"
                continue
            elif word[0] == "DEPOT_SECTION":
                keywords = "DEPOT_SECTION"
                continue
            elif word[0] == '-1':
                break

            if keywords == "NODE_COORD_SECTION":
                if problem_size != 0:  # problem_size is the number of customers plus the depot
                    # store initial objects
                    node_list.append([int(word[0]) - 1, float(word[1]), float(word[2])])
                else:
                    print("Error in NODE_COORD_SECTION!!!")
                    exit(0)
            elif keywords == "DEMAND_SECTION":
                if problem_size != 0:
                    cust_demand[int(word[0]) - 1] = int(word[1])
            elif keywords == "STATIONS_COORD_SECTION":
                if problem_size != 0:
                    charging_station[int(word[0]) - 1] = True
            elif keywords == "DEPOT_SECTION":
                DEPOT = int(word[0]) - 1
                charging_station[int(word[0]) - 1] = True

    TERMINATION = 25000 * ACTUAL_PROBLEM_SIZE
    compute_distances()


'''
/****************************************************************/
/* Returns the solution quality of the solution. Taken as input */
/* an array of node indeces and its length                      */
/****************************************************************/
'''


def fitness_evaluation(routes, size: int):
    global distances
    global current_best
    global best_routes
    global evals
    tour_length = 0.0

    """	the format of the solution that this method evaluates is the following
	Node id:  0 - 5 - 6 - 8 - 0 - 1 - 2 - 3 - 4 - 0 - 7 - 0
	Route id: 1 - 1 - 1 - 1 - 2 - 2 - 2 - 2 - 2 - 3 - 3 - 3
	this solution consists of three routes: 
	Route 1: 0 - 5 - 6 - 8 - 0
	Route 2: 0 - 1 - 2 - 3 - 4 - 0
	Route 3: 0 - 7 - 0"""

    for i in range(size - 1):
        tour_length += distances[routes[i]][routes[i + 1]]

    if tour_length < current_best:
        current_best = tour_length
        best_routes = routes

    # adds complete evaluation to the overall fitness evaluation count
    evals += 1
    return tour_length


'''
/****************************************************************/
/* Outputs the routes of the solution. Taken as input           */
/* an array of node indeces and its length                      */
/****************************************************************/
'''


def print_solution(routes, size: int):
    for i in range(size):
        print(routes[i], sep=', ')
    print()


'''
/****************************************************************/
/* Returns the distance between two points: from and to. Can be */
/* used to evaluate a part of the solution. The fitness         */
/* evaluation count will be proportional to the problem size    */
/****************************************************************/
'''


def get_distance(_from: int, _to: int):
    global evals
    global ACTUAL_PROBLEM_SIZE
    global distances
    # adds partial evaluation to the overall fitness evaluation count
    # It can be used when local search is used and a whole evaluation is not necessary
    evals += (1.0 / ACTUAL_PROBLEM_SIZE)
    return distances[_from][_to]


'''
/****************************************************************/
/* Returns the energy consumed when travelling between two      */
/* points: from and to.                                         */
/****************************************************************/
'''


def get_energy_consumption(_from: int, _to: int):
    global energy_consumption
    global distances
    # DO NOT USE THIS FUNCTION MAKE ANY CALCULATIONS TO THE ROUTE COST
    return energy_consumption * distances[_from][_to]


'''
/****************************************************************/
/* Returns the demand for a specific customer                   */
/* points: from and to.                                         */
/****************************************************************/
'''


def get_customer_demand(customer: int):
    global cust_demand
    return cust_demand[customer]


'''
/****************************************************************/
/* Returns true when a specific node is a charging station;     */
/* and false otherwise                                          */
/****************************************************************/
'''


def is_charging_station(node: int):
    global charging_station

    flag = False
    if charging_station[node]:
        flag = True
    return flag


'''
/****************************************************************/
/* Returns the best solution quality so far                     */
/****************************************************************/
'''


def get_current_best():
    global current_best
    return current_best


def get_current_best_route():
    global best_routes
    return best_routes


'''
/*******************************************************************/
/* Reset the best solution quality so far for a new indepedent run */
/*******************************************************************/
'''


def init_current_best():
    global current_best
    global best_routes
    current_best = float('inf')
    best_routes = []


'''
/****************************************************************/
/* Returns the current count of fitness evaluations             */
/****************************************************************/
'''


def get_evals():
    global evals
    return evals


'''
/****************************************************************/
/* Reset the evaluation counter for a new indepedent run        */
/****************************************************************/
'''


def init_evals():
    global evals
    evals = 0.0


'''
/****************************************************************/
/* Validates the routes of the solution. Taken as input         */
/* an array of node indeces and its length                      */
/****************************************************************/
'''


def check_solution(t, size: int):
    global BATTERY_CAPACITY
    global MAX_CAPACITY
    global DEPOT

    energy_temp = BATTERY_CAPACITY
    capacity_temp = MAX_CAPACITY
    distance_temp = 0.0

    for i in range(size - 1):
        _from = t[i]
        _to = t[i + 1]
        capacity_temp -= get_customer_demand(_to)
        energy_temp -= get_energy_consumption(_from, _to)
        distance_temp += get_distance(_from, _to)

        if capacity_temp < 0.0:
            print("error: capacity below 0 at customer {}".format(_to))
            print_solution(t, size)
            exit(1)
        if energy_temp < 0.0:
            print("error: energy below 0 from {} to {}".format(_from, _to))
            print_solution(t, size)
            exit(1)
        if _to == DEPOT:
            capacity_temp = MAX_CAPACITY
        if is_charging_station(_to) or _to == DEPOT:
            energy_temp = BATTERY_CAPACITY

    if distance_temp != fitness_evaluation(t, size):
        print("error: check fitness evaluation")
