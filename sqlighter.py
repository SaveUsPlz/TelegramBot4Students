import sqlite3

class SQLighter:

    def __init__(self, database_file):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def get_subscriptions(self, status = True):
         """"получаем всех активных юзеров"""
         with self.connection:
             return self.cursor.execute("SELECT * FROM 'subscriptions' WHERE 'status = ?", (status,)).fetchall()

    def subscriber_exists(self, user_id):
