#интерфейс для работы с базой данных
import sqlite3
from sqlite3 import Error
create_user = """
INSERT INTO
  users (name, Snils, Program)
VALUES
  (?, ?, ?);
"""
create_users_table = """
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT,
  Snils TEXT,
  Program TEXT
);
"""


class DataBase:
    def __init__(self, path='users.db'):
        self.cursor = None
        self.connection = None
        try:
            self.connection = sqlite3.connect(path, check_same_thread=False)
            print("Connection to SQLite DB successful")
        except Error as e:
            raise Exception(e)
    def create_table(self):
        self.cursor=self.connection.cursor()
        self.cursor.execute(create_users_table)
        self.connection.commit()
        self.cursor.close()
    def __del__(self):
        self.connection.close()
        print(" disconnection from the sqlite3 DB")
    def add_user(self, chat_id, snils, program):
        data_tuple = (chat_id, snils, program)
        self.cursor = self.connection.cursor()
        try:
            self.cursor.execute(create_user, data_tuple)
            self.connection.commit()
            print("Query executed successfully")
        except Error as e:
            raise Exception(e)
        self.cursor.close()
    def check_exist(self, chat_id):
        self.cursor = self.connection.cursor()
        info = self.cursor.execute('SELECT * FROM users WHERE name=?', (chat_id,)).fetchone()
        if info:
            self.cursor.close()
            return True
        else:
            self.cursor.close()
            return False
    def get_from_table(self, chat_id):
        self.cursor = self.connection.cursor()
        info = self.cursor.execute('SELECT * FROM users WHERE name=?', (chat_id,)).fetchone()
        self.cursor.close()
        return info
    def set_snils(self,chat_id,snils):
        self.cursor=self.connection.cursor()
        self.cursor.execute('''UPDATE users SET Snils = ? WHERE name = ?''', (snils, chat_id))
        self.connection.commit()
        self.cursor.close()
    def set_program(self,chat_id,program):
        self.cursor = self.connection.cursor()
        self.cursor.execute('''UPDATE users SET Program = ? WHERE name = ?''', (program, chat_id))
        self.connection.commit()
        self.cursor.close()