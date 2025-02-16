import os
import matplotlib.pyplot as plt
import numpy as np
import pickle
import networkx as nx

# allow keyboard interrupt to close pyplot
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)


def plot_school_zones():
    with open('data/schools.pickle', 'rb') as f:
        graphs = pickle.load(f)

    zones = dict()

    node_counts = []
    for i, graph in graphs.items():
        with open(f'results/school-zones/zone-school-{i}.txt', 'r') as f:
            lines = f.readlines()
            zone = {int(line.strip()) for line in lines}

        zones[i] = zone
        
        # print(i, len(zone), graph.number_of_nodes())

        node_counts.append(graph.number_of_nodes())

    print('Avg nodes', np.mean(node_counts))
    print('Min nodes', min(node_counts))
    print('Max nodes', max(node_counts))

    trivial = sum(1 if len(zones[i]) == graphs[i].number_of_nodes() else 0 for i in graphs)
    print('trivial count:', trivial)
    print('trivial frac:', trivial / len(graphs))
    print('Mean size:', np.mean([len(zones[i]) / len(graphs[i]) for i in graphs ]))
    print('Mean size without outlier:', np.mean([len(zones[i]) / len(graphs[i]) for i in graphs if i != 26]))
    
    print('Mean size of nontrivial:', np.mean([len(zones[i]) / len(graphs[i]) for i in graphs  if len(zones[i]) / len(graphs[i]) != 1]))
    print('Mean size of nontrivial without outlier:', np.mean([len(zones[i]) / len(graphs[i]) for i in graphs if i != 26 and len(zones[i]) / len(graphs[i]) != 1]))

    print('Min size:', np.min([len(zones[i]) / len(graphs[i]) for i in graphs]))
    print('Min size without outlier:', np.min([len(zones[i]) / len(graphs[i]) for i in graphs if i != 26]))


    print('AFTER RERUNNING 26:')
    with open(f'results/school-zones/high-precision-zone-school-26.txt', 'r') as f:
        lines = f.readlines()
        zone = {int(line.strip()) for line in lines}
        zones[26] = zone

    trivial = sum(1 if len(zones[i]) == graphs[i].number_of_nodes() else 0 for i in graphs)
    print('trivial count:', trivial)
    print('trivial frac:', trivial / len(graphs))
    print('Mean size:', np.mean([len(zones[i]) / len(graphs[i]) for i in graphs ]))
    print('Mean size of nontrivial:', np.mean([len(zones[i]) / len(graphs[i]) for i in graphs  if len(zones[i]) / len(graphs[i]) != 1]))
    print('Min size:', np.min([len(zones[i]) / len(graphs[i]) for i in graphs]))

    print('Size of 26:', len(zones[26]), len(graphs[26]))

    for school_num in (5, 50):
        pos = nx.spring_layout(graphs[school_num], seed=5)
        # nx.draw_networkx_nodes(graphs[school_num], pos, node_color=['blue' if node in zones[school_num] else 'white' for node in graphs[school_num].nodes], edgecolors='black', linewidths=1, node_size=60)
        # nx.draw_networkx_edges(graphs[school_num], pos)

        nx.draw(graphs[school_num], node_color=['blue' if node in zones[school_num] else 'red' for node in graphs[school_num].nodes], pos=pos, node_size=100, font_size=8, font_color='white', linewidths=0.5, edgecolors='black')
        plt.savefig(f'plots/school-{school_num}.pdf', bbox_inches='tight')
        plt.close()




def plot_small_zone():
    with open('data/schools.pickle', 'rb') as f:
        graphs = pickle.load(f)

    with open('results/school-zones/zone-school-26.txt', 'r') as f:
        lines = f.readlines()
        zone = {int(line.strip()) for line in lines}

    graph = graphs[26]

    nx.draw(graph, node_color=['red' if node in zone else 'blue' for node in graph.nodes], with_labels=True, node_size=200, font_size=8, font_color='white')
    plt.show()


def plot_tree_zones():
    with open('results/tree-zones.pickle', 'rb') as f:
        zones = pickle.load(f)

    print('\n\n')

    print('$n$ & \# Trees & \# Nontrivial & \# 2-node\\\\')
    for n in range(3, 16):
        num_connected = 0
        num_nontrivial = 0
        num_smallest = 0
        for graph, zone in zones[n]:
            num_connected += 1
            if len(zone) < n:
                num_nontrivial += 1
            if len(zone) == 2:
                num_smallest += 1

        print(f'${n}$ & ${num_connected}$ & ${num_nontrivial}$ & ${num_smallest}$\\\\')

    # for i in range(3, 16):
    #     for tree, zone in zones[i]:
    #         max_degree = max(d for n, d in tree.degree())

            # if len(zone) == 2 and max_degree == 3:
            #     pos = nx.nx_agraph.graphviz_layout(tree)
            #     nx.draw(tree, pos, node_color=['red' if node in zone else 'blue' for node in tree.nodes])
            #     plt.show()
            #     plt.close()

    # max_degrees = []
    # zone_sizes = []
    # for tree, zone in zones[15]:
    #     max_degrees.append(max(d for n, d in tree.degree()))
    #     zone_sizes.append(len(zone))

        # if max_degrees[-1] == 3 and zone_sizes[-1] == 2:
        #     pos = nx.nx_agraph.graphviz_layout(tree)
        #     nx.draw(tree, pos, node_color=['red' if node in zone else 'blue' for node in tree.nodes])
        #     plt.show()


    # plt.scatter(max_degrees, zone_sizes)
    # plt.xlabel('Max degree')
    # plt.ylabel('Zone size')
    # plt.title('All trees on 15 nodes')
    # plt.show()


def plot_graph_zones():
    with open('results/graph-zones.pickle', 'rb') as f:
        zones = pickle.load(f)

    max_degrees = []
    zone_sizes = []
    for graph, zone in zones[7]:
        max_degrees.append(max(d for n, d in graph.degree()))
        zone_sizes.append(len(zone))

        # if max_degrees[-1] == 3 and zone_sizes[-1] == 2:
        #     pos = nx.nx_agraph.graphviz_layout(graph)
        #     nx.draw(graph, pos, node_color=['red' if node in zone else 'blue' for node in graph.nodes])
        #     plt.show()


    # plt.scatter(max_degrees, zone_sizes)
    # plt.xlabel('Max degree')
    # plt.ylabel('Zone size')
    # plt.title('All connected graphs on 7 nodes')
    # plt.show()

    print('\n\n')
    print('$n$ & \# Connected Graphs & \# Nontrivial & \# 2-node\\\\')
    for n in range(3, 8):
        num_connected = 0
        num_nontrivial = 0
        num_smallest = 0
        for graph, zone in zones[n]:
            num_connected += 1
            if len(zone) < n:
                num_nontrivial += 1
            if len(zone) == 2:
                num_smallest += 1

        print(f'${n}$ & ${num_connected}$ & ${num_nontrivial}$ & ${num_smallest}$\\\\')
    



if __name__ == '__main__':
    os.makedirs('plots/', exist_ok=True)

    plot_school_zones()
    plot_graph_zones()
    plot_tree_zones()
