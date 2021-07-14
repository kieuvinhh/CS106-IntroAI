import EVRP
import numpy as np


def CWS():
    a = len(EVRP.node_list)
    c = np.zeros((a, a))
    print(c.shape)
    s = []
    for i in range(a):
        for j in range(a):
            if i != j:
                c[i][j] = EVRP.get_distance(EVRP.node_list[i][0], EVRP.node_list[j][0])

    for i in range(a):
        for j in range(a):
            if i!= j:
                s.append([i, j, c[0][i] + c[j][0] - c[i][j]])

    for i in range(len(s)):
        s.sort(key=lambda x: x[2], reverse=True)
    route = [0]
    print(s)
    size_s = len(s)
    for i in range(0, size_s):
        if s[i][0] not in route:
            route.append(s[i][0])
        if s[i][1] not in route:
            route.append(s[i][1])
    route.append(0)
    print(route)