from entities.Player import Player
from repositories.playerrepository import PlayerRepository


class PlayerService:
    def __init__(self):
        self.player_repository = PlayerRepository()

    def find_player(self, discord_id: str) -> Player:
        return self.player_repository.find_player_by_discord_id(discord_id)

    def save_player(self, player: Player):
        return self.player_repository.save_player(
            Player(None, player.discord_id, player.name, player.rank, player.points, player.wins, player.losses,
                   player.queue_status))
