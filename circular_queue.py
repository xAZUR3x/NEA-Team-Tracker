from abc import ABC, abstractmethod


# abstract class used as the implementation of these methods may be updated at
# some point
class AbstractQueue(ABC):
    def __init__(self, size):
        self.size = size
        self.queue = [None] * size
        self.front = -1
        self.rear = -1

    @abstractmethod
    def is_empty(self):
        pass

    @abstractmethod
    def is_full(self):
        pass

    @abstractmethod
    def enqueue(self, item):
        pass

    @abstractmethod
    def dequeue(self):
        pass


class CircularQueue(AbstractQueue):
    def __init__(self, size):
        super().__init__(size)

    def is_empty(self):
        return self.front == -1

    def is_full(self):
        return (self.rear + 1) % self.size == self.front

    def enqueue(self, item):
        if self.is_full():
            return

        # the front is only modified to indicate that the queue is no longer
        # empty
        if self.is_empty():
            self.front = 0

        self.rear = (self.rear + 1) % self.size
        self.queue[self.rear] = item

    def dequeue(self):
        if self.is_empty():
            return None

        item = self.queue[self.front]
        if self.front == self.rear:
            # essentially resets the queue if it is empty
            self.front = -1
            self.rear = -1
        else:
            self.front = (self.front + 1) % self.size

        return item
