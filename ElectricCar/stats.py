import math
import ElectricCar.EVRP as EVRP

MAX_TRIALS = 1
log_performance = None  # Used to output offline performance and population diversity
perf_filename = ""  # output files
perf_of_trials = []


# EVRP.problem_instance


def open_stats():
    global perf_of_trials
    global perf_filename
    global log_performance
    global MAX_TRIALS

    # Initialize
    perf_of_trials = [0.0] * MAX_TRIALS

    # get problem name
    name = (EVRP.problem_instance.split('\\')[-1]).split('.')[0]

    # initialize and open output files
    perf_filename = "Statistic/{}.txt".format(name)

    # for performance
    try:
        log_performance = open(perf_filename, mode='w', encoding='UTF-8')
    except:
        print("Can't open file")
        exit(1)


# initialize and open output files


def get_mean(r: int, value: float):
    global perf_of_trials
    perf_of_trials[r] = value


def mean(values, size: int):
    m = 0.0
    for i in range(size):
        m += values[i]

    m = m / float(size)
    return m  # mean


def stdev(values, size: int, average: float):
    dev = 0.0

    if size <= 1:
        return 0.0
    for i in range(size):
        dev += (float(values[i]) - average) * (float(values[i]) - average)
    return math.sqrt(dev / float(size - 1))  # standard deviation


def best_of_vector(values, l: int):
    k = 0
    min = values[k]

    for k in range(1, l):
        if values[k] < min:
            min = values[k]

    return min


def worst_of_vector(values, l: int):
    k = 0
    max = values[k]

    for k in range(1, l):
        if values[k] > max:
            max = values[k]

    return max


def close_stats():
    global MAX_TRIALS
    global log_performance
    global perf_of_trials

    # For statistics
    for i in range(MAX_TRIALS):
        log_performance.write("{0:.2f}".format(perf_of_trials[i]))
        log_performance.write("\n")

    perf_mean_value = mean(perf_of_trials, MAX_TRIALS)
    perf_stdev_value = stdev(perf_of_trials, MAX_TRIALS, perf_mean_value)

    log_performance.write("Mean: {0:.5f}".format(perf_mean_value))
    log_performance.write("\n")
    log_performance.write("Std Dev: {0:.5f}".format(perf_stdev_value))
    log_performance.write("\n")
    log_performance.write("Min: {0:.5f}".format(best_of_vector(perf_of_trials, MAX_TRIALS)))
    log_performance.write("\n")
    log_performance.write("Max: {0:.5f}".format(worst_of_vector(perf_of_trials, MAX_TRIALS)))
    log_performance.write("\n")

    log_performance.close()
