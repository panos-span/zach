import math
import sol_checker
import pprint


class Node:
    def __init__(self, idd, xx, yy, dem=0, st=0):
        self.x = xx
        self.y = yy
        self.ID = idd
        self.isRouted = False
        self.demand = dem
        self.serv_time = st


class Model:

    # instance variables
    def __init__(self):
        all_nodes, vehicles, capacity = sol_checker.load_model('Instance.txt')
        self.allNodes = all_nodes
        self.vehicles = vehicles
        self.matrix = []
        self.capacity = capacity

    def BuildModel(self):
        rows = len(self.allNodes)
        self.matrix = [[0.0 for x in range(rows)] for y in range(rows)]

        for i in range(0, len(self.allNodes)):
            for j in range(0, len(self.allNodes)):
                a = self.allNodes[i]
                b = self.allNodes[j]
                dist = math.sqrt(math.pow(a.x - b.x, 2) + math.pow(a.y - b.y, 2))
                self.matrix[i][j] = dist


def distance(from_node, to_node):
    dx = from_node.x - to_node.x
    dy = from_node.y - to_node.y
    dist = math.sqrt(dx ** 2 + dy ** 2)
    return dist


class Route:
    def __init__(self, dp, cap):
        self.sequenceOfNodes = []
        self.sequenceOfNodes.append(dp)
        self.sequenceOfNodes.append(dp)
        self.cost = 0
        self.capacity = cap
        self.load = 0


# all_nodes, vehicles, capacity = sol_checker.load_model('Instance.txt')
# for i in range(len(all_nodes)):
#    print(all_nodes[i].ID,all_nodes[i].x, all_nodes[i].y, all_nodes[i].demand, all_nodes[i].serv_time)


# m = Model()
# m.BuildModel()
# pprint.pprint(m.matrix)
# for i in range(len(m.matrix)):
#    for j in range(len(m.matrix)):
#        if m.matrix[i][j] != m.matrix[j][i]:
#            print('ERROR')


def bin_packing():
    m = Model()
    m.BuildModel()
    cap = [m.capacity for i in range(m.vehicles)]
    bins = [[m.allNodes[0].ID] for i in range(m.vehicles)]
    ids = [0 for i in range(0, len(m.allNodes))]
    f = False
    for node in m.allNodes:
        if not f:
            f = True
            continue
        for i in range(len(cap)):
            if cap[i] >= node.demand:
                bins[i].append(node.ID)
                cap[i] -= node.demand
                break
    return bins, cap

bins, cap = bin_packing()
pprint.pprint(bins)
pprint.pprint(cap)
