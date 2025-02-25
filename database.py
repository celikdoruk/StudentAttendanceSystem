import sqlite3

class Database:
    def __init__(self, db_name):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()

    def insert_data(self, insert_sql, data):
        try:
            self.cursor.execute(insert_sql, data)
            self.connection.commit()
        except sqlite3.Error as e:
            print(f'Error inserting data {e}')

    def update_data(self, update_sql, data):
        try:
            self.cursor.execute(update_sql, data)
            self.connection.commit()
        except sqlite3.Error as e:
            print(f'Error updating data {e}')

    def delete_data(self, delete_sql, data):
        try:
            self.cursor.execute(delete_sql, data)
            self.connection.commit()
        except sqlite3.Error as e:
            print(f'Error deleting data {e}')

    def query_data(self, query, params=None):
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f'Error querying data {e}')
            return []

    def close(self):
        self.connection.close()

