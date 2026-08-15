import stt
import threading

import context as context

import dashboard.server as dashboard

from agent import _runner, SESSION_ID, USER_ID
from google.genai.types import Content, Part

import asyncio

def handle_command(prompt: str, silent: bool = False, save_history: bool= True):
    stt.set_status("thinking")

    # add memory later ( add on to prompt maybe? )
    message = Content(
        role="user",
        parts=[
            Part(text=prompt)
        ]
    )

    final_reply = ""

    async def run():
        nonlocal final_reply
        async for event in _runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=message):
            tool_responses = event.get_function_responses()
            if tool_responses:
                for tr in tool_responses:
                    dashboard.push_event(
                        tr.name,
                        tr.response['result'],
                        f"Command: {prompt}",
                    )

            if event.is_final_response():
                final_reply = event.content.parts[0].text

    asyncio.run(run())

    # add to conversation history

    if not silent:
        dashboard.push_event("reply", final_reply, "")

    stt.set_status("muted" if not dashboard.is_mic_enabled() else "listening")

    return final_reply


def on_transcript(transcript: str):
    is_command, command = context.is_command(transcript)
    print(f"\r\033[K> (transcribed) {transcript}")

    if not is_command:
        if command:
            print(f"\r\033[K> (command not found) {command}")

        return

    if command:
        resp = handle_command(command)
        print(resp)


def main():

    dashboard.start(open_browser=True, port=8000)

    print("voice assistant starting...")
    print("you can speak now!")
    print("press ctrl+c to stop.\n")

    stop_event = threading.Event()
    model = stt.STT()
    try:
        model.listen_and_transcribe(on_transcript, stop_event=stop_event)
    except KeyboardInterrupt:
        print("\nshutting down.")
        stop_event.set()

if __name__ == "__main__":
    main()