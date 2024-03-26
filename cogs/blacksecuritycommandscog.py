import discord
from discord.app_commands import CommandInvokeError
from discord.ext import commands
from discord import app_commands

from repositories.blacksecurityrepository import BlackSecurityRepository
from services.blacksecurityservice import BlackSecurityService


class BlackSecurityCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.black_security_service = BlackSecurityService()

    async def check_permissions_and_channel(self, interact, channel_name):
        if not interact.user.guild_permissions.administrator:
            await interact.response.send_message("Você precisa ser um ADM para usar esse comando!!!", ephemeral=True)
            return False
        if interact.channel.name != channel_name:
            await interact.response.send_message(f"Esse comando deve ser utilizado no canal #{channel_name}",
                                                 ephemeral=True)
            return False
        return True

    @app_commands.command()
    async def addkey(self, interact: discord.Interaction, key: str):
        if not await self.check_permissions_and_channel(interact, "keys"):
            return
        if self.black_security_service.save_key(key) is False:
            await interact.response.send_message("Formato inválido ou key já existente!!!", ephemeral=True)
            return
        await interact.response.send_message("Keys do BlackSecurity salvas!!!!", ephemeral=True)

    @app_commands.command()
    async def verkeys(self, interact: discord.Interaction, quantidade: int):
        if not await self.check_permissions_and_channel(interact, "keys"):
            return
        keys = self.black_security_service.get_keys(quantidade)
        if not keys:
            await interact.response.send_message("Não foi encontrada nenhuma KEY!", ephemeral=True)
            return
        await interact.response.send_message(embed=self.black_security_service.send_keys(keys))

    @app_commands.command()
    async def removerkey(self, interact: discord.Interaction, key: str):
        if not await self.check_permissions_and_channel(interact, "keys"):
            return
        self.black_security_service.remove_keys(key)
        await interact.response.send_message("Key removida!!!", ephemeral=True)

    @app_commands.command()
    async def removerkeys(self, interact: discord.Interaction):
        if not await self.check_permissions_and_channel(interact, "keys"):
            return
        self.black_security_service.remove_all_keys()
        await interact.response.send_message("Todas as keys do Black security foram removidas!!!", ephemeral=True)

    @app_commands.command()
    async def keyaleatoria(self, interact: discord.Interaction):
        if not await self.check_permissions_and_channel(interact, "keys"):
            return
        key = self.black_security_service.get_random_key()
        await interact.response.send_message(embed=self.black_security_service.send_random_key(key))


async def setup(bot):
    await bot.add_cog(BlackSecurityCommands(bot))
