from entities.Player import Player


class Queue:

    def __init__(self, id):
        self.id: str = id
        self.players_on_queue = {}

    def add_player(self, plauer: Player):
        # if len(self.players_on_queue) > 01
        self.players_on_queue[plauer.id] = plauer

    def get_player_by_id(self, id_player: str):
        for player in self.players_on_queue.values():
            if player.id == id_player:
                return player
            return None

