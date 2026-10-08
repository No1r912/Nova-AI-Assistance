"""Small, transparent local tools that Nova may run only on direct requests."""

import ast
import json
import operator
import re
import subprocess
import webbrowser
import shlex
from datetime import datetime
from urllib.parse import quote_plus

from core.analytics import analyze_file, create_chart, system_status
from core.file_access import find_files, list_files, read_file
from core.web_search import search as web_search


APPS = {
    "notepad": ["notepad.exe"],
    "calculator": ["calc.exe"],
    "files": ["explorer.exe"],
    "explorer": ["explorer.exe"],
    "edge": ["msedge.exe"],
    "chrome": ["chrome.exe"],
    "vscode": ["code"],
    "visual studio code": ["code"],
}

_OPERATORS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod, ast.Pow: operator.pow, ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _calculate(expression):
    def evaluate(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in _OPERATORS:
            return _OPERATORS[type(node.op)](evaluate(node.left), evaluate(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in _OPERATORS:
            return _OPERATORS[type(node.op)](evaluate(node.operand))
        raise ValueError("Only basic arithmetic is allowed.")

    if len(expression) > 100:
        raise ValueError("That calculation is too long.")
    return evaluate(ast.parse(expression, mode="eval").body)


def help_text():
    return """Built-in tools:
  /apps                         List apps Nova can open
  /open <app>                   Open a supported app
  /search <query>               Search the web in your default browser
  /web <query>                  Search the web and return results in Nova
  /calc <expression>            Calculate basic arithmetic
  /time                         Show the local date and time
  /analyze <file>               Analyze CSV, TSV, or JSON inside Nova
  /chart <file> [x] [y]         Create and open a dataset chart
  /system                       Show basic system and disk status
  /files [folder]               List files and folders at any accessible path
  /find <name>                  Find files by name on accessible drives
  /read <file>                  Read a text file (common encodings supported)

You can also say “open Notepad”, “search for Python tutorials”, or “calculate 12 * 8”."""


def handle(request):
    """Return a direct tool result, or None for normal AI conversation."""
    text = request.strip()
    lower = text.lower()

    if lower in {"/apps", "what apps can you open", "which apps can you open"}:
        return "Nova can open: " + ", ".join(sorted(set(APPS))) + "."

    app_name = None
    for prefix in ("/open ", "open "):
        if lower.startswith(prefix):
            app_name = lower[len(prefix):].strip()
            break
    if app_name is not None:
        command = APPS.get(app_name)
        if not command:
            return f"I don't have a safe launcher configured for '{app_name}'. Type /apps to see supported apps."
        try:
            subprocess.Popen(command)
            return f"Opened {app_name}."
        except OSError as error:
            return f"I couldn't open {app_name}: {error}"

    query = None
    for prefix in ("/search ", "search for ", "search "):
        if lower.startswith(prefix):
            query = text[len(prefix):].strip()
            break
    if query is not None:
        if not query:
            return "Tell me what you want to search for."
        webbrowser.open(f"https://duckduckgo.com/?q={quote_plus(query)}")
        return f"Opened a search for: {query}"

    web_query = None
    for prefix in (
        "/web ", "web search for ", "search online for ", "search the web for ",
        "look online for ", "look up online ",
    ):
        if lower.startswith(prefix):
            web_query = text[len(prefix):].strip()
            break
    if web_query is not None:
        try:
            return web_search(web_query)
        except (OSError, ValueError) as error:
            return f"I couldn't search the web: {error}"

    if lower in {
        "can you access the internet", "can you access internet", "can you go online",
        "can you access online", "do you have internet access", "are you online",
    }:
        return "Yes. I can search the public web when you ask, for example: /web latest Python news"

    expression = None
    for prefix in ("/calc ", "calculate ", "calculator "):
        if lower.startswith(prefix):
            expression = text[len(prefix):].strip()
            break
    if expression is None and lower.startswith("what is "):
        candidate = text[8:].strip().rstrip("?= ")
        if re.fullmatch(r"[0-9\s+\-*/%.()]+", candidate):
            expression = candidate
    if expression is not None:
        try:
            return f"Result: {_calculate(expression)}"
        except (SyntaxError, ValueError, ZeroDivisionError) as error:
            return f"I couldn't calculate that: {error}"

    if lower in {"/time", "what time is it", "what is the time"}:
        return datetime.now().strftime("Local time: %A, %d %B %Y, %I:%M %p")

    file_folder = None
    if lower in {
        "/files", "show my files", "show all my files", "show all files",
        "list my files", "list all files", "look at my files", "look at all my files",
        "can you see my files", "can you see all my files", "can you see all files",
        "what files do i have", "what files can you see",
    }:
        file_folder = ""
    else:
        for prefix in ("/files ", "show files in ", "list files in ", "browse files in "):
            if lower.startswith(prefix):
                file_folder = text[len(prefix):].strip()
                break
    if file_folder is not None:
        try:
            return list_files(file_folder)
        except (OSError, ValueError) as error:
            return f"I couldn't list that folder: {error}"

    file_query = None
    for prefix in ("/find ", "find file ", "find files named ", "find files called "):
        if lower.startswith(prefix):
            file_query = text[len(prefix):].strip()
            break
    if file_query is not None:
        try:
            return find_files(file_query)
        except (OSError, ValueError) as error:
            return f"I couldn't search your files: {error}"

    file_to_read = None
    for prefix in ("/read ", "read file ", "read the file ", "read ", "show file ", "show the file "):
        if lower.startswith(prefix):
            file_to_read = text[len(prefix):].strip()
            break
    if file_to_read is not None:
        try:
            return read_file(file_to_read)
        except (OSError, ValueError) as error:
            return f"I couldn't read that file: {error}"

    if lower.startswith("/analyze "):
        file_path = text[9:].strip().strip('"')
        if not file_path:
            return "Usage: /analyze <CSV, TSV, or JSON file inside the Nova folder>"
        try:
            return analyze_file(file_path)
        except (OSError, ValueError, json.JSONDecodeError) as error:
            return f"I couldn't analyze that file: {error}"

    if lower.startswith("/chart "):
        try:
            arguments = [part.strip('"') for part in shlex.split(text[7:], posix=False)]
        except ValueError:
            return 'Usage: /chart "file.csv" [x column] [y column]'
        if not arguments or len(arguments) > 3:
            return 'Usage: /chart "file.csv" [x column] [y column]'
        try:
            chart_path = create_chart(*arguments)
            webbrowser.open(chart_path.as_uri())
            return f"Created and opened chart: {chart_path}"
        except (OSError, ValueError, json.JSONDecodeError) as error:
            return f"I couldn't create that chart: {error}"

    if lower in {"/system", "system status", "computer status"}:
        return system_status()

    return None
