#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <libgen.h>
#include "vote.h"
#include "graph.h"
#include "queue.h"

/**
 * Generate a random integer between min and max
 * Credit: https://stackoverflow.com/a/18386648/6866505
 * @param min the minimum value
 * @param max the maximum value
 * @return a random integer
*/
int randint(int min, int max){
    return min + rand() / (RAND_MAX / (max - min + 1) + 1);
}


/**
 * Get the vote shares of the candidates
 * @param graph the graph
 * @param cands the candidates
 * @param k the number of candidates
 * @return an array of vote shares
 */
float *get_vote_shares(struct Graph *graph, int *cands, int k) {
    float *votes = malloc(k * sizeof(int));

    // visited[i] = 1 if node i has been visited
    int *visited = malloc(graph->n * sizeof(int));

    // distances[i] = shortest distance from any candidate to node i
    int *distances = malloc(graph->n * sizeof(int));

    // voronoi[i][j] = 1 if node i is in the voronoi region of the jth candidate
    int **voronoi = malloc(graph->n * sizeof(int *));


    for (int i = 0; i < graph->n; i++) {
        visited[i] = 0;
        distances[i] = -1;
        voronoi[i] = calloc(k, sizeof(int));
    }

    struct Queue *queue = new_queue(graph->n);

    for (int i = 0; i < k; i++) {
        distances[cands[i]] = 0;
        visited[cands[i]] = 1;
        voronoi[cands[i]][i] = 1;
        enqueue(queue, cands[i]);
    }

    int dist;
    struct AdjListNode *nbr;
    int node;

    // Run BFS to find the Voronoi regions of the candidates
    while (queue->size > 0) {
        node = dequeue(queue);
        visited[node] = 1;
        nbr = graph->adjLists[node].next;

        // printf("visiting %d with dist %d\n", node, distances[node]);

        while (nbr != NULL) {
            dist = distances[node] + 1;
            // printf("\tchecking %d with dist %d\n", nbr->node, distances[nbr->node]);
            if (dist < distances[nbr->node] || distances[nbr->node] == -1) {
                // printf("\tupdating %d to %d\n", nbr->node, dist);
                distances[nbr->node] = dist;
                for (int i = 0; i < k; i++) {
                    voronoi[nbr->node][i] = voronoi[node][i];
                }
            } else if (dist == distances[nbr->node]) {
                // printf("\tmerging %d, new: ", nbr->node);
                for (int i = 0; i < k; i++) {
                    voronoi[nbr->node][i] = voronoi[node][i] | voronoi[nbr->node][i];
                    // printf("%d ", voronoi[nbr->node][i]);
                }
                // printf("\n");
            }

            if (!visited[nbr->node]) {
                enqueue(queue, nbr->node);
            }

            nbr = nbr->next;
        }
    }

    // Each voter votes for the candidates in their Voronoi region, splitting their vote equally
    for (int voter = 0; voter < graph->n; voter++) {
        
        // Count the number of candidates in whose Voronoi region the voter is in
        int count = 0;
        for (int i = 0; i < k; i++) {
            count += voronoi[voter][i];
        }
        
        for (int i = 0; i < k; i++) {
            if (voronoi[voter][i]) {
                votes[i] += 1.0 / count;
            }
        }
    }

    free(visited);
    free_queue(queue);
    for (int i = 0; i < graph->n; i++) {
        free(voronoi[i]);
    }
    free(voronoi);
    free(distances);

    return votes;
}

/**
 * Get the index of the smallest entry in the input array,
 * breaking ties uniformly at random
 * @param arr the input array
 * @param n the length of the array
 * @return the index of the smallest entry
 */
int argmin_random(float *arr, int n) {
    int min_val = arr[0];
    int index = 0;
    int count = 1;

    // Find the minimum value
    for (int i = 1; i < n; i++) {
        if (arr[i] < min_val) {
            min_val = arr[i];
            count = 1;
            index = i;
        } else if (arr[i] == min_val) {
            count++;
        }
    }

    // If there are multiple minimum values, pick one uniformly at random
    if (count > 1) {
        int picked = randint(0, count-1);
        for (int i = 0; i < n; i++) {
            if (arr[i] == min_val) {
                if (picked == 0) {
                    index = i;
                    break;
                } else {
                    picked--;
                }
            }
        }
    }

    return index;
}


/**
 * Graph IRV. Sorts the candidates in reverse elimination order, so that
 * cands[0] is the winner after the method completes.
 * @param graph the graph
 * @param cands the candidates
 * @param k the number of candidates
 */
void graph_irv(struct Graph *graph, int *cands, int k) {
    float *votes;
    int tmp;
    int min_index;

    while (k > 1) {
        votes = get_vote_shares(graph, cands, k);
        min_index = argmin_random(votes, k);
        free(votes);

        tmp = cands[min_index];
        cands[min_index] = cands[k - 1];
        cands[k - 1] = tmp;

        k--;
    }
}


/**
 * Get the pairwise loss graph of a voting graph, with an edge from i to j 
 * if votes(i) <= votes(j) in the pairwise contest i vs j
 * @param graph the graph
 * @return the pairwise loss graph
 */
struct Graph *pairwise_loss_graph(struct Graph *graph) {
    struct Graph *loss_graph = new_graph(graph->n);
    int pair[2] = {0, 0};

    // print_graph(graph);

    for (int i = 0; i < graph->n; i++) {
        // printf("i: %d\n", i);
        for (int j = i+1; j < graph->n; j++) {

            pair[0] = i;
            pair[1] = j;
            float *votes = get_vote_shares(graph, pair, 2);

            // printf("%d, %d, %f, %f\n", i, j, votes[0], votes[1]);

            if (votes[0] <= votes[1]) {
                add_edge(loss_graph, i, j);
            }

            if (votes[1] <= votes[0]) {
                add_edge(loss_graph, j, i);
            }

            free(votes);
        }
    }
    return loss_graph;
}


/**
 * Count the number of nonzero entries in an int array
 * @param arr the array
 * @param n the length of the array
 * @return the number of nonzero entries
*/
int count_nonzero(int *arr, int n) {
    int count = 0;
    for (int i = 0; i < n; i++) {
        if (arr[i]) {
            count++;
        }
    }
    return count;
}

/**
 * Find a probable approximate exclusion zone of a graph, returning a pointer
 * to an length n int array where zone[i] = 1 if i is in the zone
 * @param graph the graph
 * @param epsilon the approximation factor
 * @param delta the failure probability
 * @return a probable approximate exclusion zone
 */
int *find_probable_approximate_exclusion_zone(struct Graph *graph, float epsilon, float delta) {
    int *S = calloc(graph->n, sizeof(int));

    // printf("Getting pairwise loss graph...\n");
    struct Graph *loss_graph = pairwise_loss_graph(graph);
    int **loss_reachability = get_reachability_matrix(loss_graph); 

    // printf("Getting initial S...\n");
    int *cands = malloc(graph->n * sizeof(int));
    for (int i = 0; i < graph->n; i++) {
        cands[i] = i;
    }

    // Initial S contains IRV winner(s) with a candidate at every node
    for (int i = 0; i < graph->n; i++) {
        graph_irv(graph, cands, graph->n);
        S[cands[0]] = 1;
        for (int j = 0; j < graph->n; j++) {
            if (loss_reachability[cands[0]][j]) {
                S[j] = 1;
            }
        }
    }

    // printf("intial S: ");
    // for (int i = 0; i < graph->n; i++) {
    //     printf("%d ", S[i]);
    // }
    // printf("\n");

    // Number of iterations we want with no updates to S
    int T = log(2 / delta) / (2 * epsilon * epsilon) + 1;
    int cur_iter = 0;
    int last_update = 0;
    int S_size;
    int k;
    while (cur_iter - last_update < T) {
        
        S_size = count_nonzero(S, graph->n);
        if (S_size == graph->n) {
            break;
        }

        // if (cur_iter % 100 == 0) {
        //     printf("iter: %d / %d, S size: %d\n", cur_iter - last_update, T, S_size);
        // }

        // initialize X to be a random subset of nodes
        k = 0;
        for (int i = 0; i < graph->n; i++) {
            if (rand() % 2) {
                cands[k++] = i;
            }
        }

        // Make sure X has at least one element from S
        int idx = randint(0, S_size - 1);
        for (int i = 0; i < graph->n; i++) {
            if (S[i]) {
                if (idx == 0) {
                    int has_i = 0;
                    for (int j = 0; j < k; j++) {
                        if (cands[j] == i) {
                            has_i = 1;
                            break;
                        }
                    }
                    if (!has_i) {
                        cands[k++] = i;
                    }
                    break;
                } else {
                    idx--;
                }
            }
        }

        // Run IRV on cands
        graph_irv(graph, cands, k);

        // Update S
        if (S[cands[0]] == 0) {
            last_update = cur_iter;

            // printf("Updated S with winner %d\n", cands[0]);

            S[cands[0]] = 1;
            for (int j = 0; j < graph->n; j++) {
                if (loss_reachability[cands[0]][j]) {
                    S[j] = 1;
                    // printf("\tAdded descdendant %d to S\n", j);
                }
            }
        }

        cur_iter++;
    }

    free(cands);
    free_graph(loss_graph);
    for (int i = 0; i < graph->n; i++) {
        free(loss_reachability[i]);
    }
    free(loss_reachability);
   
    return S;
}


int main(int argc, char **argv) {
    srand(0);

    if (argc != 2) {
        fprintf(stderr, "Usage: %s <graph file>\n", argv[0]);
        exit(1);
    }

    struct Graph *graph = load_graph(argv[1]);

    // struct Graph *loss_graph = pairwise_loss_graph(graph);


    // int **reachability = get_reachability_matrix(loss_graph);
    // for (int i = 0; i < graph->n; i++) {
    //     printf("%d: ", i);
    //     for (int j = 0; j < graph->n; j++) {
    //         if (reachability[i][j]) {
    //             printf("%d ", j);
    //         }
    //     }
    //     printf("\n");
    // }
    // free_graph(loss_graph);
    // exit(0);

    int *S = find_probable_approximate_exclusion_zone(graph, 0.01, 0.01);

    FILE *fptr;
    char buf[100];
    snprintf(buf, 100, "../results/school-zones/zone-%s", basename(argv[1]));

    // Open a file in writing mode
    fptr = fopen(buf, "w");
    for (int i = 0; i < graph->n; i++) {
        if (S[i])
            fprintf(fptr, "%d\n", i);
    }

    // Close the file
    fclose(fptr);

    free_graph(graph);
    free(S);
    // free(cands);

    return 0;
}

// Ran with 
// find ../data/schools/*.txt -print0 | xargs -0 -t -I % -P 30 ./graph_voting %