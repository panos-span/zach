from VRP_Model import *


class Solution:
    def __init__(self):
        self.cost = 0.0
        self.routes = []


class Saving:
    def __init__(self, n1, n2, sav):
        self.n1 = n1
        self.n2 = n2
        self.score = sav


def distance(from_node, to_node):
    dx = from_node.x - to_node.x
    dy = from_node.y - to_node.y
    dist = math.sqrt(dx ** 2 + dy ** 2)
    return dist


def calculate_route_details(nodes_sequence):
    rt_load = 0
    rt_cumulative_cost = 0
    tot_time = 0
    for i in range(len(nodes_sequence) - 1):
        from_node = nodes_sequence[i]
        to_node = nodes_sequence[i + 1]
        tot_time += distance(from_node, to_node)
        rt_cumulative_cost += tot_time
        tot_time += to_node.serv_time
        rt_load += from_node.demand
    return rt_cumulative_cost, rt_load


class Solver:
    def __init__(self, m):
        self.allNodes = m.allNodes
        self.customers = m.customers
        self.depot = m.allNodes[0]
        self.distanceMatrix = m.matrix
        self.capacity = m.capacity
        self.sol = None
        self.bestSolution = None

    def solve(self):
        # self.SetRoutedFlagToFalseForAllCustomers()
        self.Clarke_n_Wright()
        self.ReportSolution(self.sol)
        return self.sol

    def SetRoutedFlagToFalseForAllCustomers(self):
        for i in range(0, len(self.customers)):
            self.customers[i].isRouted = False

        for c in self.customers:
            c.isRouted = False

    def ReportSolution(self, sol):
        for i in range(0, len(sol.routes)):
            rt = sol.routes[i]
            for j in range(0, len(rt.sequenceOfNodes)):
                print(rt.sequenceOfNodes[j].ID, end=',')
            print()
            # print(rt.cost)
        print(self.sol.cost)

    # Correct!!
    def CalculateTotalCost(self, sol):
        c = 0
        for i in range(0, len(sol.routes)):
            rt = sol.routes[i]
            cst, load = calculate_route_details(rt.sequenceOfNodes)
            c += cst
            # for j in range(0, len(rt.sequenceOfNodes) - 1):
            #    cst, load = calculate_route_details(rt.sequenceOfNodes)
            #    # a = rt.sequenceOfNodes[j]
            #    # b = rt.sequenceOfNodes[j + 1]
            #    c += cst
            #    # c += self.distanceMatrix[a.ID][b.ID]
        return c

    def UpdateRouteCostAndLoad(self, rt: Route):
        tc = 0
        tl = 0
        cst, load = calculate_route_details(rt.sequenceOfNodes)
        tc += cst
        tl += load
        # for i in range(0, len(rt.sequenceOfNodes) - 1):
        #    A = rt.sequenceOfNodes[i]
        #    B = rt.sequenceOfNodes[i + 1]
        #    tc += self.distanceMatrix[A.ID][B.ID]
        #    tl += A.demand
        rt.load = tl
        rt.cost = tc

    def Clarke_n_Wright(self):
        self.sol = self.create_initial_routes()
        # Problem with scores in savings
        #self.UpdateRouteCostAndLoad(self.sol.routes[0])
        savings: list = self.calculate_savings()
        savings.sort(key=lambda s: s.score, reverse=True)
        for i in range(0, len(savings)):
            sav = savings[i]
            n1 = sav.n1
            n2 = sav.n2
            rt1 = n1.route
            rt2 = n2.route

            if n1.route == n2.route:
                continue
            if self.not_first_or_last(rt1, n1) or self.not_first_or_last(rt2, n2):
                continue
            if rt1.load + rt2.load > self.capacity:
                continue

            self.merge_routes(n1, n2)

            self.sol.cost -= sav.score
            cst = self.CalculateTotalCost(self.sol)

            print(cst, self.sol.cost)



    def calculate_savings(self):
        savings = []
        for i in range(0, len(self.customers)):
            n1 = self.customers[i]
            for j in range(i + 1, len(self.customers)):
                n2 = self.customers[j]
                #cst, load = calculate_route_details([n1,self.depot, self.depot,n2])
                score = self.distanceMatrix[n1.ID][self.depot.ID] + self.distanceMatrix[self.depot.ID][n2.ID]
                score -= self.distanceMatrix[n1.ID][n2.ID]
                #score = cst
                sav = Saving(n1, n2, score)
                savings.append(sav)

        return savings

    def create_initial_routes(self):
        s = Solution()
        for i in range(0, len(self.customers)):
            n = self.customers[i]
            rt = Route(self.depot, self.capacity)
            n.route = rt
            n.position_in_route = 1
            rt.sequenceOfNodes.insert(1, n)
            #cst, load = calculate_route_details(rt.sequenceOfNodes)
            #rt.load = load
            #rt.cost = cst
            rt.load = n.demand
            rt.cost = self.distanceMatrix[self.depot.ID][n.ID] + self.distanceMatrix[n.ID][self.depot.ID]
            #rt.cost = cst
            s.routes.append(rt)
            #s.cost += cst
            s.cost += rt.cost
        return s

    def not_first_or_last(self, rt, n):
        if n.position_in_route != 1 and n.position_in_route != len(rt.sequenceOfNodes) - 2:
            return True
        return False

    def merge_routes(self, n1, n2):
        rt1 = n1.route
        rt2 = n2.route

        if n1.position_in_route == 1 and n2.position_in_route == len(rt2.sequenceOfNodes) - 2:
            # for i in range(len(rt2.sequenceOfNodes) - 2, 0, -1):
            #     n = rt2.sequenceOfNodes[i]
            #     rt1.sequenceOfNodes.insert(1, n)
            rt1.sequenceOfNodes[1:1] = rt2.sequenceOfNodes[1:len(rt2.sequenceOfNodes) - 1]
        elif n1.position_in_route == 1 and n2.position_in_route == 1:
            # for i in range(1, len(rt2.sequenceOfNodes) - 1, 1):
            #     n = rt2.sequenceOfNodes[i]
            #     rt1.sequenceOfNodes.insert(1, n)
            rt1.sequenceOfNodes[1:1] = rt2.sequenceOfNodes[len(rt2.sequenceOfNodes) - 2:0:-1]
        elif n1.position_in_route == len(rt1.sequenceOfNodes) - 2 and n2.position_in_route == 1:
            # for i in range(1, len(rt2.sequenceOfNodes) - 1, 1):
            #     n = rt2.sequenceOfNodes[i]
            #     rt1.sequenceOfNodes.insert(len(rt1.sequenceOfNodes) - 1, n)
            rt1.sequenceOfNodes[len(rt1.sequenceOfNodes) - 1:len(rt1.sequenceOfNodes) - 1] = rt2.sequenceOfNodes[1:len(
                rt2.sequenceOfNodes) - 1]
        elif n1.position_in_route == len(rt1.sequenceOfNodes) - 2 and n2.position_in_route == len(
                rt2.sequenceOfNodes) - 2:
            # for i in range(len(rt2.sequenceOfNodes) - 2, 0, -1):
            #     n = rt2.sequenceOfNodes[i]
            #     rt1.sequenceOfNodes.insert(len(rt1.sequenceOfNodes) - 1, n)
            rt1.sequenceOfNodes[len(rt1.sequenceOfNodes) - 1:len(rt1.sequenceOfNodes) - 1] = rt2.sequenceOfNodes[
                                                                                             len(rt2.sequenceOfNodes) - 2:0:-1]
        rt1.load += rt2.load
        self.sol.routes.remove(rt2)
        self.update_route_customers(rt1)

    def update_route_customers(self, rt):
        for i in range(1, len(rt.sequenceOfNodes) - 1):
            n = rt.sequenceOfNodes[i]
            n.route = rt
            n.position_in_route = i
