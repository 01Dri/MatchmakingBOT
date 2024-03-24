import discord

from embeds.embedsmessages import embed_queues_message


class QueueButtonService:
    # _instance = None
    #
    # def __new__(cls, *args, **kwargs):
    #     if not cls._instance:
    #         cls._instance = super().__new__(cls, *args, **kwargs)
    #     return cls._instance

    def __init__(self, callback_button, message_button_create=None):
        self.view = discord.ui.View(timeout=None)
        self.message_button_create = message_button_create
        self.callback_button = callback_button
        self.button = None

    def get_view(self):
        return self.view

    def create_button_queue(self, label_button, custom_id=None, style=None):
        if style is not None:
            self.button = discord.ui.Button(label=label_button, style=style)
        else:
            self.button = discord.ui.Button(label=label_button)
        if custom_id is not None:
            self.button.custom_id = custom_id

        self.button.callback = self.callback_button
        self.view.add_item(self.button)
        return self.button

    async def update_message_queue(self, players, matches):
        await self.message_button_create.edit(
            embed=embed_queues_message(players, matches))

    def get_message_queues_button(self):
        return self.message_button_create

    def get_view_buttons(self):
        return self.view

    def clear_view(self):
        self.view.clear_items()

    async def delete_message_button(self):
        await self.message_button_create.delete()

    async def update_button_id(self, new_custom_id):
        # Remove o botão atual
        self.view.remove_item(self.button)

        # Cria um novo botão com o novo ID
        self.button = discord.ui.Button(label=self.button.label)
        self.button.custom_id = new_custom_id
        self.button.callback = self.callback_button

        # Adiciona o novo botão à view
        self.view.add_item(self.button)

    def set_message_button_queues_created(self, message):
        self.message_button_create = message

    async def update_message_button_queues(self, message):

        await self.message_button_create.edit(embed=message)

    async def update_custom_id_button_queues(self, new_id, callback):
        new_button = discord.ui.Button(label="Entrar/Sair")
        new_button.custom_id = new_id
        self.view.clear_items()
        self.view.add_item(new_button)
        new_button.callback = callback
        await self.message_button_create.edit(view=self.view)

    def get_message_button_queues(self):
        return self.message_button_create
