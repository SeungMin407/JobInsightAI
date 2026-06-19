import sqlite3

conn = sqlite3.connect("jobs.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS recommendations(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    company TEXT,
    url TEXT,
    embedding_similarity REAL,
    score INTEGER,
    summary TEXT,
    reason TEXT
)
""")

conn.commit()
conn.close()

print("DB 생성 완료")