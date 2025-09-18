import random
import textwrap
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

from click import wrap_text

from db import (
    init_db, seed_from_csv, get_lessons, get_sentences_by_lesson,
    update_audio_paths, add_sentence, update_sentence, delete_sentence
)
from tts import synthesize, play_audio
from threading import Thread

PROJECT_DIR = Path(__file__).parent
CSV_PATH = PROJECT_DIR / "data" / "sentences.csv"


def ensure_db_seeded():
    init_db()
    seed_from_csv(str(CSV_PATH))


class TrainerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("VI→EN Reflex Trainer")
        self.master.geometry("950x750")

        self.queue = []
        self.use_random = True
        self.current_index = 0
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

        # Nút quản lý câu
        self.btn_manage = tk.Button(lesson_frame, text="⚙ Manage Sentences", command=self.open_manage_window)
        self.btn_manage.pack(side=tk.LEFT, padx=10)
        
        self.btn_manage_lesson = tk.Button(lesson_frame, text="⚙ Manage Lessons", command=self.open_manage_lesson_window)
        self.btn_manage_lesson.pack(side=tk.LEFT, padx=10)

        # Label hiển thị VI/EN
        self.vi_label = tk.Label(master, text="", font=("Arial", 14), wraplength=700)
        self.vi_label.pack(pady=10)

        self.en_label = tk.Label(master, text="", font=("Arial", 14), fg="blue", wraplength=700)
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

        self.btn_next = tk.Button(frame, text="Next ➡️", command=self.next_sentence)
        self.btn_next.grid(row=0, column=3, padx=5)

        # Nút chọn kiểu Next
        frame2 = tk.Frame(master)
        frame2.pack(pady=5)

        self.btn_random = tk.Button(frame2, text="Next 🔀 (Random)", command=self.toggle_random)
        self.btn_random.pack(side=tk.LEFT, padx=5)

        self.btn_order = tk.Button(frame2, text="Next 🔁 (Theo thứ tự)", command=self.toggle_order)
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

    def toggle_random(self):
        self.use_random = True
        self.next_sentence()

    def toggle_order(self):
        self.use_random = False
        self.current_index = 0
        self.next_sentence()

    def set_lesson(self, lesson):
        self.current_lesson = int(lesson)
        self.lesson_var.set(lesson)
        self.reset_queue()
        self.load_sentences_table()
        self.current_index = 0
        self.next_sentence()

    def reset_queue(self):
        rows = get_sentences_by_lesson(self.current_lesson)
        self.queue = list(rows)
        if self.use_random:
            random.shuffle(self.queue)

    def load_sentences_table(self):
        rows = get_sentences_by_lesson(self.current_lesson)
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in rows:
            self.tree.insert("", tk.END, iid=row["id"], values=(row["vi"], row["en"]))


    def next_sentence(self):
        rows = get_sentences_by_lesson(self.current_lesson)
        if not rows:
            self.vi_label.config(text="(Không có câu trong bài này)")
            self.en_label.config(text="")
            return

        if self.use_random:
            if not self.queue:
                self.reset_queue()
            if self.queue:
                row = self.queue.pop()
            else:
                return
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
        self.en_label.config(text="")

        # Thread(target=self._play_vi_audio_thread).start()

    def _play_vi_audio_thread(self):
        if not self.vi_audio or not Path(self.vi_audio).exists():
            vi_path = synthesize(self.vi, "vi", f"vi_{self._id}")
            update_audio_paths(self._id, vi_audio=str(vi_path))
            self.vi_audio = str(vi_path)
        play_audio(Path(self.vi_audio))

    def _play_en_audio_thread(self):
        self.en_label.config(text=f"EN: {self.en}")
        if not self.en_audio or not Path(self.en_audio).exists():
            en_path = synthesize(self.en, "en", f"en_{self._id}")
            update_audio_paths(self._id, en_audio=str(en_path))
            self.en_audio = str(en_path)
        play_audio(Path(self.en_audio))

    def play_vi(self):
        Thread(target=self._play_vi_audio_thread).start()

    def show_en(self):
        Thread(target=self._play_en_audio_thread).start()

    def play_en(self):
        Thread(target=self._play_en_audio_thread).start()

    def open_manage_window(self):
        win = tk.Toplevel(self.master)
        win.title("Manage Sentences")
        win.geometry("600x250")

        frame_form = tk.Frame(win, padx=10, pady=10)
        frame_form.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame_form, text="Lesson:").grid(row=0, column=0, sticky="w")
        entry_lesson = tk.Entry(frame_form)
        entry_lesson.grid(row=0, column=1, sticky="ew", padx=5)
        entry_lesson.insert(0, str(self.current_lesson))

        tk.Label(frame_form, text="VI:").grid(row=1, column=0, sticky="w")
        entry_vi = tk.Entry(frame_form)
        entry_vi.grid(row=1, column=1, sticky="ew", padx=5)

        tk.Label(frame_form, text="EN:").grid(row=2, column=0, sticky="w")
        entry_en = tk.Entry(frame_form)
        entry_en.grid(row=2, column=1, sticky="ew", padx=5)

        frame_form.grid_columnconfigure(1, weight=1)

        def on_tree_select(event=None):
            selected = self.tree.focus()
            if not selected: return
            values = self.tree.item(selected, "values")
            entry_vi.delete(0, tk.END)
            entry_en.delete(0, tk.END)
            entry_lesson.delete(0, tk.END)
            entry_vi.insert(0, values[0])
            entry_en.insert(0, values[1])
            entry_lesson.insert(0, str(self.current_lesson))

        self.tree.bind("<<TreeviewSelect>>", on_tree_select)

        def add():
            try:
                lesson = int(entry_lesson.get())
                vi = entry_vi.get().strip()
                en = entry_en.get().strip()
                if not vi or not en:
                    messagebox.showerror("Error", "VI và EN không được trống!")
                    return
                add_sentence(lesson, vi, en)
                messagebox.showinfo("Success", "Đã thêm câu!")
                self.load_sentences_table()
                self.reset_queue()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        def update():
            selected = self.tree.focus()
            if not selected:
                messagebox.showerror("Error", "Chọn một câu để sửa!")
                return
            try:
                lesson = int(entry_lesson.get())
                vi = entry_vi.get().strip()
                en = entry_en.get().strip()
                update_sentence(int(selected), lesson=lesson, vi=vi, en=en)
                messagebox.showinfo("Success", "Đã cập nhật câu!")
                self.load_sentences_table()
                self.reset_queue()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        def delete():
            selected = self.tree.focus()
            if not selected:
                messagebox.showerror("Error", "Chọn một câu để xoá!")
                return
            try:
                delete_sentence(int(selected))
                messagebox.showinfo("Success", "Đã xoá câu!")
                self.load_sentences_table()
                self.reset_queue()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        frame_buttons = tk.Frame(win)
        frame_buttons.pack(pady=10)
        tk.Button(frame_buttons, text="Add", command=add).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_buttons, text="Update", command=update).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_buttons, text="Delete", command=delete).pack(side=tk.LEFT, padx=5)

    def open_manage_lesson_window(self):
        win = tk.Toplevel(self.master)
        win.title("Manage Lessons")
        win.geometry("300x200")

        frame = tk.Frame(win, padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)

        lessons = get_lessons()
        lesson_listbox = tk.Listbox(frame)
        lesson_listbox.pack(fill=tk.BOTH, expand=True)

        for lesson in lessons:
            lesson_listbox.insert(tk.END, lesson)

        def add_lesson():
            new_lesson = simpledialog.askinteger("Add Lesson", "Enter new lesson number:")
            if new_lesson and new_lesson not in lessons:
                lessons.append(new_lesson)
                lessons.sort()
                lesson_listbox.insert(tk.END, new_lesson)
                self.lesson_menu['menu'].add_command(label=new_lesson, command=tk._setit(self.lesson_var, new_lesson, self.set_lesson))
            else:
                messagebox.showerror("Error", "Lesson already exists or invalid input.")

        def delete_lesson():
            selected = lesson_listbox.curselection()
            if not selected:
                messagebox.showerror("Error", "Select a lesson to delete!")
                return
            lesson_to_delete = lesson_listbox.get(selected[0])
            if messagebox.askyesno("Confirm", f"Are you sure you want to delete lesson {lesson_to_delete}? This will also delete all its sentences."):
                # Delete all sentences in this lesson
                rows = get_sentences_by_lesson(lesson_to_delete)
                for row in rows:
                    delete_sentence(row["id"])
                lessons.remove(lesson_to_delete)
                lesson_listbox.delete(selected[0])
                self.lesson_menu['menu'].delete(lesson_to_delete)
                if self.current_lesson == lesson_to_delete:
                    self.current_lesson = None
                    self.vi_label.config(text="")
                    self.en_label.config(text="")
                    self.tree.delete(*self.tree.get_children())
                    self.queue = []

        btn_frame = tk.Frame(win)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Add Lesson", command=add_lesson).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Delete Lesson", command=delete_lesson).pack(side=tk.LEFT, padx=5)

if __name__ == "__main__":
    ensure_db_seeded()
    root = tk.Tk()
    app = TrainerApp(root)
    root.mainloop()