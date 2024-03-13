from entities.Player import Player
from exceptions.exceptions import InvalidRankPlayerException, CrowdedQueueException
from utils.Rank import Rank


class Queue:

    def __init__(self, id, rank: Rank, max_players):
        self.id: str = str(id)
        self.rank = rank.name
        self.max_players = max_players
        self.players_on_queue = []

    def add_player(self, plauer: Player):
        if len(self.players_on_queue) == self.max_players:
            raise CrowdedQueueException(f"A fila está cheia!!!")

        if plauer.rank.name != self.rank:
            raise InvalidRankPlayerException(f"O player deve ter o rank {self.rank}")

        self.players_on_queue.append(plauer)

    def get_player_by_id(self, id_player: str):
        for player in self.players_on_queue:
            if player.discord_id == id_player:
                return player

    def get_all_players_name(self):
        players = []
        for player in self.players_on_queue:
            players.append(player.name)
        return players


    def remove_player(self, id_plauer: str):
        for p in self.players_on_queue:
            if p.discord_id == id_plauer:
                print("player removido")
                self.players_on_queue.remove(p)

    def get_amount_players(self):
        return len(self.players_on_queue)
