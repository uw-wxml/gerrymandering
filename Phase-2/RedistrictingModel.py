import UdGraph
import IowaFileParser
import math
import random

"""
Mathematics of Gerrymandering, Phase 2
Washington Experimental Mathematics Lab, 18 Wi
Project GitHub: https://github.com/weifanjiang/WXML-18wi-Research

This file contains the model to perform Metropolis-Ising algorithm on
a graph which represents an actual state
"""


class RedistrictingModel:

    def __init__(self, alpha, beta, num_districts, iter):
        """
        Construct a model to simulate Metropolis Algorithm on data of a real-life state
        :param alpha: weight of population energy
        :param beta: weight of compactness energy
        :param num_districts: number of districts in this state
        :param: iter: number of iterations of random walk
        """
        self.alpha = alpha
        self.beta = beta
        self.num_districts = num_districts
        self.iter = iter
        self.g = IowaFileParser.IowaFileParser.parse_alex()
        self.population_map = IowaFileParser.IowaFileParser.parse_namyoung()
        self.total_population = 0
        for v in self.population_map.keys():
            self.total_population += self.population_map[v]

    @staticmethod
    def count_marks(g, s, x, m):
        """
        Return the number of vertices in s that are marked x in mapping m
        :param g: graph g
        :param s: subset of vertex s
        :param x: marking that we want to count
        :param m: mapping from s to marks
        :return: an int
        """
        confirm_start = (random.sample(s, 1))[0]
        connected = set()
        connected.add(confirm_start)
        active = [confirm_start, ]
        while active != []:
            curr = active[0]
            active = active[1:]
            curr_nei = g.get_neighbors(curr)
            for v in curr_nei:
                if v not in connected and v in s and m[v] == x:
                    connected.add(v)
                    active.append(v)
        return len(connected)

    @staticmethod
    def split_into_2(g, s, a, b):
        """
        Split a set of vertices into 2 groups
        :param g: graph
        :param s: subset of vertices in g
        :param a: marker for group 1
        :param b: marker for group 2
        :return: a dict maps from elements in s to either a or b
        """
        ret = {}
        start = (random.sample(s, 1))[0]
        ret[start] = a
        prob = 1.0 / len(s)
        curr = start
        potential = set()
        while len(ret.keys()) < len(s) - 1:
            curr_prob = random.uniform(0.0, 1.0)
            if math.fabs(curr_prob - prob) <= 0.01:
                break
            curr_neighbors = g.get_neighbors(curr)
            in_s = set()
            for v in curr_neighbors:
                if v in s:
                    in_s.add(v)
            if len(in_s) == 0:
                curr = (random.sample(potential, 1))[0]
                potential.remove(curr)
            else:
                curr = (random.sample(in_s, 1))[0]
                for v in in_s:
                    if v != curr and v not in potential:
                        potential.add(v)
            ret[curr] = a
        non_chosen = set()
        for v in s:
            if v not in ret.keys():
                non_chosen.add(v)
        confirm_start = (random.sample(non_chosen, 1))[0]
        connected = set()
        connected.add(confirm_start)
        curr = confirm_start
        active = [confirm_start, ]
        while active != []:
            curr = active[0]
            active = active[1:]
            curr_nei = g.get_neighbors(curr)
            for v in curr_nei:
                if v not in connected and v in non_chosen:
                    connected.add(v)
                    active.append(v)
        if len(connected) + len(ret.keys()) == len(s):
            for v in connected:
                ret[v] = b
            return ret
        return RedistrictingModel.split_into_2(g, s, a, b)

    def get_random_redistricting_4(self):
        """
        Return a random redistricting plan of current state
        This method brute_forcely split whole map into 4 groups, as in Iowa
        :return: a dict representation of redistricting plan, which key is the precinct number and value
            is a number from 1 to self_num_districts indicating which district it belongs to.
        """
        initial_split = RedistrictingModel.split_into_2(self.g, self.g.get_nodes(), "a", "b")
        first_half = set()
        second_half = set()
        for v in initial_split.keys():
            if initial_split[v] == "a":
                first_half.add(v)
            else:
                second_half.add(v)
        one_two = RedistrictingModel.split_into_2(self.g, first_half, "1", "2")
        three_four = RedistrictingModel.split_into_2(self.g, second_half, "3", "4")
        ret = {}
        for v in one_two.keys():
            ret[v] = one_two[v]
        for v in three_four.keys():
            ret[v] = three_four[v]
        return ret

    def get_current_borders(self, plan):
        """
        Return a set of edges which joins two precincts in different districts
        :param plan: map from precinct to district number
        :return: set of edges
        """
        all_edges = self.g.get_edges()
        ret = set()
        for e in all_edges:
            precincts = e.split(" ")
            if plan[precincts[0]] != plan[precincts[1]]:
                ret.add(e)
        return ret

    def get_next_redistricting_helper(self, currplan):
        """
        Returns another valid redistricting plan which only differs from current plan by 1 precinct.
        And also its border set,
        :param currplan: current redistricting plan
        :return: the new redistricting plan, or null on failure
        """
        candidate = {}
        for v in currplan.keys():
            candidate[v] = currplan[v]
        border = self.get_current_borders(currplan)
        sample = (random.sample(border, 1))[0]
        vertices = sample.split(" ")
        if random.uniform(0.0, 1.0) < 0.5:
            candidate[vertices[0]] = candidate[vertices[1]]
        else:
            candidate[vertices[1]] = candidate[vertices[0]]
        confirm = 0
        for i in range(1, self.num_districts + 1):
            confirm += RedistrictingModel.count_marks(self.g, self.g.get_nodes(), str(i), candidate)
        if confirm == self.g.get_node_count():
            return candidate
        else:
            return None

    def get_next_redistricting(self, currplan):
        """
        Returns another valid redistricting plan which only differs from current plan by 1 precinct.
        And also its border set,
        :param currplan: current redistricting plan
        :return: the new redistricting plan
        """
        result = None
        while result == None:
            result = self.get_next_redistricting_helper(currplan)
        return result

    def compress_energy(self, plan):
        """
        Compute the compress energy of current redistricting plan
        :param plan: a redistricting plan
        :return: energy
        """
        return None

    def population_energy(self, plan):
        """
        Compute the population energy of current redistricting plan
        :param plan: a redistricting plan
        :return: energy
        """
        return None

    def get_prob_ratio(self, curr_plan, candidate):
        """
        Compute the probability ratio of candidate redistricting plan and current redistricting plan
        :param curr_plan: current redistricting plan
        :param candidate: candidate redistricting plan
        :return: float
        """
        exponential = self.alpha * self.compress_energy(candidate) + self.beta * self.population_energy(candidate)
        exponential -= self.alpha * self.compress_energy(curr_plan) + self.beta * self.population_energy(curr_plan)
        return math.exp(exponential)

    @staticmethod
    def run():
        """
        Main method which promps user for parameters and start simulation
        """
        return None


test = RedistrictingModel(1, 2, 4, 10)
m = test.get_random_redistricting_4()
print(m)
x = test.get_next_redistricting(m)
print(x)