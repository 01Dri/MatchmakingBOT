import uuid

import discord
from discord import app_commands
from discord.ext import commands
from entities.Player import Player
from entities.Queue import Queue
from repositories.QueueRepository import QueueRepository


class CommandsQueue(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.queues_repository = QueueRepository()
        self.view = discord.ui.View()
        self.button_join = discord.ui.Button(label="Entrar/Sair", style=discord.ButtonStyle.green)
        self.button_join.callback = self.button_join_callback
        self.button_join.custom_id = "default"
        self.view.add_item(self.button_join)
        super().__init__()

    @app_commands.command()
    async def start(self, interact: discord.Interaction):
        queue = self.queues_repository.get_queue_by_player_id(str(interact.user.id))
        print(f"QUEUE DO COMANDO /START {queue}")
        if queue is not None:
            await interact.response.send_message("Você já está em uma QUEUE!!!", ephemeral=True)
            return

        player = Player(interact.user.id, interact.user.name, None)
        queue = Queue(str(uuid.uuid4()))
        queue.add_player(player)
        self.queues_repository.save_queue(queue)
        await interact.response.send_message("Você criou uma QUEUE", ephemeral=True)

        # Atualizar o botão com o novo ID da fila
        self.button_join.custom_id = queue.id
        await interact.followup.send("Uma QUEUE foi iniciada!!!|", view=self.view)

    async def button_join_callback(self, interact: discord.Interaction):
        id_queue_from_button = interact.data['custom_id']  # O id do botão é o mesmo da QUEUE
        print(f"ID QUEUE: {id_queue_from_button}")
        print(self.queues_repository.get_amount_queue())
        queue_user = self.queues_repository.get_queue_by_player_id(str(interact.user.id))
        print(f"QUEUE USER: {queue_user}")
        if queue_user is not None:
            queue_user.remove_player(str(interact.user.id))
            await interact.response.send_message("Você saiu da QUEUE", ephemeral=True)
            await interact.followup.send(f"Players na fila: {queue_user.get_amount_players()}")
            return

        queue = self.queues_repository.get_queue_by_id(str(id_queue_from_button))
        print(f"QUEUE: {queue}")
        if queue is not None:
            player = Player(interact.user.id, interact.user.name, None)
            queue.add_player(player)
            # queue.get_all_players_name()
            await interact.response.send_message(f"@{player.name} Entrou!!!")
            await interact.followup.send(f"Players na fila: {queue.get_amount_players()}")
            return
        print("NÃO ACHOU A QUEUE")


async def setup(bot):
    await bot.add_cog(CommandsQueue(bot))
