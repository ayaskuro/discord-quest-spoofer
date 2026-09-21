#!/usr/bin/env python3
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path 

BASE_DIR = Path(__file__).resolve().parent
CONFIG_FILE = BASE_DIR / "games.json"
RUN_DIR = Path.home() / ".discord_spoof_games"
def get_dummy_path() -> Path:
    ext = ".exe" if sys.platform == "win32" else ""
    dummy_path = BASE_DIR / "dummy" / f"dummy{ext}"

    if not dummy_path.exists():
        print(f"[!] Binary not found: {dummy_path}")
        print("[!] Compile it: gcc -O2 src/dummy/dummy.c -o src/dummy/dummy")
        sys.exit(1)

    return dummy_path

def load_games(config_path: Path) -> list[dict]:
    if not config_path.exists():
        print(f"[!] Configuration file not found: {config_path}")
        sys.exit(1)

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as err:
        print(f"[!] Error reading JSON: {err}")
        sys.exit(1)

def display_menu(games: list[dict]):
    print("\n"+"="* 45)
    print("      DISCORD ORBS QUES SPOOFER    ")
    print("="*45)
    for game in games:
        print(f"  [{game['id']}] {game['name']} -> ({game['exe']})")
    print("[0] Launch custom .exe")
    print("=" * 45)

def run_game_process(executable_path: Path):
    print(f"\n[+] Запуск процесса: {executable_path.name}")
    print("[*] Discord должен обнаружить игру.")
    print("[*] Нажми Ctrl+C, чтобы завершить эмуляцию.\n")

    process = subprocess.Popen([str(executable_path)])

    try:
        process.wait()
    except KeyboardInterrupt:
        print("\n[-] Получен сигнал остановки (Ctrl+C). Завершаем процесс...")
        process.terminate()
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            print("[!] Процесс завис, принудительное убийство (SIGKILL)...")
            process.kill()

        print("[+] Процесс успешно остановлен.")

def main():
    dummy_source = get_dummy_path()
    games = load_games(CONFIG_FILE)

    display_menu(games)
    choice = input("\nВыбери пункт меню: ").strip()

    if choice == "0":
        target_exe = input("Введи имя процесса (например, Game.exe): ").strip()
        if not target_exe.endswith(".exe"):
            target_exe += ".exe"
    else:
        matched = next((g for g in games if g["id"] == choice), None)
        if matched:
            target_exe = matched["exe"]
        else:
            print("[!] Неверный ввод.")
            return

    # Создаем рабочую папку ~/.discord_spoof_games, если ее еще нет
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    spoofed_executable = RUN_DIR / target_exe

    # Копируем dummy с новым именем
    shutil.copy2(dummy_source, spoofed_executable)

    # На Linux/macOS даем файлу права на исполнение (+x)
    if sys.platform != "win32":
        spoofed_executable.chmod(0o755)

    run_game_process(spoofed_executable)


if __name__ == "__main__":
    main()
