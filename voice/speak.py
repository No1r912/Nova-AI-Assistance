"""Reliable Windows text-to-speech with Piper and SAPI backends."""

from pathlib import Path
import os
import shutil
import subprocess
import tempfile

from core.logger import error, info


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PIPER_MODEL = PROJECT_ROOT / "en_US-lessac-medium.onnx"


def _speak_with_piper(text):
    """Speak using Piper when its executable and local voice are available."""
    piper = shutil.which("piper")
    if not piper or not PIPER_MODEL.is_file():
        return False

    wav_path = None
    try:
        import sounddevice as sd
        import soundfile as sf

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as file:
            wav_path = file.name
        result = subprocess.run(
            [piper, "--model", str(PIPER_MODEL), "--output_file", wav_path],
            input=text,
            text=True,
            capture_output=True,
            check=True,
            timeout=120,
        )
        if not os.path.exists(wav_path) or os.path.getsize(wav_path) == 0:
            raise RuntimeError(result.stderr.strip() or "Piper did not create an audio file.")
        audio, sample_rate = sf.read(wav_path)
        sd.play(audio, sample_rate)
        sd.wait()
        return True
    except Exception as exc:
        error(f"Piper speech failed: {exc}")
        return False
    finally:
        if wav_path and os.path.exists(wav_path):
            os.remove(wav_path)


def _speak_with_windows_sapi(text):
    """Use Windows' built-in speech engine; no downloaded voice is required."""
    script = (
        "Add-Type -AssemblyName System.Speech; "
        "$voice = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
        "$voice.Rate = 1; $voice.Speak($args[0]);"
    )
    try:
        subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script, text],
            check=True,
            capture_output=True,
            text=True,
            timeout=120,
        )
        return True
    except Exception as exc:
        error(f"Windows SAPI speech failed: {exc}")
        return False


def speak(text):
    """Speak text, preferring Piper and falling back to built-in Windows speech."""
    text = str(text).strip()
    if not text:
        return True
    if _speak_with_piper(text):
        info("Reply speech completed with Piper.")
        return True
    if _speak_with_windows_sapi(text):
        info("Reply speech completed with Windows SAPI.")
        return True
    error("Speech unavailable: install Piper or enable Windows Speech components.")
    return False
