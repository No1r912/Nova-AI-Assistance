"""Microphone recording for Nova voice mode."""

from pathlib import Path
import tempfile

import numpy as np
import scipy.io.wavfile as wav
import sounddevice as sd

from core.settings import get as get_setting


def record_audio():
    """Record from the default microphone unless one is configured in settings."""
    sample_rate = int(get_setting("audio.sample_rate", 16000))
    duration = float(get_setting("audio.record_seconds", 8))
    device = get_setting("audio.input_device", None)

    if sample_rate < 8_000 or duration <= 0 or duration > 120:
        raise ValueError("Audio settings must use a sample rate of at least 8000 Hz and 1–120 seconds.")

    print("Recording...")
    try:
        audio = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype="int16",
            device=device,
        )
        sd.wait()
        audio = np.asarray(audio, dtype=np.int16).reshape(-1)

        if not len(audio) or np.max(np.abs(audio.astype(np.int32))) < 100:
            print("Audio signal is too low.")
            return None

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as file:
            output_path = Path(file.name)
        wav.write(output_path, sample_rate, audio)
        return str(output_path)
    except Exception as error:
        print(f"Recording error: {error}")
        return None
