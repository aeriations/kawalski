AGENT_NAME="kawalski"
MODEL_NAME="qwen2.5:7b-instruct"
CHAT_URL="http://localhost:11434/api/chat"

SYSTEM_PROMPT = """
You are Kawalski, a voice assistant controlling a PC.
You have access to tools. If a tool is required, you MUST call it using the structured function call feature. Never output raw tool JSON or markdown code blocks into your message text directly.
TOOLS: When a request matches a tool, call it immediately. Never describe what you will do — just call it. After a tool runs, use its result to form your reply.

MEMORY: 
- Always check long-term memory first to personalise responses.
- Use remember() for stable preferences, project details, setup info, or anything useful later. Don't ask — just save it.
- Use search_memory() when past context might help. Don't ask first, just check.
- Use forget_memory() when asked to forget something.
- Never invent or alter information when saving. Store exactly what the user said.
- Don't store casual conversation, jokes, or one-off questions.

WEB:
- Use fetch_webpage() to read a specific URL. Only claim you read it if the tool succeeded.
- Use web_search() when asked to search the internet or research something. Only claim you searched if the tool was called.

If no tool matches, reply conversationally.
If LONG TERM MEMORY is provided below, use it naturally without announcing it.
""".strip()
FILTER_SYSTEM_PROMPT = f"""
You are a voice-command filter. Reply with JSON only, nothing else.

{{"is_command": true, "command": "..."}}
{{"is_command": false, "command": null}}

RULES:
- If "{AGENT_NAME}" is present → always true, strip the name from the command
- If speech is a clear instruction/question directed at an assistant → true
- If it sounds like background talk, casual conversation, or directed at someone else → false
- When uncertain → false

Examples:
"{AGENT_NAME} open discord" → {{"is_command": true, "command": "open discord"}}
"{AGENT_NAME} what do you think about Python?" → {{"is_command": true, "command": "what do you think about Python?"}}
"open spotify" → {{"is_command": true, "command": "open spotify"}}
"yeah I'll be there in a second" → {{"is_command": false, "command": null}}
"oh that's interesting" → {{"is_command": false, "command": null}}
"can you pass me that?" → {{"is_command": false, "command": null}}
""".strip()

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "open_app",
            "description": (
                "Open or launch an application on the PC by name. "
                "Use this when the user asks to open, start, or launch a program."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "app_name": {
                        "type": "string",
                        "description": "Name of the application, e.g. 'chrome', 'discord', 'notepad'",
                    }
                },
                "required": ["app_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "call_on_discord",
            "description": (
                "Start a Discord call with a named friend. "
                "Use this when the user asks to call someone on Discord."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The friend's Discord name to call",
                    }
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "go_to_discord_direct_messages",
            "description": (
                "Go to direct messages with someone and the user.. "
                "Use this when the user asks to go to someones direct messages (also known as dms) on discord. "
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The friend's Discord name to go to",
                    }
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "remember",
            "description": (
                "Save useful information about the user, their preferences, "
                "projects, setup, or other information likely to be useful later."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The information to remember."
                    },
                    "category": {
                        "type": "string",
                        "description": "Category such as Preference, Project, Setup, or General."
                    }
                },
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_memory",
            "description": (
                "Search the assistant's stored memories for information "
                "that may help answer the user's request."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "What information to search for."
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "forget_memory",
            "description": "Delete a stored memory when the user asks you to forget it.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The memory or phrase to remove."
                    }
                },
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_webpage",
            "description": (
                "Fetches a webpage and extracts its readable text. "
                "Use this when the user asks to read, analyse, or summarise "
                "a specific webpage."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL of the webpage to fetch."
                    }
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": (
                "Searches the internet for information. "
                "Use this when the user asks to search the web, "
                "find information online, research a topic, "
                "or find websites."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The user's web search query."
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return.",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "press_key",
            "description": (
                "Press a single keyboard key. Use for things like "
                "'press space', 'press escape', 'press f5', 'press enter'. "
                "Also use for media keys: play_pause, next_track, prev_track, "
                "volume_up, volume_down."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "Key name e.g. 'space', 'enter', 'f5', 'play_pause'"
                    }
                },
                "required": ["key"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "press_combo",
            "description": (
                "Press a keyboard shortcut combination. "
                "Use for things like 'ctrl c', 'ctrl shift s', 'alt f4', 'win d'. "
                "Pass keys as a list, modifiers first."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "keys": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of keys e.g. ['ctrl', 'c'] or ['ctrl', 'shift', 's']"
                    }
                },
                "required": ["keys"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "type_text",
            "description": (
                "Type a string of text as if typed on a keyboard. "
                "Use when the user wants to dictate text into an app."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text to type"
                    }
                },
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "focus_window",
            "description": (
                "Bring a window to the foreground and give it keyboard focus. "
                "ALWAYS call this before sending any keypresses to an app. "
                "For example, before pressing space in Spotify, call focus_window('Spotify') first."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": (
                            "Part of the window title to search for. "
                            "e.g. 'Spotify', 'Notepad', 'Discord'. "
                            "Does not need to be the full title."
                        )
                    }
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "skip_song",
            "description": (
                "Skip the current song playing using windows media control keys."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "previous_song",
            "description": (
                "Play the previous song playing using windows media control keys."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
            }
        }
    },
]