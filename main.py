import asyncio
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
token = os.getenv("TOKEN_DISCORD")
main_guild_id: int = 1069132221388177468
bot = commands.Bot(command_prefix=".", intents=intents)


async def load_cogs():
    await bot.load_extension("cogs.queuecommandscog")


@bot.event
async def on_ready():
    await load_cogs()
    await bot.tree.sync()


def add_command(command):
    cmd = commands.Command(command)
    bot.add_command(cmd)


bot.run(token)
