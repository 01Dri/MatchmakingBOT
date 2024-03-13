import discord

from entities.Player import Player
from entities.Queue import Queue


def queue_join_embed_message(player: Player, queue: Queue):
    embed = discord \
        .Embed(title='MATCHMAKING FILA', description=player.name)
    embed.add_field(name="ID DA FILA", value=queue.id, inline=False)
    embed.add_field(name="RANK DA FILA", value=queue.rank, inline=False)
    embed.add_field(name="QUANTIDADE DE JOGADORES:", value=queue.get_amount_players(), inline=False)
    embed.add_field(name="TODOS OS JOGADORES:", value=queue.get_all_players_name(), inline=False)
    embed.set_image(url="https://i.ibb.co/G3mkZ1p/Screenshot-from-2024-03-13-14-31-37.png")
    return embed

