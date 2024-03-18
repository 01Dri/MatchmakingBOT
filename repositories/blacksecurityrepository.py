import sqlite3
from typing import Tuple, List


class BlackSecurityRepository:

    def __init__(self):
        self.conn = sqlite3.connect("match.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS blackkeys (
                                   id INTEGER PRIMARY KEY,
                                   key TEXT,
                                   password TEXT
                               )''')

    def save_key(self, key_value: {str, str}):
        QUERY = "INSERT INTO blackkeys (key, password) VALUES (?, ?)"
        cursor = self.get_cursor()
        cursor.execute(QUERY, (key_value,))
        self.conn.commit()
        self.close_connections()

    def save_many_keys(self, keys: {}):
        cursor = self.get_cursor()
        QUERY = "INSERT INTO blackkeys (key, password) VALUES (?, ?)"
        for key, password in keys.items():
            cursor.execute(QUERY, (key, password))
            self.conn.commit()
        self.close_connections()

    def get_keys(self, num_keys):
        QUERY = "SELECT * FROM blackkeys LIMIT ?"
        cursor = self.get_cursor()
        cursor.execute(QUERY, (num_keys,))
        keys = cursor.fetchall()
        return keys

    def get_cursor(self):
        self.conn = sqlite3.connect("match.db")
        return self.conn.cursor()

    def close_connections(self):
        self.cursor.close()
        self.conn.close()
