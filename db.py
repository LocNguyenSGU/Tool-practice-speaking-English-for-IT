import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "sentences.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS sentences (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lesson INTEGER DEFAULT 1,
        vi TEXT NOT NULL,
        en TEXT NOT NULL,
        vi_audio TEXT,
        en_audio TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()
    conn.close()


def get_random_sentence(lesson: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, vi, en, vi_audio, en_audio FROM sentences WHERE lesson=? ORDER BY RANDOM() LIMIT 1;", (lesson,))
    row = cur.fetchone()
    conn.close()
    return row


def seed_from_csv(csv_path: str):
    import csv
    conn = get_conn()
    cur = conn.cursor()
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = [(r['lesson'], r['vi'], r['en']) for r in reader]
    cur.executemany("INSERT INTO sentences(lesson, vi, en) VALUES (?, ?, ?);", rows)
    conn.commit()
    conn.close()

def get_lessons():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT lesson FROM sentences ORDER BY lesson;")
    lessons = [row[0] for row in cur.fetchall()]
    conn.close()
    return lessons

def get_sentences_by_lesson(lesson: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, vi, en, vi_audio, en_audio FROM sentences WHERE lesson=?;", (lesson,))
    rows = cur.fetchall()
    conn.close()
    return rows


def update_audio_paths(_id: int, vi_audio: str = None, en_audio: str = None):
    conn = get_conn()
    cur = conn.cursor()
    if vi_audio is not None and en_audio is not None:
        cur.execute("UPDATE sentences SET vi_audio=?, en_audio=? WHERE id=?;", (vi_audio, en_audio, _id))
    elif vi_audio is not None:
        cur.execute("UPDATE sentences SET vi_audio=? WHERE id=?;", (vi_audio, _id))
    elif en_audio is not None:
        cur.execute("UPDATE sentences SET en_audio=? WHERE id=?;", (en_audio, _id))
    conn.commit()
    conn.close()
