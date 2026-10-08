"""Explicit, local-only controls for a Nova conversation."""

import json

from core import memory as memory_manager


HELP_TEXT = """Nova commands:
  /help                 Show this guide
  /clear                Start a fresh conversation
  /history              Show recent conversation turns
  /memory               Show stored long-term memory
  /forget <fact>        Remove a saved important fact
  /forget all           Remove all stored long-term memory
  /model <name>         Use a different installed Ollama model
  /remember <fact>      Save an important fact
  /apps, /open <app>    App launcher and supported-app list
  /search <query>       Search DuckDuckGo in the default browser
  /web <query>          Search the public web and return results in Nova
  /calc <expression>    Safely calculate basic arithmetic
  /time                 Show local time
  /analyze <file>       Analyze CSV, TSV, or JSON in the Nova folder
  /chart <file> [x] [y] Create and open a chart from a local dataset
  /system               Show basic system and disk status
  /files [folder]       List folders or files at any accessible path
  /find <name>          Find a file by name on accessible drives
  /read <file>          Read a file at any accessible path
  /exit                 Leave text mode"""


def handle(command, history):
    """Return a response for a command, or None when it is not a command."""
    command = command.strip()
    if not command.startswith("/"):
        return None

    normalized = command.lower()
    if normalized == "/help":
        return HELP_TEXT
    if normalized == "/clear":
        history.clear()
        return "Conversation cleared. Your saved memory is unchanged."
    if normalized == "/history":
        if not history:
            return "There is no conversation history yet."
        turns = history[-5:]
        return "\n\n".join(
            f"You: {item['user']}\nNova: {item['assistant']}" for item in turns
        )
    if normalized == "/memory":
        data = memory_manager.all()
        if not data:
            return "No long-term memory is saved yet."
        return "Saved memory:\n" + json.dumps(data, indent=2, ensure_ascii=False)
    if normalized == "/forget all":
        memory_manager.clear_all()
        return "All long-term memory has been removed."
    if normalized.startswith("/forget "):
        fact = command[8:].strip()
        if not fact:
            return "Usage: /forget <saved fact>, or /forget all"
        if memory_manager.remove_important_fact(fact):
            return "Okay, I forgot that."
        return "I couldn't find that exact saved fact. Try /memory to check it."
    if normalized.startswith("/remember "):
        fact = command[10:].strip()
        if not fact:
            return "Usage: /remember <fact>"
        memory_manager.add_important_fact(fact)
        return "I'll remember that."
    if normalized.startswith("/model "):
        model = command[7:].strip()
        if not model:
            return "Usage: /model <installed-ollama-model>"
        from core.settings import set as save_setting
        save_setting("ai.model", model)
        return f"Model changed to {model} for new replies."
    if normalized in {"/apps", "/time", "/system", "/files"} or normalized.startswith(("/open ", "/search ", "/web ", "/calc ", "/analyze ", "/chart ", "/files ", "/find ", "/read ")):
        return None
    return "Unknown command. Type /help to see available controls."
