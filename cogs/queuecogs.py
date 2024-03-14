import asyncio
import uuid
import discord
from discord import app_commands
from discord.ext import commands

from embeds.embedsmessages import queue_join_embed_message, queue_start_voting_maps_message
from entities.Player import Player
from entities.Queue import Queue
from enums.StatusQueue import StatusQueue
from exceptions.exceptions import InvalidRankPlayerException
from repositories.QueueRepository import QueueRepository
from repositories.playerrepository import PlayerRepository
from enums.Rank import Rank


class CommandsQueue(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.queues_repository = QueueRepository()
        self.player_repository = PlayerRepository()
        self.queue_rank_a = None
        self.queue_rank_b = None
        self.view = discord.ui.View()
        self.button_rank_a = discord.ui.Button(label="RANK A - Entrar/Sair")#, style=discord.ButtonStyle.green)
        self.button_rank_b = discord.ui.Button(label="RANK B - Entrar/Sair")# style=discord.ButtonStyle.green)
        self.message = None  # Referência para a mensagem enviada

        self.button_rank_a.custom_id = "default0"
        self.button_rank_b.custom_id = "default1"
        self.button_rank_a.callback = self.button_rank_callback
        self.button_rank_b.callback = self.button_rank_callback

        self.view.add_item(self.button_rank_a)
        self.view.add_item(self.button_rank_b)

        super().__init__()

    async def start_checking_queue(self, interact):
        while True:
            await self.check_quantity_player_on_queue(interact)
            await asyncio.sleep(20)

    @app_commands.command()
    async def start(self, interact: discord.Interaction):

        if self.queues_repository.get_amount_queue() == 0:
            self.create_queues()
        else:
            if self.queues_repository.get_amount_queue() >= 2:
                await interact.response.send_message("Já existem filas iniciadas.", ephemeral=True)
                return

        # Sistema para se alguma fila já atingiu seu limite maximo de players
        self.bot.loop.create_task(self.start_checking_queue(interact))
        await interact.response.send_message("Você iniciou as filas", ephemeral=True)
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
                    if player.queue_status == StatusQueue.IN_VOTING_MAPS.value:
                        await interact.response.send_message(
                            f"Vocẽ está no processo de votação de mapas, por favor retorne a sua sala ", ephemeral=True)
                        return
                    current_queue.add_player(player, interact.user)
                except InvalidRankPlayerException:
                    await interact.response.send_message(f"Você não pode jogar nesse rank ", ephemeral=True)
                    return
            else:
                player = self.player_repository.save_player(
                    Player(None, interact.user.id, interact.user.name, Rank.RANK_B, 0, StatusQueue.IN_QUEUE))
                current_queue.add_player(player, interact.user)

            member = interact.user
            await member.create_dm()
            await member.dm_channel.send(embed=queue_join_embed_message(player, current_queue))
            await interact.response.send_message(f"Você entrou na fila!!!", ephemeral=True)
            await self.update_queue_message()
            return

    # Atualizar o embed com a quantidade jogadores nas filas de rank a e rank B
    async def update_queue_message(self):
        if self.message:
            embed = discord.Embed(title="JOGADORES NAS FILAS: ", color=discord.Color.red())
            embed.add_field(name="Rank A", value=str(self.queue_rank_a.get_amount_players()), inline=True)
            embed.add_field(name="Rank B", value=str(self.queue_rank_b.get_amount_players()), inline=True)
            embed.set_thumbnail(url="https://i.ibb.co/G3mkZ1p/Screenshot-from-2024-03-13-14-31-37.png")
            embed.set_footer(text="Quantidade de partidas: ")
            await self.message.edit(embed=embed)
            self.view.clear_items()
            self.view.add_item(self.button_rank_a)
            self.view.add_item(self.button_rank_b)

    async def check_quantity_player_on_queue(self, interact):
        queues_to_remove = []
        guild = interact.guild

        for queue_id, queue in self.queues_repository.queues.items():
            if queue.get_amount_players() == queue.max_players:
                voting_maps_role = await guild.create_role(name=queue.id, color=discord.Color.gold())
                queues_to_remove.append(queue_id)
                channel_voting = await self.create_channel_voting_maps(interact, queue, voting_maps_role)
                # Este for itera em cada conta do discord presente na fila e adiciona o cargo da fila e manda uma
                # mensagem na DM
                for discord_user in queue.get_all_discord_users():
                    await discord_user.add_roles(voting_maps_role)
                    await discord_user.create_dm()
                    await discord_user.dm_channel.send(embed=queue_start_voting_maps_message(queue, channel_voting))

                    # Este for itera em cada objeto player da queue e atualiza o status da fila no banco
                    for player in queue.get_all_players():
                        player = self.player_repository.find_player_by_id(player.discord_id)
                        self.player_repository.save_player(
                            Player(player.id, player.discord_id, player.name, player.rank, player.points,
                                   StatusQueue.IN_VOTING_MAPS))

        # Este for remove todos as filas cheias.
        for queue_id in queues_to_remove:
            queue = self.queues_repository.queues.pop(queue_id)
            self.set_rank_to_queue(queue)
            await self.message.delete()
            self.view.clear_items()
            self.set_new_buttons()
            self.message = await interact.followup.send("Filas iniciadas", view=self.view)
            await self.update_queue_message()

    async def create_channel_voting_maps(self, interact: discord.Interaction, queue: Queue, role):
        guild = interact.guild
        channel = await guild.create_text_channel(queue.id)
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            role: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        await channel.edit(overwrites=overwrites)
        return channel

    def create_queues(self):
        self.queue_rank_a = Queue(str(uuid.uuid4()), Rank.RANK_A, 2)
        self.queue_rank_b = Queue(str(uuid.uuid4()), Rank.RANK_B, 2)
        self.queues_repository.save_queue(self.queue_rank_a)
        self.queues_repository.save_queue(self.queue_rank_b)
        self.button_rank_a.custom_id = self.queue_rank_a.id
        self.button_rank_b.custom_id = self.queue_rank_b.id

    def set_rank_to_queue(self, queue: Queue):
        if queue.rank == Rank.RANK_A.name:
            self.update_queue_id(Rank.RANK_A, self.queues_repository, self.button_rank_a, 2)

        if queue.rank == Rank.RANK_B.name:
            self.update_queue_id(Rank.RANK_B, self.queues_repository, self.button_rank_b, 2)

    def update_queue_id(self, rank , queue_repository, button_rank, max_player):
        queue = Queue(str(uuid.uuid4()), rank, max_player)
        queue_repository.save_queue(queue)
        button_rank.custom_id = queue.id

    def create_button(self, label, custom_id, callback):
        button = discord.ui.Button(label=label, style=discord.ButtonStyle.green)
        button.custom_id = custom_id
        button.callback = callback
        return button

    def set_new_buttons(self):
        new_button_rank_a = self.create_button("RANK A - Entrar/Sair", self.queue_rank_a.id, self.button_rank_callback)
        new_button_rank_b = self.create_button("RANK B - Entrar/Sair", self.queue_rank_b.id, self.button_rank_callback)

        self.view.add_item(new_button_rank_a)
        self.view.add_item(new_button_rank_b)


async def setup(bot):
    await bot.add_cog(CommandsQueue(bot))
