# Nova

Nova is a privacy-first Windows desktop assistant. It runs its language model locally through [Ollama](https://ollama.com/), keeps chat memory on the machine, and offers optional voice input and Piper text-to-speech.

## Recommended profile: MSI Thin GF63 12VE

The default `gemma3:4b` profile is deliberately tuned for the laptop's RTX 4050 6 GB GPU:

- 4K context and modest batching for predictable VRAM usage.
- Local Ollama inference; no cloud key is required.
- GPU Whisper where available, with a CPU fallback.
- Voice is optional, so text chat remains lightweight and reliable.

For a more capable model, use `/model qwen2.5:7b` only if it fits comfortably on your system. Smaller models are usually faster and more stable on 6 GB VRAM.

The 16 GB system-memory upgrade gives Windows and Ollama more room to coexist, but the 6 GB GPU remains the limit for fast GPU inference. Keep the default model for the smoothest experience; try a 7B model only if you are comfortable with slower partial CPU offload.

## Quick start

1. Install Python 3.11–3.13 and [Ollama](https://ollama.com/download/windows).
2. In PowerShell from the project folder:

   ```powershell
   py -3.11 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ollama pull gemma3:4b
   python main.py --gui
   ```

3. Use `python main.py --text` for the terminal interface.

Ollama must be running before Nova can answer. If voice transcription falls back to CPU, install a CUDA-compatible PyTorch build from the official PyTorch selector.

Spoken replies work out of the box through Windows Speech. For a higher-quality local voice, install the [Piper command-line release](https://github.com/rhasspy/piper/releases), place its executable on `PATH`, and place a compatible `.onnx` model plus `.onnx.json` metadata in the project root. Nova automatically prefers Piper and falls back to Windows Speech.

## Commands

`/help` lists all commands. Common controls include `/model <ollama-model>`, `/web <query>`, `/memory`, `/clear`, `/system`, `/analyze <file>`, and `/chart <file>`.

Nova's file and analytics tools are read-only. Web search is only run when directly requested.

## Privacy and security

- Personal conversation history, memories, settings, logs, and charts are stored in `data/` and ignored by Git.
- `.env` is ignored. Do not commit API keys, model files, audio files, or virtual environments.
- This project does not need an OpenAI key. If a key was ever placed in `.env`, revoke it at the provider before publishing.

## Development

Run tests after installing dependencies:

```powershell
python -m unittest discover -s tests -v
python -m compileall -q ai core ui voice main.py
```

## License

Released under the MIT License. See [LICENSE](LICENSE).
