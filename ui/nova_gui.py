"""Modern Tkinter desktop interface for Nova."""

import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import scrolledtext

from core.config import AI_NAME
from core.conversation import clear_history, respond
from core.logger import error, info
from voice.speak import speak


BACKGROUND = "#0b1020"
SURFACE = "#121a2c"
SURFACE_RAISED = "#19233a"
INPUT = "#0f1729"
TEXT = "#f4f7ff"
MUTED = "#a6b1c7"
ACCENT = "#7c5cff"
ACCENT_HOVER = "#9279ff"
USER_COLOR = "#a8c5ff"
NOVA_COLOR = "#7ee7c5"
BORDER = "#2a3856"


class NovaApp:
    """Responsive, keyboard-first interface for the local assistant."""

    def __init__(self, root):
        self.root = root
        self.root.title(f"{AI_NAME} — Local AI Assistant")
        self.root.geometry("1040x720")
        self.root.minsize(760, 560)
        self.root.configure(bg=BACKGROUND)
        self.root.option_add("*Font", ("Segoe UI", 10))
        icon_path = Path(__file__).resolve().parent.parent / "assets" / "nova.ico"
        if icon_path.exists():
            self.root.iconbitmap(default=str(icon_path))

        self.messages = queue.Queue()
        self.working = False
        self.speak_replies = tk.BooleanVar(value=False)
        self._build()
        self._write("Nova", "Ready when you are. Ask anything, or type /help for Nova's controls.")
        self.root.after(75, self._read_queue)
        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)
        self.root.after_idle(self.composer.focus_set)

    def _button(self, parent, text, command, *, primary=False, width=None):
        color = ACCENT if primary else SURFACE_RAISED
        active = ACCENT_HOVER if primary else "#253351"
        return tk.Button(
            parent,
            text=text,
            command=command,
            relief="flat",
            borderwidth=0,
            bg=color,
            fg="white" if primary else TEXT,
            activebackground=active,
            activeforeground="white",
            cursor="hand2",
            font=("Segoe UI Semibold", 10),
            padx=14,
            pady=9,
            width=width,
        )

    def _build(self):
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        header = tk.Frame(self.root, bg=BACKGROUND, padx=24, pady=16)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(1, weight=1)
        tk.Label(header, text=f"{AI_NAME}  ✦", font=("Segoe UI Semibold", 22), bg=BACKGROUND, fg=TEXT).grid(row=0, column=0, sticky="w")
        tk.Label(header, text="LOCAL AI  •  PRIVATE BY DEFAULT", font=("Segoe UI Semibold", 9), bg=BACKGROUND, fg=MUTED).grid(row=0, column=1, sticky="w", padx=16)
        self._button(header, "Clear chat", self._clear).grid(row=0, column=2, sticky="e")

        workspace = tk.Frame(self.root, bg=BACKGROUND, padx=20)
        workspace.grid(row=1, column=0, sticky="nsew")
        workspace.grid_rowconfigure(0, weight=1)
        workspace.grid_columnconfigure(1, weight=1)

        sidebar = tk.Frame(workspace, bg=SURFACE, width=190, padx=14, pady=16, highlightthickness=1, highlightbackground=BORDER)
        sidebar.grid(row=0, column=0, sticky="nsw", padx=(0, 14))
        sidebar.grid_propagate(False)
        tk.Label(sidebar, text="SESSION", bg=SURFACE, fg=MUTED, font=("Segoe UI Semibold", 9)).pack(anchor="w")
        tk.Label(sidebar, text="New conversation", bg=SURFACE, fg=TEXT, font=("Segoe UI Semibold", 11), pady=12).pack(anchor="w")
        tk.Frame(sidebar, height=1, bg=BORDER).pack(fill="x", pady=(2, 16))
        tk.Label(sidebar, text="QUICK START", bg=SURFACE, fg=MUTED, font=("Segoe UI Semibold", 9)).pack(anchor="w")
        for label in ("/help", "/model gemma3:4b", "/memory", "/system"):
            quick = tk.Button(sidebar, text=label, command=lambda value=label: self._insert_quick(value), anchor="w", relief="flat", borderwidth=0, bg=SURFACE, fg=USER_COLOR, activebackground=SURFACE_RAISED, activeforeground=TEXT, padx=8, pady=7, cursor="hand2")
            quick.pack(fill="x", pady=2)
        tk.Frame(sidebar, bg=SURFACE).pack(expand=True, fill="both")
        tk.Checkbutton(sidebar, text="Speak replies", variable=self.speak_replies, bg=SURFACE, fg=MUTED, selectcolor=SURFACE, activebackground=SURFACE, activeforeground=TEXT, font=("Segoe UI", 9), highlightthickness=0).pack(anchor="w")

        panel = tk.Frame(workspace, bg=SURFACE, padx=1, pady=1, highlightthickness=1, highlightbackground=BORDER)
        panel.grid(row=0, column=1, sticky="nsew")
        panel.grid_rowconfigure(0, weight=1)
        panel.grid_columnconfigure(0, weight=1)
        self.chat = scrolledtext.ScrolledText(panel, wrap="word", state="disabled", borderwidth=0, relief="flat", font=("Segoe UI", 11), bg=SURFACE, fg=TEXT, insertbackground=TEXT, padx=24, pady=22, spacing1=4, spacing3=12)
        self.chat.grid(row=0, column=0, sticky="nsew")
        self.chat.tag_configure("user", foreground=USER_COLOR, font=("Segoe UI Semibold", 10))
        self.chat.tag_configure("nova", foreground=NOVA_COLOR, font=("Segoe UI Semibold", 10))
        self.chat.tag_configure("body", foreground=TEXT, spacing3=16)

        composer_panel = tk.Frame(self.root, bg=BACKGROUND, padx=20)
        composer_panel.grid(row=2, column=0, sticky="ew", pady=(14, 8))
        composer_panel.grid_columnconfigure(0, weight=1)
        composer = tk.Frame(composer_panel, bg=INPUT, padx=14, pady=10, highlightthickness=1, highlightbackground=ACCENT)
        composer.grid(row=0, column=0, sticky="ew")
        composer.grid_columnconfigure(0, weight=1)
        self.composer = tk.Text(composer, height=3, wrap="word", borderwidth=0, relief="flat", font=("Segoe UI", 11), bg=INPUT, fg=TEXT, insertbackground=TEXT, padx=3, pady=2, undo=True)
        self.composer.grid(row=0, column=0, sticky="ew", padx=(0, 12))
        self.composer.bind("<Return>", self._send_if_not_shift)
        self.composer.bind("<Control-Return>", self._send)
        self.send_button = self._button(composer, "Send  ↵", self._send, primary=True)
        self.send_button.grid(row=0, column=1, sticky="ns")

        footer = tk.Frame(self.root, bg=BACKGROUND, padx=24)
        footer.grid(row=3, column=0, sticky="ew", pady=(0, 12))
        self.status = tk.Label(footer, text="●  Ready", anchor="w", bg=BACKGROUND, fg=NOVA_COLOR, font=("Segoe UI", 9))
        self.status.pack(side="left")
        tk.Label(footer, text="Enter to send • Shift+Enter for a new line", bg=BACKGROUND, fg=MUTED, font=("Segoe UI", 9)).pack(side="right")

    def _insert_quick(self, command):
        if self.working:
            return
        self.composer.delete("1.0", "end")
        self.composer.insert("1.0", command)
        self.composer.focus_set()

    def _write(self, speaker, text):
        tag = "user" if speaker == "You" else "nova"
        self.chat.configure(state="normal")
        self.chat.insert("end", f"{speaker.upper()}\n", tag)
        self.chat.insert("end", f"{text.strip()}\n\n", "body")
        self.chat.configure(state="disabled")
        self.chat.see("end")

    def _send_if_not_shift(self, event):
        if event.state & 0x0001:
            return None
        self._send()
        return "break"

    def _send(self, event=None):
        if self.working:
            return "break" if event else None
        message = self.composer.get("1.0", "end-1c").strip()
        if not message:
            self.composer.focus_set()
            return "break" if event else None
        self.composer.delete("1.0", "end")
        self._write("You", message)
        self.working = True
        self.send_button.configure(state="disabled", text="Thinking…")
        self.status.configure(text="●  Nova is thinking", fg=USER_COLOR)
        threading.Thread(target=self._reply, args=(message, self.speak_replies.get()), daemon=True).start()
        return "break" if event else None

    def _reply(self, message, should_speak):
        try:
            answer = respond(message)
            self.messages.put(("answer", answer))
            if should_speak:
                threading.Thread(target=self._speak_reply, args=(answer,), daemon=True).start()
        except Exception as exc:
            error(f"GUI response error: {exc}")
            self.messages.put(("error", "Sorry, something went wrong while preparing that reply."))

    def _speak_reply(self, answer):
        if not speak(answer):
            self.messages.put(("speech_error", "Speech could not be played. Check data/logs/nova.log for details."))

    def _read_queue(self):
        try:
            while True:
                kind, content = self.messages.get_nowait()
                if kind == "speech_error":
                    self.status.configure(text=content, fg=MUTED)
                    continue
                self._write(AI_NAME, content)
                self.working = False
                self.send_button.configure(state="normal", text="Send  ↵")
                self.status.configure(text="●  Ready" if kind == "answer" else "●  Reply failed", fg=NOVA_COLOR if kind == "answer" else "#ff9ba7")
                self.composer.focus_set()
        except queue.Empty:
            pass
        self.root.after(75, self._read_queue)

    def _clear(self):
        if self.working:
            return
        clear_history()
        self.chat.configure(state="normal")
        self.chat.delete("1.0", "end")
        self.chat.configure(state="disabled")
        self._write(AI_NAME, "Conversation cleared. Saved memory is unchanged.")
        self.status.configure(text="●  Ready", fg=NOVA_COLOR)
        self.composer.focus_set()


def run():
    info(f"{AI_NAME} GUI starting...")
    root = tk.Tk()
    NovaApp(root)
    root.mainloop()
