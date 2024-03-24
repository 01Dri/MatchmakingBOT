import re

import discord

from entities.BlackSecurityKey import Key
from repositories.blacksecurityrepository import BlackSecurityRepository


class BlackSecurityService:

    def __init__(self):
        self.black_security_repository = BlackSecurityRepository()

    def save_key(self, key: str):
        self.black_security_repository.save_many_keys(self.format_key_str_to_key(key))

    def get_keys(self, num_keys: int):
        return self.black_security_repository.get_keys(num_keys)

    def get_random_key(self):
        return self.black_security_repository.get_key()

    def send_keys(self, keys):
        embed = discord.Embed(title="KEYS DO BLACK SECURITY", color=discord.Color.blue())

        for key in keys:
            embed.add_field(
                name=f"ID: {key.id}",
                value=f"SENHA: {key.password}",
                inline=False
            )

        embed.set_thumbnail(url="https://i.ibb.co/G3mkZ1p/Screenshot-from-2024-03-13-14-31-37.png")
        embed.set_footer(text="Black Security - Protegendo o que é importante")

        return embed

    def send_random_key(self, key):
        embed = discord.Embed(title="KEYS DO BLACK SECURITY", color=discord.Color.blue())

        embed.add_field(
            name=f"ID: {key.id}",
            value=f"SENHA: {key.password}")

        embed.set_thumbnail(url="https://i.ibb.co/G3mkZ1p/Screenshot-from-2024-03-13-14-31-37.png")
        embed.set_footer(text="Black Security - Protegendo o que é importante")
        return embed

    def remove_one_key(self, key):
        self.black_security_repository.remove_key(key)

    def remove_keys(self, key):
        self.black_security_repository.remove_keys(self.format_key_str_to_key(key))

    def format_key_str_to_key(self, key: str):
        split = key.split(" - ")
        keys_to_send = []
        for value in split:
            splits = value.split(",")
            keys_to_send.append(Key(splits[0], splits[1]))
        return keys_to_send
