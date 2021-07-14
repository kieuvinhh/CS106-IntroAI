import ElectricCar.EVRP as EVRP
import random

'''
This file hold all the function to run the heuristic
We use meta-heuristic to solve the problem 
Meta-heuristic has two characteristics: intensification and diversification 
	For diversification we use Variable Neighborhood Search (VNS)
		In perturbation we randomly use shuffle, invert and reconnect to create a new path, then repair it using SSF
	For intensification we use Randomized Variable Neighborhood Descent (RVND) as local search
		The operator for local search are: exchange, relocation, two-opt, or-opt and AFS reallocation
'''
PERTURBATION_NUM = 3			# The number of routes that we want to split


def initialize_heuristic():
	pass


# implement your heuristic in this function
def run_heuristic():
	# Construct initial solution
	current_route = initial_construction()
	stop = False

	while not stop:
		perm_route = perturbation(current_route)
		new_route = seperate_sequential_fixing(perm_route)

		new_route, stop = local_search(new_route)

		if EVRP.fitness_evaluation(new_route, len(new_route)) < EVRP.fitness_evaluation(current_route, len(current_route)):
			current_route = new_route


def local_search(solution_route: list):
	i = 0
	stop = False
	current_route = solution_route[:]
	choice = [1, 2, 3, 4, 5]
	random.shuffle(choice)

	while i < 5:
		method = choice[i]

		if method == 1:
			new_route = relocate(current_route, len(current_route))
		elif method == 2:
			new_route = exchange(current_route, len(current_route))
		elif method == 3:
			new_route = two_opt(current_route, len(current_route))
		elif method == 4:
			new_route = or_opt(current_route, len(current_route))
		else:
			new_route = AFS_reallocation(current_route, len(current_route))

		if EVRP.fitness_evaluation(new_route, len(new_route)) < EVRP.fitness_evaluation(current_route, len(current_route)):
			current_route = new_route
			i = 0
			random.shuffle(choice)
		else:
			i += 1

		if EVRP.evals >= EVRP.TERMINATION:
			stop = True
			break

	return current_route, stop


def initial_construction():
	# 2 phase construction
	initial_solution = nearest_neighbour()
	repaired_solution = seperate_sequential_fixing(initial_solution)

	return repaired_solution


def nearest_neighbour():
	nn_solution = []
	un_visited = list(range(1, EVRP.NUM_OF_CUSTOMERS + 1))

	nn_solution.append(0)

	while True:
		if not un_visited:
			break

		last_node_index = nn_solution[-1]
		current_best = 2**32 - 1
		current_index_route = 0
		current_index = 0

		for index, value in enumerate(un_visited):
			distance = EVRP.get_distance(last_node_index, value)

			if distance < current_best:
				current_best = distance
				current_index_route = value
				current_index = index

		nn_solution.append(current_index_route)
		del un_visited[current_index]

	nn_solution.append(0)

	return nn_solution


def seperate_sequential_fixing(solution_route: list):
	# First phase: check load constraint
	customers = EVRP.cust_demand
	load_limit = EVRP.MAX_CAPACITY
	temp_load = 0

	for index, value in enumerate(solution_route):
		if customers[value] <= 0:
			continue
		temp_load += customers[value]

		# If total load of the next customer exceed the limit then insert depot
		if temp_load > load_limit:
			solution_route.insert(index, 0)
			temp_load = 0

	# Second phase: check battery limit
	max_battery = EVRP.BATTERY_CAPACITY
	temp_battery = max_battery
	add_battery_flag = False
	index = 1

	while index < len(solution_route):
		_from = solution_route[index-1]
		_to = solution_route[index]

		# If current is depot:
		if _from == EVRP.DEPOT:
			temp_battery = EVRP.BATTERY_CAPACITY

		# Check if nearest station can be reach from current and prevent infinity loop
		# Check nearest station in current node
		nearest_station = get_nearest_station(_from)
		temp_battery_station = temp_battery - EVRP.get_energy_consumption(_from, nearest_station)
		# Check nearest station in next node
		nearest_station_next = get_nearest_station(_to)
		temp_battery_next = temp_battery - EVRP.get_energy_consumption(_from, _to) - EVRP.get_energy_consumption(_to, nearest_station_next)

		# If current node can't reach next station, then fallback and find next addable station
		if temp_battery_station < 0:
			add_battery_flag = True
			index -= 1
			temp_battery = get_current_battery_consumption(solution_route, index - 1)
			continue
		# If flag to add station is on then add the nearest station to the solution
		elif add_battery_flag:
			solution_route.insert(index, nearest_station)
			temp_battery = EVRP.BATTERY_CAPACITY
			index += 1
			add_battery_flag = False
			continue
		# If current node is a station and next node can't reach the station then add the station of the
		# next node to break infinity loop
		elif _from == nearest_station and temp_battery_next < 0:
			solution_route.insert(index, nearest_station_next)
			temp_battery = EVRP.BATTERY_CAPACITY
			index += 1
			add_battery_flag = False
			continue

		temp_battery -= EVRP.get_energy_consumption(_from, _to)

		# If vehicle can't reach the next customer then add nearest station
		if temp_battery < 0:
			solution_route.insert(index, nearest_station)
			temp_battery = EVRP.BATTERY_CAPACITY

		index += 1

	return solution_route


def get_nearest_station(node: int):
	station_start_index = EVRP.problem_size
	current_best_length = 2**32 - 1
	current_station = 0

	for station in range(station_start_index, EVRP.ACTUAL_PROBLEM_SIZE):
		distance = EVRP.get_distance(node, station)

		if distance < current_best_length:
			current_best_length = distance
			current_station = station

	return current_station


def get_current_battery_consumption(solution_route: list, index: int):
	temp_battery = EVRP.BATTERY_CAPACITY

	for i in range(1, index + 1):
		head = solution_route[i-1]
		tail = solution_route[i]

		if EVRP.is_charging_station(tail):
			temp_battery = EVRP.BATTERY_CAPACITY
		else:
			temp_battery -= EVRP.get_energy_consumption(head, tail)

	return temp_battery


def perturbation(solution_route: list):
	global PERTURBATION_NUM
	length = len(solution_route)
	routes = []
	new_route = []
	random_index = random.sample(range(length), PERTURBATION_NUM)
	random_index.sort()

	start_index = 0
	end_index = length

	# Get route in solution based on random index
	for p in random_index:
		routes.append(solution_route[start_index:p])
		start_index = p

	routes.append(solution_route[start_index:end_index])

	# Random do nothing, shuffle and invert
	random_choice = ['nothing', 'shuffle', 'invert']

	for route in routes:
		choice = random.choice(random_choice)

		if choice == 'shuffle':
			random.shuffle(route)
		elif choice == 'invert':
			route.reverse()

	list_number = list(range(PERTURBATION_NUM + 1))
	random.shuffle(list_number)

	# Randomly reconnecting route
	for i in list_number:
		new_route += routes[i]

	# Make sure the begin and the end are depot
	if new_route[0] != 0:
		new_route.insert(0, 0)
	if new_route[-1] != 0:
		new_route.append(0)

	# Remove any redundancy in the solution
	new_route = remove_duplicate_node(new_route)

	return new_route


def remove_duplicate_node(solution_route: list):
	index = 0

	while index < len(solution_route) - 1:
		if solution_route[index] == solution_route[index + 1]:
			del solution_route[index + 1]
			continue
		index += 1

	return solution_route


def check_solution(route: list):
	energy_temp = EVRP.BATTERY_CAPACITY
	capacity_temp = EVRP.MAX_CAPACITY
	size = len(route)

	for i in range(size - 1):
		_from = route[i]
		_to = route[i + 1]
		capacity_temp -= EVRP.get_customer_demand(_to)
		energy_temp -= EVRP.get_energy_consumption(_from, _to)

		if capacity_temp < 0.0:
			return False
		if energy_temp < 0.0:
			return False
		if _to == EVRP.DEPOT:
			capacity_temp = EVRP.MAX_CAPACITY
		if EVRP.is_charging_station(_to) or _to == EVRP.DEPOT:
			energy_temp = EVRP.BATTERY_CAPACITY

	return True


'''
/****************************************************************/
/*                Local search operator                         */
/****************************************************************/
'''
def two_opt(solution_route: list, steps: int):
	best = solution_route[:]
	best_cost = 0

	for i in range(1, steps-2):
		for j in range(i+1, steps):
			if j-i == 1:
				continue
			if cost_two_opt(best[i-1], best[i], best[j-1], best[j]) > best_cost:
				temp = best[:]
				temp[i:j] = temp[j - 1:i - 1:-1]

				if check_solution(temp):
					return temp

	return best


def cost_two_opt(id1: int, id2: int, id3: int, id4: int):
	first_cut = EVRP.get_distance(id1, id2)
	second_cut = EVRP.get_distance(id3, id4)
	first_add = EVRP.get_distance(id3, id1)
	second_add = EVRP.get_distance(id2, id4)

	return (first_cut + second_cut) - (first_add + second_add)


def exchange(solution_route: list, steps: int):
	best = solution_route[:]
	best_cost = 0

	for i in range(1, steps - 2):
		for j in range(i + 1, steps - 1):
			if j - i == 1:
				continue
			if cost_exchange(best[i - 1], best[i], best[i + 1], best[j - 1], best[j], best[j + 1]) > best_cost:
				temp = best[:]
				temp[i], temp[j] = temp[j], temp[i]

				if check_solution(temp):
					return temp

	return best


def cost_exchange(id1: int, id2: int, id3: int, id4: int, id5: int, id6: int):
	cut_one = EVRP.get_distance(id1, id2)
	cut_two = EVRP.get_distance(id2, id3)
	cut_three = EVRP.get_distance(id4, id5)
	cut_four = EVRP.get_distance(id5, id6)

	add_one = EVRP.get_distance(id1, id5)
	add_two = EVRP.get_distance(id5, id3)
	add_three = EVRP.get_distance(id4, id2)
	add_four = EVRP.get_distance(id2, id6)

	return (cut_one + cut_two + cut_three + cut_four) - (add_one + add_two + add_three + add_four)


def relocate(solution_route: list, steps: int):
	best = solution_route[:]
	best_cost = 0

	for i in range(1, steps - 2):
		for j in range(i + 1, steps):
			if j - i == 1:
				continue
			if cost_relocate(best[i - 1], best[i], best[i + 1], best[j - 1], best[j]) > best_cost:
				temp = best[:]
				temp.insert(j, temp[i])
				del temp[i]

				if check_solution(temp):
					return temp

	return best


def cost_relocate(id1: int, id2: int, id3: int, id4: int, id5: int):
	cut_one = EVRP.get_distance(id1, id2)
	cut_two = EVRP.get_distance(id2, id3)
	cut_three = EVRP.get_distance(id4, id5)

	add_one = EVRP.get_distance(id1, id3)
	add_two = EVRP.get_distance(id4, id2)
	add_three = EVRP.get_distance(id2, id5)

	return (cut_one + cut_two + cut_three) - (add_one + add_two + add_three)


def or_opt(solution_route: list, steps: int):
	best = solution_route[:]
	best_cost = 0

	for i in range(1, steps - 3):
		for j in range(i + 2, steps - 2):
			if j - i < 3:
				continue
			if cost_or_opt(best[i - 1], best[i], best[i + 1], best[i + 2],
							best[j - 1], best[j], best[j + 1], best[j + 2]) > best_cost:
				temp = best[:]
				temp[i:i+2], temp[j:j+2] = temp[j:j+2], temp[i:i+2]

				if check_solution(temp):
					return temp

	return best


def cost_or_opt(id1: int, id2_first: int, id3_first: int, id4: int, id5: int, id6_second: int, id7_second: int, id8: int):
	cut_one = EVRP.get_distance(id1, id2_first)
	cut_two = EVRP.get_distance(id3_first, id4)
	cut_three = EVRP.get_distance(id5, id6_second)
	cut_four = EVRP.get_distance(id7_second, id8)

	add_one = EVRP.get_distance(id1, id6_second)
	add_two = EVRP.get_distance(id7_second, id4)
	add_three = EVRP.get_distance(id5, id2_first)
	add_four = EVRP.get_distance(id3_first, id8)

	return (cut_one + cut_two + cut_three + cut_four) - (add_one + add_two + add_three + add_four)


def AFS_reallocation(solution_route: list, steps: int):
	# Delete all the station in the route
	index = 0
	while index < len(solution_route):
		if EVRP.is_charging_station(solution_route[index]) and solution_route[index] != EVRP.DEPOT:
			del solution_route[index]
			continue
		index += 1

	# Reallocate all the charging station to the route
	max_battery = EVRP.BATTERY_CAPACITY
	temp_battery = max_battery
	add_battery_flag = False
	index = 1

	while index < len(solution_route):
		_from = solution_route[index - 1]
		_to = solution_route[index]

		# If current is depot:
		if _from == EVRP.DEPOT:
			temp_battery = EVRP.BATTERY_CAPACITY

		# Check if nearest station can be reach from current and prevent infinity loop
		# Check nearest station in current node
		nearest_station = get_nearest_station(_from)
		temp_battery_station = temp_battery - EVRP.get_energy_consumption(_from, nearest_station)
		# Check nearest station in next node
		nearest_station_next = get_nearest_station(_to)
		temp_battery_next = temp_battery - EVRP.get_energy_consumption(_from, _to) - EVRP.get_energy_consumption(_to,
																												 nearest_station_next)

		# If current node can't reach next station, then fallback and find next addable station
		if temp_battery_station < 0:
			add_battery_flag = True
			index -= 1
			temp_battery = get_current_battery_consumption(solution_route, index - 1)
			continue
		# If flag to add station is on then add the nearest station to the solution
		elif add_battery_flag:
			solution_route.insert(index, nearest_station)
			temp_battery = EVRP.BATTERY_CAPACITY
			index += 1
			add_battery_flag = False
			continue
		# If current node is a station and next node can't reach the station then add the station of the
		# next node to break infinity loop
		elif _from == nearest_station and temp_battery_next < 0:
			solution_route.insert(index, nearest_station_next)
			temp_battery = EVRP.BATTERY_CAPACITY
			index += 1
			add_battery_flag = False
			continue

		temp_battery -= EVRP.get_energy_consumption(_from, _to)

		# If vehicle can't reach the next customer then add nearest station
		if temp_battery < 0:
			solution_route.insert(index, nearest_station)
			temp_battery = EVRP.BATTERY_CAPACITY

		index += 1

	return solution_route

