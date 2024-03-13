import uuid
import discord
from discord import app_commands
from discord.ext import commands

from embeds.embedsmessages import queue_join_embed_message
from entities.Player import Player
from entities.Queue import Queue
from exceptions.exceptions import InvalidRankPlayerException
from repositories.QueueRepository import QueueRepository
from repositories.playerrepository import PlayerRepository
from utils.Rank import Rank


class CommandsQueue(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.queues_repository = QueueRepository()
        self.player_repository = PlayerRepository()
        self.queue_rank_a = None
        self.queue_rank_b = None
        self.view = discord.ui.View()
        self.button_rank_a = discord.ui.Button(label="RANK A - Entrar/Sair", style=discord.ButtonStyle.green)
        self.button_rank_b = discord.ui.Button(label="RANK B - Entrar/Sair", style=discord.ButtonStyle.green)
        self.message = None  # Referência para a mensagem enviada

        self.button_rank_a.custom_id = "default0"
        self.button_rank_b.custom_id = "default1"
        self.button_rank_a.callback = self.button_rank_callback
        self.button_rank_b.callback = self.button_rank_callback

        self.view.add_item(self.button_rank_a)
        self.view.add_item(self.button_rank_b)

        super().__init__()

    @app_commands.command()
    async def start(self, interact: discord.Interaction):

        if self.queues_repository.get_amount_queue() == 0:
            self.queue_rank_a = Queue(str(uuid.uuid4()), Rank.RANK_A, 2)
            self.queue_rank_b = Queue(str(uuid.uuid4()), Rank.RANK_B, 2)
            self.queues_repository.save_queue(self.queue_rank_a)
            self.queues_repository.save_queue(self.queue_rank_b)
        else:
            if self.queues_repository.get_amount_queue() >= 2:
                await interact.response.send_message("Já existem filas iniciadas.", ephemeral=True)
                return

        await interact.response.send_message("Você iniciou as filas", ephemeral=True)
        self.button_rank_a.custom_id = self.queue_rank_a.id
        self.button_rank_b.custom_id = self.queue_rank_b.id

        # Envie a mensagem inicial com a quantidade de jogadores em cada fila
        self.message = await interact.followup.send("Filas iniciadas", view=self.view)
        await self.update_queue_message()

    async def button_rank_callback(self, interact: discord.Interaction):
        id_queue_from_button = interact.data['custom_id']
        queue_user = self.queues_repository.get_queue_by_player_id(str(interact.user.id))
        current_queue = self.queues_repository.get_queue_by_id(str(id_queue_from_button))
        player = self.player_repository.find_player_by_id(str(interact.user.id))

        if queue_user is not None:
            queue_user.remove_player(player.discord_id)
            await interact.response.send_message("Você saiu da fila", ephemeral=True)
            await self.update_queue_message()  # Atualizar a mensagem após a remoção do jogador
            return

        if current_queue is not None:
            if player is not None:
                try:
                    current_queue.add_player(player)
                except InvalidRankPlayerException:
                    await interact.response.send_message(f"Você não pode jogar nesse rank ", ephemeral=True)
                    return
            else:
                player = self.player_repository.save_player(
                    Player(None, interact.user.id, interact.user.name, Rank.RANK_B, 0))
                current_queue.add_player(player)
            member = interact.user
            await member.create_dm()
            await member.dm_channel.send(embed=queue_join_embed_message(player, current_queue))
            await interact.response.send_message(f"Você entrou na fila!!!", ephemeral=True)
            await self.update_queue_message()
            return

    async def update_queue_message(self):
        if self.message:
            embed = discord.Embed(title="Filas iniciadas", color=discord.Color.green())
            embed.add_field(name="Rank A", value=str(self.queue_rank_a.get_amount_players()), inline=True)
            embed.add_field(name="Rank B", value=str(self.queue_rank_b.get_amount_players()), inline=True)
            await self.message.edit(embed=embed)


async def setup(bot):
    await bot.add_cog(CommandsQueue(bot))
