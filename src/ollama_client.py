import urllib.request
import urllib.error

import json

import config as config

def chat(messages, tools=None):
    payload = {
        "model": config.MODEL_NAME,
        "messages": messages,
        "stream": False,
    }
    if tools:
        payload["tools"] = tools

    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        config.CHAT_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=40) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw)
    except urllib.error.URLError:
        raise RuntimeError(f"Unable to connect to chat at url: {config.CHAT_URL}")