import sqlite3

class Database:
    def __init__(self, db_path='database.db'):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS topers (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                score INTEGER NOT NULL
            )
        ''')
        self.conn.commit()

    def save_score(self, name, score):
        player = self.cursor.execute("SELECT * FROM topers WHERE name = ?", (name, )).fetchone()
        if not player:
            self.cursor.execute('INSERT INTO topers (name, score) VALUES (?, ?)', (name, score))
        else:
            self.cursor.execute('UPDATE topers SET score = ? WHERE name = ?', (score, name))
        self.conn.commit()

    def get_topers(self):
        self.cursor.execute('SELECT name, score FROM topers ORDER BY score DESC LIMIT 5')
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()