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
