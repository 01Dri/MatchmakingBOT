import asyncio
import random

import discord
from discord.ext import commands
from discord import app_commands

from embeds.embedsmessages import embed_queues_message, embed_join_queue_message, queue_start_voting_maps_message, \
    embed_map_wiiner, team_mate_embed_message
from entities.Match import Match
from enums.Rank import Rank
from enums.StatusQueue import StatusQueue
from services.blacksecurityservice import BlackSecurityService
from services.matchservice import MatchService
from services.messageservices import MessageService
from services.playerservice import PlayerService
from services.queuebuttonservice import QueueButtonService
from services.queueservice import QueueService
from services.votesendservices import VotesEndService
from services.votesmapsservice import VotesMapsService
from utils.constants import MAX_PLAYER_ON_QUEUE


class QueueCommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue_service = QueueService()
        self.button_service = QueueButtonService(self.button_join_queue_callback)
        self.match_service = MatchService()
        self.player_service = PlayerService()
        self.message_service = MessageService()
        self.black_security_service = BlackSecurityService()
        self.votes_maps_service = VotesMapsService()
        self.votes_end_service = VotesEndService()
        self.vote_end_message_reference = {}

    @app_commands.command()
    async def iniciarfilas(self, interact: discord.Interaction):
        if await self.is_adm(interact):
            self.bot.loop.create_task(self.start_queue_full(interact))
            current_channel = interact.channel.name
            if await self.is_correct_channel(current_channel, "filas", interact):
                if self.queue_service.start_queues() is False:
                    await interact.response.send_message("Já existem filas inicializadas", ephemeral=True)
                    return
                await interact.response.send_message("Você iniciou as filas", ephemeral=True)
                self.button_service.create_button_queue("Entrar - Sair", self.queue_service.get_queues_id())
                self.button_service.set_message_button_queues_created(await self.send_message_button_queues(interact))

    @app_commands.command()
    async def cancelarfilas(self, interact: discord.Interaction):
        if await self.is_adm(interact):
            current_channel = interact.channel.name
            if await self.is_correct_channel(current_channel, "filas", interact):
                if self.queue_service.close_queues() is False:
                    await interact.response.send_message("Não existem filas para serem removidas")
                    return
                await self.button_service.delete_message_button()
                self.button_service.clear_view()
                await interact.response.send_message("Filas removidas!", ephemeral=True)

    async def is_adm(self, interact):
        if not interact.user.guild_permissions.administrator:
            await interact.response.send_message("Você precisa ser um ADM para usar esse comando!!!", ephemeral=True)
            return False
        return True

    async def is_correct_channel(self, current_channel, channel_correct, interact):
        if current_channel != channel_correct:
            await interact.response.send_message(f"Esse comando deve ser utilizado no canal #{channel_correct}",
                                                 ephemeral=True)
            return
        return True

    async def button_join_queue_callback(self, interact: discord.Interaction):
        if await self.check_black_security_key(interact) is False:
            return
        queue_rank_a, queue_rank_b = self.get_queues_id_by_button_queue(interact.data['custom_id'])
        player = self.player_service.find_player_by_discord_id(str(interact.user.id), interact.user.name)
        current_queue_user = self.queue_service.find_current_queue_player(player)
        if current_queue_user is None and player.queue_status == StatusQueue.DEFAULT.value:
            queue = self.queue_service.add_player_on_queue(player, interact.user)
            await interact.response.send_message("Você entrou na fila", ephemeral=True)
            await self.send_embed_message_join_queue(queue, interact)

            if queue.get_amount_players() == MAX_PLAYER_ON_QUEUE:
                await self.start_queue_full(interact)
            return

        if current_queue_user is not None and (
                current_queue_user.id == queue_rank_a.id or current_queue_user.id == queue_rank_b.id):
            self.queue_service.remove_player_on_queue_by_discord_id(player.discord_id)
            await self.message_service.delete_message_embed_join_queue(interact.user.name)
            await interact.response.send_message("Você saiu da fila!", ephemeral=True)
            await self.button_service.update_message_button_queues(
                embed_queues_message(self.queue_service.get_quantity_players_on_queues(),
                                     self.match_service.get_quantity_matches()))
            return
        print(player.queue_status)
        if player.queue_status != StatusQueue.DEFAULT.value:
            await interact.response.send_message("Você já está em uma partida!", ephemeral=True)

    async def start_queue_full(self, interact):
        full_queues = self.queue_service.find_full_queues()
        if full_queues:
            for queue in full_queues:
                print(queue.id)
                print(self.match_service.get_matches())
                await self.process_full_queue(queue, interact)
        # await asyncio.sleep(40)

    async def process_full_queue(self, queue, interact):
        print(f"INICIANDO QUEUE: {queue.id}")
        self.queue_service.remove_full_queue([queue])
        key = self.black_security_service.get_random_key()
        self.black_security_service.remove_one_key(key)
        self.update_queue_status_player(queue)
        new_queue = self.create_new_queue_after_full_queue(queue)
        await self.update_queues_button_id(queue, new_queue)
        team_a, team_b = self.create_teams_match(queue)
        match = self.create_match(queue)
        print(f"CRIANDO A PARTIDA: {match.id}")
        self.match_service.add_match(match)  # SALVANDO UMA NOVA PARTIDA
        category_queue_session = await self.create_category_channels(interact, queue)
        channel_a, channel_b = await self.create_voices_channels(interact, category_queue_session, queue)

        await self.update_message_join_queue(self.message_service.get_channel_session_voting_maps(queue),
                                             queue)  # ATUALIZANDO EMBED APÓS ENTRAR NA FILA
        match = self.update_match(match, channel_a, channel_b, category_queue_session, queue, team_a, team_b)

        await self.button_service.update_message_button_queues(
            embed_queues_message(self.queue_service.get_quantity_players_on_queues(),
                                 self.match_service.get_quantity_matches()))

        await self.message_service.send_maps_vote_to_channel(queue, self.vote_maps_callback_button)
        await asyncio.sleep(15)
        map_winner = self.votes_maps_service.get_result_votes_session(queue.id)
        channel_maps = self.message_service.get_channel_session_voting_maps(queue)
        await self.send_winner_map_to_channel(queue, map_winner, channel_maps)
        await self.message_service.delete_message_button_maps(queue)

        await self.send_teams_to_channel(map_winner, key, channel_a, channel_b, match.team_a, match.team_b,
                                         channel_maps)
        await self.send_voting_end_match_to_channel(self.message_service.get_channel_session_voting_maps(queue))
        await self.wait_for_vote_result(queue)

    async def wait_for_vote_result(self, queue):
        while self.votes_end_service.get_result_votes_session(
                self.votes_end_service.get_session_vote(queue.id)) is None:
            if self.match_service.find_match_by_id(str(queue.id)) is not None:
                print("TO PRESO AQ")
                await asyncio.sleep(20)
            else:
                print("NÃO ENCONTROU A PARTIDA!")
                break
                # await self.start_queue_full(interact)
        else:
            result = self.votes_end_service.get_result_votes_session(self.votes_end_service.get_session_vote(queue.id))
            match = self.match_service.find_match_by_id(queue.id)
            print(f"PARTIDA ENCONTRADA! {match}")
            await self.match_service.send_points_to_users(match, result, self.vote_end_message_reference)
            await asyncio.sleep(20)
            await self.match_service.remove_attributes_on_match(match)

    async def send_voting_end_match_to_channel(self, channel):
        view_end = discord.ui.View(timeout=None)
        voting_end_button_yes = self.button_service.create_button_queue("TIME A", "a")
        voting_end_button_no = self.button_service.create_button_queue("TIME B", "b")
        voting_end_button_yes.callback = self.vote_end_callback_button
        voting_end_button_no.callback = self.vote_end_callback_button
        view_end.add_item(voting_end_button_yes)
        view_end.add_item(voting_end_button_no)
        await channel.send("VOTAÇÃO EQUIPE VENCEDORA:", view=view_end)

    async def vote_end_callback_button(self, interact: discord.Interaction):
        vote = str(interact.data['custom_id'])
        queue_id = str(interact.channel.category.name)
        session = self.votes_end_service.get_session_vote(queue_id)
        if self.votes_end_service.add_vote_user_to_session(interact.user.name, session, vote) is False:
            await interact.response.send_message("Você já votou!", ephemeral=True)
            return
        self.votes_end_service.add_vote_map_to_session(session, vote)
        await interact.response.send_message(f"Você votou em {vote}", ephemeral=True)
        self.vote_end_message_reference[interact.user.name] = await interact.followup.send(
            "STATUS VOTAÇÃO: EM ANDAMENTO!", ephemeral=True)

    async def vote_maps_callback_button(self, interact: discord.Interaction):
        map_button_id = str(interact.data['custom_id'])
        category_channel_name = str(interact.channel.category.name)
        if self.votes_maps_service.add_vote_user_to_session(interact.user.name, category_channel_name, map_button_id) is False:
            await interact.response.send_message("VOcê já votou!", ephemeral=True)
            return
        self.votes_maps_service.add_vote_map_to_session(category_channel_name, map_button_id)
        await interact.response.send_message(f"Você votou no {map_button_id}", ephemeral=True)

    async def send_winner_map_to_channel(self, queue, winner, channeç):
        file = discord.File(rf"maps/{winner}.jpeg")
        await channeç.send(file=file, embed=embed_map_wiiner(winner,self.votes_maps_service.get_quantity_votes_by_map_name(winner, queue.id)))

    def update_queue_status_player(self, queue):
        players = queue.get_all_players()
        for player in players:
            player.queue_status = StatusQueue.IN_VOTING_MAPS
            self.player_service.save_player(player)

    def create_teams_match(self, queue):
        players = queue.get_all_players()
        random.shuffle(players)
        halfway_point = len(players) // 2
        teammate_a = players[:halfway_point]
        teammate_b = players[halfway_point:]
        return teammate_a, teammate_b

    async def send_teams_to_channel(self, map_winner, key, voice_a, voice_b, team_a, team_b, channel):

        await channel.send(
            embed=team_mate_embed_message(voice_a, voice_b, map_winner, key, team_a, team_b))
        # self.black_security_service.remove_one_key(key)

    def update_match(self, match, channel_a, channel_b, category_queue_session, queue, team_a, team_b):
        match.channel_voting_maps = self.message_service.get_channel_session_voting_maps(queue)
        match.voice_channel_teams_a = channel_a
        match.voice_channel_teams_b = channel_b
        match.team_a = team_a
        match.team_b = team_b
        match.category = category_queue_session
        self.match_service.add_match(match)
        return match

    def create_match(self, queue):
        # team_a, team_b = self.create_teams_match(queue)
        match = Match(queue.id, None, None, None, None,
                      None, None,
                      self.button_service.get_message_queues_button(), queue.rank)
        return match

    async def update_message_join_queue(self, channel, queue):
        users = queue.get_all_discord_users()
        for user in users:
            await self.message_service.get_message_embed_join_queue(user).edit(
                embed=queue_start_voting_maps_message(queue, channel))

    async def create_voices_channels(self, interact, category_session_queue, queue):
        channel_team_a = await category_session_queue.create_voice_channel(
            f"PARTIDA - {self.match_service.get_quantity_matches()} - TIME A",
            overwrites=self.get_overwrites_channels(interact, queue))
        channel_team_b = await category_session_queue.create_voice_channel(
            f"PARTIDA - {self.match_service.get_quantity_matches()} - TIME B",
            overwrites=self.get_overwrites_channels(interact, queue))
        self.message_service.set_voice_channel_session(channel_team_a, channel_team_b, queue)
        return channel_team_a, channel_team_b

    def get_overwrites_channels(self, interact, queue):
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

    async def create_category_channels(self, interact, queue):

        self.message_service.set_guild_category(await interact.guild.create_category(queue.id), queue)
        category_session_queue = self.message_service.get_category_queue(queue)
        channel_voting_maps_session = await category_session_queue.create_text_channel("Votação de mapas",
                                                                                       overwrites=self.get_overwrites_channels(
                                                                                           interact, queue))
        self.message_service.set_channel_session_queue(queue, channel_voting_maps_session)
        return category_session_queue

    def create_new_queue_after_full_queue(self, queue):
        new_queue = None
        if queue.rank == Rank.RANK_A:
            new_queue = self.queue_service.create_queue(Rank.RANK_A, StatusQueue.DEFAULT)
        else:
            new_queue = self.queue_service.create_queue(Rank.RANK_B, StatusQueue.DEFAULT)
        return new_queue

    async def update_queues_button_id(self, queue, new_queue):
        queues_id = self.queue_service.get_queues_id()
        if queue.rank == Rank.RANK_A:
            parts = queues_id.split(" - ")
            queues_id = parts[1] + " - " + new_queue.id
            self.queue_service.queue_rank_a = new_queue
        else:
            parts = queues_id.split(" - ")
            queues_id = parts[0] + " - " + new_queue.id
            self.queue_service.queue_rank_b = new_queue

        self.queue_service.set_queues_id(queues_id)
        await self.button_service.update_custom_id_button_queues(queues_id, self.button_join_queue_callback)

    async def check_black_security_key(self, interact):
        key = self.black_security_service.get_random_key()
        role_adm_id = 1126973920252280912
        role = interact.guild.get_role(role_adm_id)
        if key is None:
            try:
                await interact.response.send_message(
                    "Não foi possivel entrar na fila, pois não há chaves da black security disponiveis!", ephemeral=True)
            except:
                await interact.followup.send(
                    "Não foi possivel entrar na fila, pois não há chaves da black security disponiveis!",
                    ephemeral=True)

            await interact.followup.send(
                f"NÃO FOI POSSÍVEL INICIAR A PARTIDA, POIS NÃO FOI ENCONTRADA NENHUMA BLACK KEY!!! {role.mention}")
            return False

        return key

    async def send_message_button_queues(self, interact):
        return await interact.followup.send(
            embed=embed_queues_message(self.queue_service.get_quantity_players_on_queues(),
                                       self.match_service.get_quantity_matches()),
            view=self.button_service.get_view())

    async def send_embed_message_join_queue(self, queue, interact):
        self.message_service.set_embed_message_join_queue(interact.user, await interact.followup.send(
            embed=embed_join_queue_message(queue), ephemeral=True))
        await self.button_service.update_message_button_queues(
            embed_queues_message(self.queue_service.get_quantity_players_on_queues(),
                                 self.match_service.get_quantity_matches()))

    def get_queues_id_by_button_queue(self, queus_id):
        queues_split = queus_id.split(" - ")
        queue_a = self.queue_service.find_queue_by_id(queues_split[0])
        queue_b = self.queue_service.find_queue_by_id(queues_split[1])
        return queue_a, queue_b


async def setup(bot):
    await bot.add_cog(QueueCommandsCog(bot))
