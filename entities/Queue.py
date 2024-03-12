from entities.Player import Player


class Queue:

    def __init__(self, id):
        self.id: str = str(id)
        self.players_on_queue = []

    def add_player(self, plauer: Player):
        # if len(self.players_on_queue) > 01
        self.players_on_queue.append(plauer)

    def get_player_by_id(self, id_player: str):
        for player in self.players_on_queue:
            if player.id == id_player:
                # print(f"PLAYER: {player}")
                return player

    def get_all_players_name(self):
        for player in self.players_on_queue:
            print(player.name)

    def remove_player(self, id_plauer: str):
        for p in self.players_on_queue:
            if p.id == id_plauer:
                print("player removido")
                self.players_on_queue.remove(p)

    def get_amount_players(self):
        return len(self.players_on_queue)

    # def get_all_players(self):
    #     players = []
    #     for player in self.players_on_queue:
    #         players.append(Player(player.id, player.name, player.rank))
    #     return players
