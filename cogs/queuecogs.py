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
        super().__init__()

    @app_commands.command()
    async def start(self, interact: discord.Interaction):
        plauer = Player(interact.user.id, interact.user.name, None)
        await self.check_if_player_already_queue(plauer, interact)
        queue = Queue(plauer.id)
        queue.add_player(plauer)
        self.queues_repository.save_queue(queue)
        await interact.response.send_message("Você criou uma QUEUE", ephemeral=True)

    async def check_if_player_already_queue(self, plauer: Player, interact: discord.Interaction):
        if self.queues_repository.get_queue_by_player_id(plauer.id) is not None:
            await interact.response.send_message("Você já está em uma QUEUE!!!", ephemeral=True)
            return

async def setup(bot):
    await bot.add_cog(CommandsQueue(bot))
