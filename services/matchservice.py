from entities.Match import Match
from repositories.matchrepository import MatchRepository


class MatchService:

    # SINGLETON
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.match_repository = MatchRepository()

    def add_match(self, match: Match):
        return self.match_repository.save_match(match)

    def get_quantity_matches(self):
        return self.match_repository.get_amount_matches()

    def get_matches(self):
        return self.match_repository.matches.items()

    def find_match_by_id(self, match_id: str) -> Match:
        return self.match_repository.find_match_by_id(match_id)

    def remove_match(self, match: Match):
        match = self.match_repository.find_match_by_id(match.id)
        if match is not None:
            return self.match_repository.remove_match(match)
        return False
