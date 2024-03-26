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
        if await self.is_correct_channel(interact.channel.name, "perfil", interact):
            player = self.player_service.find_player_by_discord_id(str(interact.user.id), interact.user.name)
            if player is None:
                player = self.player_service.save_player(
                    Player(None, str(interact.user.id), str(interact.user.name), Rank.RANK_B, 0, 0, 0,
                           StatusQueue.DEFAULT))
            await interact.response.send_message(embed=embed_profile_message(player, interact.user), ephemeral=True)

    async def is_correct_channel(self, current_channel, channel_correct, interact):
        if current_channel != channel_correct:
            await interact.response.send_message(f"Esse comando deve ser utilizado no canal #{channel_correct}",
                                                 ephemeral=True)
            return
        return True


async def setup(bot):
    await bot.add_cog(PlayerCommandCog(bot))
