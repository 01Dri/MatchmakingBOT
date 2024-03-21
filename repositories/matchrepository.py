from entities.Match import Match


class MatchRepository:

    def __init__(self):
        self.matches = {}

    def save_match(self, match: Match):
        self.matches[match.id] = match
        return self.matches[match.id]

    def find_match_by_id(self, id_match: str):
        for keys in self.matches.keys():
            if keys == id_match:
                return self.matches[keys]
            return None

    def remove_match(self, match: Match):
        for matches in self.matches.values():
            if matches.id == match.id:
                self.matches.pop(match.id)
                return True
        return False
    def get_amount_matches(self):
        return len(self.matches)
