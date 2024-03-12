from entities.Player import Player
from entities.Queue import Queue


class QueueRepository:

    def __init__(self):
        self.queues = {}
        pass

    def save_queue(self, queue: Queue) -> Queue:
        self.queues[queue.id] = queue
        return self.queues[queue.id]

    def get_queue_by_id(self, id_queue) -> Queue:
        return self.queues[id_queue]

    def get_queue_by_player_id(self, id_player: str) -> Queue:
        for queue in self.queues.values():
            if queue.get_player_by_id(id_player) is not None:
                return queue

    def get_amount_queue(self):
        return len(self.queues)

    def remove_queue(self, queue: Queue):
        self.queues.pop(queue.id)
