from __future__ import annotations

import platform
import shutil
import subprocess
import threading
import time
from collections.abc import Callable
from pathlib import Path

import click
import numpy as np
import sounddevice as sd
from openai import OpenAI
from scipy.io import wavfile


def _with_retries(
    operation_name: str,
    func: Callable[[], str] | Callable[[], None],
    max_attempts: int = 3,
    base_delay_seconds: float = 0.8,
) -> str | None:
    """Run a callable with simple exponential backoff and jitter; return string if provided."""
    last_exception: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            result = func()
            # type: ignore[return-value]
            return result  # can be None or str depending on func
        except Exception as exc:  # noqa: BLE001
            last_exception = exc
            sleep_seconds = base_delay_seconds * (2 ** (attempt - 1)) + (0.1 * attempt)
            click.secho(
                f"{operation_name} failed (attempt {attempt}/{max_attempts}): {exc}",
                fg="yellow",
            )
            if attempt < max_attempts:
                time.sleep(sleep_seconds)
    if last_exception is not None:
        raise last_exception
    return None


def record_audio(output_wav_path: str, sample_rate_hz: int = 16000) -> None:
    """
    Record audio from the default microphone using Enter-to-start and Enter-to-stop.
    Audio is saved as a mono WAV file at the given sample rate.
    """
    click.secho("Press Enter to start recording, and Enter again to stop.", fg="blue")
    input()

    click.secho("\n🔴 Recording... Press Enter to stop.", fg="red")

    frames: list[np.ndarray] = []
    stop_event = threading.Event()

    def on_keyboard() -> None:
        input()
        stop_event.set()

    keyboard_thread = threading.Thread(target=on_keyboard, daemon=True)
    keyboard_thread.start()

    def audio_callback(
        indata: np.ndarray, frames_count: int, time_info: dict, status: sd.CallbackFlags
    ) -> None:  # noqa: ARG001
        # indata shape: (frames, channels)
        frames.append(indata.copy())

    with sd.InputStream(
        samplerate=sample_rate_hz,
        channels=1,
        dtype="float32",
        callback=audio_callback,
    ):
        while not stop_event.is_set():
            time.sleep(0.05)

    if not frames:
        raise RuntimeError("No audio captured from microphone.")

    audio_data = np.concatenate(frames, axis=0)
    audio_int16 = np.int16(np.clip(audio_data, -1.0, 1.0) * 32767)

    output_path = Path(output_wav_path)
    wavfile.write(output_path, sample_rate_hz, audio_int16)


def transcribe_audio(audio_wav_path: str, model_name: str = "whisper-1") -> str:
    """Transcribe a WAV file using OpenAI Whisper with retries and basic timing."""
    client = OpenAI()

    audio_path = Path(audio_wav_path)
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_wav_path}")

    def _transcribe() -> str:
        start_time = time.monotonic()
        with audio_path.open("rb") as audio_file:
            response = client.audio.transcriptions.create(
                model=model_name,
                file=audio_file,
            )
        duration_ms = int((time.monotonic() - start_time) * 1000)
        click.secho(f"STT complete in {duration_ms} ms", fg="white")
        return response.text or ""

    return str(_with_retries("Speech-to-Text", _transcribe))


def speak_text(
    text: str,
    model_name: str = "tts-1",
    voice_name: str = "alloy",
    playback_speed: float | None = None,
) -> None:
    """Convert text to speech using OpenAI TTS, optionally speed up playback, then play it.

    If playback_speed is provided and ffmpeg is available, we apply an atempo filter to
    the generated MP3 to speed up playback (pitch-preserving). If ffmpeg is not found
    or the speed is invalid, we fall back to normal speed.
    """
    if not text.strip():
        return

    client = OpenAI()

    def _synthesize_and_play() -> None:
        start_time = time.monotonic()
        # Use streaming response API when available to reduce memory spikes
        speech_file = Path.cwd() / f"tts_{int(time.time() * 1000)}.mp3"
        try:
            with client.audio.speech.with_streaming_response.create(
                model=model_name,
                voice=voice_name,
                input=text,
            ) as response:
                response.stream_to_file(speech_file)
            tts_ms = int((time.monotonic() - start_time) * 1000)
            click.secho(f"TTS synthesis in {tts_ms} ms", fg="white")

            # Optionally generate a speed-adjusted file using ffmpeg atempo
            file_to_play = speech_file
            try:
                if playback_speed and playback_speed > 0 and shutil.which("ffmpeg"):
                    # atempo supports 0.5..2.0, chain if outside range
                    speed_filters: list[str] = []
                    remaining = playback_speed
                    # Decompose into factors within [0.5, 2.0]
                    while remaining > 2.0:
                        speed_filters.append("atempo=2.0")
                        remaining /= 2.0
                    while remaining < 0.5:
                        speed_filters.append("atempo=0.5")
                        remaining *= 2.0
                    speed_filters.append(f"atempo={remaining}")
                    filter_arg = ",".join(speed_filters)

                    sped_file = (
                        Path.cwd()
                        / f"tts_{int(time.time() * 1000)}_x{playback_speed}.mp3"
                    )
                    subprocess.run(
                        [
                            "ffmpeg",
                            "-y",
                            "-i",
                            str(speech_file),
                            "-filter:a",
                            filter_arg,
                            "-vn",
                            str(sped_file),
                        ],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        check=True,
                    )
                    file_to_play = sped_file
            except Exception as e:
                click.secho(f"Playback speed adjustment skipped: {e}", fg="yellow")

            play_start = time.monotonic()
            played = False
            try:
                if platform.system() == "Darwin":
                    # Use native macOS player; -q 1 reduces console noise
                    subprocess.run(["afplay", "-q", "1", str(file_to_play)], check=True)
                    played = True
            except Exception:
                played = False

            if not played:
                # Fallback to playsound only if needed, import lazily to avoid AppKit requirement during import
                try:
                    from playsound import playsound as _playsound  # type: ignore

                    _playsound(str(file_to_play))
                    played = True
                except Exception as playback_exc:  # noqa: BLE001
                    raise playback_exc

            play_ms = int((time.monotonic() - play_start) * 1000)
            click.secho(f"Audio playback in {play_ms} ms", fg="white")
        finally:
            try:
                speech_file.unlink(missing_ok=True)
            except Exception:  # noqa: BLE001
                # If cleanup fails, continue without blocking the UX
                pass
            # Also attempt to remove any speed-adjusted artifact
            try:
                for p in Path.cwd().glob("tts_*_x*.mp3"):
                    p.unlink(missing_ok=True)
            except Exception:
                pass

    _with_retries("Text-to-Speech", _synthesize_and_play)
