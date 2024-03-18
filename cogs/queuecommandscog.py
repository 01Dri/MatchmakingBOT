import asyncio
import random

import discord.ui
from discord import app_commands
from discord.ext import commands
from embeds.embedsmessages import embed_queues_message, embed_join_queue_message, emebed_map_voted, embed_map_wiiner, \
    embed_join_voting_maps
from entities.Player import Player
from entities.Queue import Queue
from enums.Rank import Rank
from enums.StatusQueue import StatusQueue
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
        self.maps_votes_record = {}
        self.maps_votes_users_record = {}
        self.map_path_image_vote = {}
        self.vote_message = None
        self.channel_vote_maps = None
        super().__init__()

    @app_commands.command()
    async def iniciarfila(self, interact: discord.Interaction):
        ## Verificando a cada segundo filas que podem estar cheias, ou seja. filas que devem ser inicializadas!!!
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
        self.buttons_queues_service.message_button_create = await interact.followup.send(
            embed=embed_queues_message(self.queue_service.get_quantity_players_on_queues()),
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
                       StatusQueue.DEFAULT))
        print(player.queue_status)

        current_queue_user = self.queue_service.find_current_queue_player(player)
        if player is not None and player.queue_status == StatusQueue.IN_VOTING_MAPS.value:
            await interact.response.send_message("Você já está em uma partida!!!", ephemeral=True)
            return

        if current_queue_user is not None:
            if current_queue_user == self.queue_rank_a or current_queue_user == self.queue_rank_b:
                if self.queue_service.remove_player_on_queue(player, current_queue_user):
                    embed_user = self.embeds_message_join.get(interact.user.name)
                    if embed_user:
                        await embed_user.delete()
                    await interact.response.send_message("Você saiu da fila!!!", ephemeral=True)
                    print(f"PLAYERS NA FILA: {current_queue_user.get_all_players()}")
                    await self.buttons_queues_service.message_button_create.edit(
                        embed=embed_queues_message(self.queue_service.get_quantity_players_on_queues()))
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
        await self.buttons_queues_service.message_button_create.edit(
            embed=embed_queues_message(self.queue_service.get_quantity_players_on_queues()))

        self.player_service.save_player(
            Player(None, discord_id_player, str(interact.user.name), player.rank, player.points, player.wins, player.losses,
                   StatusQueue.IN_QUEUE))
        # await self.buttons_queues_service.message_button_create.edit(embed=embed_queues_message(self.queue_service.get_quantity_players_on_queues())

    async def check_full_queues(self, interact):
        guild = interact.guild
        while True:
            if len(self.queue_service.find_full_queues()) == 0:
                pass
            else:
                queue = self.queue_service.remove_full_queue(self.queue_service.find_full_queues())
                # role = await self.set_role_queue_to_users(guild, queue)
                new_queue = self.queue_service.create_queue(queue.rank)
                self.update_new_queue_after_full_queue(new_queue)
                await self.update_button_queue_message()

                self.channel_vote_maps = await self.create_channel_voting_maps(interact, queue)
                await self.embeds_message_join[interact.user.name].edit(embed=embed_join_voting_maps(queue, self.channel_vote_maps))
                await self.send_maps_vote_to_map()

                await asyncio.sleep(30)
                await self.print_map_with_most_votes()

            await asyncio.sleep(10)

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
        await self.buttons_queues_service.message_button_create.edit(
            embed=embed_queues_message(self.queue_service.get_quantity_players_on_queues()),
            view=self.buttons_queues_service.get_view())
        print(self.button_queues.custom_id)

    async def create_channel_voting_maps(self, interact: discord.Interaction, queue: Queue):
        guild = interact.guild
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True),  # Garante que o bot possa ler mensagens
        }

        for player in queue.get_all_players():
            self.player_service.save_player(
                Player(None, player.discord_id, str(interact.user.name), player.rank, player.points, player.wins,
                       player.losses,
                       StatusQueue.IN_VOTING_MAPS))

        for discord_user in queue.get_all_discord_users():
            member = guild.get_member(discord_user.id)
            if member:
                overwrites[member] = discord.PermissionOverwrite(read_messages=True)

        channel = await guild.create_text_channel(queue.id, overwrites=overwrites)
        return channel

    async def send_maps_vote_to_map(self):

        maps = [
            "Ankara-T",
            "MexicoT",
            "OLHO-2.0",
            "Porto-T",
            "Satelite-T",
            "Sub-Base",
            "ViuvaT"
        ]

        for map in maps:
            self.maps_votes_record[map] = 0

        embed = discord.Embed(title="SELEÇÃO DE MAPAS", description="Escolha um mapa:",
                              color=0xFF0000)  # Cor vermelha: 0xFF0000
        for map_name in maps:
            embed.add_field(name=map_name, value=f"Vote pelo botão  para escolher o mapa {map_name}", inline=False)

        buttons = [
            discord.ui.Button(style=discord.ButtonStyle.primary, label=map_name) for map_name in maps
        ]

        view = discord.ui.View()
        for b, map_name in zip(buttons, maps):
            b.custom_id = map_name
            b.callback = self.map_button_vote_callback
            view.add_item(b)

        await self.channel_vote_maps.send(embed=embed, view=view)
        # print(f"mapa escolhido: {max(self.maps_votes_record, key=self.maps_votes_record.get)}")

    async def map_button_vote_callback(self, interact: discord.Interaction):
        map_button_id = str(interact.data['custom_id'])
        id_user = str(interact.user.id)

        async def register_vote():
            if id_user in self.maps_votes_users_record.keys():
                current_map_vote_user = self.maps_votes_users_record[id_user]
                if current_map_vote_user != map_button_id:
                    current_votes = self.maps_votes_record[current_map_vote_user]
                    self.maps_votes_record[current_map_vote_user] = current_votes - 1

                if map_button_id == current_map_vote_user:
                    await interact.response.send_message(content="Você já votou neste mapa!!!",
                                                         embed=emebed_map_voted(map_button_id), ephemeral=True)
                    return

            if map_button_id not in self.maps_votes_record.keys():
                self.maps_votes_record[map_button_id] = 1
                self.maps_votes_users_record[id_user] = map_button_id
                self.map_path_image_vote[id_user] = rf"maps/{map_button_id}.jpeg"
            else:
                current_votes = self.maps_votes_record[map_button_id]
                self.maps_votes_record[map_button_id] = current_votes + 1
                self.maps_votes_users_record[id_user] = map_button_id
                self.map_path_image_vote[id_user] = rf"maps/{map_button_id}.jpeg"

            embed = emebed_map_voted(map_button_id)

            await interact.response.send_message(content="Voto registrado", embed=embed, ephemeral=True)

        try:
            await asyncio.wait_for(register_vote(), timeout=30)
        except asyncio.TimeoutError:
            await self.print_map_with_most_votes()

    async def print_map_with_most_votes(self):
        map_with_most_votes = None
        if not self.maps_votes_record:
            # Se não houver votos registrados, escolha um mapa aleatório
            random_map = random.choice(list(self.maps_votes_users_record.keys()))
            max_votes = 0
        else:
            map_with_most_votes = self.get_map_with_most_votes()
            max_votes = self.maps_votes_record[map_with_most_votes]
            random_map = None

        if random_map:
            await self.channel_vote_maps.send(f"Ninguém votou! O mapa escolhido aleatoriamente é: {random_map}")
        else:
            file = discord.File(rf"maps/{map_with_most_votes}.jpeg")
            await self.channel_vote_maps.send(file=file, embed=embed_map_wiiner(map_with_most_votes, max_votes))

            # await channel.send(f"O mapa escolhido é: {map_with_most_votes}, com {max_votes} votos.")

    def get_map_with_most_votes(self):
        if not self.maps_votes_record:
            return None  # Retorna None se não houver nenhum voto registrado ainda

        max_votes = max(self.maps_votes_record.values())
        map_with_most_votes = None

        for map_id, votes in self.maps_votes_record.items():
            if votes == max_votes:
                map_with_most_votes = map_id
                break

        return map_with_most_votes


async def setup(bot):
    await bot.add_cog(QueueCommandCog(bot))
