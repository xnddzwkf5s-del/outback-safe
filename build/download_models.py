#!/usr/bin/env python3
"""
Download GGUF models from HuggingFace with SHA256 verification.

Usage:
    python3 download_models.py --output /path/to/models
"""

import argparse
import hashlib
import os
import sys
import time
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


# ---------------------------------------------------------------------------
# Model registry
# ---------------------------------------------------------------------------

MODELS = [
    {
        "url": "https://huggingface.co/bartowski/Qwen2.5-3B-Instruct-GGUF/resolve/main/Qwen2.5-3B-Instruct-Q4_K_M.gguf",
        "filename": "qwen2.5-3b-q4.gguf",
        "sha256": None,  # Update when available
    },
    {
        "url": "https://huggingface.co/bartowski/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/Qwen2.5-1.5B-Instruct-Q4_K_M.gguf",
        "filename": "qwen2.5-1.5b-q4.gguf",
        "sha256": None,  # Update when available
    },
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _human_size(n: int) -> str:
    """Return a human-readable size string from a byte count."""
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"


def _sha256_path(path: str) -> str:
    """Compute the SHA-256 hex digest of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(1 << 20):  # 1 MiB reads
            h.update(chunk)
    return h.hexdigest()


def _verify(path: str, expected: str | None) -> tuple[bool, str]:
    """
    Verify *path* against *expected* SHA-256.

    Returns (True, "") on match.
    Returns (False, reason) otherwise.
    """
    if expected is None:
        print("  ⚠  SHA-256 not known — skipping integrity check")
        return (False, "no expected hash")
    actual = _sha256_path(path)
    if actual == expected:
        return (True, "")
    return (False, f"hash mismatch: expected {expected[:16]}…, got {actual[:16]}…")


def _download(url: str, dest: str) -> bool:
    """
    Download *url* to *dest* with progress output.  Returns True on success.
    """
    retries = 1
    for attempt in range(retries + 1):
        try:
            req = Request(url, headers={"User-Agent": "SHTF-USB-download-script/1.0"})
            with urlopen(req, timeout=30) as resp:
                total = resp.headers.get("Content-Length")
                total = int(total) if total else None
                downloaded = 0
                start = time.monotonic()
                with open(dest, "wb") as f:
                    while True:
                        chunk = resp.read(1 << 20)  # 1 MiB
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total:
                            pct = downloaded / total * 100
                            elapsed = time.monotonic() - start or 0.001
                            rate = downloaded / elapsed
                            print(
                                f"\r  ↓ {_human_size(downloaded)} / {_human_size(total)} "
                                f"({pct:.0f}%)  {_human_size(rate)}/s   ",
                                end="",
                                flush=True,
                            )
                    print()  # newline after progress
            return True
        except (URLError, HTTPError, OSError) as exc:
            print(f"\n  ✗ Download failed (attempt {attempt + 1}): {exc}")
            if attempt < retries:
                print("  ↻ Retrying in 3 seconds…")
                time.sleep(3)
                if os.path.exists(dest):
                    os.remove(dest)
            else:
                if os.path.exists(dest):
                    os.remove(dest)
    return False


def _write_sha256_file(model_path: str, sha256_path: str):
    """Persist the SHA-256 digest to a sibling .sha256 file."""
    digest = _sha256_path(model_path)
    with open(sha256_path, "w") as fh:
        fh.write(f"{digest}  {os.path.basename(model_path)}\n")
    print(f"  ✓ Wrote checksum → {sha256_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Download GGUF models from HuggingFace with SHA-256 verification."
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Directory to save downloaded model files",
    )
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)
    errors = 0

    for model in MODELS:
        dest = os.path.join(args.output, model["filename"])
        sha256_sidecar = dest + ".sha256"

        print(f"\n{'─' * 60}")
        print(f"Model: {model['filename']}")
        print(f"URL:   {model['url']}")

        # --- Already downloaded and valid? ---
        if os.path.exists(dest):
            size = _human_size(os.path.getsize(dest))
            print(f"  File exists ({size}), verifying…")
            ok, reason = _verify(dest, model["sha256"])
            if ok:
                print(f"  ✓ SHA-256 matches — skipping download")
                if not os.path.exists(sha256_sidecar):
                    _write_sha256_file(dest, sha256_sidecar)
                continue
            if model["sha256"] is None:
                # No expected hash; reuse the file as-is
                print(f"  → Keeping existing file (no expected hash to validate)")
                if not os.path.exists(sha256_sidecar):
                    _write_sha256_file(dest, sha256_sidecar)
                continue
            print(f"  ✗ {reason} — re-downloading…")

        # --- Download ---
        if not _download(model["url"], dest):
            print(f"  ✗ FAILED to download {model['filename']}")
            errors += 1
            continue

        size = _human_size(os.path.getsize(dest))
        print(f"  ✓ Downloaded ({size})")

        # --- Verify ---
        ok, reason = _verify(dest, model["sha256"])
        if model["sha256"] is not None and not ok:
            print(f"  ✗ SHA-256 verification failed: {reason}")
            print(f"  → Corrupted file left at {dest} for inspection")
            errors += 1
            continue

        # --- Write sidecar ---
        _write_sha256_file(dest, sha256_sidecar)

    print(f"\n{'─' * 60}")
    if errors:
        print(f"Done — {errors} model(s) failed to download.")
        sys.exit(1)
    else:
        print("Done — all models downloaded and verified.")


if __name__ == "__main__":
    main()
