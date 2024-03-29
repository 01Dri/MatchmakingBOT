import uuid

import discord

from embeds.embedsmessages import queue_join_embed_message, queue_start_voting_maps_message
from entities.Player import Player
from entities.Queue import Queue
from enums.Rank import Rank
from enums.StatusQueue import StatusQueue
from exceptions.exceptions import InvalidRankPlayerException, CrowdedQueueException
from repositories.QueueRepository import QueueRepository
from repositories.playerrepository import PlayerRepository
from services.channelservice import ChannelService
from services.playerservice import PlayerService
from services.queuebuttonservice import QueueButtonService
from services.roleservice import RoleService
from utils.constants import MAX_PLAYER_ON_QUEUE, MAX_QUEUES, MINIMUM_PLAYER_QUEUE_START


class QueueService:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.max_players_for_queue = 2
        self.view = discord.ui.View()
        self.queues_repository = QueueRepository()
        self.player_service = PlayerService()
        self.queue_rank_a: Queue = None
        self.queue_rank_b: Queue = None
        self.queues_id = None

    def create_queue(self, rank, status) -> Queue:
        queue = Queue(str(uuid.uuid4()), rank, self.max_players_for_queue, status)
        self.queues_repository.save_queue(queue)
        return queue

    def start_queues(self):
        if self.get_quantity_queue() >= MAX_QUEUES:
            return False
        self.queue_rank_a = self.create_queue(Rank.RANK_A, StatusQueue.DEFAULT)
        self.queue_rank_b = self.create_queue(Rank.RANK_B, StatusQueue.DEFAULT)
        self.queues_id = f"{self.queue_rank_a.id} - {self.queue_rank_b.id}"

    def close_queues(self):
        try:
            self.queues_repository.remove_queue(self.queue_rank_a)
            self.queues_repository.remove_queue(self.queue_rank_b)
        except:
            return False

    def get_queues_id(self):
        return self.queues_id

    def set_queues_id(self, queues_id):
        self.queues_id = queues_id

    def find_current_queue_player(self, player: Player):
        return self.queues_repository.get_current_queue_user_by_discord_id(player.discord_id)

    def find_queue_by_id(self, queue_id):
        return self.queues_repository.get_queue_by_id(queue_id)

    def get_queue_by_id(self, queue_id: str):
        return self.queues_repository.get_queue_by_id(id_queue=queue_id)

    def get_quantity_queue(self):
        return self.queues_repository.get_amount_queue()

    def add_player_on_queue(self, player: Player, user):
        if player.rank == Rank.RANK_A:
            print("rank a")
            print(self.queue_rank_a.get_amount_players())
            if self.queue_rank_a.get_amount_players() < MINIMUM_PLAYER_QUEUE_START and self.queue_rank_b.get_amount_players() >= MINIMUM_PLAYER_QUEUE_START:
                print("ENTROU NA RANK A")
                self.queue_rank_b.add_player_queue(player, user)

                return self.queue_rank_b
            else:
                self.queue_rank_a.add_player_queue(player, user)
                return self.queue_rank_a

        else:
            print("ENTROU NA QUEUE B")
            self.queue_rank_b.add_player_queue(player, user)
            return self.queue_rank_b

    def remove_player_on_queue_by_discord_id(self, discord_id: str):
        for queue in self.queues_repository.get_all_queues():
            queue.remove_player_by_discord_id(discord_id)

    def remove_player_on_queue(self, plauer: Player, queue: Queue):
        return queue.remove_player_by_discord_id(plauer.discord_id)

    def find_player_on_queue(self, player: Player, queue: Queue):
        for p in queue.get_all_players():
            if p.discord_id == player.discord_id:
                return True
        return False

    def get_status_queue_by_player(self, player: Player):
        return player.queue_status

    def get_all_queues_to_remove(self) -> [Queue]:
        queues_to_remove = []
        queues_copy = dict(self.queues_repository.get_all_queues())
        for queue_id, queue in queues_copy.items():
            if queue.get_amount_players() == self.max_players_for_queue:
                queues_to_remove.append(queue)
        return queues_to_remove

    def remove_queues_by_list_queue(self, queues: []):
        for queue in queues:
            self.queues_repository.remove_queues_by_id(queue.id)

    def remove_all_discord_user_on_queue(self, queue: Queue):
        for discord_user in queue.get_all_discord_users():
            queue.remove_player_by_discord_id(discord_user.id)

    def remove_all_players_on_queu(self, queue: Queue):
        for p in queue.get_all_players():
            queue.remove_player_by_discord_id(p)

    def find_full_queues(self):
        queues_full = []
        for queue in self.queues_repository.get_all_queues():
            if queue.get_amount_players() == self.max_players_for_queue:
                queues_full.append(queue)
        return queues_full

    async def set_role_all_users_on_queue(self, role, queue):
        for user in queue.get_all_discord_users():
            await user.add_roles(role)

    def remove_full_queue(self, list_queues_full: [Queue]):
        for queue_full in list_queues_full:
            self.queues_repository.remove_queue(queue_full)
            return queue_full

    def get_quantity_players_on_queues(self):
        return self.queues_repository.get_all_players_on_queues()

    def remove_queue_by_id(self, queue_id: str):
        self.queues_repository.remove_queues_by_id(queue_id)

    def get_all_id_queues(self):
        return self.queues_repository.get_all_queues_id()

    # async def remove_full_queues(self):
    #     full_queue = self.get_all_queues_to_remove()
    #     if full_queue:
    #         for queue in full_queue:
    #             role = await self.role_service.create_role(queue.id, discord.Color.gold())
    #             channel_voting = await self.channel_service.create_channel_text(queue, role)
    #             await self.message_service.send_dm_message_all_discord_users(queue.get_all_discord_users(),
    #                                                                          queue_start_voting_maps_message(queue,
    #                                                                                                          channel_voting))
    #             await self.channel_service.send_voting_maps_message_to_channel(queue)
    #             self.save_status_voting_for_players(queue)
    #             self.remove_all_discord_user_on_queue(queue)
    #             self.remove_all_players_on_queu(queue)
    #             self.remove_queues_by_list_queue(full_queue)
    #             self.button_service.clear_view()
    #             await self.button_service.delete_message_button()
    #             return True
    #     return False

    def save_status_voting_for_players(self, queue: Queue):
        players = queue.get_all_players()
        for player in players:
            self.player_repository.save_player(
                Player(player.id, player.discord_id, player.name, player.rank, player.points,
                       StatusQueue.IN_VOTING_MAPS))

    def remove_all_queues(self):
        for queue in self.queues_repository.get_all_queues():
            self.queues_repository.remove_queue(queue)

    async def update_players_on_queue_message(self, message, queue_a, queue_b):
        embed = discord.Embed(title="JOGADORES NAS FILAS: ", color=discord.Color.red())
        embed.add_field(name="Rank A", value=str(queue_a.get_amount_players()), inline=True)
        embed.add_field(name="Rank B", value=str(queue_b.get_amount_players()), inline=True)
        embed.set_thumbnail(url="https://i.ibb.co/G3mkZ1p/Screenshot-from-2024-03-13-14-31-37.png")
        embed.set_footer(text="Quantidade de partidas: ")
        await message.edit(embed=embed)
