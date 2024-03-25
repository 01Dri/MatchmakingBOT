from embeds.embedsmessages import win_embed_message, losse_embed_message, embed_queues_message
from entities.Match import Match
from enums.Rank import Rank
from enums.StatusQueue import StatusQueue
from repositories.matchrepository import MatchRepository
from repositories.playerrepository import PlayerRepository
from services.queueservice import QueueService


class MatchService:
    # SINGLETON
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.match_repository = MatchRepository()
        self.player_repository = PlayerRepository()
        self.queue_service = QueueService()

    def add_match(self, match: Match):
        return self.match_repository.save_match(match)

    def get_quantity_matches(self):
        return self.match_repository.get_amount_matches()

    def get_matches(self):
        return self.match_repository.matches.items()

    def find_match_by_id(self, match_id: str) -> Match:
        return self.match_repository.find_match_by_id(match_id)

    def remove_match(self, match: Match):
        match = self.match_repository.find_match_by_id(match.id)
        if match is not None:
            return self.match_repository.remove_match(match)
        return False

    async def send_points_to_users(self, match_id, result, message_reference):
        match = self.find_match_by_id(match_id)
        if result == 'a':
            await self.add_points_winner(match, match.team_a, message_reference)
            await self.remove_points_losser(match, match.team_b, message_reference)
            return
        elif result == 'b':
            await self.add_points_winner(match, match.team_b, message_reference)
            await self.remove_points_losser(match, match.team_a, message_reference)
            return

    async def add_points_winner(self, match, team, message_reference):
        rank_match = match.rank
        gain_points = 0
        for player in team:
            rank_player = player.rank
            if rank_player != rank_match:
                if rank_player == Rank.RANK_A and rank_match == Rank.RANK_B:
                    player.wins += 1
                    player.points += 2
                    gain_points = 2
            elif rank_player == Rank.RANK_A:
                player.wins += 1
                player.points += 4
                gain_points = 4

            elif rank_player == Rank.RANK_B:
                player.wins += 1
                player.points += 4
                gain_points = 4
                if player.points >= 150:
                    self.up_rank(player)
            player.queue_status = StatusQueue.DEFAULT
            self.player_repository.save_player(player)
            await message_reference[player.name].edit(embed=win_embed_message(player, gain_points))

    async def remove_points_losser(self, match, team, message_reference):
        rank_match = match.rank
        losse_points = 0
        for player in team:
            rank_player = player.rank
            if rank_player != rank_match:
                if rank_player == Rank.RANK_A and rank_match == Rank.RANK_B:
                    player.losses += 1
                    player.points -= 4
                    losse_points = 4
                    self.drop_rank(player)

            elif rank_player == Rank.RANK_A and rank_player == Rank.RANK_A:
                player.losses += 1
                player.points -= 2
                losse_points = 2
                self.drop_rank(player)

            elif rank_player == Rank.RANK_B and rank_player == Rank.RANK_B:
                if player.points == 0:
                    player.losses += 1
                else:
                    player.losses += 1
                    player.points -= 2
                    losse_points = 2
            player.queue_status = StatusQueue.DEFAULT
            self.player_repository.save_player(player)
            await message_reference[player.name].edit(embed=losse_embed_message(player, losse_points))

    def up_rank(self, player):
        if player.rank == Rank.RANK_B:
            if player.points >= 150:
                player.rank = Rank.RANK_A
                player.points -= 150  # ZERAR OS PONTOS

    def drop_rank(self, player):
        if player.rank == Rank.RANK_A:
            if player.points <= -10:
                player.rank = Rank.RANK_B  # DROPOU

    async def remove_attributes_on_match(self, match: Match):
        await match.category.delete()
        await match.voice_channel_teams_a.delete()
        await match.voice_channel_teams_b.delete()
        await match.channel_voting_maps.delete()
        # await match.category.delete()
        self.remove_match(match)
        await match.message_amount_matches.edit(
            embed=embed_queues_message(self.queue_service.get_quantity_players_on_queues(),
                                       self.get_quantity_matches()))

