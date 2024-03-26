import sqlite3
from typing import Tuple, List

from entities.BlackSecurityKey import Key


class BlackSecurityRepository:

    def __init__(self):
        self.conn = sqlite3.connect("match.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS blackkeys (
                                   id INTEGER PRIMARY KEY,
                                   key TEXT UNIQUE,
                                   password TEXT UNIQUE
                               )''')

    def save_key(self, key: Key):
        QUERY = "INSERT INTO blackkeys (key, password) VALUES (?, ?)"
        cursor = self.get_cursor()
        cursor.execute(QUERY, (key.id, key.password))
        self.conn.commit()
        self.close_connections()

    def save_many_keys(self, keys: [Key]):
        cursor = self.get_cursor()
        QUERY = "INSERT INTO blackkeys (key, password) VALUES (?, ?)"
        for key in keys:
            cursor.execute(QUERY, (key.id, key.password))
            self.conn.commit()
        self.close_connections()

    def get_keys(self, num_keys) -> [Key]:
        QUERY = "SELECT key, password FROM blackkeys LIMIT ?"
        cursor = self.get_cursor()
        cursor.execute(QUERY, (num_keys,))
        keys = cursor.fetchall()
        keys_to_retur = []
        for key in keys:
            keys_to_retur.append(Key(key[0], key[1]))
        return keys_to_retur

    def get_key(self):
        QUERY = "SELECT key, password FROM blackkeys ORDER BY RANDOM() LIMIT 1"
        cursor = self.get_cursor()
        cursor.execute(QUERY)
        key = cursor.fetchall()
        self.close_connections()
        try:
            return Key(key[0][0], key[0][1])
        except:
            return None

    def remove_keys(self, keys: [Key]):
        QUERY = "DELETE FROM blackkeys WHERE key = ?"
        cursor = self.get_cursor()
        for key in keys:
            cursor.execute(QUERY, (key.id,))
        self.conn.commit()
        self.close_connections()

    def remove_key(self, key):
        if key is None:
            return
        QUERY = "DELETE FROM blackkeys WHERE key = ?"
        cursor = self.get_cursor()
        cursor.execute(QUERY, (key.id,))
        self.conn.commit()
        self.close_connections()

    def remove_all_keys(self):
        QUERY = "DELETE FROM blackkeys"
        cursor = self.get_cursor()
        cursor.execute(QUERY)
        self.conn.commit()
        self.close_connections()


    def get_cursor(self):
        self.conn = sqlite3.connect("match.db")
        return self.conn.cursor()

    def close_connections(self):
        self.cursor.close()
        self.conn.close()
