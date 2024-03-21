import asyncio

import discord
from discord import app_commands
from discord.ext import commands

from embeds.embedsmessages import embed_queues_message
from entities.Match import Match
from entities.Player import Player
from enums.StatusQueue import StatusQueue
from services.matchservice import MatchService
from services.playerservice import PlayerService
from services.queuebuttonservice import QueueButtonService
from services.queueservice import QueueService


class MatchCommandCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.match_service = MatchService()
        self.player_service = PlayerService()
        self.queue_service = QueueService()
        self.button_service = QueueButtonService(self.callback_vote_cancel_button)
        self.button_yes = self.button_service.create_button_queue("SIM", "sim")
        self.button_no = self.button_service.create_button_queue("NÃO", "nao")
        self.message_button = None
        self.result = None
        self.votes = {}
        self.votes_users = {}

    @app_commands.command()
    async def afkcancelar(self, interact: discord.Interaction):
        channel_id = str(interact.channel.category)  # CHANNEL ID É O ID DA MATCH
        match = self.match_service.find_match_by_id(channel_id)
        print(self.message_button)
        if match is None:
            await interact.response.send_message("Nenhuma partida encontrada nesse canal", ephemeral=True)
            return

        if self.message_button is not None:
            await interact.response.send_message("Já existe uma votação em andamento!", ephemeral=True)
            return

        if self.votes.values() is not None:
            self.votes.clear()
        await interact.response.send_message("Votação para cancelar a partida iniciada", ephemeral=True)
        self.message_button = await interact.followup.send("VOTAÇÃO PARA CANCELAR A PARTIDA: ",
                                                           view=self.button_service.get_view())
        if "nao" not in self.votes.keys():
            self.votes["nao"] = 0

        if "sim" not in self.votes.keys():
            self.votes["sim"] = 0

        await asyncio.sleep(20)
        if self.votes['sim'] == 0 and self.votes['nao'] == 0:
            await self.message_button.delete()
            print("CAIU AQUI")
            self.message_button = None
            await interact.followup.send(
                f"Não houve um número suficiente de votos para cancelar a partida, a partida continuará")
            return

        if self.get_result_cancel(2):
            await interact.followup.send(f"Com {self.votes['sim']} votos em SIM, a partida será encerrada!")
            await asyncio.sleep(5)
            await self.remove_attributes_on_match(match)
            self.update_queue_status_players(match)
            self.message_button = None
            return

        await interact.followup.send(
            f"Não houve um número suficiente de votos para cancelar a partida, a partida continuará")
        await self.message_button.delete()
        self.message_button = None

    async def remove_attributes_on_match(self, match: Match):
        await match.category.delete()
        await match.voice_channel_teams_a.delete()
        await match.voice_channel_teams_b.delete()
        await match.channel_voting_maps.delete()
        # await match.category.delete()
        self.match_service.remove_match(match)
        await match.message_amount_matches.edit(
            embed=embed_queues_message(self.queue_service.get_quantity_players_on_queues(),
                                       self.match_service.get_quantity_matches()))

    def update_queue_status_players(self, match: Match):
        players_a = match.team_a
        players_b = match.team_b
        full_players = players_a + players_b
        for player in full_players:
            self.player_service.save_player(
                Player(player.id, player.discord_id, player.name, player.rank, player.points, player.wins,
                       player.losses, StatusQueue.DEFAULT))
        return

    async def callback_vote_cancel_button(self, interact: discord.Interaction):
        channel_id = str(interact.channel.category)
        match = self.match_service.find_match_by_id(channel_id)
        button_id = str(interact.data['custom_id'])
        if self.add_vote(button_id, interact.user.name) is False:
            await interact.response.send_message("Você já votou!!!", ephemeral=True)
            return

        await interact.response.send_message(f"Você votou em {button_id}", ephemeral=True)

    def add_vote(self, button_id, user):

        if user in self.votes_users.keys():
            return False

        if button_id not in self.votes.keys() and user not in self.votes_users.keys():
            self.votes[button_id] = 1
            self.votes_users[user] = button_id

        else:
            self.votes[button_id] += 1
            self.votes_users[user] = button_id

    def get_result_cancel(self, max_votes):

        if self.votes["sim"] >= max_votes:
            return True
            # return self.votes["sim"]
        elif self.votes["nao"] >= max_votes:
            return False

        self.votes.clear()
        self.votes_users.clear()
        # return False

        # return self.votes["nao"]


async def setup(bot):
    await bot.add_cog(MatchCommandCog(bot))
