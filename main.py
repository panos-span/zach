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
        self.customers = all_nodes[1:]
        self.matrix = []
        self.capacity = capacity

    def BuildModel(self):
        rows = len(self.allNodes)
        self.matrix = [[0.0 for x in range(rows)] for y in range(rows)]

        for i in range(0, len(self.allNodes)):
            for j in range(0, len(self.allNodes)):
                a = self.allNodes[i]
                b = self.allNodes[j]
                dist = math.sqrt(math.pow(a.x - b.x, 2) + math.pow(a.y - b.y, 2)) + a.serv_time
                self.matrix[i][j] = dist
                if i == j:
                    self.matrix[i][j] = 100000


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


def bin_packing(m):
    cap = [m.capacity for _ in range(m.vehicles)]
    # bins = [[m.allNodes[0]] for _ in range(m.vehicles)]
    binsID = [[m.allNodes[0].ID] for _ in range(m.vehicles)]
    all_nodes = m.allNodes
    all_nodes.sort(key=lambda s: s.demand, reverse=True)
    for node in all_nodes:
        if node.ID == 0:
            break
        max_index = cap.index(max(cap))
        binsID[max_index].append(node.ID)
        cap[max_index] -= node.demand

    return binsID


def calculate_route_details(nodes_sequence, matrix):
    rt_cumulative_cost = 0
    tot_time = 0

    for i in range(len(nodes_sequence) - 1):
        from_node = nodes_sequence[i]
        to_node = nodes_sequence[i + 1]
        tot_time += matrix[from_node][to_node]
        rt_cumulative_cost += tot_time
    return rt_cumulative_cost

def tsp_matrix(bin):
    m = Model()
    m.BuildModel()
    for i in range(len(m.matrix)):
        for j in range(len(m.matrix)):
            if i not in bin or j not in bin:
                m.matrix[i][j] = 100000
    return m.matrix


def tsp(bins):
    orders = []
    for bin in bins:
        order = []
        cost_matrix = tsp_matrix(bin)
        order.append(bin[0])
        for i in range(len(cost_matrix)):
            cost_matrix[i][0] = 100000
        while (len(order) < len(bin)):
            i = order[-1]
            temp = cost_matrix[i][:]
            min_index = temp.index(min(temp))
            order.append(min_index)
            for i in range(len(cost_matrix)):
                cost_matrix[i][min_index] = 100000
        orders.append(order)
    return orders


m = Model()
m.BuildModel()
matrix = m.matrix
all_nodes = m.allNodes
bins = bin_packing(m)
orders = tsp(bins)
cost = 0
for order in orders:
    for x in order:
        if order.index(x) == len(order) - 1:
            print(x, end='')
            break
        print(x, end=',')
    print()

total_cost = 0
for order in orders:
    cost = calculate_route_details(order, matrix)
    total_cost += cost
print(total_cost)
