from entities.Player import Player
from enums.Rank import Rank
from enums.StatusQueue import StatusQueue
from repositories.playerrepository import PlayerRepository


class PlayerService:
    def __init__(self):
        self.player_repository = PlayerRepository()

    def find_player_by_discord_id(self, discord_id: str, username) -> Player:
        player = self.player_repository.find_player_by_discord_id(discord_id)
        if player is None:
            player = self.save_player(
                Player(None, discord_id, str(username), Rank.RANK_B, 0, 0, 0,
                       StatusQueue.DEFAULT))
        return player

    def save_player(self, player: Player):
        return self.player_repository.save_player(
            Player(None, player.discord_id, player.name, player.rank, player.points, player.wins, player.losses,
                   player.queue_status))

    def reset_all_players_record(self):
        return self.player_repository.reset_all()
