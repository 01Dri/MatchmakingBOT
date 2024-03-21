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
        if await self.is_adm(interact):
            self.black_security_service.save_key(key)
            await interact.response.send_message("Keys do BlackSecurity salvas!!!!", ephemeral=True)

    @app_commands.command()
    async def verkeys(self, interact: discord.Interaction, quantidade: int):
        if await self.is_adm(interact):
            keys = self.black_security_service.get_keys(quantidade)
            if len(keys) == 0:
                await interact.response.send_message("Não foi encontrada nenhuma KEY!", ephemeral=True)
                return
            await interact.response.send_message(embed=self.black_security_service.send_keys(keys))

    @app_commands.command()
    async def removerkeys(self, interact: discord.Interaction, key: str):
        if await self.is_adm(interact):
            self.black_security_service.remove_keys(key)
            await interact.response.send_message("Key removida!!!", ephemeral=True)

    @app_commands.command()
    async def keyaleatoria(self, interact: discord.Interaction):
        key = self.black_security_service.get_random_key()
        await interact.response.send_message(embed=self.black_security_service.send_random_key(key))

    async def is_adm(self, interact):
        if not interact.user.guild_permissions.administrator:
            await interact.response.send_message("Você precisa ser um ADM para usar esse comando!!!", ephemeral=True)
            return False
        return True


async def setup(bot):
    await bot.add_cog(BlackSecurityCommands(bot))
