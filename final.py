import random
import timeit
from copy import deepcopy
from math import sqrt, pow
from time import time


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
                # calculate distance between two nodes taking into account the serving time
                dist = sqrt(pow(a.x - b.x, 2) + pow(a.y - b.y, 2)) + a.serv_time
                self.matrix[i][j] = dist
                # for the diagonal elements, assign a very large value (big_value=100000)
                if i == j:
                    self.matrix[i][j] = big_value


# put every node in the vehicle that has more capacity each time
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

    return binsID  # returns the IDs of the nodes in each vehicle


# calculates the time needed for each route
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


# prepare the cost matrix for TSP in each bin
# if the node is not in the bin
# we assign big_value=100000 in every column and row
# that it is present so that it is not selected in the TSP algorithm
def tsp_matrix(bin):
    m = Model()
    m.BuildModel()
    for i in range(len(m.matrix)):
        for j in range(len(m.matrix)):
            if i not in bin or j not in bin:
                m.matrix[i][j] = big_value
    return m.matrix


# TSP nearest neighbour in a bin
def tsp(bins):
    orders = []
    for bin in bins:
        order = []
        cost_matrix = tsp_matrix(bin)
        order.append(bin[0])  # node 0 is always the first node of the route
        for i in range(len(cost_matrix)):
            cost_matrix[i][0] = big_value  # assign the cost in the first column as 100000
            # so that node 0 is not selected again
        while len(order) < len(bin):  # if we haven't ordered all the nodes
            # find the node that is shortest to the last ordered node
            i = order[-1]
            temp = cost_matrix[i][:]
            min_index = temp.index(min(temp))
            order.append(min_index)
            for i in range(len(cost_matrix)):
                cost_matrix[i][min_index] = big_value  # assign the cost in the ordered node's column
                # as 100000 so that it is not selected again
        orders.append(order)
    return orders  # returns the bin with the nodes order with the nearest neighbour method


# Calculates cumulative cost for all the routes (the objective function)
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
                for l in range(1, len(final_routes[j])-1):
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


def OrOptCrossRoute(routes, matrix, all_nodes):
    # Or-opt move cross route
    # Or-opt for each pair of routes
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
                    new_route1[k:k + 1] = final_routes[j][l:l + 1]
                    new_route2[l:l + 1] = final_routes[i][k:k + 1]

                    new_cost, new_load = calculate_route_details(new_route1, matrix, all_nodes)
                    new_cost += calculate_route_details(new_route2, matrix, all_nodes)[0]
                    if new_cost < cost and new_load <= capacity:
                        final_routes[i] = new_route1
                        final_routes[j] = new_route2
                        cost = new_cost
                        load = new_load
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


def VND(temp, matrix, all_nodes):
    # Variable neighborhood descent
    k = 0
    total = CalculateTotalCost(temp)
    while k < 5:
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
            temp, total_cost = OrOptCrossRoute(temp, matrix, all_nodes)
            if total_cost < total:
                total = total_cost
                k = 0
            else:
                k += 1
        elif k == 4:
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
    j = 1
    while time() < end:  # run VNS for 179 seconds, result 6134 comes up at the 171st loop
        # "shaking" action for the routes
        for i in range(len(shaker)):
            copy1 = shaker[i][1:]
            random.shuffle(copy1)
            shaker[i][1:] = copy1
        temp, cost = VND(shaker, matrix, all_nodes)
        if cost < total:
            total = cost
            final_routes = deepcopy(temp)
        print(j, cost)
        j += 1
    return final_routes, total


if __name__ == '__main__':
    print("Start")
    start = timeit.default_timer()
    # Initialise "magic" variable
    global big_value
    big_value = 100000
    # set the assignment's data
    m = Model()
    m.BuildModel()
    global capacity
    capacity = m.capacity
    matrix = m.matrix
    all_nodes = m.allNodes

    # create initial solution with a greedy algorithm
    bins = bin_packing(m)
    routes = tsp(bins)

    # provide the initial solution to the VNS method
    random.seed(1)  # seed 3 = 6185.988925532871
    routes, total_cost = VNS(routes, matrix, all_nodes)

    print("Total cost: ", total_cost)

    # Write the solution in solution.txt file
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
    print("Processing time: ", stop - start)
