#include <stdlib.h>
#include "queue.h"


/**
 * Create a new queue with a given capacity
 * @param capacity the capacity of the queue
 * @return a pointer to the new queue
*/
struct Queue *new_queue(int capacity) {
    struct Queue *queue = malloc(sizeof(struct Queue));
    queue->capacity = capacity;
    queue->front = 0;
    queue->size = 0;
    queue->rear = capacity - 1;
    queue->array = malloc(capacity * sizeof(int));
    return queue;
}

/** 
 * Free the memory allocated for the queue
 * @param queue the queue to free
*/
void free_queue(struct Queue *queue) {
    free(queue->array);
    free(queue);
}

/**
 * Enqueue an element in the queue
 * @param queue the queue
 * @param item the item to enqueue
*/
void enqueue(struct Queue *queue, int item) {
    // Resize the queue if necessary and copy the elements
    if (queue->size == queue->capacity) {
        int *new_array = malloc(2 * queue->capacity * sizeof(int));
        for (int i = 0; i < queue->size; i++) {
            new_array[i] = queue->array[(queue->front + i) % queue->capacity];
        }
        free(queue->array);
        queue->array = new_array;
        queue->front = 0;
        queue->rear = queue->size - 1;
        queue->capacity *= 2;
    }

    queue->rear = (queue->rear + 1) % queue->capacity;
    queue->array[queue->rear] = item;
    queue->size++;
}

/** 
 * Dequeue an element from the queue
 * Assumes there is an element to dequeue!!!   
 * @param queue the queue 
 * @return the dequeued element
*/
int dequeue(struct Queue *queue) {
    int item = queue->array[queue->front];
    queue->front = (queue->front + 1) % queue->capacity;
    queue->size--;
    return item;
}