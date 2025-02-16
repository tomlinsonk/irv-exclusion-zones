#ifndef GRAPH_H
#define GRAPH_H



struct Graph {
    int n;
    struct AdjListNode *adjLists;
};

struct AdjListNode {
    int node;
    struct AdjListNode *next;
};



struct Graph *new_graph(int n);
void free_graph(struct Graph *graph);
struct Graph *load_graph(const char *filename);
void print_graph(struct Graph *graph);
int **get_reachability_matrix(struct Graph *graph);
void add_edge(struct Graph *graph, int u, int v);
int has_edge(struct Graph *graph, int u, int v);

#endif // GRAPH_H