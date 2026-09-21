# Discord Orbs Quest Spoofer

A lightweight CLI utility designed to spoof running game processes for Discord quests without downloading or running heavy game clients.

## Features

- **Zero Overhead**: Uses a compiled C binary in a sleeping/paused state (< 2 MB RAM, 0% CPU usage).
- **Graceful Shutdown**: Properly handles OS signals (`SIGINT`, `SIGTERM`) to prevent orphaned processes.
- **Config-Driven**: Games are decoupled into `games.json` for easy updates.
- **Cross-Platform**: Supports both Linux and Windows environments.

## Project Structure

```text
.
├── .gitignore
├── README.md
└── src
    ├── dummy
    │   └── dummy.c
    ├── games.json
    └── main.py
    
    
    How It Works
Discord scans running OS processes by executable name (e.g., GenshinImpact.exe). This tool copies a lightweight paused dummy binary under the target executable name into an isolated runtime directory (~/.discord_spoof_games/) and starts it as a child process.

Getting Started
1. Build the dummy binary
On Linux:

Bash
gcc -O2 src/dummy/dummy.c -o src/dummy/dummy
On Windows (MinGW):

Bash
gcc -O2 src/dummy/dummy.c -o src/dummy/dummy.exe
2. Run the tool
Bash
python3 src/main.py
Select a game from the list, start streaming in Discord, and press Ctrl+C once the quest timer completes.