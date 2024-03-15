import random

import discord

from entities.Player import Player
from entities.Queue import Queue


def queue_join_embed_message(player: Player, queue: Queue):
    embed = discord.Embed(title='MATCHMAKING FILA', description=player.name, color=0xff0000)
    embed.set_thumbnail(url="https://i.ibb.co/G3mkZ1p/Screenshot-from-2024-03-13-14-31-37.png")
    embed.add_field(name="ID DA FILA", value=queue.id, inline=False)
    embed.add_field(name="RANK DA FILA", value=queue.rank.replace("_", " "), inline=False)
    embed.add_field(name="QUANTIDADE DE JOGADORES:", value=queue.get_amount_players(), inline=False)
    players = ', '.join([player.name for player in queue.get_all_players()])
    embed.add_field(name="JOGADORES NA FILA:", value=players, inline=False)
    return embed


def queue_start_voting_maps_message(queue: Queue, channel):

    embed = discord.Embed(title='MATCHMAKING VOTAÇÃO', description="", color=0xff0000)
    embed.set_thumbnail(url="https://i.ibb.co/G3mkZ1p/Screenshot-from-2024-03-13-14-31-37.png")
    embed.add_field(name="ID DA FILA", value=queue.id, inline=False)
    embed.add_field(name="RANK DA FILA", value=queue.rank.replace("_", " "), inline=False)
    embed.add_field(name="QUANTIDADE DE JOGADORES:", value=queue.get_amount_players(), inline=False)
    players = ', '.join([player.name for player in queue.get_all_players()])
    embed.add_field(name="JOGADORES NA FILA:", value=players, inline=False)
    embed.add_field(name="CANAL PARA VOTAÇÃO DOS MAPS:", value=f"[{channel.name}](https://discord.com/channels/{channel.guild.id}/{channel.id})", inline=False)
    return embed


def team_mate_embed_message(players, map):
    # Embaralhar os jogadores
    random.shuffle(players)

    halfway_point = len(players) // 2
    teammate_a = players[:halfway_point]
    teammate_b = players[halfway_point:]

    embed = discord.Embed(title='MATCHMAKING TIMES', description="", color=0xff0000)
    embed.set_thumbnail(url="https://i.ibb.co/G3mkZ1p/Screenshot-from-2024-03-13-14-31-37.png")
    embed.add_field(name="TIME A", value=','.join([player.name for player in teammate_a]), inline=False)
    embed.add_field(name="TIME B", value=','.join([player.name for player in teammate_b]), inline=False)
    embed.add_field(name="MAPA:", value=map, inline=False)
    return embed


