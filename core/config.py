"""Central, portable defaults for Nova."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
MEMORY_FILE = DATA_DIR / "memory.json"
HISTORY_FILE = DATA_DIR / "history.json"
SETTINGS_FILE = DATA_DIR / "settings.json"


# ==========================================================
# AI
# ==========================================================

# MSI Thin GF63 12VE / RTX 4050 6 GB VRAM profile.
LLM_MODEL = "gemma3:4b"
LLM_NUM_CTX = 4096
LLM_NUM_BATCH = 128
LLM_NUM_PREDICT = 1024
LLM_KEEP_ALIVE = "2m"
# Explicit loopback endpoint avoids accidental proxy or stale OLLAMA_HOST settings.
OLLAMA_HOST = "http://127.0.0.1:11434"



# ==========================================================
# Speech Recognition
# ==========================================================

WHISPER_MODEL = "base"

WHISPER_DEVICE = "cuda"

# Reduced VRAM use compared with float16 while retaining GPU transcription.
WHISPER_COMPUTE_TYPE = "int8_float16"



# ==========================================================
# Text To Speech
# ==========================================================

TTS_SAMPLE_RATE = 24000



# ==========================================================
# Audio
# ==========================================================

SAMPLE_RATE = 16000

CHANNELS = 1

RECORD_DURATION = 5



# ==========================================================
# Wake Word
# ==========================================================

WAKEWORD_THRESHOLD = 0.5

WAKEWORD_SAMPLE_RATE = 16000



# ==========================================================
# Memory
# ==========================================================

MAX_HISTORY = 8

SUMMARY_INTERVAL = 20

MAX_SUMMARIES = 10



# ==========================================================
# Project
# ==========================================================

AI_NAME = "Nova"

VERSION = "1.0"



# ==========================================================
# Debug
# ==========================================================

DEBUG = True

# ==========================================================
# StyleTTS2
# ==========================================================
