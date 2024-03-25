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
    await bot.wait_until_ready()
    # await bot.load_extension("cogs.queuecommandscog")
    await bot.load_extension("cogs.blacksecuritycommandscog")
    await bot.load_extension("cogs.matchcommandcog")
    await bot.load_extension("cogs.playercommandcog")
    await bot.load_extension("cogs.queuecommandcog")



@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await load_cogs()


@bot.command()
async def loadcogs(ctx):
    await bot.tree.sync()
    await load_cogs()
    await ctx.send("Comandos carregados!!!")


bot.run(token)
