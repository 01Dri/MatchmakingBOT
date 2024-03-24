class Vote:

    def __init__(self, map_name):
        self.map_name = map_name
        self.users = []
        self.quantity_votes = 0

    def add_user(self, user):
        self.users.append(user)

    def add_vote_quantity(self):
        self.quantity_votes += 1