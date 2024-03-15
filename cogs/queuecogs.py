import asyncio
import time
import uuid
import discord
from discord import app_commands
from discord.ext import commands

from embeds.embedsmessages import queue_join_embed_message, queue_start_voting_maps_message
from entities.Player import Player
from entities.Queue import Queue
from enums.StatusQueue import StatusQueue
from exceptions.exceptions import InvalidRankPlayerException, CrowdedQueueException
from repositories.QueueRepository import QueueRepository
from repositories.playerrepository import PlayerRepository
from enums.Rank import Rank


class CommandsQueue(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.queues_repository = QueueRepository()
        self.player_repository = PlayerRepository()
        self.queue_rank_a = None
        self.queue_rank_b = None
        self.view = discord.ui.View()
        self.button_rank_a = discord.ui.Button(label="RANK A - Entrar/Sair")  # , style=discord.ButtonStyle.green)
        self.button_rank_b = discord.ui.Button(label="RANK B - Entrar/Sair")  # style=discord.ButtonStyle.green)
        self.message = None  # Referência para a mensagem enviada
        self.time_select_map_message = None

        self.button_rank_a.custom_id = "default0"
        self.button_rank_b.custom_id = "default1"
        self.button_rank_a.callback = self.button_rank_callback
        self.button_rank_b.callback = self.button_rank_callback

        self.view.add_item(self.button_rank_a)
        self.view.add_item(self.button_rank_b)

        super().__init__()

    async def start_checking_queue(self, interact):
        while True:
            await self.check_quantity_player_on_queue(interact)
            await asyncio.sleep(5)

    @app_commands.command()
    async def startq(self, interact: discord.Interaction):

        if self.queues_repository.get_amount_queue() == 0:
            self.queue_rank_a = Queue(str(uuid.uuid4()), Rank.RANK_A, 2)
            self.queue_rank_b = Queue(str(uuid.uuid4()), Rank.RANK_B, 2)
            self.queues_repository.save_queue(self.queue_rank_a)
            self.queues_repository.save_queue(self.queue_rank_b)
        else:
            if self.queues_repository.get_amount_queue() >= 2:
                await interact.response.send_message("Já existem filas iniciadas.", ephemeral=True)
                return

        # Sistema para se alguma fila já atingiu seu limite maximo de players
        self.bot.loop.create_task(self.start_checking_queue(interact))
        await interact.response.send_message("Você iniciou as filas", ephemeral=True)
        self.button_rank_a.custom_id = self.queue_rank_a.id
        self.button_rank_b.custom_id = self.queue_rank_b.id

        self.message = await interact.followup.send("Filas iniciadas", view=self.view)
        await self.update_queue_message()

    @app_commands.command()
    async def cancelq(self, interact: discord.Interaction):
        queues_to_remove = []
        for queue in self.queues_repository.queues.values():
            queues_to_remove.append(queue)
            for p in queue.get_all_discord_users():
                await p.create_dm()
                await p.dm_channel.send("Sua fila foi cancelada!!!")
                queue.remove_player(p.id)
        for q in queues_to_remove:
            self.queues_repository.remove_queue(q)
        await self.message.delete()
        self.view.clear_items()
        await interact.response.send_message("Filas canceladas!!!")

    async def button_rank_callback(self, interact: discord.Interaction):
        id_queue_from_button = interact.data['custom_id']  # ID DA QUEUE  PELO BOTAO
        queue_user = self.queues_repository.get_queue_by_player_id(str(interact.user.id))
        current_queue = self.queues_repository.get_queue_by_id(str(id_queue_from_button))
        player = self.player_repository.find_player_by_id(str(interact.user.id))

        if queue_user is not None:
            queue_user.remove_player(player.discord_id)
            await interact.response.send_message("Você saiu da fila", ephemeral=True)
            await self.update_queue_message()  # Atualizar a mensagem após a remoção do jogador
            return

        if current_queue is not None:
            # if player is not None:
            try:
                if player is None:
                    player = self.player_repository.save_player(
                        Player(None, interact.user.id, interact.user.name, Rank.RANK_B, 0, StatusQueue.IN_QUEUE))

                if player.queue_status == StatusQueue.IN_VOTING_MAPS.value:
                    await interact.response.send_message(
                        f"Vocẽ está no processo de votação de mapas, por favor retorne a sua sala ", ephemeral=True)
                    return
                current_queue.add_player(player, interact.user)

            except InvalidRankPlayerException:
                await interact.response.send_message(f"Você não pode jogar nesse rank ", ephemeral=True)
                return
            except CrowdedQueueException:
                await interact.response.send_message(f"A fila já está cheia. por favor aguarde a proxima!!!", ephemeral=True)
                return

            member = interact.user
            await member.create_dm()
            await member.dm_channel.send(embed=queue_join_embed_message(player, current_queue))
            await interact.response.send_message(f"Você entrou na fila!!!", ephemeral=True)
            await self.update_queue_message()
            return

    # Atualizar o embed com a quantidade jogadores nas filas de rank a e rank B
    async def update_queue_message(self):
        if self.message:
            embed = discord.Embed(title="JOGADORES NAS FILAS: ", color=discord.Color.red())
            embed.add_field(name="Rank A", value=str(self.queue_rank_a.get_amount_players()), inline=True)
            embed.add_field(name="Rank B", value=str(self.queue_rank_b.get_amount_players()), inline=True)
            embed.set_thumbnail(url="https://i.ibb.co/G3mkZ1p/Screenshot-from-2024-03-13-14-31-37.png")
            embed.set_footer(text="Quantidade de partidas: ")
            await self.message.edit(embed=embed)
            self.view.clear_items()
            self.view.add_item(self.button_rank_a)
            self.view.add_item(self.button_rank_b)

    async def check_quantity_player_on_queue(self, interact):
        queues_to_remove = []
        guild = interact.guild
        channel_voting = None
        queues_copy = dict(self.queues_repository.queues)
        for queue_id, queue in queues_copy.items():
            if queue.get_amount_players() == queue.max_players:
                voting_maps_role = await guild.create_role(name=queue.id, color=discord.Color.gold())
                queues_to_remove.append(queue_id)
                await self.reset_buttons_and_queues(interact, queues_to_remove)
                channel_voting = await self.create_channel_voting_maps(interact, queue, voting_maps_role)
                # Este for itera em cada conta do discord presente na fila e adiciona o cargo da fila e manda uma
                # mensagem na DM
                for discord_user in queue.get_all_discord_users():
                    await discord_user.add_roles(voting_maps_role)
                    await discord_user.create_dm()
                    await discord_user.dm_channel.send(embed=queue_start_voting_maps_message(queue, channel_voting))

                    # Este for itera em cada objeto player da queue e atualiza o status da fila no banco
                    for player in queue.get_all_players():
                        player = self.player_repository.find_player_by_id(player.discord_id)
                        self.player_repository.save_player(
                            Player(player.id, player.discord_id, player.name, player.rank, player.points,
                                   StatusQueue.IN_VOTING_MAPS))
                await self.send_maps_vote_to_map(channel_voting, interact)

    async def reset_buttons_and_queues(self, interact, queues_to_remove):
        for queue_id in queues_to_remove:
            queue = self.queues_repository.queues.pop(queue_id)
            if queue.rank == Rank.RANK_A.name:
                self.queue_rank_a = Queue(str(uuid.uuid4()), Rank.RANK_A, 2)
                self.queues_repository.save_queue(self.queue_rank_a)
                self.button_rank_a.custom_id = self.queue_rank_a.id

            if queue.rank == Rank.RANK_B.name:
                self.queue_rank_b = Queue(str(uuid.uuid4()), Rank.RANK_B, 2)
                self.queues_repository.save_queue(self.queue_rank_b)
                self.button_rank_b.custom_id = self.queue_rank_b.id

            # Apagar a mensagem e os botões existentes
            await self.message.delete()
            self.view.clear_items()

            await asyncio.sleep(10)

            # Criar novos botões
            new_button_rank_a = discord.ui.Button(label="RANK A - Entrar/Sair")
            new_button_rank_b = discord.ui.Button(label="RANK B - Entrar/Sair")

            new_button_rank_a.custom_id = self.queue_rank_a.id
            new_button_rank_b.custom_id = self.queue_rank_b.id

            new_button_rank_a.callback = self.button_rank_callback
            new_button_rank_b.callback = self.button_rank_callback

            # Adicionar os novos botões à view
            self.view.add_item(new_button_rank_a)
            self.view.add_item(new_button_rank_b)

            # await asyncio.sleep(20)
            # Enviar uma nova mensagem com a view atualizada
            self.message = await interact.followup.send("Filas iniciadas", view=self.view)
            await self.update_queue_message()

    async def create_channel_voting_maps(self, interact: discord.Interaction, queue: Queue, role):
        guild = interact.guild
        channel = await guild.create_text_channel(queue.id)
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            role: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        await channel.edit(overwrites=overwrites)
        return channel

    async def send_maps_vote_to_map(self, channel, interact):
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
        emoji_react = '✅'
        await channel.send("VOTAÇÃO DOS MAPAS")
        for map_name, path in maps.items():
            embed = discord.Embed(title="MAPAS: ", color=discord.Color.red())
            embed.add_field(name=map_name, value="Vote", inline=True)
            file = discord.File(path, filename=f"{map_name}.jpeg")
            embed.set_image(url=f"attachment://{map_name}.jpeg")
            message = await channel.send(file=file, embed=embed)
            await message.add_reaction('✅')
            messages[path] = message
        self.time_select_map_message = await channel.send("Tempo restante: 1:00)")
        await self.get_votes_maps(messages, emoji_react, votes, interact)
        winner_map = max(votes, key=votes.get)
        await self.time_select_map_message.edit(content=f"Mapa escolhido: {winner_map}")

    async def get_votes_maps(self, messages, emoji_react, votes, interact):
        end_time = time.time() + 30
        while time.time() < end_time:
            remaining_time = int(end_time - time.time())
            formatted_time = time.strftime("%M:%S", time.gmtime(remaining_time))  # Formatando o tempo restante
            await self.time_select_map_message.edit(content=f"Tempo restante: {formatted_time}")

            for path, message in messages.items():
                message = await message.channel.fetch_message(message.id)
                react = discord.utils.get(message.reactions, emoji=emoji_react)
                if react:
                    count = react.count
                    votes[path] = count
            await asyncio.sleep(5)

        return votes


async def setup(bot):
    await bot.add_cog(CommandsQueue(bot))
