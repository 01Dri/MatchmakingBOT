class Player:

    def __init__(self, id, discord_id, name, rank, points, wins: int, losses: int, queue_status):
        self.id: str = str(id)
        self.discord_id = str(discord_id)
        self.name = name
        self.rank = rank
        self.points = points
        self.wins = wins
        self.losses = losses
        self.queue_status = queue_status


