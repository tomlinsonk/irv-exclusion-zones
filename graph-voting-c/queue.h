#ifndef QUEUE_H
#define QUEUE_H

struct Queue {
    int front, rear, size;
    int capacity;
    int *array;
};

struct Queue *new_queue(int capacity);
void free_queue(struct Queue *queue);
void enqueue(struct Queue *queue, int item);
int dequeue(struct Queue *queue);


#endif // QUEUE_H