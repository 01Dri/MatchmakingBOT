import random

from entities.vote import Vote


class VotesMapsServices:

    def __init__(self):
        self.votes: {Vote} = {}
        self.session_votes = {}

    def add_vote(self, map_name, user, queue_id):
        session = self.add_session_votes(queue_id)

        if self.check_if_user_already_vote(user, queue_id):
            return False

        if map_name in session.keys():
            vote = session[map_name]
            vote_user = self.get_vote_by_user(user, queue_id)
            if vote_user is not None:
                return False
            vote.add_user(user)
            vote.add_vote_quantity()
            session[map_name] = vote
            self.session_votes[queue_id] = session
            print("VOTOS")
            print(vote.quantity_votes)
            return
        else:
            print("NOVO VOTO")
            new_vote = Vote(map_name)
            new_vote.add_user(user)
            new_vote.add_vote_quantity()
            session[map_name] = new_vote
            self.session_votes[queue_id] = session
            print(new_vote.quantity_votes)
            return

    def add_session_votes(self, queue_id):
        if queue_id not in self.session_votes.keys():
            self.session_votes[queue_id] = self.votes
            return self.session_votes[queue_id]
        else:
            return self.session_votes[queue_id]

    def get_map_with_max_votes(self, queue_id):
        map_winners = []
        max_votes = 0
        session = self.add_session_votes(queue_id)
        for vote in session.values():
            if vote.quantity_votes > max_votes:
                max_votes = vote.quantity_votes
                map_winners = [vote.map_name]
            elif vote.quantity_votes == max_votes:
                map_winners.append(vote.map_name)
        if len(map_winners) > 1:
            return self.get_result_map_from_draw(map_winners)
        if len(map_winners) == 0:
            return self.get_random_map()  # Ninguem votou, então um mapa aleatorio foi escolhido

        del self.session_votes[queue_id]  # APAGA A SESSÃO DE VOTOS DESSA QUEUE
        return map_winners[0]  # RETORNA O UNICO MAPA ESCOLHIDO

    def get_result_map_from_draw(self, maps):
        return random.choice(maps)

    def get_random_map(self):
        maps = [
            "Ankara-T",
            "MexicoT",
            "OLHO-2.0",
            "Porto-T",
            "Satelite-T",
            "Sub-Base",
            "ViuvaT"
        ]
        return random.choice(maps)

    def get_votes_map_by_map_name(self, map_name, queue_id):
        session = self.add_session_votes(queue_id)

        for vote in session.values():
            if vote.map_name == map_name:
                return vote.quantity_votes

    def get_vote_by_user(self, user_name, queue_id) -> Vote:
        session = self.add_session_votes(queue_id)
        for vote in session.values():
            for user in vote.users:
                if user == user_name:
                    return vote

    def check_if_user_already_vote(self, user_name, queue_id):
        session = self.add_session_votes(queue_id)
        try:
            for votes in session:
                for user in votes.users:
                    if user == user_name:
                        return True
        except:
            return None

