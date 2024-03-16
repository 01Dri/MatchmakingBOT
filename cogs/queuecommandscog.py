import discord.ui
from discord import app_commands
from discord.ext import commands

from embeds.embedsmessages import embed_queues_message, embed_join_queue_message
from entities.Player import Player
from enums.Rank import Rank
from enums.StatusQueue import StatusQueue
from repositories.playerrepository import PlayerRepository
from services.playerservice import PlayerService
from services.queuebuttonservice import QueueButtonService
from services.queueservice import QueueService


class QueueCommandCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.view_ui_discord = discord.ui.View()
        self.queue_service = QueueService(2, None, self.view_ui_discord, None)
        self.buttons_queues_service = QueueButtonService(self.view_ui_discord, None)
        self.player_service = PlayerService()
        self.queue_ranked = None
        self.queue_unranked = None
        super().__init__()

    @app_commands.command()
    async def iniciarfila(self, interact: discord.Interaction):
        if self.queue_service.get_quantity_queue() == 0:
            ## DEPOIS CRIAR FILA RANKED
            self.queue_unranked = self.queue_service.create_queue_unranked()
            self.buttons_queues_service.create_button_queue("UNRANKED: ENTRAR/SAIR", self.queue_unranked.id, self.callback_button_queue)
        else:
            await interact.response.send_message("FILAS JÁ INICIADAS!!!")
            return
        await interact.response.send_message("Você iniciou as filas", ephemeral=True)
        print(f"QUANTIDADE DE FILAS INICIADAS: {self.queue_service.get_quantity_queue()}")
        self.buttons_queues_service.message_button_queues = await interact.followup.send(embed=embed_queues_message(self.queue_unranked), view=self.view_ui_discord)
    @app_commands.command()
    async def cancelarfilas(self, interact: discord.Interaction):
        if self.queue_service.get_quantity_queue() >= 1:
            self.queue_service.remove_all_queues()
            self.buttons_queues_service.clear_view()
            await self.buttons_queues_service.delete_message_button()
            await interact.response.send_message("Filas canceladas!!!", view=self.view_ui_discord)
            print(f"QUANTIDADE DE FILAS APÓS REMOÇÃO: {self.queue_service.get_quantity_queue()}")
            return
        await interact.response.send_message("NÃO EXISTEM FILAS PARA SER REMOVIDAS!!!", ephemeral=True)

    async def callback_button_queue(self, interact: discord.Interaction):
        queue_id_from_button = str(interact.data['custom_id'])
        discord_id_player = str(interact.user.id)
        current_queue = self.queue_service.find_queue_by_id(queue_id_from_button)
        player = self.player_service.find_player(discord_id_player)
        if player is None:
            player = self.player_service.save_player(Player(None, discord_id_player, str(interact.user.name), Rank.UNRAKED, 0, 0, 0, StatusQueue.IN_QUEUE))
        if self.queue_service.remove_player_on_queue(player, current_queue):
            await interact.response.send_message("Você saiu da fila!!!", ephemeral=True)
            await self.queue_service.message_join_embed.delete()
            print(f"PLAYERS NA FILA: {current_queue.get_all_players()}")
            return
        self.queue_service.add_player_on_queue(player, current_queue, interact.user)
        await interact.response.send_message("Você entrou na fila!!!", ephemeral=True)
        self.queue_service.message_join_embed = await interact.followup.send(embed=embed_join_queue_message(self.queue_unranked))
        print(f"PLAYERS NA FILA: {current_queue.get_all_players()}")



async def setup(bot):
    await bot.add_cog(QueueCommandCog(bot))
