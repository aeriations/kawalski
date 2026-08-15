import threading
import queue
import time

import sounddevice as sd
import numpy as np
import faster_whisper

import dashboard.server as dashboard

current_status = "listening"  # ← track current status
_status_lock = threading.Lock()

def set_status(s):
    with _status_lock:
        global current_status
        if s != current_status:  # ← only push if changed
            current_status = s
            dashboard.push_status(s)

SAMPLE_RATE = 16000
MODEL_SIZE = "small"
DEVICE = "cuda"
COMPUTE_TYPE = "float16"

SILENCE_THRESHOLD = 0.02
SILENCE_DURATION = 1.2

MIN_SPEECH_DURATION = 0.5
MAX_SPEECH_DURATION = 10.0

TRANSCRIPTION_CORRECTIONS = {
    "row blocks": "roblox",
    "row block": "roblox",
    "rowblocks": "roblox",
    "road blocks": "roblox",
    "roadblocks": "roblox",
    "disc cord": "discord",
    "opera gx": "opera gx",  # this one's usually fine
    "you tube": "youtube",
    "spot of fire": "spotify",  # whisper sometimes does this
}

class STT:
    def __init__(self):
        print("initializing STT...")
        self.model = faster_whisper.WhisperModel(MODEL_SIZE, device=DEVICE, compute_type=COMPUTE_TYPE)
        print("whisper model initialized!\n")

    def transcribe(self, audio: np.ndarray) -> str:
        segments, _ = self.model.transcribe(
            audio,
            language='en',
            vad_filter=True,
            vad_parameters={
                "min_silence_duration_ms": 500,
                "speech_pad_ms": 200,
            },
            beam_size=5
        )

        text =  " ".join(segment.text.strip() for segment in segments)

        return text.strip()

    @staticmethod
    def apply_corrections(text: str) -> str:
        """Fix known whisper mishearings of app/brand names."""
        lower = text.lower()
        for wrong, right in TRANSCRIPTION_CORRECTIONS.items():
            lower = lower.replace(wrong, right)
        return lower

    def _flush_buffer(self, buffer, callback):
        print(f"\r\033[K(flushing buffer & transcribing...)", end="", flush=True)
        clip = np.concatenate(buffer)
        duration = len(clip) / SAMPLE_RATE

        if duration < MIN_SPEECH_DURATION:
            return

        threading.Thread(
            target=self._transcribe_and_callback,
            args=(clip, callback),
            daemon=True
        ).start()

    def _transcribe_and_callback(self, clip, callback):
        set_status("transcribing")
        transcription = self.transcribe(clip)
        if transcription:
            transcription = self.apply_corrections(transcription)
            dashboard.push_transcript(transcription)
            callback(transcription)
        else:
            set_status("listening")

    def listen_and_transcribe(self, callback, stop_event: threading.Event = None):
        audio_queue = queue.Queue()

        def audio_callback(in_data, frame_count, time_info, status):
            chunk = in_data[:, 0].copy()
            audio_queue.put(chunk)
            if dashboard.is_mic_enabled():
                e = float(np.sqrt(np.mean(chunk ** 2)))
                dashboard.push_energy(e)

        def proc_loop():
            buffer = []
            silence_start = None
            recording = False

            while not (stop_event and stop_event.is_set()):
                try:
                    chunk = audio_queue.get(timeout=0.5)
                    #print(f"got chunk size={len(chunk)} energy={np.sqrt(np.mean(chunk ** 2)):.6f}", flush=True)
                except queue.Empty:
                    continue

                if not dashboard.is_mic_enabled():
                    buffer = []
                    recording = False
                    silence_start = None
                    continue

                try:
                    energy = np.sqrt(np.mean(chunk ** 2))
                    print(f"energy: {energy:.4f}", end="\r", flush=True)

                    is_speech = energy > SILENCE_THRESHOLD

                    if is_speech:
                        if not recording:
                            recording = True
                            silence_start = None
                            buffer = []
                            set_status("recording")

                        buffer.append(chunk)
                        silence_start = None

                        total_duration = len(buffer) * (len(chunk) / SAMPLE_RATE)
                        if total_duration >= MAX_SPEECH_DURATION:
                            self._flush_buffer(buffer, callback)
                            buffer = []
                            recording = False
                            set_status("listening")

                    else:
                        if recording:
                            if silence_start is None:
                                silence_start = time.time()
                            elapsed = time.time() - silence_start
                            buffer.append(chunk)

                            if elapsed >= SILENCE_DURATION:
                                self._flush_buffer(buffer, callback)
                                buffer = []
                                recording = False
                                silence_start = None
                                set_status("listening")

                    print(f"\r\033[K>energy: {energy:.4f}", end="", flush=True)
                except Exception as e:
                    print(f"[ERROR]: {e}")
                    import traceback
                    traceback.print_exc()
                    break

        process_thread = threading.Thread(target=proc_loop, daemon=True)
        process_thread.start()

        with sd.InputStream(
                samplerate=SAMPLE_RATE,
                channels=1,
                dtype="float32",
                blocksize=int(0.1 * SAMPLE_RATE),
                callback=audio_callback,
        ):
            try:
                while not (stop_event and stop_event.is_set()):
                    time.sleep(0.1)
            except KeyboardInterrupt:
                print("\nstopped.")


if __name__ == "__main__":
    def on_transcript(text):
        print(f"\r\033[K> (transcribed) {text}\n")

    stt = STT()
    stt.listen_and_transcribe(on_transcript)