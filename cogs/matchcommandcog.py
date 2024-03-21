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

    @app_commands.command()
    async def afkcancelar(self, interact: discord.Interaction):
        channel_id = str(interact.channel.category)  # CHANNEL ID É O ID DA MATCH
        match = self.match_service.find_match_by_id(channel_id)
        if match is not None:
            if self.votes.values() is not None:
                self.votes.clear()
            await interact.response.send_message("Votação para cancelar a partida iniciada")
            self.message_button = await interact.followup.send("VOTAÇÃO PARA CANCELAR A PARTIDA: ",
                                                               view=self.button_service.get_view())

            await asyncio.sleep(30)
            if self.get_result_cancel():
                await interact.followup.send(f"Com {self.votes['sim']} votos em SIM, a partida será encerrada!")
                await asyncio.sleep(5)
                await self.remove_attributes_on_match(match)
                self.update_queue_status_players(match)
                return

            print(self.votes)
            await interact.followup.send(
                f"Não houve um número suficiente de votos para cancelar a partida, a partida continuará")

            return
        else:
            await interact.response.send_message("Nenhuma partida encontrada!!!", ephemeral=True)
            return

    async def remove_attributes_on_match(self, match: Match):
        # await match.category.delete()
        await match.voice_channel_teams_a.delete()
        await match.voice_channel_teams_b.delete()
        await match.channel_voting_maps.delete()
        await match.category.delete()
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
        channel_id = str(interact.channel.category)  # CHANNEL ID É O ID DA MATCH
        match = self.match_service.find_match_by_id(channel_id)
        button_id = str(interact.data['custom_id'])
        await interact.response.send_message(f"Você votou em {button_id}!!!", ephemeral=True)
        if button_id not in self.votes.keys():
            self.votes[button_id] = 1
        else:
            self.votes[button_id] += 1

        # await asyncio.sleep(30)
        # if self.get_result_cancel():
        #     await interact.followup.send(f"Com {self.votes['sim']} votos em SIM, a partida será encerrada!")
        #     await asyncio.sleep(5)
        #     await  self.remove_attributes_on_match(match)
        #     self.update_queue_status_players(match)
        #     return
        # print(self.votes)
        # await interact.followup.send(
        #     f"Não houve um número suficiente de votos para cancelar a partida, a partida continuará")

    def get_result_cancel(self):
        if "nao" not in self.votes.keys():
            return True
            # return self.votes["sim"]

        if "sim" not in self.votes.keys():
            return False
            # return self.votes["nao"]

        if self.votes["sim"] > self.votes["nao"]:
            return True
            # return self.votes["sim"]
        elif self.votes["nao"] > self.votes["sim"]:
            return False

        return False

        # return self.votes["nao"]


async def setup(bot):
    await bot.add_cog(MatchCommandCog(bot))
