import mysql.connector
from mysql.connector import Error
import csv
from pathlib import Path

# =============================
# Cấu hình kết nối MySQL server
# =============================
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "12345abc",
}
DB_NAME = "sentences_db"


def get_server_conn():
    """Kết nối MySQL server (chưa chọn database)."""
    return mysql.connector.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"]
    )


def get_conn():
    """Kết nối trực tiếp tới database sentences_db."""
    try:
        return mysql.connector.connect(**DB_CONFIG, database=DB_NAME)
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None


def init_db():
    """Tạo database + table nếu chưa có."""
    conn = None
    try:
        conn = get_server_conn()
        if not conn: return
        cur = conn.cursor()
        cur.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        conn.commit()
        cur.close()
    except Error as e:
        print(f"Error during database initialization: {e}")
    finally:
        if conn and conn.is_connected():
            conn.close()

    conn = None
    try:
        conn = get_conn()
        if not conn: return
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS sentences (
            id INT AUTO_INCREMENT PRIMARY KEY,
            lesson INT DEFAULT 1,
            vi TEXT NOT NULL,
            en TEXT NOT NULL,
            vi_audio VARCHAR(255),
            en_audio VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        conn.commit()
        cur.close()
    except Error as e:
        print(f"Error creating table: {e}")
    finally:
        if conn and conn.is_connected():
            conn.close()


def seed_from_csv(csv_path: str):
    """Seed dữ liệu từ CSV nếu bảng đang rỗng."""
    conn = get_conn()
    if not conn: return
    cur = conn.cursor()
    try:
        cur.execute("SELECT COUNT(*) FROM sentences;")
        count = cur.fetchone()[0]
        if count == 0 and Path(csv_path).exists():
            with open(csv_path, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = [(r['lesson'], r['vi'], r['en']) for r in reader]
            cur.executemany("""
                INSERT INTO sentences(lesson, vi, en) 
                VALUES (%s, %s, %s);
            """, rows)
            conn.commit()
    except Error as e:
        print(f"Error seeding data: {e}")
    finally:
        cur.close()
        conn.close()


def get_lessons():
    conn = get_conn()
    if not conn: return []
    cur = conn.cursor()
    try:
        cur.execute("SELECT DISTINCT lesson FROM sentences ORDER BY lesson;")
        lessons = [row[0] for row in cur.fetchall()]
        return lessons
    except Error as e:
        print(f"Error getting lessons: {e}")
        return []
    finally:
        cur.close()
        conn.close()


def get_sentences_by_lesson(lesson: int):
    conn = get_conn()
    if not conn: return []
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("""
            SELECT id, vi, en, vi_audio, en_audio
            FROM sentences
            WHERE lesson=%s;
        """, (lesson,))
        rows = cur.fetchall()
        return rows
    except Error as e:
        print(f"Error getting sentences: {e}")
        return []
    finally:
        cur.close()
        conn.close()


def update_audio_paths(_id: int, vi_audio: str = None, en_audio: str = None):
    conn = get_conn()
    if not conn: return
    cur = conn.cursor()
    try:
        if vi_audio is not None and en_audio is not None:
            cur.execute("""
                UPDATE sentences SET vi_audio=%s, en_audio=%s WHERE id=%s;
            """, (vi_audio, en_audio, _id))
        elif vi_audio is not None:
            cur.execute("UPDATE sentences SET vi_audio=%s WHERE id=%s;", (vi_audio, _id))
        elif en_audio is not None:
            cur.execute("UPDATE sentences SET en_audio=%s WHERE id=%s;", (en_audio, _id))
        conn.commit()
    except Error as e:
        print(f"Error updating audio paths: {e}")
    finally:
        cur.close()
        conn.close()


def add_sentence(lesson: int, vi: str, en: str):
    conn = get_conn()
    if not conn: return None
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO sentences(lesson, vi, en)
            VALUES (%s, %s, %s);
        """, (lesson, vi, en))
        conn.commit()
        new_id = cur.lastrowid
        return new_id
    except Error as e:
        print(f"Error adding sentence: {e}")
        return None
    finally:
        cur.close()
        conn.close()


def update_sentence(_id: int, lesson: int = None, vi: str = None, en: str = None):
    conn = get_conn()
    if not conn: return
    cur = conn.cursor()
    try:
        fields = []
        values = []
        if lesson is not None:
            fields.append("lesson=%s")
            values.append(lesson)
        if vi is not None:
            fields.append("vi=%s")
            values.append(vi)
        if en is not None:
            fields.append("en=%s")
            values.append(en)

        if fields:
            sql = f"UPDATE sentences SET {', '.join(fields)} WHERE id=%s"
            values.append(_id)
            cur.execute(sql, tuple(values))
            conn.commit()
    except Error as e:
        print(f"Error updating sentence: {e}")
    finally:
        cur.close()
        conn.close()


def delete_sentence(_id: int):
    conn = get_conn()
    if not conn: return
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM sentences WHERE id=%s;", (_id,))
        conn.commit()
    except Error as e:
        print(f"Error deleting sentence: {e}")
    finally:
        cur.close()
        conn.close()