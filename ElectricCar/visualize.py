import matplotlib.pyplot as plt


def draw_graph(solution_route, node_list, cust_demand, charging_station, ACTUAL_PROBLEM_SIZE: int):
	'''
	solution_route: có dạng [id-1, ...] là route của solution
	node_list: có dạng [[id:int, x:double, y:double], ...] là vị trí các node
	cust_demand: có dạng [demand, ...] là weight của customer
	charging_station: [bool, ...] là các recharge station
	ACTUAL_PROBLEM_SIZE: int là kích thước problem
	'''


	depot = plt.Circle((node_list[0][1], node_list[0][2]), 2, color='red')
	stations = []
	customers = []
	rect_width = rect_height = 1

	# Vẽ hình vuông, hình tròn và đường đi của route
	for i in range(1, ACTUAL_PROBLEM_SIZE):
		if cust_demand[i] > 0:
			customers.append(plt.Circle((node_list[i][1], node_list[i][2]), 0.5, color='blue'))
		elif charging_station[i]:
			stations.append(plt.Rectangle((node_list[i][1] - rect_width/2, node_list[i][2] - rect_height/2),
									rect_width, rect_height,
									lw = 1,
									color='black'))

	plt.axes()
	plt.gca().add_patch(depot)

	for patch in customers:
		plt.gca().add_patch(patch)
	for patch in stations:
		plt.gca().add_patch(patch)

	for i in range(1, len(solution_route)):
		head = [node_list[solution_route[i - 1]][1], node_list[solution_route[i - 1]][2]]
		tail = [node_list[solution_route[i]][1], node_list[solution_route[i]][2]]
		x = [head[0], tail[0]]
		y = [head[1], tail[1]]
		plt.plot(x, y, 'green', lw=1)

	plt.axis('equal')
	plt.show()

