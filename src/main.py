from pydantic_core.core_schema import is_instance_schema

import stt
import threading

import context as context

import dashboard.server as dashboard
import disc

from agent import _runner, SESSION_ID, USER_ID
from google.genai.types import Content, Part

import asyncio

_agent_lock = threading.Lock()

def get_response_result(response):
    if isinstance(response, dict):
        value = response.get("result", response) if "result" in response else response
        return value
    return str(response)

def handle_command(prompt: str, silent: bool = False, save_history: bool= True, additional_info: str= ""):
    stt.set_status("thinking")

    # add memory later ( add on to prompt maybe? )
    parts = [Part(text=prompt)]
    if additional_info:
        context_block = (
            f"[CONTEXT INFO / BACKGROUND DATA]\n"
            f"{additional_info}\n"
            f"[END CONTEXT INFO]"
        )
        parts.append(Part(text=context_block))

    message = Content(
        role="user",
        parts=parts
    )

    final_reply = ""

    async def run():
        nonlocal final_reply
        async for event in _runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=message):
            tool_responses = event.get_function_responses()
            if tool_responses:
                for tr in tool_responses:
                    print(get_response_result(tr.response))
                    dashboard.push_event(
                        tr.name,
                        get_response_result(tr.response),
                        f"Command: {prompt}",
                    )

            if event.is_final_response():
                final_reply = event.content.parts[0].text

    def worker_thread_target():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(run())
        finally:
            try:
                pending = asyncio.all_tasks(loop)
                if pending:
                    for task in pending:
                        task.cancel()

                    loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
            except Exception:
                pass

            loop.close()

    with _agent_lock:
        thread = threading.Thread(target=worker_thread_target)
        thread.start()
        thread.join()

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

    disc.client.handle_command = handle_command
    asyncio.run(disc.main())

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