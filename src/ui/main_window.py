import customtkinter as ctk
from tkinter import messagebox
from src.core.downloader import install_game
from src.core.launcher import launch_game
from src.utils.config import load_config, save_config
import threading

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Guguverse Minecraft Launcher")
        self.geometry("500x400")
        self.resizable(False, False)

        self.config = load_config()

        # Заголовок
        ctk.CTkLabel(self, text="GUGUVERSE STUDIOS", font=("Arial Black", 24), text_color="#2ecc71").pack(pady=20)

        # Никнейм
        self.nick_entry = ctk.CTkEntry(self, placeholder_text="Введите ник", width=300)
        self.nick_entry.pack(pady=10)
        if self.config.get("nick"):
            self.nick_entry.insert(0, self.config["nick"])

        # Версия
        self.version_combo = ctk.CTkComboBox(self, values=["1.8.9", "1.12.2", "1.20.1", "1.21"], width=300)
        self.version_combo.set("1.20.1")
        self.version_combo.pack(pady=10)

        # Кнопка
        self.play_btn = ctk.CTkButton(self, text="ИГРАТЬ", font=("Arial", 18, "bold"), command=self.start)
        self.play_btn.pack(pady=20)

        self.status_label = ctk.CTkLabel(self, text="Готов к запуску", text_color="gray")
        self.status_label.pack(side="bottom", pady=10)

    def start(self):
        nick = self.nick_entry.get().strip()
        version = self.version_combo.get()

        if not nick:
            messagebox.showerror("Ошибка", "Введите никнейм!")
            return

        save_config({"nick": nick})
        self.play_btn.configure(state="disabled", text="ЗАГРУЗКА...")
        
        # Запускаем в отдельном потоке, чтобы окно не зависало
        threading.Thread(target=self.run_game, args=(version, nick), daemon=True).start()

    def run_game(self, version, nick):
        try:
            self.status_label.configure(text=f"Скачивание {version}...")
            install_game(version)
            
            self.status_label.configure(text="Запуск...")
            launch_game(version, nick)
            
            self.status_label.configure(text="Игра запущена!")
            self.play_btn.configure(state="normal", text="ИГРАТЬ")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
            self.status_label.configure(text="Ошибка!")
            self.play_btn.configure(state="normal", text="ИГРАТЬ")