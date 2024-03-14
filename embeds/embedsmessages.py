import discord

from entities.Player import Player
from entities.Queue import Queue


def queue_join_embed_message(player: Player, queue: Queue):
    embed = discord.Embed(title='MATCHMAKING FILA', description=player.name, color=0xff0000)
    embed.set_thumbnail(url="https://i.ibb.co/G3mkZ1p/Screenshot-from-2024-03-13-14-31-37.png")
    embed.add_field(name="ID DA FILA", value=queue.id, inline=False)
    embed.add_field(name="RANK DA FILA", value=queue.rank.replace("_", " "), inline=False)
    embed.add_field(name="QUANTIDADE DE JOGADORES:", value=queue.get_amount_players(), inline=False)
    players = ', '.join(queue.get_all_players())
    embed.add_field(name="JOGADORES NA FILA:", value=players, inline=False)
    return embed


def queue_start_voting_maps_message(queue: Queue):
    embed = discord.Embed(title='MATCHMAKING VOTAÇAÕ', description="", color=0xff0000)
    embed.set_thumbnail(url="https://i.ibb.co/G3mkZ1p/Screenshot-from-2024-03-13-14-31-37.png")
    embed.add_field(name="ID DA FILA", value=queue.id, inline=False)
    embed.add_field(name="RANK DA FILA", value=queue.rank.replace("_", " "), inline=False)
    embed.add_field(name="QUANTIDADE DE JOGADORES:", value=queue.get_amount_players(), inline=False)
    players = ', '.join(queue.get_all_players())
    embed.add_field(name="JOGADORES NA FILA:", value=players, inline=False)
    embed.add_field(name="CANAL PARA VOTAÇÃO DOS MAPS: :", value="canalaqui", inline=False)

    return embed

