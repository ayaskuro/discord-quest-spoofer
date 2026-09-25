#!/usr/bin/env python3
import difflib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


class UI:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # Цвета
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"

    @staticmethod
    def banner():
        art = f"""{UI.MAGENTA}
  ██████╗ ██████╗ ██████╗ ██╗███████╗██╗   ██╗
 ██╔═══██╗██╔══██╗██╔══██╗██║██╔════╝╚██╗ ██╔╝
 ██║   ██║██████╔╝██████╔╝██║█████╗   ╚████╔╝ 
 ██║   ██║██╔══██╗██╔══██╗██║██╔══╝    ╚██╔╝  
 ╚██████╔╝██║  ██║██████╔╝██║██║        ██║   
  ╚═════╝ ╚═╝  ╚═╝╚═════╝ ╚═╝╚═╝        ╚═╝   
{UI.CYAN}       :: DISCORD ORBS QUEST SPOOFER ::{UI.RESET}
{UI.DIM}──────────────────────────────────────────────────{UI.RESET}"""
        print(art)


BASE_DIR = Path(__file__).resolve().parent
CONFIG_FILE = BASE_DIR / "games.json"
RUN_DIR = Path.home() / ".discord_spoof_games"


def get_dummy_path() -> Path:
    ext = ".exe" if sys.platform == "win32" else ""
    dummy_path = BASE_DIR / "dummy" / f"dummy{ext}"

    if not dummy_path.exists():
        print(f"{UI.RED}[!] Ошибка: бинарник не найден: {dummy_path}{UI.RESET}")
        print(f"{UI.YELLOW}[*] Скомпилируй его: gcc -O2 src/dummy/dummy.c -o src/dummy/dummy{UI.RESET}")
        sys.exit(1)

    return dummy_path


def load_games(config_path: Path) -> list[dict]:
    if not config_path.exists():
        print(f"{UI.RED}[!] Файл конфигурации не найден: {config_path}{UI.RESET}")
        sys.exit(1)

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as err:
        print(f"{UI.RED}[!] Ошибка чтения JSON: {err}{UI.RESET}")
        sys.exit(1)


def search_games(query: str, games: list[dict]) -> list[dict]:

    query = query.strip().lower()
    exact_matches = []
    fuzzy_matches = []

    for game in games:
        name_lower = game["name"].lower()
        exe_lower = game["exe"].lower()

        if query in name_lower or query in exe_lower:
            exact_matches.append(game)
            continue

        similarity = difflib.SequenceMatcher(None, query, name_lower).ratio()
        if similarity > 0.45:  # Порог схожести
            fuzzy_matches.append((similarity, game))

    fuzzy_matches.sort(key=lambda x: x[0], reverse=True)
    fuzzy_results = [item[1] for item in fuzzy_matches]

    # Объединяем результаты без дубликатов
    results = exact_matches + [g for g in fuzzy_results if g not in exact_matches]
    return results


def run_game_process(executable_path: Path):
    print(f"\n{UI.GREEN}[+] Запуск процесса:{UI.RESET} {UI.BOLD}{executable_path.name}{UI.RESET}")
    print(f"{UI.CYAN}[*] Discord должен обнаружить активность в статусе.{UI.RESET}")
    print(f"{UI.YELLOW}[*] Нажми Ctrl+C в терминале для завершения.{UI.RESET}\n")

    process = subprocess.Popen([str(executable_path)])

    try:
        process.wait()
    except KeyboardInterrupt:
        print(f"\n{UI.YELLOW}[-] Получен сигнал остановки. Завершаем процесс...{UI.RESET}")
        process.terminate()
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            print(f"{UI.RED}[!] Принудительное завершение (kill)...{UI.RESET}")
            process.kill()

        print(f"{UI.GREEN}[+] Процесс успешно остановлен.{UI.RESET}")


def select_game_interactive(games: list[dict]) -> str | None:
    """
    Интерактивный диалог поиска и выбора игры.
    """
    while True:
        UI.banner()
        print(f"{UI.BOLD}Команды:{UI.RESET} введи {UI.CYAN}название игры{UI.RESET} для поиска, "
              f"{UI.YELLOW}'all'{UI.RESET} для полного списка, "
              f"{UI.MAGENTA}'custom'{UI.RESET} для своего .exe или {UI.RED}'q'{UI.RESET} для выхода.\n")

        query = input(f"{UI.GREEN}search > {UI.RESET}").strip()

        if not query:
            continue

        if query.lower() in ("q", "quit", "exit"):
            return None

        if query.lower() == "custom":
            custom_exe = input(f"{UI.MAGENTA}Введи имя exe (например, Game.exe): {UI.RESET}").strip()
            if not custom_exe.endswith(".exe"):
                custom_exe += ".exe"
            return custom_exe

        if query.lower() == "all":
            matched = games
        else:
            matched = search_games(query, games)

        if not matched:
            print(f"\n{UI.RED}[x] Ничего не найдено по запросу '{query}'. Попробуй еще раз.{UI.RESET}\n")
            input(f"{UI.DIM}Нажми Enter для продолжения...{UI.RESET}")
            continue

        # Отображаем найденные совпадения
        print(f"\n{UI.CYAN}Найдено вариантов ({len(matched)}):{UI.RESET}")
        for idx, game in enumerate(matched, start=1):
            print(f"  {UI.BOLD}[{idx}]{UI.RESET} {game['name']} {UI.DIM}→ {game['exe']}{UI.RESET}")

        print(f"  {UI.DIM}[0] Назад к поиску{UI.RESET}")

        choice = input(f"\n{UI.GREEN}Выбери номер [1-{len(matched)}]: {UI.RESET}").strip()
        if choice == "0":
            continue

        try:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(matched):
                return matched[choice_idx]["exe"]
            else:
                print(f"{UI.RED}[!] Неверный номер.{UI.RESET}")
        except ValueError:
            print(f"{UI.RED}[!] Введи корректную цифру.{UI.RESET}")

        input(f"{UI.DIM}Нажми Enter для продолжения...{UI.RESET}")


def main():
    dummy_source = get_dummy_path()
    games = load_games(CONFIG_FILE)

    target_exe = select_game_interactive(games)
    if not target_exe:
        print(f"\n{UI.YELLOW}Выход из программы. Удачного фарма!{UI.RESET}")
        return

    RUN_DIR.mkdir(parents=True, exist_ok=True)
    spoofed_executable = RUN_DIR / target_exe

    shutil.copy2(dummy_source, spoofed_executable)

    if sys.platform != "win32":
        spoofed_executable.chmod(0o755)

    run_game_process(spoofed_executable)


if __name__ == "__main__":
    main()