import discord
from discord.ext import commands
from discord import app_commands

from repositories.blacksecurityrepository import BlackSecurityRepository
from services.blacksecurityservice import BlackSecurityService


class BlackSecurityCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.black_security_service = BlackSecurityService()

    @app_commands.command()
    async def addkey(self, interact: discord.Interaction, key: str):
        if interact.user.guild_permissions.administrator:
            self.black_security_service.save_key(key)
            await interact.response.send_message("Keys do BlackSecurity salvas!!!!", ephemeral=True)
        else:
            await interact.response.send_message("Você precisa ser um ADM para usar esse comando!!!", ephemeral=True)

    @app_commands.command()
    async def verkeys(self, interact: discord.Interaction, quantidade: int):
        if interact.user.guild_permissions.administrator:
            keys = self.black_security_service.get_keys(quantidade)
            if len(keys) == 0:
                await interact.response.send_message("Não foi encontrada nenhuma KEY!", ephemeral=True)
                return
            await interact.response.send_message(embed=self.black_security_service.send_keys(keys))




async def setup(bot):
    await bot.add_cog(BlackSecurityCommands(bot))
