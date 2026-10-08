from faster_whisper import WhisperModel

from core.config import (
    WHISPER_MODEL,
    WHISPER_DEVICE,
    WHISPER_COMPUTE_TYPE
)


# =========================
# Whisper Setup
# =========================

model = None


def get_model():
    """Load only when voice is used and fall back if GPU memory is unavailable."""
    global model
    if model is not None:
        return model

    try:
        model = WhisperModel(
            WHISPER_MODEL,
            device=WHISPER_DEVICE,
            compute_type=WHISPER_COMPUTE_TYPE,
        )
    except Exception as error:
        print(f"GPU Whisper unavailable ({error}); using CPU transcription.")
        model = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")
    return model


# =========================
# Transcribe Audio
# =========================

def transcribe(audio_file, language="en"):

    try:

        segments, info = get_model().transcribe(
            audio_file,
            language=language,
            beam_size=3,
            condition_on_previous_text=False,
            vad_filter=True,
        )


        text = ""


        for segment in segments:

            print(
                "Whisper:",
                segment.text
            )

            text += segment.text + " "


        return text.strip()


    except Exception as e:

        print(
            "Whisper error:",
            e
        )

        return None
