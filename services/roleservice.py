class RoleService:

    def __init__(self, guild):
        self.guild = guild
        pass

    async def create_role(self, name_role, color):
        return await self.guild.create_role(name=name_role, color=color)

