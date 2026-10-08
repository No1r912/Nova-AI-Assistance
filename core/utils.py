import os
import json
import tempfile
from datetime import datetime


# ==========================================================
# File Helpers
# ==========================================================

def load_json(path, default=None):
    """
    Load JSON file safely.
    """

    if not os.path.exists(path):
        return default

    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)

    except Exception as e:
        print(f"JSON load error: {e}")
        return default



def save_json(path, data):
    """
    Save JSON atomically so an interrupted write does not corrupt memory.
    """

    try:
        directory = os.path.dirname(path) or "."
        os.makedirs(directory, exist_ok=True)

        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=directory, delete=False
        ) as file:
            json.dump(
                data,
                file,
                indent=2,
                ensure_ascii=False
            )
            temporary_path = file.name

        os.replace(temporary_path, path)

    except Exception as e:
        print(f"JSON save error: {e}")



# ==========================================================
# Time Helpers
# ==========================================================

def get_time():
    """
    Returns current time.
    """

    return datetime.now().strftime("%H:%M:%S")



def get_date():
    """
    Returns current date.
    """

    return datetime.now().strftime("%Y-%m-%d")



# ==========================================================
# Text Helpers
# ==========================================================

def clean_text(text):
    """
    Removes unnecessary spaces.
    """

    return " ".join(text.strip().split())



def truncate(text, length=100):
    """
    Shortens long text.
    """

    if len(text) <= length:
        return text

    return text[:length] + "..."



# ==========================================================
# Debug
# ==========================================================

def debug(message):
    """
    Simple debug printer.
    """

    print(f"[DEBUG] {message}")
