# Outback-Safe USB

**Offline AI Survival Assistant + Australian Remote Travel Reference**

A portable USB drive containing an offline AI assistant with RAG over 142 pages of Australian outback survival knowledge. **Zero internet required. No cloud dependencies. No data leaves the device.**

> [Download Outback Safe.zip](https://wescan.net/downloads/Outback%20Safe.zip) — 79 MB, works offline immediately

---

## Why This Exists

Most AI projects assume connectivity. For government, defence, critical infrastructure, and remote travel — that assumption doesn't hold. This project explores a practical question: **what does AI look like when it has to work without a network, without an API key, and without any data leaving the device?**

The answer is a layered system where every component has a fallback. The AI can fail entirely and the static survival site still works. The model can be swapped. The knowledge base can be replaced. There's no single point of failure. That's not just good engineering — it's the same thinking you'd apply to deploying AI in a regulated enterprise environment.

---

## What's Inside

Two things in one USB:

**1. Static Survival Site** — 142 HTML pages covering outback 4WD travel, first aid, snake bite treatment, track guides (Simpson Desert, Canning Stock Route, Cape York), radio communications, and bush medicine. Works in any browser. No install, no Python, no internet. Always functional.

**2. Offline AI Assistant** — A RAG system running a quantised LLM locally. Ask questions about survival, first aid, or vehicle recovery and get answers grounded in the curated knowledge base.

Plug it in, open the web UI, and you have a knowledgeable survival companion even when you're hours from the nearest signal.

---

## Key Features

- **Fully air-gapped** — no internet, no API calls, no data exfiltration. Suitable for classified or regulated environments.
- **RAG-powered AI** — the LLM answers from its own curated knowledge base, not generic training data. Reduces hallucination risk compared to raw LLM prompting.
- **Cross-platform** — macOS (native app + CLI), Windows (PowerShell + batch), any OS (static HTML). Startup scripts handle dependency detection and graceful failure.
- **User-extendable** — drop `.md` files into the content folder, reindex, and the AI learns from them. The knowledge base is designed to be swapped for any domain.
- **Layered architecture** — each component (static site, AI server, LLM backend) operates independently. No cascading failures.
- **Graceful degradation** — if Python is missing, the static site still works. If the model fails to load, the chat UI shows a helpful error. Built for the failure case first.

---

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Architecture** | RAG (not fine-tuning) | Knowledge base can be updated without retraining. Domain-agnostic — swap the content to repurpose for any field. |
| **Model** | Qwen 2.5 3B (4-bit GGUF) | Small enough to run on consumer hardware (4 GB RAM), capable enough for factual QA over a narrow knowledge base. 4-bit quantisation reduces model size by ~75% with minimal accuracy loss. |
| **Runtime** | llama.cpp | Runs on CPU with no GPU required. Cross-platform (macOS ARM + Windows x64). Battle-tested in offline/edge deployments. |
| **Vector Search** | Sentence embeddings stored in JSON index | No external vector database dependency. Entire index fits in ~1 MB. Rebuild in seconds. |
| **Content Format** | Markdown → static HTML | The content must be readable without any software stack. Every page is a standalone HTML file. |
| **Packaging** | Split releases (site + AI) | Users who only need the reference material download 5 MB. Those who want the full AI stack get it separately. The model is downloaded on demand via script — not bundled in the repo. |

---

## Technical Specifications

| Metric | Value |
|--------|-------|
| Knowledge base size | 142 pages, ~200K words across survival, medical, navigation, communications |
| Vector index size | ~1 MB (sentence embeddings) |
| Model | Qwen 2.5 3B, 4-bit GGUF quantisation |
| Model RAM usage | ~2.5 GB at runtime |
| Startup time (macOS ARM) | 3-5 seconds (model load) |
| Query response time | 2-8 seconds depending on hardware |
| Chunk size | 500 tokens with 50-token overlap (optimised for factual recall) |
| Embedding model | Built-in (sentence-transformers compatible, bundled in index) |
| Fallback mode | Static HTML site, no Python required |

---

## Architecture

The USB contains four layers, each independently operable:

| Layer | Role | Dependency |
|-------|------|-----------|
| **Static HTML Site** | 142 pages, opens in any browser | None — always works |
| **AI Assistant** | Flask web UI + RAG query handler | Requires Python + model |
| **Knowledge Base** | Vector index + markdown content | Built from content/ |
| **Build System** | Makefile + Python tools for assembly | Development only |

The static site has no dependencies and functions as a fallback if the AI layer can't start. The AI layer queries the knowledge base via vector search. The build system assembles everything onto a USB.

**File structure:**

```
outback-safe/
├── ai/                    # AI assistant (RAG + LLM)
│   ├── app/
│   │   ├── server.py      # Flask web server & RAG query handler
│   │   ├── rag.py         # Vector search & context retrieval
│   │   ├── templates/     # HTML templates for chat UI
│   │   └── static/        # CSS, JS for chat interface
│   ├── start-macos.command      # macOS launcher
│   ├── start-windows.bat          # Windows batch launcher
│   ├── reindex.command    # Rebuild search index (macOS)
│   ├── reindex.bat        # Rebuild search index (Windows)
│   └── Start AI.app/      # macOS native app wrapper
├── build/                 # USB build tooling
│   ├── preprocess.py              # Obsidian vault → HTML converter
│   ├── build_search_index.py      # Vector index builder (500-token chunks, 50-token overlap)
│   ├── download_models.py         # Model downloader (Qwen 2.5 3B GGUF)
│   ├── fetch_llama_binaries.py    # llama.cpp binary fetcher per platform
│   ├── bundle_deps.py             # Python dependency bundler per platform
│   └── generate_emergency_pages.py  # Quick-access landing page generator
├── content/               # Knowledge base source (markdown)
├── docs/                  # Built static site (GitHub Pages)
├── static/                # Site CSS, service worker, manifest
├── build.py               # Static site generator (Markdown → HTML)
├── Makefile               # USB build orchestrator (make all → full USB)
├── README-FIRST.txt       # USB root instructions (what to do when you plug it in)
├── START-HERE.html        # USB landing page (AI or survival, your choice)
├── LICENSE                # CC BY-SA 4.0 (content)
└── LICENSE-CODE           # MIT (software)
```

---

## Use Cases

### Remote Outback Travel
You're crossing the Simpson Desert with no mobile reception. Plug in the USB, ask the AI "What do I do if my radiator boils over?" and get an answer grounded in the survival library. No internet, no problem.

### Air-Gapped AI Demonstration
You need to show AI capability in a government or regulated environment where cloud services are prohibited. The entire AI stack runs from a single USB — no network connection required, no data leaves the room. This is the use case the project was designed for.

### Document Intelligence Proof of Concept
The RAG framework can index any set of markdown documents and answer questions against them. Add procedure manuals, equipment guides, or operational documents to demonstrate how AI can augment existing knowledge bases in secure environments.

### Emergency Preparedness
Include your own emergency plans, contact lists, and local knowledge. The AI indexes everything on startup, giving you an interactive emergency reference that's faster than flipping through a binder.

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
| `make models` | Download the quantised LLM model (~1.8 GB) |
| `make deps` | Bundle Python dependencies per platform |
| `make clean` | Remove build output |
| `python3 build.py` | Generate static survival site to `docs/` (for GitHub Pages) |

---

## How to Use the AI Assistant

### macOS
1. Open the `ai/` folder on the USB
2. Double-click `start-macos.command` (or `Start AI.app`)
3. Wait ~3-5 seconds for the model to load
4. A browser opens to the AI chat interface

### Windows
1. Open the `ai/` folder on the USB
2. Double-click `start-windows.bat`
3. Wait ~15-45 seconds for the model to load

### Emergency (No Python)
Open `outback-safe/index.html` in any browser. All 142 pages are fully functional HTML.

---

## Roadmap

- [x] Static survival site (142 pages, fully functional offline)
- [x] RAG AI assistant with offline LLM (Qwen 2.5 3B)
- [x] Cross-platform launchers (macOS + Windows)
- [x] Build tooling and release pipeline
- [x] Dual licensing (CC BY-SA for content, MIT for code)
- [ ] Alternative model support (smaller models for lower-end hardware)
- [ ] GUI-based knowledge base management (drag-and-drop content updates)
- [ ] iOS/iPad offline app (Swift + llama.cpp bindings)
- [ ] Custom domain model fine-tuning for specialised knowledge bases

---

## License

- **Content** (survival guides, track information, medical references): [CC BY-SA 4.0](LICENSE)
- **Software** (AI assistant, build scripts, tools): [MIT](LICENSE-CODE)
- **LLM Model** (Qwen 2.5 3B): Apache 2.0 — see [Qwen licence](https://github.com/QwenLM/Qwen)
- **llama.cpp** runtime: MIT — see [llama.cpp](https://github.com/ggerganov/llama.cpp)

---

## Disclaimer

For educational and informational purposes only. Not a substitute for professional medical advice, emergency services training, or proper vehicle preparation. In an emergency, call 000 (Australia).
