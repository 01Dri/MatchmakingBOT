class VotesEndService:

    def __init__(self):
        self.votes = {}
        self.votes_users = {}
        self.votes_session = {}
        pass

    def add_vote(self, queue_id, vote, user):
        if 'a' not in self.votes.keys() and 'b' not in self.votes.keys():
            self.votes['a'] = 0
            self.votes['b'] = 0

        if queue_id not in self.votes_session.keys():
            self.votes_session[queue_id] = []
            self.votes[vote] = 1
            self.votes_users[user] = vote
            self.votes_session[queue_id].append(self.votes)
            self.votes_session[queue_id].append(self.votes_users)
        else:
            self.votes = self.votes_session[queue_id][0]
            self.votes_users = self.votes_session[queue_id][1]
            if user in self.votes_users.keys():
                return False
            if vote in self.votes.keys():
                self.votes[vote] += 1
                self.votes_users[user] = vote
            else:
                self.votes[vote] = 1
                self.votes_users[user] = vote

        self.votes_session[queue_id].append(self.votes)
        self.votes_session[queue_id].append(self.votes_users)
        print(self.votes_users)
        print(self.votes)

    def get_result_voting(self, queue_id):
        if queue_id not in self.votes_session.keys():
            return None

        self.votes = self.votes_session[queue_id][0]
        print(self.votes)
        if self.votes['a'] >= 2:
            # del self.votes['a']
            # del self.votes['b']
            # self.votes_users.clear()
            print("TIME A VENCEU")
            return 'a'

        if self.votes['b'] >= 2:
            print("TIME B VENCEU")
            return 'b'

        self.votes = self.votes_session[queue_id][0]
        self.votes_users = self.votes_session[queue_id][1]
        self.votes_users.clear()
        self.votes['a'] = 0
        self.votes['b'] = 0

        return None

