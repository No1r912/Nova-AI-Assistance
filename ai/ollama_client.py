"""Local Ollama integration for Nova."""

from core.config import (
    LLM_KEEP_ALIVE,
    LLM_MODEL,
    LLM_NUM_BATCH,
    LLM_NUM_CTX,
    LLM_NUM_PREDICT,
    OLLAMA_HOST,
)
from core.settings import get as get_setting


def generate(messages):
    """Send a conversation to the local Ollama server and return its text."""
    model = get_setting("ai.model", LLM_MODEL)
    try:
        # Keep the desktop shell available even if dependencies have not yet
        # been installed; the user gets a useful reply when they send a prompt.
        import ollama
        client = ollama.Client(host=OLLAMA_HOST)
        response = client.chat(
            model=model,
            messages=messages,
            keep_alive=LLM_KEEP_ALIVE,
            options={
                "temperature": get_setting("ai.temperature", 0.55),
                "top_p": 0.85,
                "num_ctx": LLM_NUM_CTX,
                "num_batch": LLM_NUM_BATCH,
                "num_predict": LLM_NUM_PREDICT,
            },
        )
    except Exception as error:
        raise RuntimeError(
            f"Could not reach Ollama at {OLLAMA_HOST}. Start Ollama, then run "
            f"'ollama pull {model}'. Original error: {error}"
        ) from error
    return response["message"]["content"]
