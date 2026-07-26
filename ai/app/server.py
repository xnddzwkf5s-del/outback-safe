#!/usr/bin/env python3
"""
Outback-Safe USB AI Server — Main entry point for the offline AI assistant.

Lifecycle:
  1. Detect RAM → select model (1.5B or 3B)
  2. Re-index content via rag.py (if stale)
  3. Launch llama-server subprocess, poll /health until ready
  4. Start Flask on port 8765, open browser
  5. atexit cleanup kills llama-server on exit

Routes:
  GET  /                        → index.html
  GET  /api/status              → system status JSON
  POST /api/chat                → SSE chat stream with RAG context
  GET  /api/content/search?q=   → BM25 keyword search
  POST /api/reindex             → trigger re-index
  GET  /outback-safe/<path>     → serve static survival HTML
"""

from __future__ import annotations

import argparse
import atexit
import json
import os
import subprocess
import sys
import time
import webbrowser

import sys as _sys
_sys.dont_write_bytecode = True  # Don't write .pyc to USB (cross-platform)
# Force UTF-8 on Windows (console uses cp1252 which can't print Unicode box chars)
if hasattr(_sys.stdout, "reconfigure"):
    try:
        _sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        _sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Tuple

import flask
from flask import (
    Flask,
    Response,
    jsonify,
    render_template,
    request,
    send_from_directory,
)

# ---------------------------------------------------------------------------
# CLI arguments
# ---------------------------------------------------------------------------

parser = argparse.ArgumentParser(
    description="Outback-Safe USB AI Server — offline survival & medical AI assistant"
)
parser.add_argument(
    "--usb-dir",
    default="/Volumes/SHTF_USB",
    help="USB mount point (default: /Volumes/SHTF_USB)",
)
parser.add_argument(
    "--llama-bin",
    help="Path to llama-server binary (auto-detected if omitted)",
)
parser.add_argument(
    "--port",
    type=int,
    default=8765,
    help="Flask HTTP port (default: 8765)",
)
parser.add_argument(
    "--llama-port",
    type=int,
    default=8766,
    help="llama-server API port (default: 8766)",
)
parser.add_argument(
    "--no-browser",
    action="store_true",
    help="Do not open browser on startup",
)
args = parser.parse_args()

# ---------------------------------------------------------------------------
# Derived paths & constants
# ---------------------------------------------------------------------------

USB_DIR = Path(args.usb_dir).resolve()
APP_DIR = Path(__file__).resolve().parent
LLAMA_PORT = args.llama_port
LLAMA_URL = f"http://127.0.0.1:{LLAMA_PORT}"
FLASK_PORT = args.port
FLASK_URL = f"http://localhost:{FLASK_PORT}"

OUTBACK_DIR = USB_DIR / "outback-safe"
CONTENT_DIR = USB_DIR / "content"
MODELS_DIR = USB_DIR / "ai" / "models"
BIN_DIR = USB_DIR / "ai" / "bin"
INDEX_PATH = APP_DIR / "search_index.json"
RAG_PATH = APP_DIR / "rag.py"
TEMPLATES_DIR = APP_DIR / "templates"
STATIC_DIR = APP_DIR / "static"

MODEL = MODELS_DIR / "qwen3-8b-q4.gguf"

# llama-server configuration
LLAMA_CTX_SIZE = 8192
LLAMA_BATCH_SIZE = 512
LLAMA_THREADS = 8

HEALTH_TIMEOUT = 300  # 5 minutes

# ---------------------------------------------------------------------------
# System prompt template
# ---------------------------------------------------------------------------

SYSTEM_PROMPT_TEMPLATE = """<|im_start|>system
You are a survival and medical reference assistant. Answer DIRECTLY without any thinking or reasoning. Use only relevant reference documents.

CRITICAL RULES:
1. IGNORE any retrieved documents that are about a completely different topic than the question. Only use documents that actually address the question.
2. Use metric units only (km, °C, kg, L). Answer in 2-5 concise sentences.
3. If relevant documents exist: cite as [source: name.html]. NEVER fabricate citations.
4. If NO documents are relevant: say "I don't have specific reference material on this" then give general survival knowledge.
5. NEVER insert unrelated safety advice (snake bites, crocodiles, water crossings) unless the user asks about them.
<|im_end|>
<|im_start|>user
<documents>
{rag_context}
</documents>

Question: {user_question}
<|im_end|>
<|im_start|>assistant
"""
# ---------------------------------------------------------------------------
# Global state
# ---------------------------------------------------------------------------

llama_process: Optional[subprocess.Popen] = None
start_time = time.time()
model_name: str = "unknown"
pages_indexed: int = 0
model_loaded: bool = False
fallback_mode: bool = False
searcher = None  # rag.Searcher instance, set during init

# ---------------------------------------------------------------------------
# Utility: RAM detection
# ---------------------------------------------------------------------------


def detect_ram_gb() -> float:
    """Return total system RAM in gigabytes. Cross-platform."""
    # macOS: sysconf
    try:
        page_size = os.sysconf("SC_PAGE_SIZE")
        phys_pages = os.sysconf("SC_PHYS_PAGES")
        if page_size > 0 and phys_pages > 0:
            return (page_size * phys_pages) / (1024**3)
    except (ValueError, AttributeError):
        pass

    # Windows: GlobalMemoryStatusEx via ctypes
    try:
        import ctypes
        import ctypes.wintypes

        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.wintypes.DWORD),
                ("dwMemoryLoad", ctypes.wintypes.DWORD),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]

        mem = MEMORYSTATUSEX()
        mem.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(mem)):
            return mem.ullTotalPhys / (1024**3)
    except (ImportError, AttributeError, OSError):
        pass

    # Linux: /proc/meminfo
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemTotal:"):
                    kb = int(line.split()[1])
                    return kb / (1024**2)
    except Exception:
        pass

    return 0.0


def select_model(ram_gb: float) -> Path:
    """Select model based on available RAM and what's on disk.
    
    Priority: 8B > 3B > 1.5B
    Falls back to smaller models if larger ones don't exist.
    """
    # Prefer 8B if it exists and we have enough RAM (12 GB+)
    if MODEL_8B.is_file() and ram_gb >= 12:
        print(f"[server] RAM: {ram_gb:.1f} GB → selecting 8B model")
        return MODEL_8B
    elif MODEL_LARGE.is_file() and ram_gb >= 10:
        print(f"[server] RAM: {ram_gb:.1f} GB → selecting 3B model")
        return MODEL_LARGE
    else:
        print(f"[server] RAM: {ram_gb:.1f} GB → selecting 1.5B model")
        return MODEL_SMALL


# ---------------------------------------------------------------------------
# Utility: find llama-server binary
# ---------------------------------------------------------------------------


def find_llama_binary() -> str:
    """Auto-detect llama-server binary.

    Priority:
      1. --llama-bin CLI arg
      2. llama-server-arm64 in BIN_DIR
      3. llama-server in BIN_DIR
      4. llama-server on PATH
    """
    if args.llama_bin:
        path = Path(args.llama_bin)
        if path.is_file() and os.access(path, os.X_OK):
            return str(path)
        sys.exit(f"❌ --llama-bin not found or not executable: {args.llama_bin}")

    candidates = [
        BIN_DIR / "llama-server-arm64",
        BIN_DIR / "llama-server-win64.exe",  # Windows
        BIN_DIR / "llama-server",
    ]

    for candidate in candidates:
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)

    # Fallback: PATH lookup
    result = subprocess.run(["which", "llama-server"], capture_output=True, text=True)
    if result.returncode == 0:
        return result.stdout.strip()

    sys.exit(
        "❌ Could not find llama-server binary.\n"
        f"   Checked: {', '.join(str(c) for c in candidates)}, PATH\n"
        "   Pass --llama-bin to specify the path explicitly."
    )


# ---------------------------------------------------------------------------
# Content re-index
# ---------------------------------------------------------------------------


def run_reindex() -> None:
    """Re-index content via rag.py --rebuild-if-older."""
    global pages_indexed, searcher

    print("[server] Checking search index…")

    cmd = [
        sys.executable,
        str(RAG_PATH),
        "--rebuild-if-older",
        "--content", str(OUTBACK_DIR),
        "--user-content", str(CONTENT_DIR),
        "--index", str(INDEX_PATH),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

    if result.returncode != 0:
        print(f"[server] ⚠️  Re-index failed (exit {result.returncode}):")
        print(f"    stderr: {result.stderr.strip()}")
        pages_indexed = 0
    else:
        print(result.stdout.strip())

    # Load/reload searcher with fresh index
    _load_searcher()


def _import_rag():
    """Import rag module from the app directory, adding it to sys.path if needed."""
    app_dir_str = str(APP_DIR)
    if app_dir_str not in sys.path:
        sys.path.insert(0, app_dir_str)

    # Force re-import in case of previous failed import
    import importlib
    if "rag" in sys.modules:
        importlib.reload(sys.modules["rag"])

    import rag
    return rag


def _load_searcher() -> None:
    """Load or reload the RAG searcher from the index file."""
    global searcher, pages_indexed

    try:
        rag = _import_rag()
        searcher = rag.Searcher(str(INDEX_PATH))
        pages_indexed = len(searcher._sources) if searcher._sources else 0
    except Exception as exc:
        print(f"[server] ⚠️  Failed to load RAG searcher: {exc}")
        searcher = None
        pages_indexed = 0


# ---------------------------------------------------------------------------
# llama-server subprocess lifecycle
# ---------------------------------------------------------------------------


def start_llama_server(model_path: Path) -> None:
    """Launch llama-server as a subprocess."""
    global llama_process

    bin_path = find_llama_binary()

    if not model_path.is_file():
        sys.exit(f"❌ Model file not found: {model_path}")

    cmd = [
        bin_path,
        "--model", str(model_path),
        "--host", "127.0.0.1",
        "--port", str(LLAMA_PORT),
        "--n-gpu-layers", "all",
        "--ctx-size", str(LLAMA_CTX_SIZE),
        "--batch-size", str(LLAMA_BATCH_SIZE),
        "--threads", str(LLAMA_THREADS),
        # Quiet mode — suppress per-token logs
        "--log-disable",
    ]

    print(f"[server] Launching llama-server: {' '.join(cmd[:4])} ...")
    sys.stdout.flush()

    _kwargs = {}
    if _sys.platform == "win32":
        _kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW  # type: ignore[attr-defined]
    llama_process = subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
        **_kwargs,
    )


def poll_health() -> bool:
    """Poll llama-server /health until HTTP 200 or timeout.

    Returns True if healthy, False on timeout.
    """
    import urllib.request
    import urllib.error

    health_url = f"{LLAMA_URL}/health"
    deadline = time.time() + HEALTH_TIMEOUT
    last_log = time.time()

    print(f"[server] Waiting for llama-server at {health_url} …")

    while time.time() < deadline:
        try:
            req = urllib.request.Request(health_url, method="GET")
            resp = urllib.request.urlopen(req, timeout=5)
            if resp.status == 200:
                elapsed = time.time() - (deadline - HEALTH_TIMEOUT)
                print(f"[server] ✅ llama-server ready after {elapsed:.1f}s")
                return True
        except (urllib.error.URLError, ConnectionRefusedError, OSError) as exc:
            # Only log every 10 seconds to avoid noise
            if time.time() - last_log > 10:
                print(f"[server]   still waiting… ({type(exc).__name__})")
                last_log = time.time()

        # Check if subprocess is still alive
        if llama_process and llama_process.poll() is not None:
            stderr_output = llama_process.stderr.read() if llama_process.stderr else ""
            print(f"[server] ❌ llama-server exited prematurely (code {llama_process.returncode})")
            if stderr_output:
                print(f"    stderr: {stderr_output[:500]}")
            return False

        time.sleep(2)

    return False


def stop_llama_server() -> None:
    """Gracefully terminate the llama-server subprocess."""
    global llama_process

    if llama_process is None:
        return

    print("[server] Stopping llama-server…")

    try:
        llama_process.terminate()
        try:
            llama_process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            print("[server]   llama-server not responding, force-killing…")
            llama_process.kill()
            llama_process.wait(timeout=5)

        print("[server] ✅ llama-server stopped")
    except Exception as exc:
        print(f"[server] ⚠️  Error stopping llama-server: {exc}")
    finally:
        llama_process = None


def cleanup() -> None:
    """atexit handler — ensures llama-server is killed on exit."""
    stop_llama_server()


# ---------------------------------------------------------------------------
# Flask app
# ---------------------------------------------------------------------------

app = Flask(
    __name__,
    template_folder=str(TEMPLATES_DIR),
    static_folder=str(STATIC_DIR),
    static_url_path="/static",
)

# Store config for routes
app.config["USB_DIR"] = str(USB_DIR)
app.config["LLAMA_URL"] = LLAMA_URL
app.config["OUTBACK_DIR"] = str(OUTBACK_DIR)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.route("/")
def index():
    """Serve the main chat interface."""
    return render_template("index.html")


@app.route("/api/status")
def api_status():
    """Return system status: model, pages indexed, RAM, uptime."""
    global model_name, pages_indexed, model_loaded, fallback_mode

    uptime_seconds = time.time() - start_time
    ram_gb = detect_ram_gb()

    try:
        # Check llama-server health for live status
        import urllib.request
        health_url = f"{LLAMA_URL}/health"
        req = urllib.request.Request(health_url, method="GET")
        resp = urllib.request.urlopen(req, timeout=3)
        live_health = resp.status == 200
    except Exception:
        live_health = False

    # Count pages from outback-safe directory
    try:
        page_files = list(Path(OUTBACK_DIR).glob("*.html")) if OUTBACK_DIR.is_dir() else []
        kb_pages = len(page_files)
    except Exception:
        kb_pages = 0

    return jsonify({
        "model": model_name,
        "model_loaded": model_loaded and live_health,
        "pages_indexed": pages_indexed,
        "knowledge_base_pages": kb_pages,
        "ram_gb": round(ram_gb, 1),
        "uptime_seconds": int(uptime_seconds),
        "fallback_mode": fallback_mode,
        "llama_url": LLAMA_URL,
    })


@app.route("/api/chat", methods=["POST"])
def api_chat():
    """SSE chat endpoint: RAG search → build prompt → stream from llama-server."""
    global searcher, fallback_mode

    if fallback_mode:
        return Response(
            "data: {\"type\":\"error\",\"text\":\"AI model not loaded — server is in fallback mode.\\n"
            "You can still browse the knowledge base pages.\\n"
            "Try restarting the server.\\n\"}\n\n",
            mimetype="text/event-stream",
        )

    # Parse request
    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({"error": "Request body must be JSON"}), 400
        user_message = data.get("message", "").strip()
    except Exception:
        return jsonify({"error": "Invalid JSON body"}), 400

    if not user_message:
        return jsonify({"error": "message is required"}), 400

    # Read user's unit preference
    units = data.get("units", "metric")

    # Build RAG context
    rag_context = _build_rag_context(user_message)

    # Build prompt with units preference
    units_line = "" if units == "metric" else "\nIMPORTANT: User prefers imperial units (miles, °F, pounds, gallons, inches).\n"
    prompt = SYSTEM_PROMPT_TEMPLATE.format(
        rag_context=rag_context,
        user_question=user_message,
    )
    # Inject units preference after the CRITICAL line
    prompt = prompt.replace("CRITICAL:", f"CRITICAL:{units_line}")

    return Response(
        _stream_completion(prompt),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


def _build_rag_context(query: str) -> str:
    """Search RAG index and format results as context string."""
    global searcher

    if searcher is None:
        return "(No reference material indexed. Answer from general knowledge and note this limitation.)"

    try:
        results = searcher.search(query, top_k=5)
    except Exception as exc:
        print(f"[server] RAG search error: {exc}")
        return "(Error searching reference material.)"

    # Only use the single best-matching source to prevent model confusion
    # Results boosted by title relevance below

    if not results:
        return "(No relevant reference material found for this query.)"

    # Boost results whose source titles match query terms
    # But only if some titles actually match (for medicine lookups, titles don't contain drug names)
    query_words = set(query.lower().split())
    def title_score(result):
        chunk_text, source = result
        title = source.get("title", "").lower()
        return sum(1 for w in query_words if w in title)
    if max(title_score(r) for r in results) > 0:
        results.sort(key=title_score, reverse=True)
    # Use the top 5 best-matching sources for comprehensive context
    results = results[:5]

    lines = []
    for i, (chunk_text, source) in enumerate(results, 1):
        title = source.get("title", "unknown")
        url = source.get("url", "")
        source_type = source.get("source_type", "")

        # Format citation
        citation = f"[source: {title}"
        if url:
            citation += f"|{url}"
        citation += "]"

        lines.append(f"--- Source {i}: {citation} ---")
        lines.append(chunk_text.strip())

    return "\n\n".join(lines)


def _stream_completion(prompt: str):
    """Generator: POST prompt to llama-server /completion, yield SSE chunks."""
    import urllib.request
    import urllib.error

    payload = json.dumps({
        "prompt": prompt,
        "stream": True,
        "n_predict": 600,
        "temperature": 0.5,
        "top_p": 0.9,
        "repeat_penalty": 1.1,
        "stop": ["\n\n\n", "QUESTION:", "Answer the following", "Could you provide", "###"],
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{LLAMA_URL}/completion",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        resp = urllib.request.urlopen(req, timeout=120)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode() if hasattr(exc, 'read') else str(exc)
        # Check if it's a context size error
        if 'exceed' in body.lower() and 'context' in body.lower():
            yield f"data: {{\"type\":\"error\",\"text\":\"⚠️ Knowledge base is too large for the AI model. Try a more specific question.\"}}\n\n"
        else:
            yield f"data: {{\"type\":\"error\",\"text\":\"AI model error: {exc.code} {exc.reason}\"}}\n\n"
        return
    except urllib.error.URLError as exc:
        yield f"data: {{\"type\":\"error\",\"text\":\"Cannot connect to AI model: {exc.reason}\"}}\n\n"
        return
    except Exception as exc:
        yield f"data: {{\"type\":\"error\",\"text\":\"Error contacting AI model: {exc}\"}}\n\n"
        return

    # Send initial event to confirm connection
    yield "data: {\"type\":\"start\"}\n\n"

    buffer = ""
    try:
        while True:
            chunk = resp.read(4096)
            if not chunk:
                break

            buffer += chunk.decode("utf-8", errors="replace")

            # Process complete SSE lines from buffer
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)

                if not line.strip():
                    continue

                # llama-server SSE format: "data: {...}"
                if line.startswith("data: "):
                    data_str = line[6:]  # strip "data: " prefix

                    try:
                        data_obj = json.loads(data_str)

                        # Check for stop signal
                        if data_obj.get("stop", False):
                            break

                        # Extract content token
                        content = data_obj.get("content", "")
                        if content:
                            sse_payload = json.dumps({
                                "type": "chunk",
                                "text": content,
                            })
                            yield f"data: {sse_payload}\n\n"
                    except json.JSONDecodeError:
                        # Skip malformed SSE lines from llama-server
                        pass

    except (ConnectionResetError, BrokenPipeError, OSError) as exc:
        print(f"[server] Stream disconnected: {exc}")
    finally:
        try:
            resp.close()
        except Exception:
            pass

    # Send done event
    yield "data: {\"type\":\"done\"}\n\n"


@app.route("/api/content/search")
def api_content_search():
    """BM25 keyword search over the RAG index."""
    global searcher

    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"error": "q parameter is required"}), 400

    if searcher is None:
        return jsonify({"results": [], "query": query, "error": "Search index not loaded"})

    try:
        results = searcher.search(query, top_k=5)
    except Exception as exc:
        return jsonify({"results": [], "query": query, "error": str(exc)})

    return jsonify({
        "results": [
            {
                "text": chunk_text[:500],  # truncate for response size
                "title": source.get("title", "unknown"),
                "url": source.get("url", ""),
                "source_type": source.get("source_type", ""),
            }
            for chunk_text, source in results
        ],
        "query": query,
        "count": len(results),
    })


@app.route("/api/reindex", methods=["POST"])
def api_reindex():
    """Trigger a re-index of the search index."""
    global pages_indexed, searcher

    try:
        cmd = [
            sys.executable,
            str(RAG_PATH),
            "--rebuild",
            "--content", str(OUTBACK_DIR),
            "--user-content", str(CONTENT_DIR),
            "--index", str(INDEX_PATH),
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

        if result.returncode == 0:
            _load_searcher()
            return jsonify({
                "status": "ok",
                "pages_indexed": pages_indexed,
                "output": result.stdout.strip(),
            })
        else:
            return jsonify({
                "status": "error",
                "error": result.stderr.strip() or f"Exit code {result.returncode}",
            }), 500

    except Exception as exc:
        return jsonify({"status": "error", "error": str(exc)}), 500


@app.route("/outback-safe/")
@app.route("/outback-safe/<path:filename>")
def serve_outback_safe(filename: str = "index.html"):
    """Serve static HTML from the outback-safe/ directory."""
    outback_path = Path(app.config["OUTBACK_DIR"])

    # Security: prevent directory traversal
    requested = outback_path / filename
    try:
        requested.resolve().relative_to(outback_path.resolve())
    except ValueError:
        return jsonify({"error": "Forbidden"}), 403

    if not requested.is_file():
        # Try .html extension
        html_path = outback_path / f"{filename}.html"
        if html_path.is_file():
            return send_from_directory(str(outback_path), f"{filename}.html")

        return jsonify({"error": f"Page not found: {filename}"}), 404

    return send_from_directory(str(outback_path), filename)


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------


@app.errorhandler(404)
def handle_404(e):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def handle_500(e):
    return jsonify({"error": "Internal server error"}), 500


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    global model_name, model_loaded, fallback_mode, pages_indexed, searcher

    print("═" * 60)
    print("  Outback-Safe USB AI Server")
    print("  Offline survival & medical reference assistant")
    print("═" * 60)
    print(f"  USB dir:     {USB_DIR}")
    print(f"  Flask port:  {FLASK_PORT}")
    print(f"  llama port:  {LLAMA_PORT}")
    print()

    # --- Step 1: Detect RAM & select model ---
    ram_gb = detect_ram_gb()
    if ram_gb <= 0:
        print("[server] ⚠️  Could not detect RAM — using default")
        ram_gb = 16  # Assume 16 GB
    
    model_path = MODEL
    model_name = "8B"
    
    if not model_path.is_file():
        sys.exit(f"❌ Model file not found: {model_path}")

    # --- Step 2: Re-index content ---
    try:
        run_reindex()
    except Exception as exc:
        print(f"[server] ⚠️  Re-index failed (non-fatal): {exc}")
        pages_indexed = 0

    # --- Step 3: Launch llama-server ---
    try:
        start_llama_server(model_path)
    except SystemExit:
        raise
    except Exception as exc:
        print(f"[server] ❌ Failed to launch llama-server: {exc}")
        fallback_mode = True
        print("[server] Starting in fallback mode (no AI)…")

    # --- Step 4: Health poll ---
    if not fallback_mode:
        if poll_health():
            model_loaded = True
            print(f"[server] ✅ Model '{model_name}' loaded and healthy")
        else:
            print("[server] ⚠️  llama-server health check timed out after 5 minutes")
            print("[server] Starting in fallback mode (static content only)…")
            fallback_mode = True

    # --- Step 5: Register cleanup ---
    atexit.register(cleanup)

    # --- Step 6: Open browser ---
    if not args.no_browser:
        print(f"[server] Opening browser → {FLASK_URL}")
        try:
            webbrowser.open(FLASK_URL)
        except Exception as exc:
            print(f"[server] ⚠️  Could not open browser: {exc}")

    # --- Step 7: Start Flask ---
    print()
    print("═" * 60)
    if fallback_mode:
        print("  ⚠️  FALLBACK MODE — static content only, no AI chat")
    else:
        print(f"  ✅ AI model loaded: {model_name}")
    print(f"  📚 Pages indexed: {pages_indexed}")
    print(f"  🌐 Flask: {FLASK_URL}")
    print("  Press Ctrl+C to stop")
    print("═" * 60)
    print()
    sys.stdout.flush()

    try:
        app.run(
            host="127.0.0.1",
            port=FLASK_PORT,
            debug=False,
            use_reloader=False,
            threaded=True,
        )
    except KeyboardInterrupt:
        print("\n[server] Shutting down…")
    finally:
        cleanup()


if __name__ == "__main__":
    main()
