import discord

from entities.Player import Player
from exceptions.exceptions import InvalidRankPlayerException, CrowdedQueueException
from enums.Rank import Rank


class Queue:

    def __init__(self, id, rank: Rank, max_players):
        self.id: str = str(id)
        self.rank = rank
        self.max_players = max_players
        self.players_on_queue = []
        self.discord_users = []

    def add_player_queue(self, plauer: Player, user):
        if len(self.players_on_queue) == self.max_players:
            raise CrowdedQueueException(f"A fila está cheia!!!")

        if plauer.rank.name == Rank.UNRAKED.name:
            self.add_player_queue_ranked(plauer, user)
            return
        self.add_player_queue_ranked(plauer, user)

    def add_player_queue_ranked(self, plauer: Player, user):
        self.players_on_queue.append(plauer)
        self.discord_users.append(user)


    def add_player_unraked_queue(self, plauer: Player, user):
        self.players_on_queue.append(plauer)
        self.discord_users.append(user)

    def get_player_by_id(self, id_player: str):
        for player in self.players_on_queue:
            if player.discord_id == id_player:
                return player

    def get_all_players(self) -> [Player]:
        players = []
        for player in self.players_on_queue:
            players.append(player)
        return players

    def get_all_discord_users(self) -> [discord.Interaction.user]:
        users = []
        for user in self.discord_users:
            users.append(user)
        return users

    def remove_player_by_discord_id(self, discord_id: str):
        for p in self.players_on_queue:
            if p.discord_id == discord_id:
                print("player removido")
                self.players_on_queue.remove(p)
                return True
        return False

    def get_amount_players(self):
        return len(self.players_on_queue)
