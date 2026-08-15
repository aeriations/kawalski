import json
import queue
import threading
import time
import webbrowser
from datetime import datetime
from flask import Flask, Response, render_template, request

app = Flask(__name__, template_folder='templates', static_folder='static')

_event_history: list[dict] = []
_subscriber_queues: list[queue.Queue] = []
_lock: threading.Lock = threading.Lock()

def push_event(tool: str, result: str, detail: str="", success: bool=True):
    event = {
        "type": "event",
        "id": int(time.time() * 1000),
        "tool": tool,
        "result": result,
        "detail": detail,
        "success": success,
        "time": datetime.now().strftime("%H:%M"),
        "timestamp": datetime.now().isoformat(),
    }

    with _lock:
        _event_history.append(event)

        if len(_event_history) > 100:
            _event_history.pop(0)

        for q in _subscriber_queues:
            try:
                q.put_nowait(event)
            except queue.Full:
                pass

def _broadcast(data: dict):
    with _lock:
        for q in _subscriber_queues:
            try:
                q.put_nowait(data)
            except queue.Full:
                pass

def push_status(status: str):
    _broadcast({"type": "status", "status": status})

def push_energy(energy: float):
    _broadcast({"type": "energy", "energy": float(round(float(energy), 5))})

def push_transcript(text: str):
    _broadcast({"type": "transcript", "text": text})

def _sse_format(data: dict) -> str:
    return f"data: {json.dumps(data, default=lambda o: float(o) if hasattr(o, 'item') else str(o))}\n\n"
#-------------------

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stream')
def stream():
    subscriber_queue: queue.Queue = queue.Queue(maxsize=50)
    with _lock:
        _subscriber_queues.append(subscriber_queue)

    def generate():
        with _lock:
            history_snapshot = list(_event_history)

        for event in history_snapshot:
            yield _sse_format(event)

        try:
            while True:
                try:
                    event = subscriber_queue.get(timeout=15)
                    yield _sse_format(event)
                except queue.Empty:
                    yield ": keep_alive\n\n"
        except GeneratorExit:
            pass
        finally:
            with _lock:
                if subscriber_queue in _subscriber_queues:
                    _subscriber_queues.remove(subscriber_queue)

    return Response(
        generate(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )

@app.route('/history')
def history():
    with _lock:
        return {"events": list(_event_history)}

@app.route('/command', methods=['POST'])
def command():
    data = request.get_json()
    text = data.get('text', '').strip()
    if not text:
        return {"error": "empty"}, 400

    try:
        import sys, os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
        from main import handle_command
        result = handle_command(text, True)
        return {"result": result or "Done."}
    except Exception as e:
        return {"result": str(e)}, 500

_mic_enabled = True

def is_mic_enabled() -> bool:
    return _mic_enabled

@app.route('/mic', methods=['POST'])
def mic_toggle():
    global _mic_enabled
    data = request.get_json()
    _mic_enabled = bool(data.get('enabled', True))
    push_status('listening' if _mic_enabled else 'muted')
    print(f"Mic {'enabled' if _mic_enabled else 'muted'}")
    return {"enabled": _mic_enabled}

def start(open_browser: bool = True, port: int = 8080):
    def run():
        app.run(
            host='127.0.0.1',
            port=port,
            debug=False,
            use_reloader=False,
        )

    thread = threading.Thread(target=run, daemon=True)
    thread.start()

    time.sleep(1)
    if open_browser:
        webbrowser.open_new_tab(f"http://127.0.0.1:{port}/")

    print("dashboard running on http://127.0.0.1:8000!!!")

