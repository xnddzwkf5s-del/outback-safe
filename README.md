# Outback-Safe USB

**Offline AI Survival Assistant + Australian Remote Travel Reference**

A portable USB drive containing an offline AI assistant with RAG over 142 pages of Australian outback survival knowledge. Zero internet required. No cloud dependencies. No data leaves the device.

> [Download the latest release](https://github.com/xnddzwkf5s-del/outback-safe/releases)

---

## What Is It

Two things in one USB:

**1. Static Survival Site** — 142 HTML pages covering outback 4WD travel, first aid, snake bite treatment, track guides (Simpson Desert, Canning Stock Route, Cape York), radio communications, and bush medicine. Works in any browser. No install, no Python, no internet. Always functional.

**2. Offline AI Assistant** — A RAG (Retrieval-Augmented Generation) system running a quantised LLM locally on your machine. Ask questions about survival, first aid, or vehicle recovery and get answers grounded in the knowledge base. Powered by llama.cpp and Qwen 2.5 3B.

Plug it in, open the web UI, and you have a knowledgeable survival companion even when you're hours from the nearest signal.

---

## Key Features

- **Fully air-gapped** — no internet, no API calls, no data exfiltration. Works in the most remote locations or the most secure environments.
- **RAG-powered AI** — the LLM answers from its own curated survival knowledge base, not generic training data.
- **Cross-platform** — macOS (native app + command line), Windows (PowerShell + batch), any OS (static HTML).
- **User-extendable** — drop your own `.md` files into the content folder, reindex, and the AI learns from them.
- **Always-available fallback** — the static site works even if Python isn't installed.

---

## Use Cases

### Remote Outback Travel
You're crossing the Simpson Desert with no mobile reception. Plug in the USB, ask the AI "What do I do if my radiator boils over?" and get an answer with context from the survival library. No internet, no problem.

### Air-Gapped AI Demonstration
You need to show AI capability in a government or regulated environment where cloud services are prohibited. The entire AI stack runs from a single USB — no network connection required, no data leaves the room.

### Document Intelligence Proof of Concept
The RAG framework can index any set of markdown documents and answer questions against them. Add procedure manuals, equipment guides, or operational documents to demonstrate how AI can augment existing knowledge bases in secure environments.

### Emergency Preparedness
Include your own emergency plans, contact lists, and local knowledge. The AI indexes everything on startup, giving you an interactive emergency reference that's faster than flipping through a binder.

---

## What's Inside

| Layer | Contents | Size |
|-------|----------|------|
| **Static Site** | 142 HTML pages — outback survival, first aid, track guides, comms | ~5 MB |
| **AI Engine** | llama.cpp server + Python RAG server | ~6 MB (script + source) |
| **LLM Model** | Qwen 2.5 3B (4-bit quantised GGUF) | ~1.8 GB |
| **Knowledge Base** | Vector-search index of all survival content | ~1 MB |
| **Build Tools** | Preprocessor, search index builder, dependency bundler | ~30 KB |

---

## How to Build From Source

**Prerequisites:** Python 3.10+, macOS or Linux

```bash
# Clone the repo
git clone https://github.com/xnddzwkf5s-del/outback-safe.git
cd outback-safe

# Full USB build (static site + AI + model download)
make all USB=/Volumes/OUTBACK_SAFE

# Build static site only
python3 build.py
```

### Build Targets

| Command | What It Does |
|---------|-------------|
| `make all` | Full USB build into `build/output/`, then copy to USB |
| `make USB=/path` | Specify custom USB mount point |
| `make site` | Build static HTML only (via `build.py`) |
| `make models` | Download the quantised LLM model |
| `make deps` | Bundle Python dependencies |
| `python3 build.py` | Generate static survival site to `docs/` (for GitHub Pages) |

---

## How to Use the AI Assistant

### macOS
1. Open the `ai/` folder on the USB
2. Double-click `start.command` (or `Start AI.app`)
3. Wait ~3-5 seconds for the model to load
4. A browser opens to the AI chat interface

### Windows
1. Open the `ai/` folder
2. Right-click `start.ps1` → Run with PowerShell
3. Wait ~15-45 seconds for the model to load

### Emergency (No Python)
Open `outback-safe/index.html` in any browser. All 142 pages are fully functional HTML.

---

## Project Architecture

```
outback-safe/
├── ai/                    # AI assistant (RAG + LLM)
│   ├── app/
│   │   ├── server.py      # Flask web server & RAG query handler
│   │   ├── rag.py         # Vector search & context retrieval
│   │   ├── templates/     # HTML templates for chat UI
│   │   └── static/        # CSS, JS for chat interface
│   ├── start.command      # macOS launcher
│   ├── start.bat          # Windows batch launcher
│   ├── start.ps1          # Windows PowerShell launcher
│   ├── reindex.command    # Rebuild search index (macOS)
│   ├── reindex.bat        # Rebuild search index (Windows)
│   └── Start AI.app/      # macOS native app wrapper
├── build/                 # USB build tooling
│   ├── preprocess.py      # Obsidian vault → HTML converter
│   ├── build_search_index.py  # Vector index builder
│   ├── download_models.py     # Model downloader
│   ├── fetch_llama_binaries.py  # llama.cpp binary fetcher
│   ├── bundle_deps.py     # Python dependency bundler
│   └── generate_emergency_pages.py  # Quick-access page generator
├── content/               # Knowledge base source (markdown)
├── docs/                  # Built static site (GitHub Pages)
├── static/                # Site CSS, service worker, manifest
├── build.py               # Static site generator (Markdown → HTML)
├── Makefile               # USB build orchestrator
├── README-FIRST.txt       # USB root instructions
├── START-HERE.html        # USB landing page
├── LICENSE                # CC BY-SA 4.0 (content)
└── LICENSE-CODE           # MIT (software)
```

---

## License

- **Content** (survival guides, track information, medical references): [CC BY-SA 4.0](LICENSE)
- **Software** (AI assistant, build scripts, tools): [MIT](LICENSE-CODE)
- **LLM Model** (Qwen 2.5 3B): Apache 2.0 — see [Qwen licence](https://github.com/QwenLM/Qwen)
- **llama.cpp** runtime: MIT — see [llama.cpp](https://github.com/ggerganov/llama.cpp)

---

## Disclaimer

For educational and informational purposes only. Not a substitute for professional medical advice, emergency services training, or proper vehicle preparation. In an emergency, call 000 (Australia).
