import customtkinter as ctk
import minecraft_launcher_lib
import subprocess
import os
import threading
import tkinter.messagebox as messagebox
import json
from PIL import Image

# --- НАСТРОЙКИ ОКНА ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

# Пути к файлам
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GAME_DIR = os.path.join(BASE_DIR, "Guguverse_Minecraft")
CONFIG_FILE = os.path.join(BASE_DIR, "launcher_config.json")
DEFAULT_SETTINGS_FILE = os.path.join(BASE_DIR, "configs", "default_settings.json")
VERSIONS_FILE = os.path.join(BASE_DIR, "configs", "versions_list.json")
ICON_PATH = os.path.join(BASE_DIR, "assets", "icons", "guguverse_logo.png")

class GuguverseLauncher(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Guguverse Minecraft Launcher")
        self.geometry("600x500")
        self.resizable(False, False)

        # Установка иконки окна (если файл существует)
        if os.path.exists(ICON_PATH):
            try:
                self.iconphoto(True, Image.open(ICON_PATH))
            except Exception as e:
                print(f"Не удалось загрузить иконку: {e}")

        # Загрузка конфигураций
        self.settings = self.load_json(DEFAULT_SETTINGS_FILE)
        self.versions_data = self.load_json(VERSIONS_FILE)
        self.user_config = self.load_json(CONFIG_FILE)

        # Собираем список версий (релизы + снапшоты, если включено)
        self.available_versions = self.versions_data.get("release", ["1.20.1", "1.8.9"])
        if self.settings.get("show_snapshots", False):
            self.available_versions.extend(self.versions_data.get("snapshots", []))

        self.setup_ui()

    def load_json(self, filepath):
        """Безопасная загрузка JSON"""
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Ошибка чтения {filepath}: {e}")
        return {}

    def save_user_config(self, nick, version):
        """Сохранение настроек пользователя"""
        data = {"nickname": nick, "last_version": version}
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def setup_ui(self):
        # --- ЗАГОЛОВОК ---
        self.label_title = ctk.CTkLabel(
            self, text="GUGUVERSE STUDIOS", 
            font=("Arial Black", 28, "bold"), text_color="#2ecc71"
        )
        self.label_title.pack(pady=(20, 5))

        self.label_subtitle = ctk.CTkLabel(
            self, text="Minecraft Launcher v1.0", 
            font=("Arial", 14), text_color="gray"
        )
        self.label_subtitle.pack(pady=(0, 20))

        # --- ВВОД НИКА ---
        ctk.CTkLabel(self, text="Введите никнейм:", font=("Arial", 14, "bold")).pack(pady=(5, 5))
        
        self.entry_nick = ctk.CTkEntry(self, width=300, placeholder_text="Guguverse")
        self.entry_nick.pack(pady=5)
        
        # Подставляем сохраненный ник или ник по умолчанию
        saved_nick = self.user_config.get("nickname", self.settings.get("nickname", ""))
        if saved_nick:
            self.entry_nick.insert(0, saved_nick)

        # --- ВЫБОР ВЕРСИИ ---
        ctk.CTkLabel(self, text="Выберите версию Minecraft:", font=("Arial", 14, "bold")).pack(pady=(15, 5))

        self.combo_version = ctk.CTkComboBox(self, values=self.available_versions, width=300)
        
        # Подставляем сохраненную версию или версию по умолчанию
        saved_version = self.user_config.get("last_version", self.settings.get("last_version", "1.20.1"))
        if saved_version in self.available_versions:
            self.combo_version.set(saved_version)
        else:
            self.combo_version.set(self.available_versions[0])
            
        self.combo_version.pack(pady=5)

        # --- КНОПКА ЗАПУСКА ---
        self.btn_play = ctk.CTkButton(
            self, text="СКАЧАТЬ И ИГРАТЬ", 
            font=("Arial Black", 18), 
            fg_color="#2ecc71", hover_color="#27ae60", 
            height=50, command=self.start_game_thread
        )
        self.btn_play.pack(pady=30)

        # --- СТАТУС БАР ---
        self.label_status = ctk.CTkLabel(
            self, text="Готов к запуску", 
            font=("Arial", 12), text_color="#aaaaaa"
        )
        self.label_status.pack(side="bottom", pady=10)

    def update_status(self, text):
        """Обновление текста статуса"""
        self.label_status.configure(text=text)

    def start_game_thread(self):
        nick = self.entry_nick.get().strip()
        version = self.combo_version.get()

        if not nick:
            messagebox.showwarning("Ошибка", "Введите никнейм! (Например: Guguverse)")
            return

        # Сохраняем настройки
        self.save_user_config(nick, version)

        # Блокируем кнопку
        self.btn_play.configure(state="disabled", text="ПОДОЖДИТЕ...")
        self.update_status(f"Подготовка к скачиванию {version}...")

        # Запуск в отдельном потоке
        thread = threading.Thread(target=self.install_and_launch, args=(version, nick))
        thread.daemon = True
        thread.start()

    def install_and_launch(self, version, nick):
        try:
            # 1. Скачивание игры и Java
            self.update_status(f"Скачивание Minecraft {version} и Java...")
            if not os.path.exists(GAME_DIR):
                os.makedirs(GAME_DIR)
                
            minecraft_launcher_lib.install.install_minecraft_version(version, GAME_DIR)
            
            # 2. Запуск
            self.update_status(f"Запуск Minecraft от имени {nick}...")
            
            options = {
                "username": nick,
                "uuid": "", 
                "token": "" 
            }
            
            command = minecraft_launcher_lib.command.get_minecraft_command(version, GAME_DIR, options)
            subprocess.Popen(command, cwd=GAME_DIR)
            
            self.update_status("Игра запущена! Приятной игры!")
            self.btn_play.configure(state="normal", text="СКАЧАТЬ И ИГРАТЬ")
            
        except Exception as e:
            self.update_status("Ошибка при запуске!")
            messagebox.showerror("Ошибка", f"Произошла ошибка:\n{e}")
            self.btn_play.configure(state="normal", text="СКАЧАТЬ И ИГРАТЬ")

if __name__ == "__main__":
    app = GuguverseLauncher()
    app.mainloop()