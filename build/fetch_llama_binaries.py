#!/usr/bin/env python3
"""
Download pre-built llama-server binaries from llama.cpp GitHub releases.

Usage:
    python3 fetch_llama_binaries.py --tag b10107 --output /path/to/bin
    python3 fetch_llama_binaries.py --tag b10107 --output /path/to/bin --platform mac
    python3 fetch_llama_binaries.py --tag b10107 --output /path/to/bin --platform win64
    python3 fetch_llama_binaries.py --tag b10107 --output /path/to/bin --platform all
"""

import argparse
import hashlib
import os
import shutil
import stat
import sys
import tarfile
import tempfile
import time
import zipfile
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


# ---------------------------------------------------------------------------
# Binary definitions
# ---------------------------------------------------------------------------

LLAMA_REPO = "ggml-org/llama.cpp"  # Correct repo (not ggerganov/llama.cpp)

# Each entry maps an arch label to a GitHub release asset name and an output basename.
BINARIES = [
    {
        "arch": "arm64",
        "asset": "llama-{tag}-bin-macos-arm64.tar.gz",
        "output": "llama-server-arm64",
    },
    {
        "arch": "amd64",
        "asset": "llama-{tag}-bin-macos-x64.tar.gz",
        "output": "llama-server-x64",
    },
]

RELEASE_URL = f"https://github.com/{LLAMA_REPO}/releases/download"
BINARY_NAME = "llama-server"


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


def _download(url: str, dest: str) -> bool:
    """
    Download *url* to *dest* with progress output.  Returns True on success.
    """
    retries = 1
    for attempt in range(retries + 1):
        try:
            req = Request(url, headers={"User-Agent": "SHTF-USB-fetch-llama/1.0"})
            with urlopen(req, timeout=60) as resp:
                total = resp.headers.get("Content-Length")
                total = int(total) if total else None
                downloaded = 0
                start = time.monotonic()
                with open(dest, "wb") as f:
                    while True:
                        chunk = resp.read(1 << 20)
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
                    print()
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


def _find_binary(tar_dir: str, name: str) -> str | None:
    """
    Walk *tar_dir* and return the path to the file named *name*.

    The llama.cpp release tarballs sometimes wrap files in a top-level
    directory, so a flat listing is not guaranteed.
    """
    for root, _dirs, files in os.walk(tar_dir):
        for filename in files:
            if filename == name:
                return os.path.join(root, filename)
    return None


def _set_executable(path: str):
    """Add owner-execute permission to *path*."""
    st = os.stat(path)
    os.chmod(path, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


# ---------------------------------------------------------------------------
# Windows binary fetch
# ---------------------------------------------------------------------------

def _get_win_url(tag: str) -> str:
    """Return Windows CPU x64 download URL."""
    return f"{RELEASE_URL}/{tag}/llama-{tag}-bin-win-cpu-x64.zip"


def fetch_windows_binary(output_dir: str, tag: str) -> None:
    """Download Windows x64 llama-server + all .dll dependencies."""
    win_url = _get_win_url(tag)
    print(f"\n{'─' * 60}")
    print(f"Platform: win64 (Windows x64)")
    print(f"URL:      {win_url}")

    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
        tmp_name = tmp.name

    try:
        if not _download(win_url, tmp_name):
            print("  ✗ FAILED to download Windows binary")
            return

        with tempfile.TemporaryDirectory() as tmpdir:
            with zipfile.ZipFile(tmp_name, "r") as zf:
                zf.extractall(tmpdir)

            # Find llama-server.exe
            found_exe = None
            found_dlls = []
            for root, dirs, files in os.walk(tmpdir):
                for f in files:
                    src = os.path.join(root, f)
                    if f == "llama-server.exe":
                        found_exe = src
                    elif f.endswith(".dll"):
                        found_dlls.append(src)

            if not found_exe:
                raise FileNotFoundError("llama-server.exe not found in Windows archive")

            # Copy llama-server.exe
            dest = os.path.join(output_dir, "llama-server-win64.exe")
            shutil.copy2(found_exe, dest)
            exe_size = _human_size(os.path.getsize(dest))
            print(f"  ✓ llama-server-win64.exe ({exe_size})")

            # Copy ALL .dll dependencies (lesson from macOS bug #1)
            dll_count = 0
            for dll_src in found_dlls:
                dll_name = os.path.basename(dll_src)
                shutil.copy2(dll_src, os.path.join(output_dir, dll_name))
                dll_count += 1
            print(f"  ✓ {dll_count} .dll files copied")

            # Write SHA256 for verification
            sha = hashlib.sha256()
            with open(dest, "rb") as f:
                while chunk := f.read(8192):
                    sha.update(chunk)
            sha_path = os.path.join(output_dir, ".sha256")
            with open(sha_path, "a") as f:
                f.write(f"{sha.hexdigest()}  llama-server-win64.exe\n")
            print(f"  ✓ SHA256 saved to .sha256")
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Download pre-built llama-server binaries from llama.cpp releases."
    )
    parser.add_argument(
        "--tag",
        default="b10107",
        help="llama.cpp release tag to fetch (default: b10107)",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Directory to save extracted binaries",
    )
    parser.add_argument(
        "--platform",
        choices=["mac", "win64", "all"],
        default="mac",
        help="Platform to download binaries for (default: mac)",
    )
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)
    errors = 0

    with tempfile.TemporaryDirectory(prefix="llama-fetch-") as tmpdir:
        # ── macOS binaries ──
        if args.platform in ("mac", "all"):
            for entry in BINARIES:
                asset = entry["asset"].format(tag=args.tag)
                url = f"{RELEASE_URL}/{args.tag}/{asset}"
                out_path = os.path.join(args.output, entry["output"])

                print(f"\n{'─' * 60}")
                print(f"Arch:     {entry['arch']}")
                print(f"Asset:    {asset}")
                print(f"URL:      {url}")
                print(f"Output:   {out_path}")

                # --- Download tarball ---
                tarball = os.path.join(tmpdir, asset)
                if not _download(url, tarball):
                    print(f"  ✗ FAILED to download {asset}")
                    errors += 1
                    continue

                tarball_size = _human_size(os.path.getsize(tarball))
                print(f"  ✓ Downloaded tarball ({tarball_size})")

                # --- Extract ---
                extract_dir = os.path.join(tmpdir, entry["arch"])
                os.makedirs(extract_dir, exist_ok=True)
                try:
                    with tarfile.open(tarball, "r:gz") as tf:
                        tf.extractall(path=extract_dir, filter="data")
                except (tarfile.TarError, OSError) as exc:
                    print(f"  ✗ Failed to extract tarball: {exc}")
                    errors += 1
                    continue

                # --- Copy entire build directory (includes dylibs needed by llama-server) ---
                build_root = None
                for root, _dirs, files in os.walk(extract_dir):
                    if any(f.endswith('.dylib') for f in files) and BINARY_NAME in files:
                        build_root = root
                        break
                if build_root is None:
                    # Fallback: just find the binary
                    binary_src = _find_binary(extract_dir, BINARY_NAME)
                    if binary_src is None:
                        print(f"  ✗ '{BINARY_NAME}' not found in extracted archive")
                        errors += 1
                        continue
                    shutil.copy2(binary_src, out_path)
                    _set_executable(out_path)
                else:
                    # Copy ALL files from the build directory to output
                    copied = 0
                    for f in os.listdir(build_root):
                        src = os.path.join(build_root, f)
                        dst = os.path.join(args.output, f)
                        if os.path.isfile(src):
                            shutil.copy2(src, dst)
                            if f == BINARY_NAME or f.startswith('lib'):
                                _set_executable(dst)
                            copied += 1
                    # Also update the arch-specific binary pointer
                    if os.path.exists(os.path.join(args.output, BINARY_NAME)):
                        shutil.copy2(os.path.join(args.output, BINARY_NAME), out_path)
                        _set_executable(out_path)
                    print(f"  ✓ Extracted full build → {entry['output']} (+ {copied} .dylib files)")

        # ── Windows binary ──
        if args.platform in ("win64", "all"):
            try:
                fetch_windows_binary(args.output, args.tag)
            except Exception as exc:
                print(f"  ✗ FAILED to fetch Windows binary: {exc}")
                errors += 1

    print(f"\n{'─' * 60}")
    if errors:
        print(f"Done — {errors} binary fetch(es) failed.")
        sys.exit(1)
    else:
        print("Done — all binaries fetched and extracted.")


if __name__ == "__main__":
    main()
