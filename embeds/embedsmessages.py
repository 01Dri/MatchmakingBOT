import random

import discord

from entities.Player import Player
from entities.Queue import Queue


def embed_queues_message(players, matches_amount):
    embed = discord.Embed(title='MATCHMAKING FILA', description="Filas", color=0xff0000)
    embed.set_thumbnail(url="https://i.ibb.co/G3mkZ1p/Screenshot-from-2024-03-13-14-31-37.png")
    embed.add_field(name="PLAYERS EM FILA: :", value=players, inline=False)
    embed.add_field(name="PARTIDAS EM ANDAMENTO:", value=matches_amount, inline=False)
    return embed


def emebed_map_voted(name_map):
    embed = discord.Embed(title='MATCHMAKING VOTAÇÃO DE MAPAS', description="Votos", color=0xff0000)
    embed.set_thumbnail(url="https://i.ibb.co/G3mkZ1p/Screenshot-from-2024-03-13-14-31-37.png")
    embed.add_field(name="MAPA VOTADO:", value=name_map, inline=False)
    return embed


def embed_map_wiiner(name_map, votos):
    embed = discord.Embed(title='MATCHMAKING VOTAÇÃO DE MAPAS ', description="Votos", color=0xff0000)
    embed.set_thumbnail(url="https://i.ibb.co/G3mkZ1p/Screenshot-from-2024-03-13-14-31-37.png")
    embed.add_field(name="MAPA ESCOLHIDO:", value=name_map, inline=False)
    embed.add_field(name="QUANTIDADE DE VOTOS:", value=votos, inline=False)

    return embed


def embed_join_queue_message(queue: Queue):
    embed = discord.Embed(title='MATCHMAKING FILA', description="VOCÊ ENTROU NESSA FILA", color=0xff0000)
    embed.set_thumbnail(url="https://i.ibb.co/G3mkZ1p/Screenshot-from-2024-03-13-14-31-37.png")
    embed.add_field(name="ID DA FILA", value=queue.id, inline=False)
    embed.add_field(name="RANK DA FILA", value=queue.rank.name.replace("_", " "), inline=False)
    # embed.add_field(name="QUANTIDADE DE JOGADORES:", value=len(queue.get_all_players()), inline=False)
    # embed.add_field(name="JOGADORES:", value=players, inline=False)

    return embed


def embed_join_voting_maps(queue: Queue, channel):
    players = ', '.join([player.name for player in queue.get_all_players()])
    embed = discord.Embed(title='MATCHMAKING VOTAÇÃO', description="VOTAÇÃO DE MAPAS INICIOU!!!", color=0xff0000)
    embed.set_thumbnail(url="https://i.ibb.co/G3mkZ1p/Screenshot-from-2024-03-13-14-31-37.png")
    embed.add_field(name="RANK DA FILA", value=queue.rank.name.replace("_", " "), inline=False)
    embed.add_field(name="QUANTIDADE DE JOGADORES:", value=len(queue.get_all_players()), inline=False)
    embed.add_field(name="JOGADORES:", value=players, inline=False)
    embed.add_field(name="CANAL PARA VOTAÇÃO DOS MAPS:",
                    value=f"[{channel.name}](https://discord.com/channels/{channel.guild.id}/{channel.id})",
                    inline=False)
    return embed


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
    embed.add_field(name="RANK DA FILA", value=queue.rank.name.replace("_", " "), inline=False)
    embed.add_field(name="QUANTIDADE DE JOGADORES:", value=queue.get_amount_players(), inline=False)
    players = ', '.join([player.name for player in queue.get_all_players()])
    embed.add_field(name="JOGADORES NA FILA:", value=players, inline=False)
    embed.add_field(name="CANAL PARA VOTAÇÃO DOS MAPS:",
                    value=f"[{channel.name}](https://discord.com/channels/{channel.guild.id}/{channel.id})",
                    inline=False)
    return embed


def team_mate_embed_message(channel_a, channel_b, map_winner, black_security_key, team_a, team_b):
    embed = discord.Embed(title='MATCHMAKING TIMES', description="", color=0xff0000)
    embed.set_thumbnail(url="https://i.ibb.co/G3mkZ1p/Screenshot-from-2024-03-13-14-31-37.png")
    embed.add_field(name="TIME A", value=','.join([player.name for player in team_a]), inline=False)
    embed.add_field(name="TIME B", value=','.join([player.name for player in team_b]), inline=False)
    embed.add_field(name="MAPA:", value=map_winner, inline=False)
    embed.add_field(name="CANAL DE VOZ TIME A:",
                    value=f"https://discord.com/channels/{channel_a.guild.id}/{channel_a.id}", inline=False)
    embed.add_field(name="CANAL DE VOZ TIME B:",
                    value=f"https://discord.com/channels/{channel_b.guild.id}/{channel_b.id}", inline=False)
    if black_security_key is None:
        embed.add_field(name="BLACK SECURITY KEY:", value=f"**NENHUMA KEY ENCONTRADA!!!**", inline=False)
    else:
        embed.add_field(name="BLACK SECURITY KEY:",
                        value=f"**ID**: {black_security_key.id} -  **SENHA:** {black_security_key.password}",
                        inline=False)
    return embed


def embed_profile_message(player: Player, user: discord.Interaction.user):
    all_games = player.wins + player.losses
    embed = discord.Embed(title='PERFIL', description=f"<@{player.discord_id}>", color=0xff0000)
    embed.set_thumbnail(url=user.avatar.url)
    embed.add_field(name="Vitórias", value=player.wins, inline=True)
    embed.add_field(name="Derrotas", value=player.losses, inline=True)
    embed.add_field(name="Pontos", value=player.points, inline=True)
    winrate = 0 if all_games == 0 else (player.wins / all_games) * 100

    embed.add_field(name="Winrate", value=f"{winrate:.0f}%" if winrate != 0 else "0%", inline=True)
    embed.add_field(name="Rank", value=player.rank.name, inline=True)
    return embed
    # embed.add_field(name="Pontos", value=player.points, inline=True)


def team_wins_embed(points_win, time_win, points_losse, time_losse):
    embed = discord.Embed(title='MATCHMAKING VITORIA', description="", color=0xff0000)
    embed.set_thumbnail(url="https://i.ibb.co/G3mkZ1p/Screenshot-from-2024-03-13-14-31-37.png")
    embed.add_field(name=f"TIME VENCEDOR:", value=[player.name for player in time_win], inline=False)
    embed.add_field(name=f"PONTOS RECEBIDOS:", value=points_win, inline=False)
    embed.add_field(name=f"TIME PERDEDOR:", value=[player.name for player in time_losse], inline=False)
    embed.add_field(name=f"PONTOS PERDIDOS:", value=points_losse, inline=False)

    # embed.add_field(name="CANAL PARA VOTAÇÃO DOS MAPS:",
    #                 value=f"[{channel.name}](https://discord.com/channels/{channel.guild.id}/{channel.id})",
    #                 inline=False)
    return embed
