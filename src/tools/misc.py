import os
import subprocess
import time

import tools.keyboard as keyboard


SHORTCUTS_FOLDER = r"C:\Users\ammar\voice-assistant-apps"

def open_app(app_name: str) -> str:
    name = app_name.lower().strip()

    try:
        files = os.listdir(SHORTCUTS_FOLDER)
    except FileNotFoundError:
        return f"Shortcuts folder not found: {SHORTCUTS_FOLDER}"

    for filename in files:
        if filename.lower().endswith(".lnk"):
            shortcut_name = filename[:-4].lower()  # strip .lnk
            if shortcut_name == name or name in shortcut_name:
                full_path = os.path.join(SHORTCUTS_FOLDER, filename)
                subprocess.Popen(f'start "" "{full_path}"', shell=True)
                return f"Launched {filename[:-4]}."

    return f"No shortcut found for '{app_name}'."

def go_to_discord_direct_messages(name: str):
    result = keyboard.focus_window("Discord")
    if "No window found" in result:
        return "Discord doesn't seem to be open"
    time.sleep(0.5)
    keyboard.press_combo("ctrl", "k")
    time.sleep(0.4)

    keyboard.type_text(name, 0.03)
    time.sleep(0.6)

    keyboard.press_key("enter")

    return f"Went to {name}'s direct messages on discord."

def call_on_discord(name: str):
    result = go_to_discord_direct_messages(name)
    if "No window found" in result:
        return "Discord doesn't seem to be open"

    keyboard.press_combo("ctrl", "backtick")
    return f"Called {name} on discord."