import discord


class QueueButtonService:

    def __init__(self, view, message_button_create):
        self.view = view
        self.message_button_queues = message_button_create

    def create_button_queue(self, label_button, custom_id, callback):
        button = discord.ui.Button(label=label_button)
        button.custom_id = custom_id
        button.callback = callback
        self.view.add_item(button)
        return button

    def get_view_buttons(self):
        return self.view

    def clear_view(self):
        self.view.clear_items()

    async def delete_message_button(self):
        await self.message_button_queues.delete()
