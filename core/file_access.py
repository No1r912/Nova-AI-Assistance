"""Read-only file browsing for the local system drive."""

from pathlib import Path
import ctypes
import os

from charset_normalizer import from_bytes


TEXT_EXTENSIONS = {
    ".txt", ".md", ".py", ".json", ".csv", ".tsv", ".log", ".ini", ".cfg",
    ".yaml", ".yml", ".xml", ".html", ".css", ".js", ".ts", ".jsx", ".tsx",
    ".java", ".c", ".cpp", ".h", ".cs", ".ps1", ".bat", ".sh", ".sql", ".rtf",
    ".toml", ".properties", ".env", ".srt", ".vtt", ".tex", ".rst",
}


def _resolve(value=""):
    path = Path(value.strip().strip('"')).expanduser() if value else Path.cwd()
    if not path.is_absolute():
        path = Path.cwd() / path
    return path.resolve()


def _display(path):
    return str(path)


def _search_roots():
    """Return every mounted drive Nova can search on this computer."""
    if os.name != "nt":
        return [Path("/")]
    bitmask = ctypes.windll.kernel32.GetLogicalDrives()
    return [Path(f"{letter}:/") for index, letter in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ") if bitmask & (1 << index)]


def list_files(value=""):
    """List a folder's direct contents without changing anything."""
    path = _resolve(value)
    if not path.is_dir():
        raise ValueError(f"Folder not found: {path}")
    try:
        entries = sorted(path.iterdir(), key=lambda item: (not item.is_dir(), item.name.lower()))
    except PermissionError as exc:
        raise ValueError(f"Permission denied: {path}") from exc

    lines = [f"Folder: {_display(path)}"]
    for item in entries:
        try:
            suffix = "/" if item.is_dir() else ""
            size = "" if item.is_dir() else f" ({item.stat().st_size:,} bytes)"
            lines.append(f"{item.name}{suffix}{size}")
        except OSError:
            lines.append(f"{item.name} (unavailable)")
    return "\n".join(lines)


def find_files(query):
    """Find filenames across every accessible mounted drive."""
    query = query.strip()
    if not query:
        raise ValueError("Usage: /find <part of a filename>")
    matches = []
    for root in _search_roots():
        for directory, folders, filenames in os.walk(root, onerror=lambda _: None):
            for name in folders + filenames:
                if query.casefold() in name.casefold():
                    item = Path(directory) / name
                    matches.append(_display(item) + ("/" if item.is_dir() else ""))
    return "\n".join([f"Matches for '{query}':", *matches]) if matches else f"No files found matching '{query}'."


def _decode_text(raw, path):
    """Decode a text file while rejecting clearly binary content."""
    if b"\x00" in raw[:8_192] and not raw.startswith((b"\xff\xfe", b"\xfe\xff", b"\xff\xfe\x00\x00", b"\x00\x00\xfe\xff")):
        raise ValueError(f"'{path.name}' appears to be a binary file, not readable text.")

    for encoding in ("utf-8-sig", "utf-16", "utf-32"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            pass

    match = from_bytes(raw).best()
    if match is None:
        raise ValueError(f"I couldn't determine the text encoding for '{path.name}'.")
    return str(match)


def read_file(value):
    """Read a user-selected file without an artificial size or output limit."""
    path = _resolve(value)
    if not path.is_file():
        raise ValueError(f"File not found: {path}")
    try:
        raw = path.read_bytes()
    except PermissionError as exc:
        raise ValueError(f"Permission denied: {path}") from exc

    if b"\x00" in raw[:8_192] and not raw.startswith((b"\xff\xfe", b"\xfe\xff", b"\xff\xfe\x00\x00", b"\x00\x00\xfe\xff")):
        preview = raw[:256].hex(" ")
        return f"File: {_display(path)}\n\nBinary file detected ({len(raw):,} bytes). First 256 bytes (hex):\n{preview}"

    content = _decode_text(raw, path)
    return f"File: {_display(path)}\n\n{content}"
