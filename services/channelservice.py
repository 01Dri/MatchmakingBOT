import asyncio
import time

import discord

from embeds.embedsmessages import team_mate_embed_message
from entities.Queue import Queue


class ChannelService:

    def __init__(self, guild):
        self.guild = guild
        self.channel = None
        pass

    async def create_channel_text(self, queue: Queue, role):
        self.channel = await self.guild.create_text_channel(queue.id)
        overwrites = {
            self.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            role: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        await self.channel.edit(overwrites=overwrites)
        return self.channel

    async def send_voting_maps_message_to_channel(self, queue: Queue):
        messages = {}
        votes = {}
        winner_map = None
        maps = {
            "Ankara-T": "maps/Ankara-T.jpeg",
            "Mexico-T": "maps/MexicoT.jpeg",
            "OLHO-2.0": "maps/OLHO-2.0.jpeg",
            "Porto-T": "maps/Porto-T.jpeg",
            "Satelite-T": "maps/Satelite-T.jpeg",
            "Sub-Base": "maps/Sub-Base.jpeg",
            "ViuvaT": "maps/ViuvaT.jpeg"
        }
        await self.channel.send("VOTAÇÃO DOS MAPAS")
        for map_name, path in maps.items():
            embed = discord.Embed(title="MAPAS: ", color=discord.Color.red())
            embed.add_field(name=map_name, value="Vote", inline=True)
            file = discord.File(path, filename=f"{map_name}.jpeg")
            embed.set_image(url=f"attachment://{map_name}.jpeg")
            message = await self.channel.send(file=file, embed=embed)
            await message.add_reaction('✅')
            messages[path] = message
        await self.choose_most_voted_map(messages, votes,  queue)

    async def choose_most_voted_map(self, messages, votes, queue):
        emoji_react = '✅'
        time_select_map_message = await self.channel.send("Tempo restante: 1:00)")
        await self.get_votes_maps(time_select_map_message,messages, emoji_react, votes)
        winner_map = max(votes, key=votes.get)
        await time_select_map_message.edit(content=f"Mapa escolhido: {winner_map}")
        players = queue.get_all_players()
        await self.channel.send(embed=team_mate_embed_message(players, winner_map))

    async def get_votes_maps(self, time_select_map_message, messages, emoji_react, votes):
        end_time = time.time() + 30
        while time.time() < end_time:
            remaining_time = int(end_time - time.time())
            formatted_time = time.strftime("%M:%S", time.gmtime(remaining_time))  # Formatando o tempo restante
            await time_select_map_message.edit(content=f"Tempo restante: {formatted_time}")

            for path, message in messages.items():
                message = await message.channel.fetch_message(message.id)
                react = discord.utils.get(message.reactions, emoji=emoji_react)
                if react:
                    count = react.count
                    votes[path] = count
            await asyncio.sleep(5)

        return votes
