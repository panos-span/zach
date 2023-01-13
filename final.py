from math import sqrt, pow
import random
from time import time
import timeit
from copy import deepcopy

def load_model(file_name):
    all_nodes = []
    all_lines = list(open(file_name, "r"))

    separator = ','

    line_counter = 0
    ln = all_lines[line_counter]
    no_spaces = ln.split(sep=separator)
    vehicles = int(no_spaces[1])

    line_counter += 1
    ln = all_lines[line_counter]
    no_spaces = ln.split(sep=separator)
    capacity = int(no_spaces[1])

    line_counter += 1
    ln = all_lines[line_counter]
    no_spaces = ln.split(sep=separator)
    tot_customers = int(no_spaces[1])

    line_counter += 3
    ln = all_lines[line_counter]

    no_spaces = ln.split(sep=separator)
    x = float(no_spaces[1])
    y = float(no_spaces[2])
    depot = Node(0, x, y)
    all_nodes.append(depot)

    for i in range(tot_customers):
        line_counter += 1
        ln = all_lines[line_counter]
        no_spaces = ln.split(sep=separator)
        idd = int(no_spaces[0])
        x = float(no_spaces[1])
        y = float(no_spaces[2])
        demand = int(no_spaces[3])
        serv_time = int(no_spaces[4])
        customer = Node(idd, x, y, demand, serv_time)
        all_nodes.append(customer)

    return all_nodes, vehicles, capacity


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
        all_nodes, vehicles, capacity = load_model('Instance.txt')
        self.allNodes = {node.ID: node for node in all_nodes}
        self.vehicles = vehicles
        self.matrix = []
        self.capacity = capacity

    def BuildModel(self):
        rows = len(self.allNodes)
        self.matrix = [[0.0 for _ in range(rows)] for _ in range(rows)]
        for i in range(0, len(self.allNodes)):
            for j in range(0, len(self.allNodes)):
                a = self.allNodes[i]
                b = self.allNodes[j]
                dist = sqrt(pow(a.x - b.x, 2) + pow(a.y - b.y, 2)) + a.serv_time
                self.matrix[i][j] = dist
                if i == j:
                    self.matrix[i][j] = 100000


class Route:
    def __init__(self, dp, cap):
        self.sequenceOfNodes = []
        self.sequenceOfNodes.append(dp)
        self.sequenceOfNodes.append(dp)
        self.cost = 0
        self.capacity = cap
        self.load = 0


def bin_packing(m):
    cap = [m.capacity for _ in range(m.vehicles)]
    binsID = [[m.allNodes[0].ID] for _ in range(m.vehicles)]
    all_nodes = list(m.allNodes.values())
    all_nodes.sort(key=lambda s: s.demand, reverse=True)
    for node in all_nodes:
        if node.ID == 0:
            continue
        max_index = cap.index(max(cap))
        binsID[max_index].append(node.ID)
        cap[max_index] -= node.demand

    return binsID


def calculate_route_details(nodes_sequence, matrix, all_nodes):
    rt_cumulative_cost = 0
    rt_load = 0
    tot_time = 0

    for i in range(len(nodes_sequence) - 1):
        from_node = nodes_sequence[i]
        to_node = nodes_sequence[i + 1]
        tot_time += matrix[from_node][to_node]
        rt_cumulative_cost += tot_time
        rt_load += all_nodes[from_node].demand
    return rt_cumulative_cost, rt_load


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
        while len(order) < len(bin):
            i = order[-1]
            temp = cost_matrix[i][:]
            min_index = temp.index(min(temp))
            order.append(min_index)
            for i in range(len(cost_matrix)):
                cost_matrix[i][min_index] = 100000
        orders.append(order)
    return orders


def CalculateTotalCost(routes):
    total_cost = 0
    for route in routes:
        cost, load = calculate_route_details(route, matrix, all_nodes)
        total_cost += cost
    return total_cost


def CrossRouteSwapMove(routes, matrix, all_nodes):
    # Cross route swap move
    # Cross route swap for each pair of routes
    final_routes = routes
    for i in range(len(routes)):
        for j in range(len(routes)):
            if i != j:
                route = routes[i]
                route2 = routes[j]
                cost, load = calculate_route_details(route, matrix, all_nodes)
                cost2, load2 = calculate_route_details(route2, matrix, all_nodes)
                final_route = route
                final_route2 = route2
                for k in range(1, len(final_route) - 1):
                    for l in range(1, len(final_route2) - 1):
                        new_route = final_route[:]
                        new_route2 = final_route2[:]
                        new_route[k], new_route2[l] = new_route2[l], new_route[k]
                        new_cost, new_load = calculate_route_details(new_route, matrix, all_nodes)
                        new_cost2, new_load2 = calculate_route_details(new_route2, matrix, all_nodes)
                        if new_cost < cost and new_load <= capacity and new_cost2 < cost2 and new_load2 <= capacity:
                            final_routes[i] = new_route
                            final_routes[j] = new_route2
                            cost = new_cost
                            cost2 = new_cost2
    total_cost = CalculateTotalCost(final_routes)
    return final_routes, total_cost


def TwoOptMoveCrossRoute(routes, matrix, all_nodes):
    # 2-opt move cross route
    # 2-opt for each pair of routes
    final_routes = routes
    for i in range(len(final_routes)):
        for j in range(len(final_routes)):
            if i == j:
                continue
            cost, load = calculate_route_details(final_routes[i], matrix, all_nodes)
            cost += calculate_route_details(final_routes[j], matrix, all_nodes)[0]
            for k in range(1, len(final_routes[i])):
                for l in range(1, len(final_routes[j])):
                    new_route1 = final_routes[i][:]
                    new_route2 = final_routes[j][:]
                    new_route1[k:] = final_routes[j][l:]
                    new_route2[l:] = final_routes[i][k:]

                    new_cost, new_load = calculate_route_details(new_route1, matrix, all_nodes)
                    new_cost += calculate_route_details(new_route2, matrix, all_nodes)[0]
                    if new_cost < cost and new_load <= capacity:
                        final_routes[i] = new_route1
                        final_routes[j] = new_route2
                        cost = new_cost
    total_cost = CalculateTotalCost(final_routes)
    return final_routes, total_cost


def SwapMove(routes, matrix, all_nodes):
    # Swap move
    # Swap for each route
    final_routes = []
    for route in routes:
        cost, load = calculate_route_details(route, matrix, all_nodes)
        final_route = route
        for i in range(1, len(final_route) - 1):
            for j in range(i + 1, len(final_route)):
                new_route = final_route[:]
                new_route[i], new_route[j] = new_route[j], new_route[i]
                new_cost, new_load = calculate_route_details(new_route, matrix, all_nodes)
                if new_cost < cost and new_load <= capacity:
                    final_route = new_route
                    cost = new_cost
        final_routes.append(final_route)
    total_cost = CalculateTotalCost(final_routes)
    return final_routes, total_cost


def RelocationMove(routes, matrix, all_nodes):
    # Relocation move
    # Relocation for each route
    final_routes = []
    for route in routes:
        cost, load = calculate_route_details(route, matrix, all_nodes)
        final_route = route
        for i in range(1, len(final_route)):
            for j in range(1, len(final_route)):
                if i == j:
                    continue
                new_route = final_route[:]
                new_route.insert(j, new_route.pop(i))
                new_cost, new_load = calculate_route_details(new_route, matrix, all_nodes)
                if new_cost < cost and new_load <= capacity:
                    final_route = new_route
                    cost = new_cost
        final_routes.append(final_route)
    total_cost = CalculateTotalCost(final_routes)
    return final_routes, total_cost


def VND(temp, matrix, all_nodes):  # 5,3,4,1,2,0,6
    # Variable neighborhood descent
    # 5 types of moves
    # 5 types of neighborhoods
    k = 0
    total = CalculateTotalCost(temp)
    while k < 4:
        # k = random.randint(0, 7)
        if k == 0:
            temp, total_cost = CrossRouteSwapMove(temp, matrix, all_nodes)
            if total_cost < total:
                total = total_cost
                k = 0
            else:
                k += 1
        elif k == 1:
            temp, total_cost = TwoOptMoveCrossRoute(temp, matrix, all_nodes)
            if total_cost < total:
                total = total_cost
                k = 0
            else:
                k += 1
        elif k == 3:
            temp, total_cost = SwapMove(temp, matrix, all_nodes)
            if total_cost < total:
                total = total_cost
                k = 0
            else:
                k += 1
        elif k == 2:
            temp, total_cost = RelocationMove(temp, matrix, all_nodes)
            if total_cost < total:
                total = total_cost
                k = 0
            else:
                k += 1
    return temp, total


def VNS(final_routes, matrix, all_nodes):
    # Variable neighborhood search
    end = time() + 179
    total = CalculateTotalCost(final_routes)
    temp = final_routes
    shaker = temp
    j = 0
    while time() < end:  # result 6185 comes up at the 207th loop
        j +=1
        for i in range(len(shaker)):
            copy1 = shaker[i][1:]
            random.shuffle(copy1)
            shaker[i][1:] = copy1
        temp, cost = VND(shaker, matrix, all_nodes)
        if cost < total:
            total = cost
            final_routes = deepcopy(temp)
        if cost < 6138:
            break
        print(j, cost)
    return final_routes, total


if __name__ == '__main__':
    print("Start")
    start = timeit.default_timer()
    m = Model()
    m.BuildModel()
    global capacity
    capacity = m.capacity
    matrix = m.matrix
    all_nodes = m.allNodes
    bins = bin_packing(m)
    routes = tsp(bins)
    random.seed(3)  # seed 3 = 6185.988925532871
    routes, total_cost = VNS(routes, matrix, all_nodes)

    print("Total cost: ", total_cost)

    f = open("solution.txt", "w")
    f.write("Cost:\n" + str(total_cost) + "\n")
    f.write("Routes:\n" + str(len(routes)) + "\n")

    for route in routes:
        for x in route:
            if route.index(x) == len(route) - 1:
                f.write(str(x) + "\n")
                break
            f.write(str(x) + ",")
    f.close()
    stop = timeit.default_timer()
    print("End")
    print("Proccessing time: ", stop - start)
   #total_cost = 0
   #for route in routes:
   #    cost, load = calculate_route_details(route, matrix, all_nodes)
   #    total_cost += cost
   #print(total_cost)