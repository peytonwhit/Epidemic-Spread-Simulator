from geopy.distance import geodesic
import networkx as nx
import csv
import random
import matplotlib.pyplot as plt
import math

#add nodes to the network using the airport data
airportid_to_data = {}
fh = open('airports.dat.txt', 'r', encoding='utf-8')
reader = csv.reader(fh, delimiter=',')
for line in reader:
    node_id = int(line[0])
    airport_name = line[1]
    city = line[2]
    country = line[3]
    lat = float(line[6])
    lon = float(line[7])

    airportid_to_data[node_id] = [ airport_name, city, country, lat, lon]

fh.close()

G = nx.DiGraph()

#add edges between airports using the routes data, giving a completed mobility network
fh = open('routes.dat.txt', 'r', encoding='utf-8')
reader = csv.reader(fh, delimiter=',')
for line in reader:

    try:
        source_id = int(line[3])
        target_id = int(line[5])
        if source_id not in airportid_to_data.keys():
            print(source_id)
            continue
        if target_id not in airportid_to_data.keys():
            print(target_id)
            continue
        if G.has_edge(source_id,target_id):
            G[source_id][target_id]['w'] += 1
        else:
            G.add_edge(source_id,target_id,w=1)
    except:
        print(line)

fh.close()




#SI initialization
n = G.number_of_nodes()
p_to_state = { node: 'S' for node in G.nodes() }

#keeps track of the effective distance from the origin along the infection path
effective_distance_from_origin= { node: 0 for node in G.nodes()}
infected = []
S = n
X = 0



#computes node with highest in-degree using big (for use in outbreak_location)
"""
big=0
for node in G.nodes():
    if G.in_degree(node)> big:
        big = G.in_degree(node)
"""
#computes node with highest out-degree using big (for use in outbreak_location)
"""
big=0
for node in G.nodes():
    if G.out_degree(node)>big:
        big=G.out_degree(node)
"""
# intially infect 1 node
#3077 for Hong Kong
#1824 for Mexico
outbreak_location = 3077
p_to_state[outbreak_location] = 'I'
infected.append(outbreak_location)
X += 1
S -= 1

#lists for graphing
ts = [0]
ss = [S/n]
xs = [X/n]
#effective distance list(from outbreak location)
d = []

#actual distance list(from outbreak location)
ad = []

# arrival time for disease at node
at = []


#infect the rest of the nodes
t=1
while t<160:
    print(t,X)
    nodes_to_infect = []

    for node in infected:
        for nei in G.neighbors(node):
            if p_to_state[nei] == 'S':
                # all passengers to node m
                p_from_all = 0
                for pred in G.predecessors(nei):
                    p_from_all += G[pred][nei]['w'] * 416
                #passengers from n->m
                p_to_nei_from_node = G[node][nei]['w'] * 416
                # computes the effecive distance from node->nei
                eff_d=1-(math.log10(p_to_nei_from_node/p_from_all))
                beta = 1/ eff_d
                assert(beta >= 0 and beta <= 1)
                if random.random() < beta * 0.05:
                    nodes_to_infect.append(nei)
                    #computes effective distance of node being infected and outbreak location
                    effective_distance_from_origin[nei]= effective_distance_from_origin[node] + eff_d
                    d.append(effective_distance_from_origin[nei])
                    at.append(t)
                    #computes geographic distance between node getting infected and outbreak location
                    lat1, lon1 = airportid_to_data[outbreak_location][3], airportid_to_data[outbreak_location][4]
                    lat2, lon2 = airportid_to_data[nei][3], airportid_to_data[nei][4]
                    d_euc = geodesic((lat1, lon1),(lat2, lon2)).miles
                    ad.append(d_euc)


    for node in set(nodes_to_infect):
        p_to_state[node] = "I"
        infected.append(node)
        S -= 1
        X += 1

    ts.append(t)
    ss.append(S/n)
    xs.append(X/n)

    if X == n:
        break
    t+=1

"""
print(ts)
print(d)
print(at)
print(ad)
"""



print(outbreak_location)

plt.plot(ts, xs, 'o-', lw=5, label='infected', alpha=0.5)
plt.plot(ts, ss, 'o-', lw=5, label='susceptible', alpha=0.5)
plt.xlabel('t', fontsize=25)
plt.ylabel('f(t)', fontsize=25)
plt.legend(loc='best', fontsize=20)
plt.ylim(0,1)
#plt.savefig('Spread1.pdf')
