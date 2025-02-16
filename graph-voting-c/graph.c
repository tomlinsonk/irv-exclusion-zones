#include <stdlib.h>
#include <stdio.h>
#include "graph.h"
#include "queue.h"


/**
 * Free the memory allocated for the graph
 * @param graph the graph to free
*/
void free_graph(struct Graph *graph) {
    for (int i = 0; i < graph->n; i++) {
        struct AdjListNode *node = graph->adjLists[i].next;
        struct AdjListNode *tmp;
        
        while (node != NULL) {
            tmp = node;
            node = node->next;
            free(tmp);
        }
    }

    free(graph->adjLists);
    free(graph);
}

/**
 * Create a new graph
 * @param n the number of nodes in the graph
 * @return a pointer to the new graph
*/
struct Graph *new_graph(int n) {
    struct Graph *graph = malloc(sizeof(struct Graph));
    graph->n = n;
    graph->adjLists = malloc(n * sizeof(struct AdjListNode));

    for (int i = 0; i < n; i++) {
        graph->adjLists[i].node = i;
        graph->adjLists[i].next = NULL;
    }

    return graph;
}

/**
 * Load a graph stored in a file
 * @param filename the name of the file to load
*/
struct Graph *load_graph(const char *filename) {
    FILE *file = fopen(filename, "r");
    if (file == NULL) {
        fprintf(stderr, "Error: could not open file %s\n", filename);
        exit(1);
    }

    int n;
    fscanf(file, "%d\n", &n);

    struct Graph *graph = new_graph(n);

    int node;
    char next_char;
    int neighbor;

    while (fscanf(file, "%d", &node) == 1) {
        while ((next_char = fgetc(file)) != '\n') {
            ungetc(next_char, file);
            fscanf(file, "%d", &neighbor);
            struct AdjListNode *new_node = malloc(sizeof(struct AdjListNode));
            new_node->node = neighbor;
            new_node->next = graph->adjLists[node].next;
            graph->adjLists[node].next = new_node;
        }
    }

    return graph;
}

/**
 * Check if the edge (u, v) is in the graph
 * @param graph the graph
 * @param u the first node
 * @param v the second node
 * @return 1 if the edge is in the graph, 0 otherwise
*/
int has_edge(struct Graph *graph, int u, int v) {
    struct AdjListNode *node = graph->adjLists[u].next;
    while (node != NULL) {
        if (node->node == v) {
            return 1;
        }
        node = node->next;
    }
    return 0;
}


/**
 * Add an edge (u, v) to the graph, if not already present
 * @param graph the graph
 * @param u the first node
 * @param v the second node
*/
void add_edge(struct Graph *graph, int u, int v) {
    if (has_edge(graph, u, v)) {
        return;
    }
    struct AdjListNode *new_node = malloc(sizeof(struct AdjListNode));
    new_node->node = v;
    new_node->next = graph->adjLists[u].next;
    graph->adjLists[u].next = new_node;
}

/**
 * Print the graph
 * @param graph the graph to print
*/
void print_graph(struct Graph *graph) {
    for (int i = 0; i < graph->n; i++) {
        printf("%d: ", i);
        struct AdjListNode *node = graph->adjLists[i].next;
        while (node != NULL) {
            printf("%d ", node->node);
            node = node->next;
        }
        printf("\n");
    }
}

/**
 * Get the reachability matrix of the graph, where reachable[i][j] = 1
 * if there is a path from i to j
 * @param graph the graph
 * @return the reachability matrix   
*/
int **get_reachability_matrix(struct Graph *graph) {
    int **reachable = malloc(graph->n * sizeof(int *));
    for (int i = 0; i < graph->n; i++) {
        reachable[i] = calloc(graph->n, sizeof(int));
    }

    // BFS from each node to find the reachable nodes
    for (int i = 0; i < graph->n; i++) {
        struct Queue *queue = new_queue(graph->n);
        enqueue(queue, i);
        reachable[i][i] = 1;

        while (queue->size > 0) {
            int node = dequeue(queue);
            struct AdjListNode *nbr = graph->adjLists[node].next;

            while (nbr != NULL) {
                if (!reachable[i][nbr->node]) {
                    reachable[i][nbr->node] = 1;
                    enqueue(queue, nbr->node);
                }
                nbr = nbr->next;
            }
        }

        free_queue(queue);
    }

    return reachable;
}

