import re

import discord

from repositories.blacksecurityrepository import BlackSecurityRepository


class BlackSecurityService:

    def __init__(self):
        self.black_security_repository = BlackSecurityRepository()

    def save_key(self, key: str):
        split = key.split(" - ")
        keys = {}
        for value in split:
            splits = value.split(",")
            keys[splits[0]] = splits[1]
        self.black_security_repository.save_many_keys(keys)

    def get_keys(self, num_keys: int):
        return self.black_security_repository.get_keys(num_keys)

    def send_keys(self, keys):
        embed = discord.Embed(title="KEYS DO BLACK SECURITY", color=discord.Color.blue())

        for key in keys:
            embed.add_field(
                name=f"ID: {key[1]}",
                value=f"SENHA: {key[2]}",
                inline=False
            )

        embed.set_thumbnail(url="https://i.ibb.co/G3mkZ1p/Screenshot-from-2024-03-13-14-31-37.png")
        embed.set_footer(text="Black Security - Protegendo o que é importante")

        return embed



