import UdGraph
import WashingtonModel
import paramFuncCollection

g = UdGraph.UdGraph()

master = open("master.csv", "r").readlines()
for line in master:
    tokens = line.replace("\r", "").replace("\n", "").replace('\xef\xbb\xbf', '').split(",")
    g.add_node(int(tokens[0]))
    g.add_node(int(tokens[1]))
    g.add_edge(int(tokens[0]), int(tokens[1]))

bound = set()
border = open("border_precincts.csv", "r").readlines()
for line in border:
    border_precinct = int(line.split(",")[0])
    bound.add(border_precinct)

population = dict()
pop = open("precinct_pop.txt", "r").readlines()
for line in pop:
    tokens = line.replace("\n", "").split("\t")
    population[int(tokens[0])] = int(tokens[1])

initial = dict()
ini = open("initial.txt", "r").readlines()
for line in ini:
    tokens = line.replace("\n", "").split("\t")
    initial[int(tokens[0])] = int(tokens[1])

randomWalkLength = 1000  # No magic numbers : )

model = WashingtonModel.WashingtonModel(g, bound, population, 10)
sampleRedistricting = model.run(initial, randomWalkLength, paramFuncCollection.more_population)

for precinct, district in sampleRedistricting.iteritems():
    print(str(precinct) + "\t" + str(district))
