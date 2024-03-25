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
from services.votesmapsservice import VotesMapsServices


class QueueCommandCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.queue_service = QueueService()
        self.buttons_queues_service = QueueButtonService(self.callback_button_queue)
        self.player_service = PlayerService()
        self.black_security_service = BlackSecurityService()
        self.match_service = MatchService()
        self.vote_maps_service = VotesMapsServices()
        self.embeds_message_join = {}
        self.queues_id = None
        self.button_queues = None
        self.map_path_image_vote = {}
        self.votes_end_user = {}
        self.votes_end = {}
        self.view_end = None
        self.message_end = None
        self.channel_vote_maps_references = {}
        self.guild_categories_references = {}
        self.error_black_security_message = None
        self.votes_end_records = {}
        self.votes_end_user_records = {}

        super().__init__()

    @app_commands.command()
    async def iniciarfila(self, interact: discord.Interaction):
        self.bot.loop.create_task(self.check_full_queues(interact))
        if self.queue_service.get_quantity_queue() == 0:
            self.queue_service.start_queues()
            self.button_queues = self.buttons_queues_service.create_button_queue("ENTRAR/SAIR",
                                                                                 f"{self.queue_service.queue_rank_a.id} - {self.queue_service.queue_rank_b.id}")
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
            return
        await interact.response.send_message("NÃO EXISTEM FILAS PARA SER REMOVIDAS!!!", ephemeral=True)

    async def callback_button_queue(self, interact: discord.Interaction):
        # self.bot.loop.create_task(self.check_full_queues(interact))
        self.queues_id = (str(interact.data['custom_id']))
        print(f"IDS: {self.queues_id}")
        discord_id_player = str(interact.user.id)
        queues_id_parts = self.queues_id.split(" - ")
        queus_1 = self.queue_service.find_queue_by_id(queues_id_parts[0])
        queus_2 = self.queue_service.find_queue_by_id(queues_id_parts[1])

        print(f"QUEUES: {queus_1}, {queus_2}")
        if queus_1.rank == Rank.RANK_A:
            self.queue_service.queue_rank_a = queus_1
            self.queue_service.queue_rank_b = queus_2  # QUEUE RANK B
        else:
            self.queue_service.queue_rank_b = queus_2  # QUEUE RANK B
            self.queue_service.queue_rank_a = queus_1

        player = self.player_service.find_player_by_discord_id(discord_id_player, interact.user.name)
        current_queue_user = self.queue_service.find_current_queue_player(player)
        if player is not None and player.queue_status == StatusQueue.IN_VOTING_MAPS.value:
            await interact.response.send_message("Você já está em uma partida!!!", ephemeral=True)
            return

        if current_queue_user is not None:
            if current_queue_user == self.queue_service.queue_rank_a or current_queue_user == self.queue_service.queue_rank_b:
                return await self.quit_player_on_queue(player, current_queue_user, interact)

        if await self.check_if_exist_black_keys(interact, current_queue_user):
            return

        self.queue_service.add_player_on_queue(player, interact.user)
        await interact.response.send_message("Você entrou na fila!!!", ephemeral=True)
        print(self.queue_service.find_current_queue_player(player).rank)
        self.embeds_message_join[interact.user.name] = await interact.followup.send(
            embed=embed_join_queue_message(self.queue_service.find_current_queue_player(player)), ephemeral=True)
        await self.buttons_queues_service.update_message_queue(self.queue_service.get_quantity_players_on_queues(),
                                                               self.match_service.get_quantity_matches())

    async def quit_player_on_queue(self, player, current_queue_user, interact):
        if self.queue_service.remove_player_on_queue(player, current_queue_user):
            embed_user = self.embeds_message_join.get(interact.user.name)
            if embed_user:
                await embed_user.delete()
            await interact.response.send_message("Você saiu da fila!!!", ephemeral=True)
            await self.buttons_queues_service.update_message_queue(self.queue_service.get_quantity_players_on_queues(),
                                                                   self.match_service.get_quantity_matches())
            return

    async def check_full_queues(self, interact):
        while True:
            await asyncio.sleep(10)
            if len(self.queue_service.find_full_queues()) == 0:
                continue

            queue = self.queue_service.remove_full_queue(self.queue_service.find_full_queues())
            print(f"QUEUE DO LOOP: {queue}")
            key = self.black_security_service.get_random_key()
            await self.create_channels(queue, interact)
            new_queue = self.queue_service.create_queue(queue.rank, StatusQueue.DEFAULT)
            self.update_new_queue_after_full_queue(new_queue, new_queue)

            match = Match(queue.id, self.channel_vote_maps_references[queue.id], None, None, None,
                          None, None, None)
            self.match_service.add_match(match)
            await self.update_button_queue_message()
            await self.update_embed_message_join_by_queue(queue)
            await self.send_maps_vote_to_map(queue)
            await asyncio.sleep(30)
            map_winner = await self.get_winner_map_votes(queue)

            voice_a, voice_b = await self.create_voice_channel(self.match_service.get_quantity_matches(), interact,
                                                               queue)
            team_a, team_b = self.create_teams(queue)
            await self.send_teams(queue, map_winner, key, voice_a, voice_b, team_a, team_b)
            self.update_attributes_match(match, voice_a, voice_b, team_a, team_b, queue)
            self.match_service.add_match(match)
            await self.voting_end_match(queue)
            # await self.check_result_votes(2, queue, team_a, team_b, voice_a, voice_b)
            # await self.update_button_queue_message()
            # self.clear_all_references_by_queue(queue)
            # await asyncio.sleep(10)

    def clear_all_references_by_queue(self, queue):
        del self.channel_vote_maps_references[queue.id]
        del self.guild_categories_references[queue.id]

    async def check_result_votes(self, max_votes, queue, team_a, team_b, voice_a, voice_b):
        while await self.get_result_votes_end(max_votes, queue, team_a, team_b, voice_a, voice_b) is None:
            if "a" not in self.votes_end.keys() or "b" not in self.votes_end.keys():
                self.votes_end["a"] = 0
                self.votes_end["b"] = 0
            print("REGISTRO DE VOTAÇÃO LIMPOS")
            if self.message_end is not None:
                print(self.message_end)
                await self.message_end.edit(
                    content="VOTAÇÃO STATUS: Não foi possivel determinar a equipe vencedora, por favor vote novamente!")

                self.votes_end.clear()
                self.votes_end_user.clear()
            await asyncio.sleep(30)

    async def update_embed_message_join_by_queue(self, queue):
        for user in queue.discord_users:
            await self.embeds_message_join[user.name].edit(
                embed=embed_join_voting_maps(queue, self.channel_vote_maps_references[queue.id]))

    async def check_if_exist_black_keys(self, interact, queue):
        key = self.black_security_service.get_random_key()
        if key is None:
            adm_role = interact.guild.get_role(1126973920252280912)
            await interact.response.send_message(
                "Não foi possivel entrar na fila, pois não foi encontrada nenhuma black key!!!", ephemeral=True)
            if self.error_black_security_message is None:
                self.error_black_security_message = await interact.followup.send(
                    f"NÃO FOI POSSÍVEL INICIAR A PARTIDA, POIS NÃO FOI ENCONTRADA NENHUMA BLACK KEY!!! <@&{adm_role.id}>")
            return True

    async def create_channels(self, queue, interact):
        self.guild_categories_references[queue.id] = await interact.guild.create_category(queue.id)

        for player in queue.get_all_players():
            self.player_service.save_player(
                Player(None, player.discord_id, str(interact.user.name), player.rank, player.points, player.wins,
                       player.losses,
                       StatusQueue.IN_VOTING_MAPS))
        self.channel_vote_maps_references[queue.id] = await self.guild_categories_references[
            queue.id].create_text_channel("Votação de mapas",
                                          overwrites=self.get_overwrites(
                                              interact,
                                              queue))

    async def create_voice_channel(self, match_number, interact, queue):
        print(self.guild_categories_references[queue.id])
        voice_channel_a = await self.guild_categories_references[
            queue.id].create_voice_channel(f"PARTIDA {match_number} - Time A",
                                           overwrites=self.get_overwrites(interact,
                                                                          queue))
        voice_channel_b = await self.guild_categories_references[
            queue.id].create_voice_channel(f"PARTIDA {match_number} - Time B",
                                           overwrites=self.get_overwrites(interact,
                                                                          queue))
        return voice_channel_a, voice_channel_b

    def update_attributes_match(self, match, voice_a, voice_b, team_a, team_b, queue):
        match.voice_channel_teams_a = voice_a
        match.voice_channel_teams_b = voice_b
        match.team_a = team_a
        match.team_b = team_b
        match.category = self.guild_categories_references[queue.id]
        match.message_amount_matches = self.buttons_queues_service.get_message_queues_button()

    def update_new_queue_after_full_queue(self, queue: Queue, new_queue):
        if queue.rank == Rank.RANK_A:
            parts = self.queues_id.split(" - ")
            self.queues_id = parts[1] + " - " + new_queue.id
        else:
            parts = self.queues_id.split(" - ")
            self.queues_id = parts[0] + " - " + new_queue.id

    async def update_button_queue_message(self):
        self.button_queues.custom_id = self.queues_id
        self.buttons_queues_service.clear_view()
        self.buttons_queues_service.get_view().add_item(self.button_queues)
        await self.buttons_queues_service.message_button_create.edit(
            embed=embed_queues_message(self.queue_service.get_quantity_players_on_queues(),
                                       self.match_service.get_quantity_matches()),
            view=self.buttons_queues_service.get_view())
        # print(self.button_queues.custom_id)

    async def create_channel_voting_maps(self, interact: discord.Interaction, queue: Queue):
        for player in queue.get_all_players():
            self.player_service.save_player(
                Player(None, player.discord_id, str(interact.user.name), player.rank, player.points, player.wins,
                       player.losses,
                       StatusQueue.IN_VOTING_MAPS))

        channel = await self.guild_categories_references[queue.id].create_text_channel("Votação de mapas",
                                                                                       overwrites=self.get_overwrites(
                                                                                           interact, queue))
        self.channel_vote_maps_references[queue.id] = channel

    def create_teams(self, queue):
        players = queue.get_all_players()
        random.shuffle(players)
        halfway_point = len(players) // 2
        teammate_a = players[:halfway_point]
        teammate_b = players[halfway_point:]
        return teammate_a, teammate_b

    async def send_teams(self, queue, map_winner, key, voice_a, voice_b, team_a, team_b):

        await self.channel_vote_maps_references[queue.id].send(
            embed=team_mate_embed_message(voice_a, voice_b, map_winner, key, team_a, team_b))
        self.black_security_service.remove_one_key(key)

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

    async def send_maps_vote_to_map(self, queue):

        maps = [
            "Ankara-T",
            "MexicoT",
            "OLHO-2.0",
            "Porto-T",
            "Satelite-T",
            "Sub-Base",
            "ViuvaT"
        ]

        embed = discord.Embed(title="SELEÇÃO DE MAPAS", description="Escolha um mapa:",
                              color=0xFF0000)  # Cor vermelha: 0xFF0000
        for map_name in maps:
            embed.add_field(name=map_name, value=f"Vote pelo botão  para escolher o mapa {map_name}", inline=False)

        buttons = [
            discord.ui.Button(style=discord.ButtonStyle.primary, label=map_name) for map_name in maps
        ]

        view = discord.ui.View(timeout=None)
        for b, map_name in zip(buttons, maps):
            b.custom_id = map_name
            b.callback = self.map_button_vote_callback
            view.add_item(b)
        await self.channel_vote_maps_references[queue.id].send(embed=embed, view=view)

    async def map_button_vote_callback(self, interact: discord.Interaction):
        map_button_id = str(interact.data['custom_id'])
        if self.vote_maps_service.add_vote(map_button_id, interact.user.name, interact.channel.category.name) is False:
            await interact.response.send_message("VOcê já votou!", ephemeral=True)
        await interact.response.send_message(f"Você votou no {map_button_id}", ephemeral=True)

    async def get_winner_map_votes(self, queue):
        map_winner = self.vote_maps_service.get_map_with_max_votes(queue)
        file = discord.File(rf"maps/{map_winner}.jpeg")
        await self.channel_vote_maps_references[queue.id].send(file=file,
                                                               embed=embed_map_wiiner(map_winner,
                                                                                      self.vote_maps_service.get_votes_map_by_map_name(
                                                                                          map_winner, queue)))
        return map_winner

    async def voting_end_match(self, queue):
        self.view_end = discord.ui.View(timeout=None)
        self.buttons_queues_service.callback_button = self.callback_voting_end_button
        voting_end_button_yes = self.buttons_queues_service.create_button_queue("TIME A", "a")
        voting_end_button_no = self.buttons_queues_service.create_button_queue("TIME B", "b")

        self.view_end.add_item(voting_end_button_yes)
        self.view_end.add_item(voting_end_button_no)
        await self.channel_vote_maps_references[queue.id].send("VOTAÇÃO EQUIPE VENCEDORA:", view=self.view_end)

    async def callback_voting_end_button(self, interact: discord.Interaction):
        return
    #     button_id = str(interact.data['custom_id'])
    #     user = str(interact.user.name)
    #
    #     if "a" not in self.votes_end.keys() or "b" not in self.votes_end.keys():
    #         self.votes_end["a"] = 0
    #         self.votes_end["b"] = 0
    #
    #     self.votes_end_records[interact.channel.category.name] = self.votes_end
    #     if user in self.votes_end_user_records[interact.channel.category.name].keys() and \
    #             self.votes_end_user_records[interact.channel.category.name][user] != button_id:
    #         await interact.response.send_message("Você já votou!!!", ephemeral=True)
    #         return
    #
    #     else:
    #         self.votes_end_records[interact.channel.category][button_id] += 1
    #         self.votes_end_user_records[interact.channel.category][user] = button_id
    #         await interact.response.send_message(f"Você votou em {button_id}", ephemeral=True)
    #
    #         if self.message_end is None:
    #             self.message_end = await interact.followup.send("RESULTADO STATUS: VOTAÇÃO EM ANDAMENTO")
    #         # self.message_end = await interact.followup.send("RESULTADO STATUS: VOTAÇÃO EM ANDAMENTO", ephemeral=True)
    #         return

    async def get_result_votes_end(self, max_votes, queue, team_a, team_b, voice_a, voice_b):

        if self.votes_end_records[queue.id]['a'] >= max_votes:
            await self.channel_vote_maps_references[queue.id].send(embed=team_wins_embed(3, team_a, -2, team_b))
            self.update_win_status_player(team_a)
            self.update_losse_status_player(team_b)
            await asyncio.sleep(20)
            return True
        if self.votes_end_records[queue.id]['b'] >= max_votes:
            await self.channel_vote_maps_references[queue.id].send(embed=team_wins_embed(3, team_a, -2, team_b))
            self.update_win_status_player(team_b)
            self.update_losse_status_player(team_a)
            await asyncio.sleep(20)

            return True

        return None

    def update_win_status_player(self, team):
        for player_win in team:
            new_points = player_win.points + 3
            new_wins = player_win.wins + 1
            if new_points >= 150:
                new_rank = Rank.RANK_A
                self.player_service.save_player(
                    Player(player_win.id, player_win.discord_id, player_win.name, new_rank, 0, new_wins,
                           player_win.losses, StatusQueue.DEFAULT))
            else:
                self.player_service.save_player(
                    Player(player_win.id, player_win.discord_id, player_win.name, player_win.rank, new_points,
                           new_wins,
                           player_win.losses, StatusQueue.DEFAULT))

    def update_losse_status_player(self, team):
        for player_losse in team:
            new_points = player_losse.points - 2
            new_losses = player_losse.losses + 1
            new_rank = player_losse.rank
            if new_points < 0:
                new_points = 0
            if player_losse.rank == Rank.RANK_A and new_points < 150:
                new_rank = Rank.RANK_B
                self.player_service.save_player(
                    Player(player_losse.id, player_losse.discord_id, player_losse.name, new_rank, new_points,
                           player_losse.wins,
                           new_losses, StatusQueue.DEFAULT))
            else:
                self.player_service.save_player(
                    Player(player_losse.id, player_losse.discord_id, player_losse.name, player_losse.rank, new_points,
                           player_losse.wins,
                           new_losses, StatusQueue.DEFAULT))

        return

    async def clear_references(self, queue, voice_a, voice_b):
        await self.guild_categories_references[queue.id].delete()
        await self.channel_vote_maps_references[queue.id].delete()
        await voice_a.delete()
        await voice_b.delete()
        match = self.match_service.find_match_by_id(self.guild_categories_references[queue.id].name)
        self.match_service.remove_match(match)


async def setup(bot):
    await bot.add_cog(QueueCommandCog(bot))
