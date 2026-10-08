# Nova

**Nova** is a privacy-first Windows desktop AI assistant that runs locally on your machine. It uses [Ollama](https://ollama.com/) for local language-model inference, stores conversation memory locally, and supports optional voice input and text-to-speech.

No cloud AI API key is required.

## ✨ Features

* 🧠 **Local AI** — Run models through Ollama without sending conversations to a cloud AI provider.
* 🔒 **Privacy-first** — Chat history, memories, settings, logs, and generated charts stay on your machine.
* 💬 **Text & GUI modes** — Use Nova from the terminal or desktop interface.
* 🎙️ **Voice input** — Optional speech-to-text with GPU acceleration when available.
* 🔊 **Text-to-speech** — Windows Speech support with optional Piper integration.
* 📁 **File analysis** — Read-only file analysis tools.
* 📊 **Data visualization** — Generate charts from supported files.
* 🌐 **Optional web search** — Web search only runs when explicitly requested.
* 🧩 **Multiple Ollama models** — Switch models directly from Nova.

## 💻 Recommended Hardware

Nova's default profile is tuned for the **MSI Thin GF63 12VE** with:

* **GPU:** NVIDIA RTX 4050 6 GB
* **RAM:** 16 GB
* **Default model:** `gemma3:4b`
* **Context:** 4K
* **Inference:** Local Ollama

The default `gemma3:4b` profile is recommended for a smooth experience on a 6 GB GPU.

You can try a larger model such as:

```text
/model qwen2.5:7b
```

However, a 7B model may require partial CPU offloading and can be noticeably slower. For the best balance between speed and stability, `gemma3:4b` is recommended.

## 🚀 Installation

### 1. Install Python

Install **Python 3.11–3.13**.

Verify your installation:

```powershell
python --version
```

### 2. Install Ollama

Download and install [Ollama](https://ollama.com/download/windows).

Make sure Ollama is running before starting Nova.

### 3. Clone the repository

```powershell
git clone <your-repository-url>
cd Nova
```

### 4. Create a virtual environment

```powershell
py -3.11 -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 5. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 6. Download the default model

```powershell
ollama pull gemma3:4b
```

### 7. Start Nova

GUI mode:

```powershell
python main.py --gui
```

Terminal mode:

```powershell
python main.py --text
```

## 🎮 Commands

Nova provides several built-in commands.

| Command           | Description                          |
| ----------------- | ------------------------------------ |
| `/help`           | Display available commands           |
| `/model <model>`  | Change the Ollama model              |
| `/web <query>`    | Perform a web search                 |
| `/memory`         | View/manage conversation memory      |
| `/clear`          | Clear the current conversation       |
| `/system`         | View or manage the system prompt     |
| `/analyze <file>` | Analyze a file                       |
| `/chart <file>`   | Generate a chart from supported data |

Example:

```text
/model gemma3:4b
```

## 🎙️ Voice Input

Voice input is optional.

Nova can use GPU-accelerated Whisper when a compatible CUDA/PyTorch setup is available. If GPU acceleration is unavailable, Nova can fall back to CPU transcription.

For better performance, install a CUDA-compatible PyTorch build using the official PyTorch installation selector.

## 🔊 Text-to-Speech

Nova supports Windows Speech out of the box.

For higher-quality local voices, you can optionally install **Piper**.

After installing Piper:

1. Add the Piper executable to your `PATH`.
2. Place a compatible `.onnx` voice model in the project root.
3. Place the matching `.onnx.json` metadata file alongside it.

Nova will automatically prefer Piper when available and fall back to Windows Speech when it isn't.

## 🔐 Privacy & Security

Nova is designed with local-first privacy in mind.

The following data is stored locally:

* Conversation history
* Memories
* Application settings
* Logs
* Generated charts

These files are stored under:

```text
data/
```

The `data/` directory is excluded from Git.

### Important

Do **not** commit:

* API keys
* `.env` files
* Virtual environments
* Model files
* Audio recordings
* Personal conversation data
* Local application data

Nova does not require an OpenAI API key.

If an API key was previously stored in `.env`, **revoke it before publishing the repository**.

## 🧪 Testing

After installing the dependencies, run:

```powershell
python -m unittest discover -s tests -v
```

You can also check the project for Python compilation errors:

```powershell
python -m compileall -q ai core ui voice main.py
```

## 📁 Project Structure

A typical Nova installation looks like:

```text
Nova/
├── ai/
├── core/
├── ui/
├── voice/
├── tests/
├── data/
├── main.py
├── requirements.txt
├── LICENSE
└── README.md
```

Local user data should remain inside `data/` and should not be committed to Git.

## ⚡ Performance

For the MSI Thin GF63 12VE, the recommended setup is:

```text
GPU: RTX 4050 6 GB
RAM: 16 GB
Model: gemma3:4b
Context: 4K
```

If Nova becomes slow while other applications or virtual machines are running, reduce the workload before switching to a larger model. The 6 GB VRAM capacity is the main limitation for larger local models.

## 🛠️ Troubleshooting

### Nova cannot connect to Ollama

Make sure Ollama is running:

```powershell
ollama list
```

If the command works, verify that the required model is installed:

```powershell
ollama pull gemma3:4b
```

### Voice transcription is slow

Check whether your PyTorch installation supports CUDA. If GPU acceleration is unavailable, Nova will use CPU transcription.

### The 7B model is slow

A larger model may exceed comfortable GPU memory usage on a 6 GB RTX 4050 and therefore use CPU offloading.

Try:

```text
/model gemma3:4b
```

for a faster experience.

## 🤝 Development

Contributions, improvements, bug reports, and suggestions are welcome.

Before submitting changes, run the test suite:

```powershell
python -m unittest discover -s tests -v
```

and:

```powershell
python -m compileall -q ai core ui voice main.py
```

## 📄 License

Released under the **MIT License**.

See [`LICENSE`](LICENSE) for the full license text.
