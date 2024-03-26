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
    await bot.load_extension("cogs.admcommandscog")



@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await load_cogs()


@bot.command()
async def loadcogs(ctx):
    await bot.tree.sync()
    await load_cogs()
    await ctx.send("Comandos carregados!!!")


@bot.command()
async def start(ctx):
    guild = ctx.guild
    category = await guild.create_category("🤖 BOT-ADM 🛠️")
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        guild.me: discord.PermissionOverwrite(read_messages=True),
        guild.roles[0]: discord.PermissionOverwrite(read_messages=True)  # Assumes the first role is @everyone
    }
    channel_adm_keys = await category.create_text_channel("keys", overwrites=overwrites)

    category_queues = await guild.create_category("MATCHMAKING️")
    channel_queues = await category_queues.create_text_channel("FILAS")
    channel_profile = await category_queues.create_text_channel("PERFIL")



    message = (
        f"**CANAIS PARA ADMINISTRAÇÃO CRIADOS:**\n"
        f"- {channel_adm_keys.mention}\n"
        f"Agora você pode acessar os canais de administração diretamente através dos links acima! \n"
        "\n"
        f"**CANAIS PARA OS JOGADORES:**\n"
        f"- {channel_queues.mention}\n"
        f"- {channel_profile.mention}\n"

    )

    await ctx.send(message)


bot.run(token)
