import os
import pickle
import networkx as nx
import pandas as pd
import signal


signal.signal(signal.SIGINT, signal.SIG_DFL)



def preprocess_data():
    df = pd.read_csv('data/ICPSR_37070/DS0001/37070-0001-Data.tsv', sep='\t')

    edge_cols = [f'ST{i}W2' for i in range(1, 11)]

    for col in edge_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(-1).astype(int)

    graphs = dict()

    os.makedirs('data/schools', exist_ok=True)

    for school, group in df.groupby('SCHID'):
        nodes = (group['UID'] % 10000).values
        edges = []
        for _, row in group.iterrows():
            for col in edge_cols:
                if row[col] > 0:
                    edges.append((row[col], row['UID'] % 10000))
    
        G = nx.Graph()
        G.add_nodes_from(nodes)
        G.add_edges_from(edges)
        G.remove_edges_from(nx.selfloop_edges(G))
        G = G.subgraph(max(nx.connected_components(G), key=len))
        mapping = {node: i for i, node in enumerate(G.nodes)}
        G = nx.relabel_nodes(G, mapping)



        if len(G.nodes) > 1:
            graphs[school] = G
            fname = f'data/schools/school-{school}.txt'
            with open(fname, 'w') as f:
                f.write(f'{len(G.nodes)}\n')
                for node in G.nodes:
                    f.write(f'{node}')
                    for neighbor in G[node]:
                        f.write(f' {neighbor}')
                    f.write('\n')


    with open('data/schools.pickle', 'wb') as f:
        pickle.dump(graphs, f)




if __name__ == '__main__':
    preprocess_data()
