import os
import subprocess
import time

import tools.keyboard as keyboard


SHORTCUTS_FOLDER = r"C:\Users\ammar\voice-assistant-apps"

def go_to_discord_direct_messages(name: str):
    result = keyboard.focus_window("Discord")
    if "No window found" in result:
        return "Discord doesn't seem to be open"
    time.sleep(0.5)
    keyboard.press_combo("ctrl", "k")
    time.sleep(0.4)

    keyboard.type_text(name, 0.01)
    time.sleep(0.3)

    keyboard.press_key("enter")

    return f"Went to {name}'s direct messages on discord."

def call_on_discord(name: str):
    result = go_to_discord_direct_messages(name)
    if "No window found" in result:
        return "Discord doesn't seem to be open"

    time.sleep(0.1)
    print(keyboard.press_combo("ctrl", "single_quote"))
    return f"Called {name} on discord."