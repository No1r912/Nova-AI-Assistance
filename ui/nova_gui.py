"""A friendly, app-style Tkinter home for Nova."""

import json
import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, scrolledtext, ttk

from core import memory as memory_manager
from core.config import AI_NAME
from core.conversation import clear_history, respond
from core.logger import error, info
from core.settings import get as get_setting
from core.settings import set as save_setting
from voice.speak import speak

P = {"bg": "#0A1020", "panel": "#111B31", "raised": "#172440", "input": "#0D1629", "text": "#F5F7FF", "muted": "#AAB6CE", "accent": "#8B6CFF", "accent_hover": "#A18AFF", "mint": "#73E4C1", "blue": "#A8C7FF", "border": "#293A60", "user": "#1B315A", "nova": "#172842"}
LANGUAGES = ("English", "Bahasa Melayu", "Bahasa Indonesia", "中文", "日本語")
PERSONALITIES = ("cheeky", "warm", "focused")
COPY = {
    "English": {"chat": "Chat", "memories": "Memories", "shortcuts": "Shortcuts", "settings": "Settings", "new": "New chat", "clear": "Clear chat", "send": "Send", "thinking": "Thinking…", "ready": "Ready", "copy": "Copy last reply", "local": "LOCAL • PRIVATE", "empty": "No saved memories yet."},
    "Bahasa Melayu": {"chat": "Sembang", "memories": "Memori", "shortcuts": "Pintasan", "settings": "Tetapan", "new": "Sembang baru", "clear": "Padam sembang", "send": "Hantar", "thinking": "Berfikir…", "ready": "Sedia", "copy": "Salin jawapan terakhir", "local": "TEMPATAN • PERIBADI", "empty": "Belum ada memori disimpan."},
    "Bahasa Indonesia": {"chat": "Chat", "memories": "Memori", "shortcuts": "Pintasan", "settings": "Pengaturan", "new": "Chat baru", "clear": "Hapus chat", "send": "Kirim", "thinking": "Berpikir…", "ready": "Siap", "copy": "Salin balasan terakhir", "local": "LOKAL • PRIBADI", "empty": "Belum ada memori tersimpan."},
    "中文": {"chat": "聊天", "memories": "记忆", "shortcuts": "快捷方式", "settings": "设置", "new": "新聊天", "clear": "清除聊天", "send": "发送", "thinking": "思考中…", "ready": "就绪", "copy": "复制上一条回复", "local": "本地 • 私密", "empty": "尚无已保存的记忆。"},
    "日本語": {"chat": "チャット", "memories": "メモリー", "shortcuts": "ショートカット", "settings": "設定", "new": "新しいチャット", "clear": "チャットを消去", "send": "送信", "thinking": "考え中…", "ready": "準備完了", "copy": "最後の返信をコピー", "local": "ローカル • プライベート", "empty": "保存されたメモリーはまだありません。"},
}


class NovaApp:
    """Responsive desktop shell: chat, memory, shortcuts, and settings."""

    def __init__(self, root):
        self.root = root
        self.root.title(f"{AI_NAME} — your local sidekick")
        self.root.geometry(get_setting("ui.geometry", "1120x760"))
        self.root.minsize(640, 500)
        self.root.configure(bg=P["bg"])
        self.root.option_add("*Font", ("Segoe UI", 10))
        self.messages, self.working, self.last_answer = queue.Queue(), False, ""
        self.active_view, self.views, self.nav_buttons = "chat", {}, {}
        self.language = tk.StringVar(value=get_setting("ui.language", "English"))
        self.speak_replies = tk.BooleanVar(value=get_setting("ui.speak_replies", False))
        self.status_text = tk.StringVar(value="●  Ready")
        icon = Path(__file__).resolve().parent.parent / "assets" / "nova.ico"
        if icon.exists(): self.root.iconbitmap(default=str(icon))
        self._build()
        self._show_view("chat")
        self.root.after(75, self._read_queue)
        self.root.protocol("WM_DELETE_WINDOW", self._close)
        self.root.bind_all("<Control-l>", lambda _event: self._new_chat())
        self.root.bind_all("<Control-k>", lambda _event: self._clear_composer())
        self.root.bind_all("<F1>", lambda _event: self.composer.focus_set())
        self.root.after_idle(self.composer.focus_set)

    def _t(self, key): return COPY.get(self.language.get(), COPY["English"])[key]

    def _button(self, parent, text, command, primary=False, small=False):
        return tk.Button(parent, text=text, command=command, relief="flat", borderwidth=0, bg=P["accent"] if primary else P["raised"], fg="white" if primary else P["text"], activebackground=P["accent_hover"] if primary else P["border"], activeforeground="white", cursor="hand2", font=("Segoe UI Semibold", 9 if small else 10), padx=10 if small else 13, pady=6 if small else 9)

    def _build(self):
        self.root.grid_rowconfigure(0, weight=1); self.root.grid_columnconfigure(1, weight=1)
        self._build_nav()
        main = tk.Frame(self.root, bg=P["bg"]); main.grid(row=0, column=1, sticky="nsew")
        main.grid_rowconfigure(1, weight=1); main.grid_columnconfigure(0, weight=1)
        header = tk.Frame(main, bg=P["bg"], padx=26, pady=18); header.grid(row=0, column=0, sticky="ew"); header.grid_columnconfigure(1, weight=1)
        self.page_title = tk.Label(header, text="Chat", bg=P["bg"], fg=P["text"], font=("Segoe UI Semibold", 21)); self.page_title.grid(row=0, column=0, sticky="w")
        self.privacy = tk.Label(header, text=self._t("local"), bg="#162846", fg=P["mint"], font=("Segoe UI Semibold", 8), padx=9, pady=5); self.privacy.grid(row=0, column=1, sticky="w", padx=12)
        self.header_action = self._button(header, self._t("clear"), self._new_chat, small=True); self.header_action.grid(row=0, column=2, sticky="e")
        self.content = tk.Frame(main, bg=P["bg"], padx=24, pady=10); self.content.grid(row=1, column=0, sticky="nsew"); self.content.grid_rowconfigure(0, weight=1); self.content.grid_columnconfigure(0, weight=1)
        self._build_chat(); self._build_memory(); self._build_shortcuts(); self._build_settings()
        footer = tk.Frame(main, bg=P["bg"], padx=26, pady=9); footer.grid(row=2, column=0, sticky="ew")
        tk.Label(footer, textvariable=self.status_text, bg=P["bg"], fg=P["mint"], font=("Segoe UI", 9)).pack(side="left")
        tk.Label(footer, text="Enter sends • Shift+Enter new line • Ctrl+L new chat", bg=P["bg"], fg=P["muted"], font=("Segoe UI", 9)).pack(side="right")

    def _build_nav(self):
        nav = tk.Frame(self.root, bg=P["panel"], width=194, padx=13, pady=18, highlightthickness=1, highlightbackground=P["border"]); nav.grid(row=0, column=0, sticky="nsw"); nav.grid_propagate(False)
        tk.Label(nav, text=f"{AI_NAME} ✦", bg=P["panel"], fg=P["text"], font=("Segoe UI Semibold", 22)).pack(anchor="w", padx=6)
        tk.Label(nav, text="YOUR LOCAL SIDEKICK", bg=P["panel"], fg=P["muted"], font=("Segoe UI Semibold", 8)).pack(anchor="w", padx=7, pady=(0, 18))
        self.new_button = self._button(nav, "+  New chat", self._new_chat, primary=True); self.new_button.pack(fill="x", padx=3, pady=(0, 18))
        for key, icon in (("chat", "◉"), ("memories", "◌"), ("shortcuts", "⌘"), ("settings", "⚙")):
            button = tk.Button(nav, text=f" {icon}   {key.title()}", anchor="w", command=lambda view=key: self._show_view(view), relief="flat", borderwidth=0, bg=P["panel"], fg=P["muted"], activebackground=P["raised"], activeforeground=P["text"], font=("Segoe UI Semibold", 10), padx=10, pady=10, cursor="hand2")
            button.pack(fill="x", pady=2); self.nav_buttons[key] = button
        tk.Frame(nav, bg=P["panel"]).pack(expand=True, fill="both")
        tk.Label(nav, text="PRIVATE ON THIS DEVICE", bg=P["panel"], fg=P["muted"], font=("Segoe UI Semibold", 8)).pack(anchor="w", padx=7)
        self.model_label = tk.Label(nav, text=f"Model: {get_setting('ai.model', 'gemma3:4b')}", bg=P["panel"], fg=P["blue"], font=("Segoe UI", 8), wraplength=155, justify="left"); self.model_label.pack(anchor="w", padx=7, pady=(3, 0))

    def _panel(self, name):
        frame = tk.Frame(self.content, bg=P["panel"], highlightthickness=1, highlightbackground=P["border"]); frame.grid(row=0, column=0, sticky="nsew"); self.views[name] = frame; return frame

    def _build_chat(self):
        panel = self._panel("chat"); panel.grid_rowconfigure(0, weight=1); panel.grid_columnconfigure(0, weight=1)
        self.chat = scrolledtext.ScrolledText(panel, wrap="word", state="disabled", borderwidth=0, relief="flat", font=("Segoe UI", 11), bg=P["panel"], fg=P["text"], insertbackground=P["text"], padx=24, pady=20, spacing1=3, spacing3=10); self.chat.grid(row=0, column=0, sticky="nsew")
        self.chat.tag_configure("user_name", foreground=P["blue"], font=("Segoe UI Semibold", 9)); self.chat.tag_configure("nova_name", foreground=P["mint"], font=("Segoe UI Semibold", 9))
        self.chat.tag_configure("user_body", foreground=P["text"], background=P["user"], lmargin1=12, lmargin2=12, rmargin=42, spacing1=6, spacing3=8); self.chat.tag_configure("nova_body", foreground=P["text"], background=P["nova"], lmargin1=12, lmargin2=12, rmargin=42, spacing1=6, spacing3=8)
        composer_panel = tk.Frame(panel, bg=P["panel"], padx=16, pady=12); composer_panel.grid(row=1, column=0, sticky="ew"); composer_panel.grid_columnconfigure(0, weight=1)
        composer = tk.Frame(composer_panel, bg=P["input"], padx=12, pady=9, highlightthickness=1, highlightbackground=P["border"]); composer.grid(row=0, column=0, sticky="ew"); composer.grid_columnconfigure(0, weight=1)
        self.composer = tk.Text(composer, height=3, wrap="word", borderwidth=0, relief="flat", font=("Segoe UI", 11), bg=P["input"], fg=P["text"], insertbackground=P["text"], padx=3, pady=2, undo=True); self.composer.grid(row=0, column=0, sticky="ew", padx=(0, 10)); self.composer.bind("<Return>", self._send_if_not_shift); self.composer.bind("<KeyRelease>", self._update_count)
        self.send_button = self._button(composer, self._t("send"), self._send, primary=True); self.send_button.grid(row=0, column=1, sticky="ns")
        bottom = tk.Frame(composer_panel, bg=P["panel"]); bottom.grid(row=1, column=0, sticky="ew", pady=(7, 0))
        self.count_label = tk.Label(bottom, text="0 / 4,000", bg=P["panel"], fg=P["muted"], font=("Segoe UI", 8)); self.count_label.pack(side="left")
        self.copy_button = tk.Button(bottom, text=self._t("copy"), command=self._copy_last, relief="flat", borderwidth=0, bg=P["panel"], fg=P["blue"], activebackground=P["panel"], activeforeground=P["text"], cursor="hand2", font=("Segoe UI Semibold", 8)); self.copy_button.pack(side="right")

    def _build_memory(self):
        panel = self._panel("memories"); panel.grid_rowconfigure(1, weight=1); panel.grid_columnconfigure(0, weight=1)
        top = tk.Frame(panel, bg=P["panel"], padx=22, pady=18); top.grid(row=0, column=0, sticky="ew")
        tk.Label(top, text="What Nova remembers", bg=P["panel"], fg=P["text"], font=("Segoe UI Semibold", 16)).pack(anchor="w")
        tk.Label(top, text="Saved locally, used only when it helps. You stay in charge.", bg=P["panel"], fg=P["muted"], font=("Segoe UI", 10)).pack(anchor="w", pady=(4, 0))
        self.memory_text = scrolledtext.ScrolledText(panel, wrap="word", state="disabled", borderwidth=0, relief="flat", font=("Cascadia Mono", 10), bg=P["input"], fg=P["text"], padx=18, pady=16); self.memory_text.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 12))
        actions = tk.Frame(panel, bg=P["panel"], padx=20, pady=12); actions.grid(row=2, column=0, sticky="ew")
        self._button(actions, "Refresh", self._refresh_memory, small=True).pack(side="left"); self._button(actions, "Forget everything", self._forget_all, small=True).pack(side="right")

    def _build_shortcuts(self):
        panel = self._panel("shortcuts")
        tk.Label(panel, text="Little launcher, big main-character energy", bg=P["panel"], fg=P["text"], font=("Segoe UI Semibold", 16)).pack(anchor="w", padx=22, pady=(20, 4))
        tk.Label(panel, text="These actions run only when you click them. No sneaky business.", bg=P["panel"], fg=P["muted"], font=("Segoe UI", 10)).pack(anchor="w", padx=22, pady=(0, 16))
        grid = tk.Frame(panel, bg=P["panel"], padx=18); grid.pack(fill="x")
        for column in range(2): grid.grid_columnconfigure(column, weight=1)
        for index, (label, command) in enumerate((("Calculator", "/open calculator"), ("Notepad", "/open notepad"), ("File Explorer", "/open files"), ("Web search", "/web "))):
            detail = command if command != "/web " else "Ask Nova to search the web"
            tk.Button(grid, text=f"{label}\n\n{detail}", command=lambda value=command: self._shortcut(value), justify="left", anchor="w", relief="flat", borderwidth=0, bg=P["raised"], fg=P["text"], activebackground=P["border"], activeforeground=P["text"], cursor="hand2", font=("Segoe UI Semibold", 10), padx=18, pady=16).grid(row=index // 2, column=index % 2, sticky="nsew", padx=5, pady=5)
        tk.Label(panel, text="Useful chat actions", bg=P["panel"], fg=P["muted"], font=("Segoe UI Semibold", 9)).pack(anchor="w", padx=23, pady=(24, 6))
        quicks = tk.Frame(panel, bg=P["panel"], padx=20); quicks.pack(fill="x")
        for command in ("/help", "/memory", "/time", "/system", "/calc 12 * 8"):
            self._button(quicks, command, lambda value=command: self._shortcut(value), small=True).pack(side="left", padx=(0, 7), pady=4)

    def _build_settings(self):
        panel = self._panel("settings"); panel.grid_columnconfigure(1, weight=1)
        tk.Label(panel, text="Make Nova yours", bg=P["panel"], fg=P["text"], font=("Segoe UI Semibold", 16)).grid(row=0, column=0, columnspan=2, sticky="w", padx=22, pady=(20, 5))
        tk.Label(panel, text="Preferences are saved locally. Fancy that: a settings page that actually listens.", bg=P["panel"], fg=P["muted"], font=("Segoe UI", 10)).grid(row=1, column=0, columnspan=2, sticky="w", padx=22, pady=(0, 20))
        self._setting_row(panel, 2, "App language", self.language, LANGUAGES, self._change_language)
        self.personality = tk.StringVar(value=get_setting("ai.personality", "cheeky")); self._setting_row(panel, 3, "Nova's vibe", self.personality, PERSONALITIES, self._save_personality)
        self.model = tk.StringVar(value=get_setting("ai.model", "gemma3:4b")); self._setting_row(panel, 4, "Ollama model", self.model, (), self._save_model, editable=True)
        tk.Checkbutton(panel, text="Speak Nova's replies", variable=self.speak_replies, command=self._save_speech, bg=P["panel"], fg=P["text"], selectcolor=P["raised"], activebackground=P["panel"], activeforeground=P["text"], font=("Segoe UI", 10), highlightthickness=0).grid(row=5, column=0, columnspan=2, sticky="w", padx=22, pady=14)
        tk.Label(panel, text="Shortcuts: Ctrl+L starts fresh • Ctrl+K clears draft • F1 focuses chat", bg=P["panel"], fg=P["blue"], font=("Segoe UI", 9)).grid(row=6, column=0, columnspan=2, sticky="w", padx=22, pady=(14, 0))

    def _setting_row(self, parent, row, label, variable, values, callback, editable=False):
        tk.Label(parent, text=label, bg=P["panel"], fg=P["text"], font=("Segoe UI Semibold", 10)).grid(row=row, column=0, sticky="w", padx=22, pady=10)
        widget = ttk.Combobox(parent, textvariable=variable, values=values, state="normal" if editable else "readonly", width=28); widget.grid(row=row, column=1, sticky="w", padx=10, pady=10)
        widget.bind("<<ComboboxSelected>>", lambda _event: callback()); widget.bind("<FocusOut>", lambda _event: callback()); widget.bind("<Return>", lambda _event: callback())

    def _show_view(self, view):
        self.active_view = view
        for name, frame in self.views.items(): frame.grid_remove(); self.nav_buttons[name].configure(bg=P["panel"], fg=P["muted"])
        self.views[view].grid(); self.nav_buttons[view].configure(bg=P["raised"], fg=P["text"]); self.page_title.configure(text=self._t(view))
        if view == "chat": self.header_action.configure(text=self._t("clear"), command=self._new_chat, state="normal"); self.composer.focus_set()
        elif view == "memories": self._refresh_memory(); self.header_action.configure(text="Manage here", command=lambda: None, state="disabled")
        else: self.header_action.configure(text=self._t("new"), command=lambda: self._show_view("chat"), state="normal")

    def _write(self, speaker, text):
        user = speaker == "You"; self.chat.configure(state="normal"); self.chat.insert("end", f"{speaker.upper()}\n", "user_name" if user else "nova_name"); self.chat.insert("end", f"{text.strip()}\n", "user_body" if user else "nova_body"); self.chat.insert("end", "\n"); self.chat.configure(state="disabled"); self.chat.see("end")

    def _send_if_not_shift(self, event):
        if event.state & 0x0001: return None
        self._send(); return "break"

    def _send(self, event=None):
        if self.working: return "break" if event else None
        message = self.composer.get("1.0", "end-1c").strip()
        if not message: self.composer.focus_set(); return "break" if event else None
        self.composer.delete("1.0", "end"); self._update_count()
        if self.active_view != "chat": self._show_view("chat")
        self._write("You", message); self.working = True; self.send_button.configure(state="disabled", text=self._t("thinking")); self.status_text.set("●  Nova is thinking")
        threading.Thread(target=self._reply, args=(message, self.speak_replies.get()), daemon=True).start()
        return "break" if event else None

    def _reply(self, message, should_speak):
        try:
            answer = respond(message); self.messages.put(("answer", answer))
            if should_speak: threading.Thread(target=self._speak_reply, args=(answer,), daemon=True).start()
        except Exception as exc:  # noqa: BLE001
            error(f"GUI response error: {exc}"); self.messages.put(("error", "Well, that reply tripped over its own shoelaces. Please try again."))

    def _speak_reply(self, answer):
        if not speak(answer): self.messages.put(("speech_error", "Speech could not be played. Check data/logs/nova.log."))

    def _read_queue(self):
        try:
            while True:
                kind, content = self.messages.get_nowait()
                if kind == "speech_error": self.status_text.set(content); continue
                self.last_answer = content; self._write(AI_NAME, content); self.working = False; self.send_button.configure(state="normal", text=self._t("send")); self.status_text.set("●  " + (self._t("ready") if kind == "answer" else "Reply failed")); self.composer.focus_set()
        except queue.Empty: pass
        self.root.after(75, self._read_queue)

    def _update_count(self, _event=None): self.count_label.configure(text=f"{len(self.composer.get('1.0', 'end-1c')):,} / 4,000")
    def _clear_composer(self): self.composer.delete("1.0", "end"); self._update_count(); self.composer.focus_set(); return "break"
    def _copy_last(self):
        if not self.last_answer: self.status_text.set("●  Nothing to copy yet"); return
        self.root.clipboard_clear(); self.root.clipboard_append(self.last_answer); self.status_text.set("●  Last reply copied")

    def _new_chat(self):
        if self.working: self.status_text.set("●  Let Nova finish that thought first"); return
        clear_history(); self.chat.configure(state="normal"); self.chat.delete("1.0", "end"); self.chat.configure(state="disabled"); self.last_answer = ""; self._show_view("chat"); self.status_text.set("●  " + self._t("ready"))

    def _refresh_memory(self):
        data = memory_manager.all(); formatted = json.dumps(data, indent=2, ensure_ascii=False) if data else self._t("empty")
        self.memory_text.configure(state="normal"); self.memory_text.delete("1.0", "end"); self.memory_text.insert("1.0", formatted); self.memory_text.configure(state="disabled")
    def _forget_all(self):
        if messagebox.askyesno("Forget all memory?", "This permanently removes Nova's saved long-term memory on this device. Continue?"):
            memory_manager.clear_all(); self._refresh_memory(); self.status_text.set("●  Saved memory cleared")
    def _shortcut(self, command):
        self._show_view("chat")
        if command == "/web ": self.composer.insert("1.0", command); self.composer.focus_set(); return
        self.composer.delete("1.0", "end"); self.composer.insert("1.0", command); self._send()
    def _change_language(self):
        save_setting("ui.language", self.language.get()); self.privacy.configure(text=self._t("local")); self.new_button.configure(text="+  " + self._t("new")); self.send_button.configure(text=self._t("thinking") if self.working else self._t("send")); self.copy_button.configure(text=self._t("copy"))
        for key, icon in (("chat", "◉"), ("memories", "◌"), ("shortcuts", "⌘"), ("settings", "⚙")):
            self.nav_buttons[key].configure(text=f" {icon}   {self._t(key)}")
        self._show_view(self.active_view)
    def _save_personality(self): save_setting("ai.personality", self.personality.get()); self.status_text.set("●  Nova's vibe saved")
    def _save_model(self):
        value = self.model.get().strip()
        if value: save_setting("ai.model", value); self.model_label.configure(text=f"Model: {value}"); self.status_text.set("●  Model saved for new replies")
    def _save_speech(self): save_setting("ui.speak_replies", self.speak_replies.get())
    def _close(self): save_setting("ui.geometry", self.root.geometry()); self.root.destroy()


def run():
    info(f"{AI_NAME} GUI starting...")
    root = tk.Tk(); NovaApp(root); root.mainloop()
