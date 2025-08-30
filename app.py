# import random
# import tkinter as tk
# from tkinter import ttk
# from pathlib import Path
# from db import init_db, seed_from_csv, get_random_sentence, update_audio_paths, get_lessons
# from tts import synthesize, play_audio
#
# PROJECT_DIR = Path(__file__).parent
# CSV_PATH = PROJECT_DIR / "data" / "sentences.csv"
#
#
# def ensure_db_seeded():
#     import sqlite3
#     init_db()
#     conn = sqlite3.connect(PROJECT_DIR / "sentences.db")
#     cur = conn.cursor()
#     cur.execute("SELECT COUNT(*) FROM sentences;")
#     n = cur.fetchone()[0]
#     conn.close()
#     if n == 0 and CSV_PATH.exists():
#         seed_from_csv(str(CSV_PATH))
#
#
# class TrainerApp:
#     def __init__(self, master):
#         self.master = master
#         self.master.title("VI→EN Reflex Trainer")
#         self.queue = []
#
#         # trạng thái hiện tại
#         self.current_lesson = None
#
#         # menu chọn bài
#         lesson_frame = tk.Frame(master)
#         lesson_frame.pack(pady=5, fill=tk.X)
#
#         tk.Label(lesson_frame, text="Chọn bài:").pack(side=tk.LEFT)
#
#         self.lesson_var = tk.StringVar()
#         self.lesson_menu = tk.OptionMenu(
#             lesson_frame, self.lesson_var, *get_lessons(), command=self.set_lesson
#         )
#         self.lesson_menu.pack(side=tk.LEFT)
#
#         # label hiển thị VI/EN
#         self.vi_label = tk.Label(master, text="", font=("Arial", 14))
#         self.vi_label.pack(pady=10)
#
#         self.en_label = tk.Label(master, text="", font=("Arial", 14), fg="blue")
#         self.en_label.pack(pady=10)
#
#         # khung nút
#         frame = tk.Frame(master)
#         frame.pack(pady=20)
#
#         self.btn_vi = tk.Button(frame, text="🔊 Repeat VI", command=self.play_vi)
#         self.btn_vi.grid(row=0, column=0, padx=5)
#
#         self.btn_show_en = tk.Button(frame, text="Show + Play EN", command=self.show_en)
#         self.btn_show_en.grid(row=0, column=1, padx=5)
#
#         self.btn_en = tk.Button(frame, text="🔊 Repeat EN", command=self.play_en)
#         self.btn_en.grid(row=0, column=2, padx=5)
#
#         self.btn_next = tk.Button(frame, text="Next ➡️", command=self.next_sentence)
#         self.btn_next.grid(row=0, column=3, padx=5)
#
#         # bảng hiển thị danh sách câu (Treeview)
#         table_frame = tk.Frame(master)
#         table_frame.pack(pady=10, fill=tk.BOTH, expand=True)
#
#         self.tree = ttk.Treeview(table_frame, columns=("vi", "en"), show="headings", height=20)
#         self.tree.heading("vi", text="VI")
#         self.tree.heading("en", text="EN")
#         self.tree.column("vi", width=400, anchor="w")
#         self.tree.column("en", width=400, anchor="w")
#
#         # thanh cuộn dọc
#         scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
#         self.tree.configure(yscrollcommand=scrollbar.set)
#
#         self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
#         scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
#
#         # dữ liệu hiện tại
#         self._id = None
#         self.vi = ""
#         self.en = ""
#         self.vi_audio = None
#         self.en_audio = None
#
#         # mặc định chọn bài đầu tiên
#         lessons = get_lessons()
#         if lessons:
#             self.set_lesson(lessons[0])
#
#     def set_lesson(self, lesson):
#         self.current_lesson = int(lesson)
#         self.lesson_var.set(lesson)
#         self.reset_queue()
#         self.load_sentences_table()
#         self.next_sentence()
#
#     def reset_queue(self):
#         from db import get_sentences_by_lesson
#
#         rows = get_sentences_by_lesson(self.current_lesson)
#         self.queue = list(rows)
#         random.shuffle(self.queue)
#
#     def load_sentences_table(self):
#         from db import get_sentences_by_lesson
#
#         rows = get_sentences_by_lesson(self.current_lesson)
#
#         # clear bảng cũ
#         for item in self.tree.get_children():
#             self.tree.delete(item)
#
#         # insert dữ liệu mới
#         for row in rows:
#             self.tree.insert("", tk.END, values=(row["vi"], row["en"]))
#
#     def next_sentence(self):
#         if not self.queue:  # nếu hết thì reset lại
#             self.reset_queue()
#
#         if not self.queue:  # vẫn rỗng (bài chưa có câu nào)
#             self.vi_label.config(text="(Không có câu trong bài này)")
#             self.en_label.config(text="")
#             return
#
#         row = self.queue.pop()  # lấy 1 câu và bỏ khỏi queue
#
#         self._id = row["id"]
#         self.vi = row["vi"]
#         self.en = row["en"]
#         self.vi_audio = row["vi_audio"]
#         self.en_audio = row["en_audio"]
#
#         self.vi_label.config(text=f"VI: {self.vi}")
#         self.en_label.config(text="")  # ẩn EN
#
#         if not self.vi_audio or not Path(self.vi_audio).exists():
#             vi_path = synthesize(self.vi, "vi", f"vi_{self._id}")
#             update_audio_paths(self._id, vi_audio=str(vi_path))
#             self.vi_audio = str(vi_path)
#
#         play_audio(Path(self.vi_audio))
#
#     def play_vi(self):
#         if self.vi_audio and Path(self.vi_audio).exists():
#             play_audio(Path(self.vi_audio))
#
#     def show_en(self):
#         self.en_label.config(text=f"EN: {self.en}")
#         if not self.en_audio or not Path(self.en_audio).exists():
#             en_path = synthesize(self.en, "en", f"en_{self._id}")
#             update_audio_paths(self._id, en_audio=str(en_path))
#             self.en_audio = str(en_path)
#         play_audio(Path(self.en_audio))
#
#     def play_en(self):
#         if self.en_audio and Path(self.en_audio).exists():
#             play_audio(Path(self.en_audio))
#
#
# if __name__ == "__main__":
#     ensure_db_seeded()
#     root = tk.Tk()
#     app = TrainerApp(root)
#     root.mainloop()


import random
import tkinter as tk
from tkinter import ttk
from pathlib import Path
from db import init_db, seed_from_csv, get_random_sentence, update_audio_paths, get_lessons

from tts import synthesize, play_audio

PROJECT_DIR = Path(__file__).parent
CSV_PATH = PROJECT_DIR / "data" / "sentences.csv"


def ensure_db_seeded():
    import sqlite3
    init_db()
    conn = sqlite3.connect(PROJECT_DIR / "sentences.db")
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM sentences;")
    n = cur.fetchone()[0]
    conn.close()
    if n == 0 and CSV_PATH.exists():
        seed_from_csv(str(CSV_PATH))


class TrainerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("VI→EN Reflex Trainer")
        self.queue = []
        self.use_random = True  # True: random, False: theo thứ tự
        self.current_index = 0  # chỉ số câu hiện tại khi next theo thứ tự

        # trạng thái bài hiện tại
        self.current_lesson = None

        # Menu chọn bài
        lesson_frame = tk.Frame(master)
        lesson_frame.pack(pady=5, fill=tk.X)

        tk.Label(lesson_frame, text="Chọn bài:").pack(side=tk.LEFT)

        self.lesson_var = tk.StringVar()
        self.lesson_menu = tk.OptionMenu(
            lesson_frame, self.lesson_var, *get_lessons(), command=self.set_lesson
        )
        self.lesson_menu.pack(side=tk.LEFT)

        # Label hiển thị VI/EN
        self.vi_label = tk.Label(master, text="", font=("Arial", 14))
        self.vi_label.pack(pady=10)

        self.en_label = tk.Label(master, text="", font=("Arial", 14), fg="blue")
        self.en_label.pack(pady=10)

        # Khung nút chính
        frame = tk.Frame(master)
        frame.pack(pady=10)

        self.btn_vi = tk.Button(frame, text="🔊 Repeat VI", command=self.play_vi)
        self.btn_vi.grid(row=0, column=0, padx=5)

        self.btn_show_en = tk.Button(frame, text="Show + Play EN", command=self.show_en)
        self.btn_show_en.grid(row=0, column=1, padx=5)

        self.btn_en = tk.Button(frame, text="🔊 Repeat EN", command=self.play_en)
        self.btn_en.grid(row=0, column=2, padx=5)

        self.btn_next = tk.Button(frame, text="Next ➡️", command=self.next_random)
        self.btn_next.grid(row=0, column=3, padx=5)

        # Nút chọn kiểu Next
        frame2 = tk.Frame(master)
        frame2.pack(pady=5)

        self.btn_random = tk.Button(frame2, text="Next 🔀 (Random)", command=self.next_random)
        self.btn_random.pack(side=tk.LEFT, padx=5)

        self.btn_order = tk.Button(frame2, text="Next 🔁 (Theo thứ tự)", command=self.next_order)
        self.btn_order.pack(side=tk.LEFT, padx=5)

        # Treeview hiển thị danh sách câu
        table_frame = tk.Frame(master)
        table_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(table_frame, columns=("vi", "en"), show="headings", height=20)
        self.tree.heading("vi", text="VI")
        self.tree.heading("en", text="EN")
        self.tree.column("vi", width=400, anchor="w")
        self.tree.column("en", width=400, anchor="w")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Dữ liệu hiện tại
        self._id = None
        self.vi = ""
        self.en = ""
        self.vi_audio = None
        self.en_audio = None

        # Mặc định chọn bài đầu tiên
        lessons = get_lessons()
        if lessons:
            self.set_lesson(lessons[0])

    def set_lesson(self, lesson):
        self.current_lesson = int(lesson)
        self.lesson_var.set(lesson)
        self.reset_queue()
        self.load_sentences_table()
        self.current_index = 0
        self.next_sentence()

    def reset_queue(self):
        from db import get_sentences_by_lesson

        rows = get_sentences_by_lesson(self.current_lesson)
        self.queue = list(rows)
        if self.use_random:
            random.shuffle(self.queue)

    def load_sentences_table(self):
        from db import get_sentences_by_lesson

        rows = get_sentences_by_lesson(self.current_lesson)

        # Xóa dữ liệu cũ
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Insert dữ liệu mới
        for row in rows:
            self.tree.insert("", tk.END, values=(row["vi"], row["en"]))

    def next_random(self):
        self.use_random = True
        self.next_sentence()

    def next_order(self):
        self.use_random = False
        self.next_sentence()

    def next_sentence(self):
        from db import get_sentences_by_lesson

        rows = get_sentences_by_lesson(self.current_lesson)

        if not rows:
            self.vi_label.config(text="(Không có câu trong bài này)")
            self.en_label.config(text="")
            return

        if self.use_random:
            if not self.queue:
                self.reset_queue()
            row = self.queue.pop()
        else:
            if self.current_index >= len(rows):
                self.current_index = 0
            row = rows[self.current_index]
            self.current_index += 1

        self._id = row["id"]
        self.vi = row["vi"]
        self.en = row["en"]
        self.vi_audio = row["vi_audio"]
        self.en_audio = row["en_audio"]

        self.vi_label.config(text=f"VI: {self.vi}")
        self.en_label.config(text="")  # ẩn EN

        if not self.vi_audio or not Path(self.vi_audio).exists():
            vi_path = synthesize(self.vi, "vi", f"vi_{self._id}")
            update_audio_paths(self._id, vi_audio=str(vi_path))
            self.vi_audio = str(vi_path)

        play_audio(Path(self.vi_audio))

    def play_vi(self):
        if self.vi_audio and Path(self.vi_audio).exists():
            play_audio(Path(self.vi_audio))

    def show_en(self):
        self.en_label.config(text=f"EN: {self.en}")
        if not self.en_audio or not Path(self.en_audio).exists():
            en_path = synthesize(self.en, "en", f"en_{self._id}")
            update_audio_paths(self._id, en_audio=str(en_path))
            self.en_audio = str(en_path)
        play_audio(Path(self.en_audio))

    def play_en(self):
        if self.en_audio and Path(self.en_audio).exists():
            play_audio(Path(self.en_audio))


if __name__ == "__main__":
    ensure_db_seeded()
    root = tk.Tk()
    root.geometry("900x700")
    app = TrainerApp(root)
    root.mainloop()