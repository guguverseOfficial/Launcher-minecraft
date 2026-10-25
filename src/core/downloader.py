import minecraft_launcher_lib
import os

GAME_DIR = os.path.join(os.getcwd(), "Guguverse_Minecraft")

def install_game(version):
    """Скачивает игру и Java"""
    if not os.path.exists(GAME_DIR):
        os.makedirs(GAME_DIR)
    
    # Библиотека сама скачает нужную Java
    minecraft_launcher_lib.install.install_minecraft_version(version, GAME_DIR)