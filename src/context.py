import ollama_client
import json
import asyncio
from config import FILTER_SYSTEM_PROMPT

def is_command(transcript: str) -> tuple[bool, str | None]:
    if not transcript or len(transcript) <= 2:
        return False, None

    messages = [
        {"role": "system", "content": FILTER_SYSTEM_PROMPT},
        {"role": "user", "content": transcript},
    ]

    resp = ollama_client.chat(messages)
    content = resp.get("message", {}).get("content", "").strip()

    if content.startswith("```"):
        lines = content.split("\n")
        content = "\n".join(
            line for line in lines
            if not line.startswith("```")
        ).strip()

    try:
        parsed = json.loads(content)
        command = parsed.get("command", "")
        is_command = bool(parsed.get("is_command", False))

        return is_command, command if is_command else None

    except json.JSONDecodeError:
        print(f"error decoding content, raw: {content}")
        return False, None