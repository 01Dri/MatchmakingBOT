import asyncio
import random

import discord.ui
from discord import app_commands
from discord.ext import commands
from embeds.embedsmessages import embed_queues_message, embed_join_queue_message, emebed_map_voted, embed_map_wiiner, \
    embed_join_voting_maps, team_mate_embed_message
from entities.Match import Match
from entities.Player import Player
from entities.Queue import Queue
from enums.Rank import Rank
from enums.StatusQueue import StatusQueue
from services.blacksecurityservice import BlackSecurityService
from services.matchservice import MatchService
from services.playerservice import PlayerService
from services.queuebuttonservice import QueueButtonService
from services.queueservice import QueueService


class QueueCommandCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.message_button_create = None
        self.queue_service = QueueService()
        self.buttons_queues_service = QueueButtonService(self.callback_button_queue)
        self.player_service = PlayerService()
        self.black_security_service = BlackSecurityService()
        self.match_service = MatchService()
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
        self.votes_cancel = {}
        self.vote_message = None
        self.channel_vote_maps = None
        self.voice_channel_a = None
        self.voice_channel_b = None
        self.teammate_a = []
        self.teammate_b = []
        self.queue_category = None

        super().__init__()

    @app_commands.command()
    async def iniciarfila(self, interact: discord.Interaction):
        ## Verificando a cada segundo filas que podem estar cheias, ou seja. filas que devem ser inicializadas!!!
        self.bot.loop.create_task(self.check_full_queues(interact))

        if self.queue_service.get_quantity_queue() == 0:
            self.queue_rank_a = self.queue_service.create_queue(Rank.RANK_A, StatusQueue.DEFAULT)
            self.queue_rank_b = self.queue_service.create_queue(Rank.RANK_B, StatusQueue.DEFAULT)
            self.button_queues = self.buttons_queues_service.create_button_queue("ENTRAR/SAIR",
                                                                                 f"{self.queue_rank_a.id} - {self.queue_rank_b.id}")
        else:
            await interact.response.send_message("FILAS JÁ INICIADAS!!!")
            return
        await interact.response.send_message("Você iniciou as filas", ephemeral=True)
        self.buttons_queues_service.message_button_create = await interact.followup.send(
            embed=embed_queues_message(self.queue_service.get_quantity_players_on_queues(),
                                       self.match_service.get_quantity_matches()),
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

    # @app_commands.command()
    # async def cancelarpartida(self, interact: discord.Interaction):
    #     channel_command = interact.channel
    #     queue_id_by_channel_name = channel_command.name
    #     if queue_id_by_channel_name in self.queue_service.get_all_id_queues():
    #         current_queue = self.queue_service.find_queue_by_id(queue_id_by_channel_name)
    #         self.queue_service.remove_queue_by_id(current_queue.id)
    #         button_yes_cancel = discord.ui.Button(style=discord.ButtonStyle.green, label="Sim")
    #         button_yes_cancel.custom_id = "sim"
    #         button_no_cancel = discord.ui.Button(style=discord.ButtonStyle.red, label="Não")
    #         button_yes_cancel.custom_id = "nao"
    #         view = discord.ui.View()
    #         view.add_item(button_yes_cancel)
    #         view.add_item(button_no_cancel)
    #         await interact.response.send_message("VOTAÇÃO PARA ENCERRAR A PARTIDA: ", view=view, ephemeral=False)
    #         return
    #     await interact.response.send_message("Nenhuma fila encontrada nesse canal!!!", ephemeral=True)

    # async def callback_cancel_match(self, interact: discord.Interaction):
    #     id_button = str(interact.data['custom_id'])
    #     self.votes_cancel[id_button] += 1
    #
    #     async def get_result_cancel():
    #         if not self.votes_cancel:
    #             return None
    #
    #     max_votes = max(self.votes_cancel.values())
    #     result = None
    #
    #     for vote_id, votes in self.votes_cancel.items():
    #         if votes == max_votes:
    #             result = vote_id
    #             break
    #
    #     return result

    async def callback_button_queue(self, interact: discord.Interaction):
        print("CHAMOU O CALLBACK")
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
                        embed=embed_queues_message(self.queue_service.get_quantity_players_on_queues(),
                                                   self.match_service.get_quantity_matches()))
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
            embed=embed_queues_message(self.queue_service.get_quantity_players_on_queues(),
                                       self.match_service.get_quantity_matches()))

        self.player_service.save_player(
            Player(None, discord_id_player, str(interact.user.name), player.rank, player.points, player.wins,
                   player.losses,
                   StatusQueue.IN_QUEUE))
        # await self.buttons_queues_service.message_button_create.edit(embed=embed_queues_message(self.queue_service.get_quantity_players_on_queues())

    async def check_full_queues(self, interact):
        guild = interact.guild
        while True:
            if len(self.queue_service.find_full_queues()) == 0:
                pass
            else:
                queue = self.queue_service.remove_full_queue(self.queue_service.find_full_queues())
                await self.create_category(interact, queue)
                new_queue = self.queue_service.create_queue(queue.rank, StatusQueue.DEFAULT)

                self.update_new_queue_after_full_queue(new_queue)
                # await self.update_button_queue_message()

                self.channel_vote_maps = await self.create_channel_voting_maps(interact, queue)

                match = Match(queue.id, self.channel_vote_maps, None, None, None,
                      None, None, None)
                self.match_service.add_match(match)
                await self.update_button_queue_message()

                for user in queue.discord_users:
                    await self.embeds_message_join[user.name].edit(
                        embed=embed_join_voting_maps(queue, self.channel_vote_maps))

                await self.send_maps_vote_to_map()
                await asyncio.sleep(30)
                map_winner = await self.print_map_with_most_votes()
                await self.create_voice_channel(interact, queue, self.match_service.get_quantity_matches())
                await self.send_teams(queue, map_winner, self.black_security_service.get_random_key())
                self.update_attributes_match(match)
                self.match_service.add_match(match)
                print(self.match_service.get_matches())
            await asyncio.sleep(10)

    def update_attributes_match(self, match):
        match.voice_channel_teams_a = self.voice_channel_a
        match.voice_channel_teams_b = self.voice_channel_b
        match.team_a = self.teammate_a
        match.team_b = self.teammate_b
        match.category = self.queue_category
        match.message_amount_matches = self.buttons_queues_service.message_button_create

    def update_new_queue_after_full_queue(self, queue: Queue):
        new_queue = self.queue_service.create_queue(queue.rank, StatusQueue.DEFAULT)
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
            embed=embed_queues_message(self.queue_service.get_quantity_players_on_queues(),
                                       self.match_service.get_quantity_matches()),
            view=self.buttons_queues_service.get_view())
        # print(self.button_queues.custom_id)

    async def create_category(self, interact, queue):
        self.queue_category = await interact.guild.create_category(queue.id)

    async def create_channel_voting_maps(self, interact: discord.Interaction, queue: Queue):

        for player in queue.get_all_players():
            self.player_service.save_player(
                Player(None, player.discord_id, str(interact.user.name), player.rank, player.points, player.wins,
                       player.losses,
                       StatusQueue.IN_VOTING_MAPS))

        channel = await self.queue_category.create_text_channel("Votação de mapas",
                                                                overwrites=self.get_overwrites(interact, queue))
        # channel.
        return channel

    async def send_teams(self, queue, map_winner, key):
        players = queue.get_all_players()
        random.shuffle(players)
        halfway_point = len(players) // 2
        self.teammate_a = players[:halfway_point]
        self.teammate_b = players[halfway_point:]

        await self.channel_vote_maps.send(
            embed=team_mate_embed_message(self.voice_channel_a, self.voice_channel_b, map_winner, key, self.teammate_a,
                                          self.teammate_b))
        self.black_security_service.remove_one_key(key)

    async def create_voice_channel(self, interact, queue, match_number):
        self.voice_channel_a = await self.queue_category.create_voice_channel(f"PARTIDA {match_number} - Time A",
                                                                              overwrites=self.get_overwrites(interact,
                                                                                                             queue))

        self.voice_channel_b = await self.queue_category.create_voice_channel(f"PARTIDA {match_number} - Time B",
                                                                              overwrites=self.get_overwrites(interact,
                                                                                                             queue))

    def get_overwrites(self, interact, queue):
        guild = interact.guild
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True),  # Garante que o bot possa ler mensagens
        }
        for discord_user in queue.get_all_discord_users():
            member = guild.get_member(discord_user.id)
            if member:
                overwrites[member] = discord.PermissionOverwrite(read_messages=True)
        return overwrites

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
                self.maps_votes_record[map_button_id] += 1
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
        return map_with_most_votes
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
