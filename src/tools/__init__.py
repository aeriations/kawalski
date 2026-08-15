import os
import subprocess
import time

import tools.memory as memory

import tools.media as media
import tools.scrape as scrape
import tools.keyboard as keyboard

import pkgutil
import inspect
import importlib


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

def remember(args):
    return memory.remember(
        args["text"],
        args.get("category", "General")
    )

def forget_memory(args):
    return memory.forget_memory(args["text"])

def search_memory(args):
    return memory.search_memory(args["query"])

def fetch_webpage(args):
    return scrape.fetch_webpage(args["url"])

def web_search(args):
    return scrape.web_search(args["query"])

def press_key(args):
    return keyboard.press_key(args["key"])

def press_combo(args):
    return keyboard.press_combo(args["keys"])

def type_text(args):
    return keyboard.type_text(args["text"])

def focus_window(args):
    return keyboard.focus_window(args["name"])


def go_to_discord_direct_messages(args):
    result = keyboard.focus_window("Discord")
    print(f"[debug] go_to_discord_direct_messages called with args: {args}")
    if "No window found" in result:
        return "Discord doesn't seem to be open"
    print(f"[debug] focus_window result: {result}")
    time.sleep(0.5)
    keyboard.press_combo("ctrl", "k")
    time.sleep(0.4)

    keyboard.type_text(args['name'], 0.03)
    time.sleep(0.6)

    keyboard.press_key("enter")

    return f"Went to {args['name']}'s direct messages on discord."

def call_on_discord(args) -> str:
    result = go_to_discord_direct_messages(args)
    if "No window found" in result:
        return "Discord doesn't seem to be open"

    keyboard.press_combo("ctrl", "backtick")
    return f"Called {args['name']} on discord."

def load_all_tools():
    res = []
    obj_dir = os.path.dirname(os.path.abspath(__file__))
    for _, module_name, _ in pkgutil.iter_modules([obj_dir]):
        module = importlib.import_module(f"{__name__}.{module_name}")
        for _, obj in inspect.getmembers(module, inspect.isfunction):
            if obj.__module__.startswith(__name__):
                res.append(obj)
    print(res)
    return res

ALL_TOOLS = load_all_tools()