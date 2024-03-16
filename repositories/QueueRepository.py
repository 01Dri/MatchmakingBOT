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

    def get_current_queue_user_by_discord_id(self, id_player: str) -> Queue:
        for queue in self.queues.values():
            if queue.get_player_by_id(id_player) is not None:
                return queue
        return None

    def get_amount_queue(self):
        return len(self.queues)

    def remove_queue(self, queue: Queue):
        self.queues.pop(queue.id)

    def get_all_players_on_queues(self):
        for q in self.queues.values():
            for p in q.players_on_queue:
                print(p.name)

    def remove_queues_by_id(self, queue_id):
        for queue in self.get_all_queues():
            if queue.id == queue_id:
                self.remove_queue(queue)

    def get_all_queues(self) -> [Queue]:
        queues = []
        for queue in self.queues.values():
            queues.append(queue)
        return queues
