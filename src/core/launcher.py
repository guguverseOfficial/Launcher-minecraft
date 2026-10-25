import minecraft_launcher_lib
import subprocess
import os

GAME_DIR = os.path.join(os.getcwd(), "Guguverse_Minecraft")

def launch_game(version, username):
    """Запускает игру (офлайн режим)"""
    options = {
        "username": username,
        "uuid": "", 
        "token": "" 
    }
    # Получаем команду для запуска
    command = minecraft_launcher_lib.command.get_minecraft_command(version, GAME_DIR, options)
    
    # Запускаем процесс игры
    subprocess.Popen(command)