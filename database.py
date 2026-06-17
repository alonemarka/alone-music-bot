import sqlite3
import datetime

conn = sqlite3.connect('bot.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS play_logs (
    id INTEGER PRIMARY KEY,
    query TEXT UNIQUE,
    file_path TEXT,
    play_count INTEGER DEFAULT 1,
    last_played TEXT
)''')

conn.commit()

def log_play(query, file_path):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT OR REPLACE INTO play_logs (query, file_path, play_count, last_played) 
               VALUES (?, ?, COALESCE((SELECT play_count + 1 FROM play_logs WHERE query = ?), 1), ?)", 
               (query, file_path, query, now))
    conn.commit()
