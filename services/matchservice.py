from entities.Match import Match
from repositories.matchrepository import MatchRepository


class MatchService:

    def __init__(self):
        self.match_repository = MatchRepository()

    def add_match(self, match: Match):
        return self.match_repository.save_match(match)

    def get_quantity_matches(self):
        return self.match_repository.get_amount_matches()

    def get_matches(self):
        return self.match_repository.matches.items()