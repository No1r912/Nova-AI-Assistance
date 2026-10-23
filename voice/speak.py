"""Reliable Windows text-to-speech with Piper and SAPI backends."""

from pathlib import Path
import base64
import os
import shutil
import subprocess
import tempfile
import unicodedata

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
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as file:
            wav_path = file.name
        result = subprocess.run(
            [piper, "--model", str(PIPER_MODEL), "--output_file", wav_path],
            # Piper's executable often inherits a legacy Windows code page.
            # Sending UTF-8 bytes avoids failing on emoji and non-English text.
            input=text.encode("utf-8"),
            capture_output=True,
            check=True,
            timeout=120,
        )
        if not os.path.exists(wav_path) or os.path.getsize(wav_path) == 0:
            detail = result.stderr.decode("utf-8", errors="replace").strip()
            raise RuntimeError(detail or "Piper did not create an audio file.")
        # winsound ships with Windows Python, unlike sounddevice/soundfile.
        # This makes the bundled Piper voice work immediately after setup.
        import winsound
        winsound.PlaySound(wav_path, winsound.SND_FILENAME)
        return True
    except Exception as exc:
        error(f"Piper speech failed: {exc}")
        return False
    finally:
        if wav_path and os.path.exists(wav_path):
            os.remove(wav_path)


def _speak_with_windows_sapi(text):
    """Use Windows' built-in speech engine; no downloaded voice is required."""
    encoded_text = base64.b64encode(text.encode("utf-8")).decode("ascii")
    script = (
        f"$bytes = [Convert]::FromBase64String('{encoded_text}'); "
        "$text = [Text.Encoding]::UTF8.GetString($bytes); "
        "Add-Type -AssemblyName System.Speech; "
        "$voice = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
        "$voice.Rate = 1; $voice.Speak($text);"
    )
    encoded_script = base64.b64encode(script.encode("utf-16le")).decode("ascii")
    try:
        result = subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-EncodedCommand", encoded_script],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode:
            details = (result.stderr or result.stdout).strip()
            raise RuntimeError(details or f"PowerShell exited with code {result.returncode}.")
        return True
    except Exception as exc:
        error(f"Windows SAPI speech failed: {exc}")
        return False


def _fallback_speech_text(text):
    """Keep a reply speakable if a Windows voice rejects emoji or a script."""
    text = unicodedata.normalize("NFKD", text)
    # Windows' built-in English voices can reject unsupported scripts and emoji.
    # Keep basic punctuation so the remaining message sounds natural.
    return "".join(char for char in text if ord(char) < 128).strip()


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
    fallback = _fallback_speech_text(text)
    if fallback and fallback != text and _speak_with_windows_sapi(fallback):
        info("Reply speech completed with Windows SAPI fallback text.")
        return True
    error("Speech unavailable: install Piper or enable Windows Speech components.")
    return False
