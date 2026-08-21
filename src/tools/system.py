import winreg
import subprocess
import os
from win32com.client import Dispatch

GUID_MAP = {
    # System & Program Files
    "{7C5A40EF-A0FB-4BFC-874A-C0F2E0B9FA8E}": os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"),
    "{6D809377-6AF0-444B-8957-A3773F02200E}": os.environ.get("ProgramFiles", r"C:\Program Files"),
    "{5CD7F5D0-0F11-47E0-8022-D81D9F36B57A}": os.environ.get("LOCALAPPDATA", r"C:\Users\%USERNAME%\AppData\Local"),

    # Newly added Windows System GUIDs
    "{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}": os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "System32"),
    "{D65231B0-B2F1-4857-A4CE-A8E7C6EA7D27}": os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "SysWOW64"),
    "{F38BF404-1D43-42F2-9305-67DE0B28FC23}": os.environ.get("SystemRoot", r"C:\Windows"),
}

def resolve_guid_path(path: str) -> str:
    """Replaces raw GUID strings with real file system paths."""
    for guid, real_dir in GUID_MAP.items():
        if guid in path:
            path = path.replace(guid, real_dir)
    return os.path.expandvars(path)

def _get_all_installed_programs():
    res = {}

    shell = Dispatch("Shell.Application")
    items = shell.NameSpace("shell:AppsFolder").Items()

    for item in items:
        res[item.Name] = item


    return res

LOOKUP_DICT = _get_all_installed_programs()

def open_app(name: str):
    """launches the specified app"""
    for key, item in LOOKUP_DICT.items():
        if name.lower().strip() == key.lower().strip():
            try:
                item.InvokeVerb("open")
                return f"Launched {name}"
            except Exception as e:
                print(e)

    for key, item in LOOKUP_DICT.items():
        if name.lower().strip() in key.lower().strip():
            try:
                item.InvokeVerb("open")
                return f"Launched {name}"
            except Exception as e:
                print(e)

    return "Could not launch app"

if __name__ == "__main__":
    print(LOOKUP_DICT)
    print(open_app("steam"))