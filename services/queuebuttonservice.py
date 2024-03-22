import discord


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
