import discord
from discord.ext import commands
from discord import app_commands

from embeds.embedsmessages import embed_profile_message
from entities.Player import Player
from enums.Rank import Rank
from enums.StatusQueue import StatusQueue
from services.playerservice import PlayerService


class PlayerCommandCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.player_service = PlayerService()

    @app_commands.command()
    async def perfil(self, interact: discord.Interaction):
        # if await self.is_adm(interact):
        player = self.player_service.find_player_by_discord_id(str(interact.user.id), interact.user.name)
        if player is None:
            player = self.player_service.save_player(Player(None, str(interact.user.id), str(interact.user.name), Rank.RANK_B, 0, 0, 0, StatusQueue.DEFAULT))
        await interact.response.send_message(embed=embed_profile_message(player, interact.user), ephemeral=True)

    @app_commands.command()
    async def resetall(self, interact: discord.Interaction):
        if await self.is_adm(interact):
            self.player_service.reset_all_players_record()
            await interact.response.send_message("Todas as informações sobre os jogadores foram resetadas!!!",
                                                 ephemeral=True)

    async def is_adm(self, interact):
        if not interact.user.guild_permissions.administrator:
            await interact.response.send_message("Você precisa ser um ADM para usar esse comando!!!", ephemeral=True)
            return False
        return True


async def setup(bot):
    await bot.add_cog(PlayerCommandCog(bot))
