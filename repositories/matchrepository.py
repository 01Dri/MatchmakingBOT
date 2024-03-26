from entities.Match import Match


class MatchRepository:

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.matches = {}

    def save_match(self, match: Match):
        self.matches[match.id] = match
        return self.matches[match.id]

    def find_match_by_id(self, id_match: str):
        for keys in self.matches.keys():
            print(f"KEYS DAS MATCHES: {keys}", f"TIPOS: {type(keys)}")
            print(f"ID DA MATCHE PARA REMOVER: {id_match}", f"TIPO {type(id_match)}")
            if keys == id_match:
                print("SIM O ID É IGUAL")
                return self.matches[keys]

    def remove_match(self, match: Match):
        for matches in self.matches.values():
            if matches.id == match.id:
                self.matches.pop(match.id)
                return True
        return False
    def get_amount_matches(self):
        return len(self.matches)
