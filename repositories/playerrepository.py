import sqlite3

from entities.Player import Player
from exceptions.exceptions import NotFoundPlayerException
from utils.Rank import Rank


class PlayerRepository:

    def __init__(self):
        self.conn = sqlite3.connect("match.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS players (
                            id INTEGER PRIMARY KEY,
                            discord_id TEXT NOT NULL,
                            discord_name TEXT NOT NULL,
                            rank INTEGER NOT NULL,
                            points INTEGER
                        )''')

    def save_player(self, player: Player):
        QUERY_FIND = "SELECT * FROM players p WHERE p.discord_id = ?"
        QUERY_INSERT = "INSERT INTO players (discord_id, discord_name, rank, points) VALUES (?, ?, ?, ?)"
        UPDATE_QUERY = "UPDATE players SET rank = ?, points = ? WHERE discord_id = ?"
        VALUES_TO_INSERT = (player.discord_id, player.name, player.rank.value, player.points)
        self.cursor = self.get_cursor()
        self.cursor.execute(QUERY_FIND, (player.discord_id,))
        if self.cursor.fetchone() is None:
            print("Jogador não existe, salvado-o no banco")
            self.cursor.execute(QUERY_INSERT, VALUES_TO_INSERT)
            self.conn.commit()
            id_player = self.cursor.lastrowid
            self.close_connections()
            return Player(id_player, player.discord_id, player.name, player.rank, player.points)
        print("Jogador já existe, atualizando suas informações")
        self.cursor.execute(UPDATE_QUERY, (player.rank, player.points))
        self.conn.commit()
        self.close_connections()
        return

    def find_player_by_id(self, discord_id_player: str):
        self.cursor = self.get_cursor()
        QUERY_FIND = "SELECT * FROM players WHERE discord_id = ?"
        self.cursor.execute(QUERY_FIND, (discord_id_player,))
        row = self.cursor.fetchone()
        if row:
            rank = Rank(int(row[3]))
            player = Player(row[0], row[1], row[2], rank, row[4])
            self.close_connections()
            return player
        self.close_connections()
        # raise NotFoundPlayerException("Player não encontrado!!!")
        return None

    def get_cursor(self):
        self.conn = sqlite3.connect("match.db")
        return self.conn.cursor()

    def close_connections(self):
        self.cursor.close()
        self.conn.close()
