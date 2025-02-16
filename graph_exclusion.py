import argparse
from functools import partial
from itertools import chain, combinations
from multiprocessing import Pool
import os
import pickle
import random
import networkx as nx
from networkx import graph_atlas_g
from networkx.drawing.nx_agraph import graphviz_layout
from matplotlib import pyplot as plt
import numpy as np
from collections import defaultdict, deque
from heapq import heappop, heapify, heappush
from networkx.generators.nonisomorphic_trees import nonisomorphic_trees

from tqdm import tqdm

import signal

signal.signal(signal.SIGINT, signal.SIG_DFL)

def bfs(graph, distances, frontier, visited, voronoi):
    while len(frontier) > 0:
        u = frontier.popleft()
        visited[u] = True

        # print('visiting', u, 'with dist', distances[u])

        for v in graph[u]:
            # print('\tchecking', v, 'with dist', distances[v])
            dist = distances[u] + 1
            if dist < distances[v]:
                # print('\t\tupdating', v, 'to', dist)
                distances[v] = dist
                voronoi[v] = set(voronoi[u])
            elif dist == distances[v]:
                # print('\t\tmerging', v, 'with', voronoi[v], 'and', voronoi[u])
                voronoi[v] = voronoi[v].union(voronoi[u])

            if not visited[v]:
                frontier.append(v)


def get_overlapping_voronoi_regions(graph, sources):
    distances = [np.inf for _ in graph.nodes]
    voronoi = [set() for _ in graph.nodes]
    visited = [False for _ in graph.nodes]

    frontier = deque(sources)
    for s in sources:
        distances[s] = 0
        voronoi[s].add(s)
        visited[s] = True
    
    bfs(graph, distances, frontier, visited, voronoi)

    return distances, voronoi


def graph_irv(graph, candidates):
    candidates = candidates[:]


    while len(candidates) > 1:
        distances, voronoi = get_overlapping_voronoi_regions(graph, candidates)

        vote_shares = defaultdict(int)

        for v in voronoi:
            for c in v:
                vote_shares[c] += 1 / len(v) 

        min_vote_share = min(vote_shares.values())
        possible_losers = [c for c in vote_shares if vote_shares[c] == min_vote_share]
        loser = random.choice(possible_losers)
        
        candidates.remove(loser)

    return candidates[0]


def graph_plurality_votes(graph, candidates):
    distances, voronoi = get_overlapping_voronoi_regions(graph, candidates)
    vote_shares = defaultdict(int)

    for v in voronoi:
        for c in v:
            vote_shares[c] += 1 / len(v) 

    return vote_shares

def graph_plurality(graph, candidates):
    vote_shares = graph_plurality_votes(graph, candidates)

    max_vote_share = max(vote_shares.values())
    possible_winners = [c for c, share in vote_shares.items() if share == max_vote_share]

    return random.choice(possible_winners)

def show_grid_dsn(grid_size, k):
    graph = nx.convert_node_labels_to_integers(nx.grid_2d_graph(grid_size, grid_size))
    nodes = list(graph.nodes)

    trials = 10000
    winners = []

    for i in tqdm(range(trials)):
        candidates = random.sample(nodes, k)
        winners.append(graph_irv(graph, candidates))

    win_counts = np.bincount(winners, minlength=len(nodes))
    print(win_counts)

    pos = nx.nx_agraph.graphviz_layout(graph)
    nx_nodes = nx.draw_networkx_nodes(graph, pos, node_color=win_counts, cmap=plt.cm.plasma)

    labels = {i: str(count) for i, count in enumerate(win_counts)}
    nx.draw_networkx_labels(graph, pos, labels, font_size=6, font_color='black')
    nx.draw_networkx_edges(graph, pos)
    plt.colorbar(nx_nodes)
    plt.show()


def powerset(iterable, min_size=0, max_size=None):
    s = list(iterable)
    if max_size is None:
        max_size = len(s)
    return chain.from_iterable(combinations(s, r) for r in range(min_size, max_size+1))


def irv_exclusion_fpt(G, S, hide_output=False):
    if not hide_output:
        print('testing set of size', len(S))
    outside_nodes = set(G.nodes).difference(S)
    for config in powerset(outside_nodes, min_size=1):
        for last_node in S:
            # print(f'checking {last_node} vs {config}')
            vote_shares = graph_plurality_votes(G, config + (last_node,))
            min_vote_share = min(vote_shares.values())
            if vote_shares[last_node] == min_vote_share:
                # print('loss!')
                return False
            # print('win')
    
    return True


def get_pairwise_loss_graph(graph, hide_output=False):
    L = nx.DiGraph()
    L.add_nodes_from(graph.nodes)
    
    n = graph.number_of_nodes()

    condorcet_winners = set(graph.nodes)
    condorcet_losers = set(graph.nodes)

    for (u, v) in tqdm(combinations(graph.nodes, 2), total=n*(n-1)//2, disable=hide_output):
        # if (u, v) != (0, 2): continue
        vote_shares = graph_plurality_votes(graph, (u, v))
        # print(u, v, vote_shares[u], vote_shares[v])

        if vote_shares[u] < vote_shares[v]:
            L.add_edge(u, v)
            condorcet_losers.discard(v)
            condorcet_winners.discard(u)
        elif vote_shares[v] < vote_shares[u]:
            L.add_edge(v, u)
            condorcet_losers.discard(u)
            condorcet_winners.discard(v)
        else:
            L.add_edge(u, v)
            L.add_edge(v, u)

    return L, condorcet_winners, condorcet_losers


def find_minimal_exclusion_zone(graph, hide_output=False):
    L, condorcet_winners, condorcet_losers = get_pairwise_loss_graph(graph, hide_output=hide_output)
    descendant_sets = {node: set(nx.descendants(L, node)) for node in graph.nodes}
    
    if not hide_output:
        print('got pairwise loss graph')

    for S in powerset(graph.nodes, min_size=2, max_size=graph.number_of_nodes()-1):
        impossible = False
        for u in S:
            if len(descendant_sets[u].difference(S)) != 0:
                impossible = True
                break
    
        if not impossible and irv_exclusion_fpt(graph, S, hide_output=hide_output):
            return S, condorcet_winners, condorcet_losers
        
    return graph.nodes, condorcet_winners, condorcet_losers

def find_graph_exclusion_zones():
    zones = {n: [] for n in range(3, 16)}
    for n in range(3, 16):
        print(n)
        for tree in tqdm(nonisomorphic_trees(n)):
            zone, condorcet_winners, condorcet_losers = find_minimal_exclusion_zone(tree, hide_output=True)
            zones[n].append((tree, zone))
                
    with open('results/tree-zones.pickle', 'wb') as f:
        pickle.dump(zones, f)


    graph_zones = {n: [] for n in range(3, 8)}
    for graph in tqdm(graph_atlas_g()):
        n = graph.number_of_nodes()
        if n < 3 or not nx.is_connected(graph):
            continue

        zone, condorcet_winners, condorcet_losers = find_minimal_exclusion_zone(graph, hide_output=True)
        graph_zones[n].append((graph, zone))

    with open('results/graph-zones.pickle', 'wb') as f:
        pickle.dump(graph_zones, f)


def test_condorcet_cycle_graph():
    G = nx.from_edgelist([
        (0, 1),
        (1, 2), 
        (0, 2),
        (0, 3),
        (2, 4),
        (3, 4),
        (4, 5),
        (4, 6),
        (4, 7),
        (5, 6),
        (6, 8),
        (7, 8),
        (8, 9),
        (8, 10),
        (8, 11),
        (9, 10),
        (10, 0),
        (11, 0)
    ])
    L, condorcet_winners, condorcet_losers = get_pairwise_loss_graph(G)
    zone, condorcet_winners, condorcet_losers = find_minimal_exclusion_zone(G, hide_output=True)

    pos = nx.nx_agraph.graphviz_layout(G)
    nx.draw(G, pos, node_color=['red' if node in zone else 'blue' for node in G.nodes])
    plt.show()
    plt.close()




def find_probable_approximate_exclusion_zone(graph, epsilon, delta, hide_output=False):
    if not hide_output:
        print('Getting pairwise loss graph...')
    L, condorcet_winners, condorcet_losers = get_pairwise_loss_graph(graph, hide_output=hide_output)
    descendant_sets = {node: set(nx.descendants(L, node)) for node in graph.nodes}

    S = set()
    candidates = list(graph.nodes)
    n = graph.number_of_nodes()
    
    if not hide_output:
        print('Getting initial S...')
    
    for i in tqdm(range(n), disable=hide_output):
        irv_winner = graph_irv(graph, candidates)
        S.add(irv_winner)

    for u in set(S):
        S.update(descendant_sets[u])

    rng = np.random.default_rng()

    if not hide_output:
        print('Growing S...')
    
    cur_iter = 0
    last_update = 0
    n_iters = int(np.ceil(np.log(2/delta) / (2 * epsilon**2)))
    pbar = tqdm(total=n_iters, disable=hide_output)
    while cur_iter - last_update < n_iters:
        if len(S) == n:
            break
        
        X = list(set([rng.choice(list(S))] + [u for u, selected in zip(graph.nodes, rng.integers(0, 2, n)) if selected]))
        winner = graph_irv(graph, X)
        if winner not in S:
            S.add(winner)
            S.update(descendant_sets[winner])
            last_update = cur_iter

            if not hide_output:
                print(f'Grew S! Cur size: {len(S)} / {n}')
                print(f'Added winner {winner}, descendants {descendant_sets[winner]}')

            pbar.close()
            pbar = tqdm(total=n_iters, disable=hide_output)

        cur_iter += 1
        pbar.update(1)

    pbar.close()

    if not hide_output:
        print(f'Done! Took {cur_iter} iterations.')
    
    return S


if __name__ == '__main__':
    find_graph_exclusion_zones()
    # test_condorcet_cycle_graph()