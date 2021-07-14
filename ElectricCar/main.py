import random
import EVRP as EVRP
import heuristic as heuristic
import stats as stats
from visualize import draw_graph
import RL
import MST
import numpy as np

# initialiazes a run for your heuristic
def start_run(r: int):
    random.seed(r)  # Random seed
    EVRP.init_evals()
    EVRP.init_current_best()
    print("Run: {} with random seed {}".format(r, r))


# gets an observation of the run for your heuristic
def end_run(r: int):
    stats.get_mean(r - 1, EVRP.get_current_best())
    print("End of run {} with best solution quality {} total evaluations: {}".format(r, EVRP.get_current_best(),
                                                                                     EVRP.get_evals()))


# sets the termination conidition for your heuristic
def termination_condition():
    flag = False

    if EVRP.get_evals() >= EVRP.TERMINATION:
        flag = True
    return flag


'''
/****************************************************************/
/*                Main Function                                 */
/****************************************************************/
'''
if __name__ == "__main__":
    # Step 1
    EVRP.problem_instance = "E:\Vinh\CS106-AI\CS106-IntroAI\evrp-benchmark-set\E-n22-k4.evrp"  # pass the .evrp filename as an argument
    EVRP.read_problem(EVRP.problem_instance)  # Read EVRP from file from EVRP.py
    size_of_node = len(EVRP.node_list)
    Mst_algo = MST.Graph(len(EVRP.node_list))
    d = np.zeros((size_of_node, size_of_node))
    for i in range(len(EVRP.node_list)):
        for j in range(len(EVRP.node_list)):
            if i != j:
                d[i][j] = EVRP.get_distance(EVRP.node_list[i][0], EVRP.node_list[j][0])

    for i in range(len(EVRP.node_list)):
        for j in range(len(EVRP.node_list)):
            if i != j:
                Mst_algo.addEdge(EVRP.node_list[i][0], EVRP.node_list[j][0], d[i][j])

    Mst_algo.KruskalMST()
    """

    # Step 2
    stats.open_stats()  # open text files to store the best values from the 20 runs stats.py

    for run in range(1, stats.MAX_TRIALS + 1):
        # Step 3
        start_run(run)

        # Step 4
        while not termination_condition():
            # Execute your heuristic
            heuristic.run_heuristic()

        best_route = heuristic.remove_duplicate_node(EVRP.get_current_best_route())
        EVRP.check_solution(best_route, len(best_route))

        # Step 5
        end_run(run)  # store the best solution quality for each run

        # Draw graph
        draw_graph(EVRP.get_current_best_route(), EVRP.node_list, EVRP.cust_demand, EVRP.charging_station, EVRP.ACTUAL_PROBLEM_SIZE)

    # Step 6
    stats.close_stats()  # close text files to calculate the mean result from the 20 runs stats.py

"""
