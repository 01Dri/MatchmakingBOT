import asyncio
import time

import discord.ui
from discord import app_commands, InteractionResponded
from discord.ext import commands

from embeds.embedsmessages import embed_queues_message, embed_join_queue_message, team_mate_embed_message
from entities.Player import Player
from entities.Queue import Queue
from enums.Rank import Rank
from enums.StatusQueue import StatusQueue
from exceptions.exceptions import CrowdedQueueException
from repositories.playerrepository import PlayerRepository
from services.playerservice import PlayerService
from services.queuebuttonservice import QueueButtonService
from services.queueservice import QueueService


class QueueCommandCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.message_button_create = None
        self.queue_service = QueueService(2)
        self.buttons_queues_service = QueueButtonService(self.callback_button_queue)
        self.player_service = PlayerService()
        self.queue_rank_a = None
        self.queue_rank_b = None
        self.before_embed = None
        self.embeds_message_join = {}
        self.current_queue_user = None
        self.queues_id = None
        self.button_queues = None
        self.maps_voting_message = None
        super().__init__()

    @app_commands.command()
    async def iniciarfila(self, interact: discord.Interaction):
        self.bot.loop.create_task(self.check_full_queues(interact))
        if self.queue_service.get_quantity_queue() == 0:
            self.queue_rank_a = self.queue_service.create_queue(Rank.RANK_A)
            self.queue_rank_b = self.queue_service.create_queue(Rank.RANK_B)
            self.button_queues = self.buttons_queues_service.create_button_queue("ENTRAR/SAIR",
                                                                                 f"{self.queue_rank_a.id} - {self.queue_rank_b.id}")
        else:
            await interact.response.send_message("FILAS JÁ INICIADAS!!!")
            return
        await interact.response.send_message("Você iniciou as filas", ephemeral=True)
        self.buttons_queues_service.message_button_create = await interact.followup.send(embed=embed_queues_message(),
                                                                                         content="Filas iniciadas",
                                                                                         view=self.buttons_queues_service.get_view())

    @app_commands.command()
    async def cancelarfilas(self, interact: discord.Interaction):
        if self.queue_service.get_quantity_queue() >= 2:
            self.queue_service.remove_all_queues()
            self.buttons_queues_service.clear_view()
            await self.buttons_queues_service.delete_message_button()
            await interact.response.send_message("Filas canceladas!!!", view=self.buttons_queues_service.get_view())
            print(f"QUANTIDADE DE FILAS APÓS REMOÇÃO: {self.queue_service.get_quantity_queue()}")
            return
        await interact.response.send_message("NÃO EXISTEM FILAS PARA SER REMOVIDAS!!!", ephemeral=True)

    async def callback_button_queue(self, interact: discord.Interaction):

        self.queues_id = (str(interact.data['custom_id']))
        print(self.queues_id)
        queues_id_parts = self.queues_id.split(" - ")
        queus_1 = self.queue_service.find_queue_by_id(queues_id_parts[0])
        queus_2 = self.queue_service.find_queue_by_id(queues_id_parts[1])

        if queus_1.rank == Rank.RANK_A:
            self.queue_rank_a = queus_1
        else:
            self.queue_rank_a = queus_2
            self.queue_rank_b = queus_1

        discord_id_player = str(interact.user.id)
        player = self.player_service.find_player(discord_id_player)
        if player is None:
            player = self.player_service.save_player(
                Player(None, discord_id_player, str(interact.user.name), Rank.RANK_B, 0, 0, 0,
                       StatusQueue.IN_QUEUE))

        current_queue_user = self.queue_service.find_current_queue_player(player)

        if current_queue_user is not None:
            if current_queue_user == self.queue_rank_a or current_queue_user == self.queue_rank_b:
                if self.queue_service.remove_player_on_queue(player, current_queue_user):
                    embed_user = self.embeds_message_join.get(interact.user.name)
                    if embed_user:
                        await embed_user.delete()
                    await interact.response.send_message("Você saiu da fila!!!", ephemeral=True)
                    print(f"PLAYERS NA FILA: {current_queue_user.get_all_players()}")
                    return

        if player.rank == self.queue_rank_a.rank:
            current_queue_user = self.queue_service.add_player_on_queue(player, self.queue_rank_a, interact.user)
        else:
            current_queue_user = self.queue_service.add_player_on_queue(player, self.queue_rank_b, interact.user)

        await interact.response.send_message("Você entrou na fila!!!", ephemeral=True)

        # Cria um novo embed para o usuário e armazena a referência a ele
        embed = embed_join_queue_message(current_queue_user)
        self.embeds_message_join[interact.user.name] = await interact.followup.send(embed=embed, ephemeral=True)
        print(f"PLAYERS NA FILA: {current_queue_user.get_all_players()}")

    async def check_full_queues(self, interact):
        guild = interact.guild
        while True:
            if len(self.queue_service.find_full_queues()) == 0:
                pass
            else:
                queue = self.queue_service.remove_full_queue(self.queue_service.find_full_queues())
                role = await self.set_role_queue_to_users(guild, queue)
                channel = await self.create_channel_voting_maps(interact, queue, role)
                await self.send_maps_vote_to_map(channel, interact, queue)

                # AJUSTAR O SISTEMA DE VOTAÇÃO POIS DESSA FORMA É LERDO!!!!
                new_queue = self.queue_service.create_queue(queue.rank)
                self.update_new_queue_after_full_queue(new_queue)
                await self.update_button_queue_message()

            await asyncio.sleep(5)

    async def set_role_queue_to_users(self, guild, queue):
        voting_maps_role = await guild.create_role(name=queue.id, color=discord.Color.gold())
        await self.queue_service.set_role_all_users_on_queue(voting_maps_role, queue)
        return voting_maps_role

    def update_new_queue_after_full_queue(self, queue: Queue):
        new_queue = self.queue_service.create_queue(queue.rank)
        if queue.rank == Rank.RANK_A:
            parts = self.queues_id.split(" - ")
            self.queues_id = parts[1] + " - " + new_queue.id
            self.queue_rank_a = new_queue
        else:
            parts = self.queues_id.split(" - ")
            self.queues_id = parts[0] + " - " + new_queue.id
            self.queue_rank_b = new_queue

    async def update_button_queue_message(self):
        self.button_queues.custom_id = self.queues_id
        self.buttons_queues_service.clear_view()
        self.buttons_queues_service.get_view().add_item(self.button_queues)
        await self.buttons_queues_service.message_button_create.edit(embed=embed_queues_message(),
                                                                     view=self.buttons_queues_service.get_view())

    async def create_channel_voting_maps(self, interact: discord.Interaction, queue: Queue, role):
        guild = interact.guild
        channel = await guild.create_text_channel(queue.id)
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            role: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        await channel.edit(overwrites=overwrites)
        return channel

    async def send_maps_vote_to_map(self, channel, interact, queue: Queue):
        messages = {}
        votes = {}
        winner_map = None
        maps = {
            "Ankara-T": "maps/Ankara-T.jpeg",
            "Mexico-T": "maps/MexicoT.jpeg",
            "OLHO-2.0": "maps/OLHO-2.0.jpeg",
            "Porto-T": "maps/Porto-T.jpeg",
            "Satelite-T": "maps/Satelite-T.jpeg",
            "Sub-Base": "maps/Sub-Base.jpeg",
            "ViuvaT": "maps/ViuvaT.jpeg"
        }
        emoji_react = '✅'
        await channel.send("VOTAÇÃO DOS MAPAS")
        for map_name, path in maps.items():
            embed = discord.Embed(title="MAPAS: ", color=discord.Color.red())
            embed.add_field(name=map_name, value="Vote", inline=True)
            file = discord.File(path, filename=f"{map_name}.jpeg")
            embed.set_image(url=f"attachment://{map_name}.jpeg")
            message = await channel.send(file=file, embed=embed)
            await message.add_reaction('✅')
            messages[path] = message

        self.maps_voting_message = await channel.send("Tempo restante: 1:00)")
        await self.get_votes_maps(messages, emoji_react, votes, interact)
        winner_map = max(votes, key=votes.get)
        await self.maps_voting_message.edit(content=f"Mapa escolhido: {winner_map}")
        players = queue.get_all_players()
        print(players)
        await channel.send(embed=team_mate_embed_message(players, winner_map))

    async def get_votes_maps(self, messages, emoji_react, votes, interact):
        end_time = time.time() + 30
        while time.time() < end_time:
            remaining_time = int(end_time - time.time())
            formatted_time = time.strftime("%M:%S", time.gmtime(remaining_time))  # Formatando o tempo restante
            await self.maps_voting_message.edit(content=f"Tempo restante: {formatted_time}")

            for path, message in messages.items():
                message = await message.channel.fetch_message(message.id)
                react = discord.utils.get(message.reactions, emoji=emoji_react)
                if react:
                    count = react.count
                    votes[path] = count
            await asyncio.sleep(5)

        return votes


async def setup(bot):
    await bot.add_cog(QueueCommandCog(bot))