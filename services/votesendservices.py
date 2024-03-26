from utils.constants import MAX_VOTES_END


class VotesEndService:

    def __init__(self):
        self.votes_session = {}
        self.votes = {'a': 0, 'b': 0}
        self.votes_users = {}

    def get_session_vote(self, queue_id):
        if queue_id in self.votes_session.keys():
            return self.votes_session[queue_id]
        return self.set_session_votes_teams(queue_id)

    def set_session_votes_teams(self, queue_id):
        if queue_id not in self.votes_session.keys():
            self.votes_session[queue_id] = {'votes': {'a': 0, 'b': 0}, 'users': {}}
            return self.votes_session[queue_id]

    def add_vote_user_to_session(self, user, session, team):
        if user not in session['users'].keys():
            session['users'][user] = team
            return session
        return False

    def add_vote_map_to_session(self, session, team):
        session['votes'][team] += 1
        return session

    def get_result_votes_session(self, session):
        if session['votes']['a'] >= MAX_VOTES_END:
            del session
            return 'a'
        if session['votes']['b'] >= MAX_VOTES_END:
            del session
            return 'b'
        print(session)
        print(session.keys(), session.values())
        session['votes']['a'] = 0
        session['votes']['b'] = 0
        session['users'].clear()
        return None


