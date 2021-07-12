import EVRP
import random

'''
Best solution for all independent run
The solution have the following structure:
[
	tour = [...]: List of node of the best solution,
	int id: ID of the solution,
	float tour_length: quality of the solution,
	int steps: size of the solution
]

the format of the solution is as follows:
tour:  0 - 5 - 6 - 8 - 0 - 1 - 2 - 3 - 4 - 0 - 7 - 0
steps: 12
this solution consists of three routes:
Route 1: 0 - 5 - 6 - 8 - 0
Route 2: 0 - 1 - 2 - 3 - 4 - 0
Route 3: 0 - 7 - 0
'''
best_sol = []


def initialize_heuristic():
	global best_sol

	best_sol = [None] * 4
	best_sol[0] = [-1] * (EVRP.NUM_OF_CUSTOMERS+1000)	# list of node
	best_sol[1] = 1										# id
	best_sol[2] = float('inf')							# tour_length
	best_sol[3] = 0										# steps


# implement your heuristic in this function
def run_heuristic():
	global best_sol

	# generate a random solution for the random heuristic
	tot_assigned = 0
	r = [-1] * (EVRP.NUM_OF_CUSTOMERS + 1)
	energy_temp = 0.0
	capacity_temp = 0.0

	# set indexes of objects
	for i in range(1, EVRP.NUM_OF_CUSTOMERS + 1):
		r[i-1] = i

	# randomly change indexes of objects
	random.shuffle(r)

	best_sol[3] = 0
	best_sol[2] = float('inf')

	best_sol[0][0] = EVRP.DEPOT
	best_sol[3] += 1

	'''
	best_sol = [
	0: list of node,
	1: id,
	2: tour_length,
	3: steps
	]
	'''

	i = 0
	while i < EVRP.NUM_OF_CUSTOMERS:
		_from = best_sol[0][best_sol[3] - 1]
		_to = r[i]

		if (capacity_temp + EVRP.get_customer_demand(_to)) <= EVRP.MAX_CAPACITY and energy_temp + EVRP.get_energy_consumption(_from, _to) <= EVRP.BATTERY_CAPACITY:
			capacity_temp += EVRP.get_customer_demand(_to)
			energy_temp += EVRP.get_energy_consumption(_from, _to)
			best_sol[0][best_sol[3]] = _to
			best_sol[3] += 1
			i += 1
		elif (capacity_temp + EVRP.get_customer_demand(_to)) > EVRP.MAX_CAPACITY:
			capacity_temp = 0.0
			energy_temp = 0.0
			best_sol[0][best_sol[3]] = EVRP.DEPOT
			best_sol[3] += 1
		elif energy_temp + EVRP.get_energy_consumption(_from, _to) > EVRP.BATTERY_CAPACITY:
			charging_station = random.randint(EVRP.NUM_OF_CUSTOMERS + 1, EVRP.ACTUAL_PROBLEM_SIZE - 1)

			if EVRP.is_charging_station(charging_station):
				energy_temp = 0.0
				best_sol[0][best_sol[3]] = charging_station
				best_sol[3] += 1
		else:
			capacity_temp = 0.0
			energy_temp = 0.0
			best_sol[0][best_sol[3]] = EVRP.DEPOT
			best_sol[3] += 1

	# close EVRP tour to return back to the depot
	if best_sol[0][best_sol[3] - 1] != EVRP.DEPOT:
		best_sol[0][best_sol[3]] = EVRP.DEPOT
		best_sol[3] += 1

	best_sol[2] = EVRP.fitness_evaluation(best_sol[0], best_sol[3])

