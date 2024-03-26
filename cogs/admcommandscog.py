import discord
from discord.app_commands import CommandInvokeError
from discord.ext import commands
from discord import app_commands

from services.blacksecurityservice import BlackSecurityService
from services.playerservice import PlayerService


class AdmCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.player_service = PlayerService()

    @app_commands.command()
    async def resetall(self, interact: discord.Interaction):
        if await self.is_adm(interact):
            self.player_service.reset_all_players_record()
            await interact.response.send_message("Todas as informações sobre os jogadores foram resetadas!!!",
                                                 ephemeral=True)


    async def is_correct_channel(self, current_channel, channel_correct, interact):
        if current_channel != channel_correct:
            await interact.response.send_message(f"Esse comando deve ser utilizado no canal #{channel_correct}",
                                                 ephemeral=True)
            return
        return True

    async def is_adm(self, interact):
        if not interact.user.guild_permissions.administrator:
            await interact.response.send_message("Você precisa ser um ADM para usar esse comando!!!", ephemeral=True)
            return False
        return True


async def setup(bot):
    await bot.add_cog(AdmCommands(bot))
