class Player:

    def __init__(self, id, discord_id, name, rank, points, queue_status):
        self.id: str = str(id)
        self.discord_id = str(discord_id)
        self.name = name
        self.rank = rank
        self.points = points
        self.queue_status = queue_status


