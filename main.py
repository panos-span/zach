import math
import random

import sol_checker
from time import time


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
        while (len(order) < len(bin)):
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


# def CrossExchangeMove(routes, matrix, all_nodes):
#    # Cross exchange move
#    # Cross exchange for each route
#    final_routes = []
#    for route in routes:
#        cost, load = calculate_route_details(route, matrix, all_nodes)
#        final_route = route
#        for i in range(1, len(final_route) - 2):
#            for j in range(i + 1, len(final_route) - 1):
#                for k in range(j + 1, len(final_route) - 1):
#                    for l in range(k + 1, len(final_route)):
#                        new_route = final_route[:]
#                        new_route[i:j] = final_route[k:l]
#                        new_route[k:l] = final_route[i:j]
#                        new_cost, new_load = calculate_route_details(new_route, matrix, all_nodes)
#                        if new_cost < cost and new_load <= 200:
#                            final_route = new_route
#                            cost = new_cost
#                            load = new_load
#        final_routes.append(final_route)
#    total_cost = CalculateTotalCost(final_routes)
#    return final_routes, total_cost


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
                        if new_cost < cost and new_load <= 200 and new_cost2 < cost2 and new_load2 <= 200:
                            final_routes[i] = new_route
                            final_routes[j] = new_route2
                            cost = new_cost
                            load = new_load
                            cost2 = new_cost2
                            load2 = new_load2
    total_cost = CalculateTotalCost(final_routes)
    return final_routes, total_cost


def CrossOrOptMove(routes, matrix, all_nodes):
    # Cross Or-opt move
    # Cross Or-opt for each route
    final_routes = []
    for route in routes:
        cost, load = calculate_route_details(route, matrix, all_nodes)
        final_route = route
        for i in range(1, len(final_route) - 2):
            for j in range(i + 1, len(final_route) - 1):
                for k in range(j + 1, len(final_route) - 1):
                    if i == k or j == k:
                        continue
                    new_route = final_route[:]
                    new_route[i:j] = final_route[k:j]
                    new_route[k:j] = final_route[i:j]
                    new_cost, new_load = calculate_route_details(new_route, matrix, all_nodes)
                    if new_cost < cost and new_load <= 200:
                        final_route = new_route
                        cost = new_cost
                        load = new_load
        final_routes.append(final_route)
    total_cost = CalculateTotalCost(final_routes)
    return final_routes, total_cost


def TwoOptMove(routes, matrix, all_nodes):
    # Cross 2-opt move
    # Cross 2-opt for each route
    final_routes = []
    for route in routes:
        cost, load = calculate_route_details(route, matrix, all_nodes)
        final_route = route
        for i in range(1, len(final_route) - 2):
            for j in range(i + 1, len(final_route) - 1):
                new_route = final_route[:]
                new_route[i:j] = final_route[i:j][::-1]
                new_cost, new_load = calculate_route_details(new_route, matrix, all_nodes)
                if new_cost < cost and new_load <= 200:
                    final_route = new_route
                    cost = new_cost
                    load = new_load
        final_routes.append(final_route)
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
            for k in range(1, len(final_routes[i]) - 1):
                for l in range(1, len(final_routes[j]) - 1):
                    new_route1 = final_routes[i][:]
                    new_route2 = final_routes[j][:]
                    new_route1[k:] = final_routes[j][l:]
                    new_route2[l:] = final_routes[i][k:]

                    new_cost, new_load = calculate_route_details(new_route1, matrix, all_nodes)
                    new_cost += calculate_route_details(new_route2, matrix, all_nodes)[0]
                    if new_cost < cost and new_load <= 200:
                        final_routes[i] = new_route1
                        final_routes[j] = new_route2
                        cost = new_cost
                        load = new_load
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
                if new_cost < cost and new_load <= 200:
                    final_route = new_route
                    cost = new_cost
                    load = new_load
        final_routes.append(final_route)
    total_cost = CalculateTotalCost(final_routes)
    return final_routes, total_cost


def CrossExchangeMove(routes, matrix, all_nodes):
    # Cross exchange move
    # Cross exchange for each route
    final_routes = []
    for route in routes:
        cost, load = calculate_route_details(route, matrix, all_nodes)
        final_route = route
        for i in range(1, len(final_route) - 2):
            for j in range(i + 1, len(final_route) - 1):
                for k in range(j + 1, len(final_route) - 1):
                    for l in range(k + 1, len(final_route)):
                        new_route = final_route[:]
                        new_route[i:j] = final_route[k:l]
                        new_route[k:l] = final_route[i:j]
                        new_cost, new_load = calculate_route_details(new_route, matrix, all_nodes)
                        if new_cost < cost and new_load <= 200:
                            final_route = new_route
                            cost = new_cost
                            load = new_load
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
        for i in range(1, len(final_route) - 1):
            for j in range(1, len(final_route)):
                if i == j:
                    continue
                new_route = final_route[:]
                new_route.insert(j, new_route.pop(i))
                new_cost, new_load = calculate_route_details(new_route, matrix, all_nodes)
                if new_cost < cost and new_load <= 200:
                    final_route = new_route
                    cost = new_cost
                    load = new_load
        final_routes.append(final_route)
    total_cost = CalculateTotalCost(final_routes)
    return final_routes, total_cost


def RelocationMoveCrossRoute(routes, matrix, all_nodes):
    # Relocation move cross route
    # Relocation for each pair of routes
    final_routes = routes
    for i in range(len(final_routes)):
        for j in range(len(final_routes)):
            if i == j:
                continue
            cost, load = calculate_route_details(final_routes[i], matrix, all_nodes)
            cost += calculate_route_details(final_routes[j], matrix, all_nodes)[0]
            for k in range(1, len(final_routes[i]) - 1):
                for l in range(1, len(final_routes[j]) - 1):
                    new_route1 = final_routes[i][:]
                    new_route2 = final_routes[j][:]
                    new_route1.insert(l, new_route1.pop(k))
                    new_cost, new_load = calculate_route_details(new_route1, matrix, all_nodes)
                    new_cost += calculate_route_details(new_route2, matrix, all_nodes)[0]
                    if new_cost < cost and new_load <= 200:
                        final_routes[i] = new_route1
                        final_routes[j] = new_route2
                        cost = new_cost
                        load = new_load
    total_cost = CalculateTotalCost(final_routes)
    return final_routes, total_cost


def RVNS(routes, matrix, all_nodes):
    # Randomized Variable Neighborhood Search
    # Randomly select a move
    # If the move improves the solution, accept it
    # Otherwise, reject it and try another move
    # Stop when no move can improve the solution
    final_routes = routes
    cost = CalculateTotalCost(final_routes)
    new_cost = cost
    new_routes = []
    while True:
        move = random.randint(1, 6)
        if move == 1:
            new_routes, new_cost = TwoOptMove(final_routes, matrix, all_nodes)
        elif move == 2:
            new_routes, new_cost = TwoOptMoveCrossRoute(final_routes, matrix, all_nodes)
        elif move == 3:
            new_routes, new_cost = SwapMove(final_routes, matrix, all_nodes)
        elif move == 4:
            new_routes, new_cost = CrossExchangeMove(final_routes, matrix, all_nodes)
        elif move == 5:
            new_routes, new_cost = RelocationMove(final_routes, matrix, all_nodes)
        elif move == 6:
            new_routes, new_cost = RelocationMoveCrossRoute(final_routes, matrix, all_nodes)
        if new_cost < cost:
            final_routes = new_routes
            cost = new_cost
        else:
            break
    return final_routes, cost


def VND(routes, matrix, all_nodes): #4,3,1,2,0,5
    # Variable neighborhood descent
    # 5 types of moves
    # 5 types of neighborhoods
    k = 0
    total = CalculateTotalCost(routes)
    #random.seed(seed)  # seed 11 cost = 6650.517105958828!!
    while k < 6:
        k = random.randint(0, 5)
        # print(k)
        if k == 4:
            routes, total_cost = CrossRouteSwapMove(routes, matrix, all_nodes)
            if total_cost < total:
                total = total_cost
                k = 0
            else:
                k += 1
        elif k == 3:
            routes, total_cost = TwoOptMoveCrossRoute(routes, matrix, all_nodes)
            if total_cost < total:
                total = total_cost
                k = 0
            else:
                k += 1
        elif k == 1:
            routes, total_cost = SwapMove(routes, matrix, all_nodes)
            if total_cost < total:
                total = total_cost
                k = 0
            else:
                k += 1
        elif k == 2:
            routes, total_cost = RelocationMove(routes, matrix, all_nodes)
            if total_cost < total:
                total = total_cost
                k = 0
            else:
                k += 1
        elif k == 0:
            routes, total_cost = TwoOptMove(routes, matrix, all_nodes)
            if total_cost < total:
                total = total_cost
                k = 0
            else:
                k += 1
        elif k == 5:
            routes, total_cost = RelocationMoveCrossRoute(routes, matrix, all_nodes)
            if total_cost < total:
                total = total_cost
                k = 0
            else:
                k += 1
    return routes, total


def VNS(routes, matrix, all_nodes):
    # Variable neighborhood search
    # 5 types of moves
    # 5 types of neighborhoods
    # 5 times of VND

    end = time() + 10
    total = CalculateTotalCost(routes)
    temp = routes
    while time() < end:
        for i in range(len(temp)):
            random.shuffle(temp[i][1:])
        temp, cost = VND(temp, matrix, all_nodes)
        if cost < total:
            total = cost
            routes = temp

    return routes, total


m = Model()
m.BuildModel()
matrix = m.matrix
all_nodes = m.allNodes
bins = bin_packing(m)
orders = tsp(bins)

# for order in orders:
#    for x in order:
#        if order.index(x) == len(order) - 1:
#            print(x, end='')
#            break
#        print(x, end=',')
#    print()
#
# total_cost = 0
# for order in orders:
#    cost, load = calculate_route_details(order, matrix, all_nodes)
#    total_cost += cost
# print(total_cost)

# routes = CrossExchangeMove(orders, matrix, all_nodes)

# routes = RelocationMove(orders, matrix, all_nodes, total_cost)
# routes = SwapMove(routes, matrix, all_nodes, total_cost)
# routes = TwoOptMove(routes, matrix, all_nodes, total_cost)
# routes = OrOptMove(routes, matrix, all_nodes, total_cost)

# routes, total_cost = VND(orders, matrix, all_nodes)
# routes, total_cost = VND(orders, matrix, all_nodes)
# routes, total_cost = TwoOptMoveCrossRoute(orders, matrix, all_nodes)
# routes, total_cost = CrossRouteSwapMove(orders, matrix, all_nodes)
# routes, total_cost = CrossExchangeMove(routes, matrix, all_nodes)

random.seed(2) # seed 2 cost = 6652.208781106111!!
routes, total_cost = VNS(orders, matrix, all_nodes)
print(total_cost)

for route in routes:
    for x in route:
        print(x, end=',')
    print()
total_cost = 0
for route in routes:
    cost, load = calculate_route_details(route, matrix, all_nodes)
    total_cost += cost
print(total_cost)
