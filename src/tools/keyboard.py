import ctypes
import ctypes.wintypes
import time

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.wintypes.LONG),
        ("dy", ctypes.wintypes.LONG),
        ("mouseData", ctypes.wintypes.DWORD),
        ("dwFlags", ctypes.wintypes.DWORD),
        ("time", ctypes.wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_void_p),
    ]


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", ctypes.wintypes.DWORD),
        ("wParamL", ctypes.wintypes.WORD),
        ("wParamH", ctypes.wintypes.WORD),
    ]


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", ctypes.wintypes.WORD),
        ("wScan", ctypes.wintypes.WORD),
        ("dwFlags", ctypes.wintypes.DWORD),
        ("time", ctypes.wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_void_p),
    ]


class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _pack_ = 8
        _fields_ = [
            ("mi", MOUSEINPUT),
            ("ki", KEYBDINPUT),
            ("hi", HARDWAREINPUT)
        ]

    _anonymous_ = ("_input",)
    _fields_ = [
        ("type", ctypes.wintypes.DWORD),
        ("_input", _INPUT),
    ]

user32 = ctypes.windll.user32
user32.SendInput.argtypes = [ctypes.wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int]
user32.SendInput.restype = ctypes.wintypes.UINT

INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004

KEYS = {
    # letters
    **{c: ord(c.upper()) for c in "abcdefghijklmnopqrstuvwxyz"},
    # numbers
    **{str(n): ord(str(n)) for n in range(10)},
    # special keys
    "backtick":  0xC0,
    "space":     0x20,
    "enter":     0x0D,
    "single_quote": 0xDE,
    "escape":    0x1B,
    "tab":       0x09,
    "backspace": 0x08,
    "delete":    0x2E,
    "up":        0x26,
    "down":      0x28,
    "left":      0x25,
    "right":     0x27,
    "home":      0x24,
    "end":       0x23,
    "pageup":    0x21,
    "pagedown":  0x22,
    "f1":        0x70,
    "f2":        0x71,
    "f3":        0x72,
    "f4":        0x73,
    "f5":        0x74,
    "f6":        0x75,
    "f7":        0x76,
    "f8":        0x77,
    "f9":        0x78,
    "f10":       0x79,
    "f11":       0x7A,
    "f12":       0x7B,
    # modifiers
    "ctrl":      0x11,
    "shift":     0x10,
    "alt":       0x12,
    "win":       0x5B,
    # media keys
    "play_pause":    0xB3,
    "next_track":    0xB0,
    "prev_track":    0xB1,
    "volume_up":     0xAF,
    "volume_down":   0xAE,
    "volume_mute":   0xAD,
}

def _send_key_event(vk_code: int, key_up: bool) -> int:
    flags = KEYEVENTF_KEYUP if key_up else 0

    inp = INPUT()
    inp.type = INPUT_KEYBOARD
    inp.ki = KEYBDINPUT(wVk=vk_code, wScan=0, dwFlags=flags, time=0, dwExtraInfo=None)

    result = user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))
    return result


def press_key(key: str) -> str:
    key = key.lower().strip()
    vk = KEYS.get(key)
    #print(f"[debug] key='{key}' vk={hex(vk) if vk else None}")
    if vk is None:
        return f"Unknown key: '{key}'"

    result_down = _send_key_event(vk, key_up=False)
    #print(f"[debug] keydown result: {result_down}")
    time.sleep(0.05)
    result_up = _send_key_event(vk, key_up=True)
    #print(f"[debug] keyup result: {result_up}")

    return f"Pressed {key}."

def press_combo(*keys: str) -> str:
    if keys and isinstance(keys[0], list):
        keys = keys[0]
    keys = [k.lower().strip() for k in keys]

    vk_codes = [KEYS.get(k) for k in keys if KEYS.get(k) is not None]

    for vk in vk_codes:
        _send_key_event(vk, key_up=False)
        time.sleep(0.05)

    for vk in reversed(vk_codes):
        _send_key_event(vk, key_up=True)
        time.sleep(0.05)

    return f"Pressed {' + '.join(keys)}."


def focus_window(name: str) -> str:
    import pygetwindow as gw
    matches = gw.getWindowsWithTitle(name)
    if not matches:
        return f"No window found with title containing '{name}'."

    hwnd = matches[0]._hWnd

    ctypes.windll.user32.ShowWindow(hwnd, 9)
    ctypes.windll.user32.SetForegroundWindow(hwnd)
    time.sleep(0.8)

    return f"Focused window: {matches[0].title}"

def type_text(text: str, interval: float=0.0) -> str:
    for char in text:
        inp = INPUT()
        inp.type = INPUT_KEYBOARD
        inp.ki = KEYBDINPUT(wVk=0, wScan=ord(char), dwFlags=KEYEVENTF_UNICODE, time=0, dwExtraInfo=None)
        user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))
        time.sleep(0.02)

        inp.ki.dwFlags = KEYEVENTF_UNICODE | KEYEVENTF_KEYUP
        user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))
        time.sleep(0.02 + interval)

    return f"Typed: {text}"

if __name__ == "__main__":
    time.sleep(2)
    print(press_key("single_quote"))
    time.sleep(2)
    print(press_combo("ctrl", "single_quote"))