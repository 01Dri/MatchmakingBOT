import discord


class MessageService:

    def __init__(self):
        self.embed_message_join_queue_references = {}
        self.category_guild_reference_queue = {}
        self.channel_votes_maps_session = {}
        self.voices_channel_session = {}

    def set_embed_message_join_queue(self, user, message):
        self.embed_message_join_queue_references[user.name] = message

    def get_message_embed_join_queue(self, user):
        return self.embed_message_join_queue_references[user.name]

    async def delete_message_embed_join_queue(self, user):
        await self.embed_message_join_queue_references[user].delete()
        del self.embed_message_join_queue_references[user]

    def set_guild_category(self, category, queue):
        self.category_guild_reference_queue[queue.id] = category

    def get_category_queue(self, queue):
        return self.category_guild_reference_queue[queue.id]

    def set_channel_session_queue(self, queue, channel):
        self.channel_votes_maps_session[queue.id] = channel

    def set_voice_channel_session(self, voice_a, voice_b, queue):
        voices = [voice_a, voice_b]
        self.voices_channel_session[queue.id] = voices

    def get_voices_channels_reference(self, queue):
        voices = self.voices_channel_session[queue.id]
        return voices[0], voices[1]

    def get_channel_session_voting_maps(self, queue):
        return self.channel_votes_maps_session[queue.id]

    async def send_maps_vote_to_channel(self, queue, callback_vote_map):
        channel = self.channel_votes_maps_session[queue.id]
        maps = [
            "Ankara-T",
            "MexicoT",
            "OLHO-2.0",
            "Porto-T",
            "Satelite-T",
            "Sub-Base",
            "ViuvaT"
        ]

        embed = discord.Embed(title="SELEÇÃO DE MAPAS", description="Escolha um mapa:",
                              color=0xFF0000)  # Cor vermelha: 0xFF0000
        for map_name in maps:
            embed.add_field(name=map_name, value=f"Vote pelo botão  para escolher o mapa {map_name}", inline=False)

        buttons = [
            discord.ui.Button(style=discord.ButtonStyle.primary, label=map_name) for map_name in maps
        ]

        view = discord.ui.View(timeout=None)
        for b, map_name in zip(buttons, maps):
            b.custom_id = map_name
            b.callback = callback_vote_map
            view.add_item(b)
        await channel.send(embed=embed, view=view)
