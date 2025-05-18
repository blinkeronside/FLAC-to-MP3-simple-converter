import os
import subprocess
import shutil
import tempfile
from tkinter import filedialog, messagebox
import threading
import tkinter as tk
from ttkbootstrap import Style
from ttkbootstrap.widgets import Button, Progressbar, Label, Frame


class AudioConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FLAC ➜ MP3 Audio Converter")
        self.style = Style("flatly")

        self.frame = Frame(self.root, padding=20)
        self.frame.pack()

        self.input_path = ""
        self.output_path = ""
        self.conversion_in_progress = False

        self.input_btn = Button(self.frame, text="Выбрать папку с FLAC", command=self.choose_input)
        self.input_btn.pack(pady=5)

        self.output_btn = Button(self.frame, text="Выбрать папку для MP3", command=self.choose_output)
        self.output_btn.pack(pady=5)

        self.convert_btn = Button(self.frame, text="Конвертировать", command=self.start_conversion_thread)
        self.convert_btn.pack(pady=10)

        self.progress = Progressbar(self.frame, length=300)
        self.progress.pack(pady=10)

        self.status = Label(self.frame, text="")
        self.status.pack()

    def choose_input(self):
        self.input_path = filedialog.askdirectory(title="Выберите папку с FLAC-файлами")

    def choose_output(self):
        self.output_path = filedialog.askdirectory(title="Выберите папку для сохранения MP3")

    def start_conversion_thread(self):
        if self.conversion_in_progress:
            messagebox.showinfo("Предупреждение", "Конвертация уже выполняется!")
            return

        if not self.input_path or not self.output_path:
            messagebox.showwarning("Ошибка", "Выберите обе папки перед началом конвертации.")
            return

        threading.Thread(target=self.convert_files, daemon=True).start()

    def convert_files(self):
        self.conversion_in_progress = True
        self.convert_btn.config(state="disabled")
        self.status.config(text="Конвертация...")

        flac_files = []
        for root_dir, _, files in os.walk(self.input_path):
            for file in files:
                if file.lower().endswith(".flac"):
                    flac_files.append(os.path.join(root_dir, file))

        total = len(flac_files)
        if total == 0:
            messagebox.showinfo("Нет файлов", "Файлы FLAC не найдены.")
            self.status.config(text="Ожидание")
            self.conversion_in_progress = False
            self.convert_btn.config(state="normal")
            return

        self.progress.config(maximum=total, value=0)

        # путь к встроенному ffmpeg (для PyInstaller)
        if getattr(sys, 'frozen', False):
            ffmpeg_path = os.path.join(sys._MEIPASS, "ffmpeg.exe")
        else:
            ffmpeg_path = "ffmpeg.exe"

        for i, flac_path in enumerate(flac_files, 1):
            rel_path = os.path.relpath(flac_path, self.input_path)
            mp3_path = os.path.splitext(os.path.join(self.output_path, rel_path))[0] + ".mp3"
            os.makedirs(os.path.dirname(mp3_path), exist_ok=True)

            cmd = [
                ffmpeg_path,
                "-i", flac_path,
                "-q:a", "0",  # максимальное качество MP3
                "-map_metadata", "0",
                "-id3v2_version", "3",
                mp3_path
            ]

            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            self.progress["value"] = i
            self.root.update_idletasks()

        self.status.config(text="Готово!")
        messagebox.showinfo("Готово", "Конвертация завершена.")
        self.convert_btn.config(state="normal")
        self.conversion_in_progress = False


if __name__ == "__main__":
    import sys
    root = tk.Tk()
    app = AudioConverterApp(root)
    root.mainloop()
