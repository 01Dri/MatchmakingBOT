from entities.Match import Match


class MatchRepository:

    def __init__(self):
        self.matches = {}

    def save_match(self, match: Match):
        self.matches[match.id] = match
        return self.matches[match.id]

    def get_amount_matches(self):
        return len(self.matches)
