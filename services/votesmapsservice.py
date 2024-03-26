import random


class VotesMapsService:

    def __init__(self):
        self.votes_session = {}

    def get_session_vote(self, queue_id):
        if queue_id in self.votes_session.keys():
            return self.votes_session[queue_id]
        return self.set_session_votes_maps(queue_id)

    def set_session_votes_maps(self, queue_id):
        if queue_id not in self.votes_session.keys():
            maps = [
                "Ankara-T",
                "MexicoT",
                "OLHO-2.0",
                "Porto-T",
                "Satelite-T",
                "Sub-Base",
                "ViuvaT"
            ]
            self.votes_session[queue_id] = {'votes': {name: 0 for name in maps}, 'users': {}}
        return self.votes_session[queue_id]

    def add_vote_user_to_session(self, user, queue_id, map):
        session = self.get_session_vote(queue_id)
        if user not in session['users'].keys():
            session['users'][user] = map
            return True
        return False

    def add_vote_map_to_session(self, queue_id, map):
        session = self.get_session_vote(queue_id)
        if map in session['votes']:
            session['votes'][map] += 1
            return True
        return False

    def get_result_votes_session(self, queue_id):
        session = self.votes_session.get(queue_id)
        if session:
            map_winners = []
            max_votes = max(session['votes'].values())
            for map_name, votes in session['votes'].items():
                if votes == max_votes:
                    map_winners.append(map_name)
            if len(map_winners) > 1:
                return random.choice(map_winners)  # Se houver empate, escolhe aleatoriamente entre eles
            elif len(map_winners) == 0:
                return self.get_random_map()  # Ninguém votou, então um mapa aleatório é escolhido
            # del self.votes_session[queue_id]  # Remove a sessão de votos dessa fila
            return map_winners[0]  # Retorna o único mapa escolhido
        return self.get_random_map()

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

    def get_quantity_votes_by_map_name(self, map_name, queue_id):
        session = self.get_session_vote(queue_id)
        print(session)
        result = session['votes'].get(map_name, 0)
        del self.votes_session[queue_id]  # Remove a sessão de votos dessa fila
        return result
