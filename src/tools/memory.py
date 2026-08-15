from pathlib import Path
from datetime import datetime


# project/
# ├── src/
# │   └── memory.py
# └── memory/
PROJECT_ROOT = Path(__file__).resolve().parent.parent
MEMORY_DIR = PROJECT_ROOT / "memory"

LONG_TERM_FILE = MEMORY_DIR / "long_term.md"
TEMPORARY_FILE = MEMORY_DIR / "temporary.md"


def _ensure_files():
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)

    if not LONG_TERM_FILE.exists():
        LONG_TERM_FILE.write_text(
            "# Long-Term Memory\n\n",
            encoding="utf-8"
        )

    if not TEMPORARY_FILE.exists():
        TEMPORARY_FILE.write_text(
            "# Temporary Memory\n\n",
            encoding="utf-8"
        )


def remember(text: str, category: str = "General"):
    _ensure_files()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    with LONG_TERM_FILE.open("a", encoding="utf-8") as f:
        f.write(
            f"## {category}\n"
            f"- {text} *(saved {timestamp})*\n\n"
        )

    return f"Remembered: {text}"


def remember_temporary(text: str, category: str = "General"):
    _ensure_files()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    with TEMPORARY_FILE.open("a", encoding="utf-8") as f:
        f.write(
            f"## {category}\n"
            f"- {text} *(saved {timestamp})*\n\n"
        )

    return f"Temporarily remembered: {text}"


def search_memory(query: str):
    _ensure_files()

    results = []

    for file in (LONG_TERM_FILE, TEMPORARY_FILE):
        content = file.read_text(encoding="utf-8")

        for line in content.splitlines():
            if query.lower() in line.lower():
                results.append(line)

    if not results:
        return "No matching memories found."

    return "\n".join(results)


def forget_memory(text: str):
    _ensure_files()

    removed = 0

    for file in (LONG_TERM_FILE, TEMPORARY_FILE):
        lines = file.read_text(encoding="utf-8").splitlines(keepends=True)

        new_lines = []

        for line in lines:
            if text.lower() in line.lower():
                removed += 1
            else:
                new_lines.append(line)

        file.write_text(
            "".join(new_lines),
            encoding="utf-8"
        )

    return f"Removed {removed} matching memory item(s)."