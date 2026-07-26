#!/usr/bin/env python3
"""
bundle_deps.py — Bundle Python dependencies for offline SHTF USB.

Pip-installs Flask + rank_bm25 + numpy into platform-specific directories
so the SHTF USB works cross-platform (macOS arm64/x64 and Windows).

Usage:
    python3 bundle_deps.py --output <BUILD_OUTPUT_DIR>
    python3 bundle_deps.py --output <BUILD_OUTPUT_DIR> --platform mac
    python3 bundle_deps.py --output <BUILD_OUTPUT_DIR> --platform win64
    python3 bundle_deps.py --output <BUILD_OUTPUT_DIR> --platform all

Output structure:
    <output>/
        deps-arm64/     # Apple Silicon deps
        deps-x64/       # Intel Mac deps
        deps-win64/     # Windows amd64 deps
"""

import argparse
import os
import platform
import shutil
import subprocess
import sys


# ── Constants ────────────────────────────────────────────────────────────────

PACKAGES = ["flask", "rank_bm25"]

# Platform tags for cross-compilation
CROSS_PLATFORM_MAP = {
    "arm64": {
        "name": "x64",
        "target": "deps-x64",
        "platform": "macosx_10_15_x86_64",
    },
    "x86_64": {
        "name": "arm64",
        "target": "deps-arm64",
        "platform": "macosx_11_0_arm64",
    },
}

# Windows deps — pure-Python transitive deps that need explicit bundling
WIN_TRANSITIVE_DEPS = [
    "blinker",
    "click",
    "itsdangerous",
    "jinja2",
    "markupsafe",
    "werkzeug",
]


# ── Helpers ──────────────────────────────────────────────────────────────────

def detect_arch() -> str:
    """Return normalized arch string: 'arm64' or 'x86_64'."""
    machine = platform.machine()
    if machine == "arm64":
        return "arm64"
    if machine in ("x86_64", "amd64", "i386"):
        return "x86_64"
    print(f"⚠️  Unknown architecture: {machine}. Assuming x86_64.")
    return "x86_64"


def detect_python_version() -> str:
    """Return 'major.minor' Python version string (e.g. '3.12')."""
    return f"{sys.version_info.major}.{sys.version_info.minor}"


def strip_pycache(target_dir: str) -> int:
    """Remove all __pycache__ directories under target_dir. Returns count removed."""
    count = 0
    for root, dirs, _files in os.walk(target_dir, topdown=False):
        if root.endswith("__pycache__"):
            shutil.rmtree(root, ignore_errors=True)
            count += 1
    return count


def pip_install(target_dir: str, packages: list[str], platform_tag: str | None = None) -> bool:
    """
    Run pip install --target <target_dir> for the given packages.
    If platform_tag is provided, cross-compile with --platform and --only-binary.

    Returns True on success, False on failure.
    """
    python_version = detect_python_version()
    cmd = [
        sys.executable, "-m", "pip", "install",
        "--target", target_dir,
    ]
    if platform_tag:
        cmd += [
            "--platform", platform_tag,
            "--python-version", python_version,
            "--only-binary", ":all:",
        ]
    cmd += packages

    label = "cross-compile" if platform_tag else "native"
    suffix = f" ({platform_tag})" if platform_tag else ""
    print(f"\n📦 [{label}] pip install{suffix} into {target_dir}")

    try:
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ pip install failed (exit {e.returncode})")
        return False


def bundle_win_deps(output_dir: str) -> bool:
    """Bundle Windows Python deps (Flask + rank_bm25 + numpy)."""
    dest = os.path.join(output_dir, "deps-win64")
    os.makedirs(dest, exist_ok=True)

    python_version = detect_python_version()
    platform_tag = "win_amd64"

    print(f"\n{'─' * 60}")
    print(f"Platform: Windows amd64 ({platform_tag})")
    print(f"Target:   {dest}")

    # Install main packages
    result = subprocess.run([
        sys.executable, "-m", "pip", "install",
        "--target", dest,
        "--platform", platform_tag,
        "--python-version", python_version,
        "--only-binary", ":all:",
        "--no-deps",
        "flask", "rank_bm25",
    ], capture_output=True, text=True)

    if result.returncode != 0:
        print(f"⚠️  Could not install main Windows packages:")
        print(f"    {result.stderr.strip()[-300:]}")
        print(f"    You may need to run 'pip install --target {dest} flask rank_bm25'")
        print(f"    on an actual Windows machine with Python {python_version}.")
        return False

    # Install numpy separately (C extensions, platform-specific)
    numpy_result = subprocess.run([
        sys.executable, "-m", "pip", "install",
        "--target", dest,
        "--platform", platform_tag,
        "--python-version", python_version,
        "--only-binary", ":all:",
        "--no-deps",
        "numpy",
    ], capture_output=True, text=True)

    if numpy_result.returncode != 0:
        print(f"⚠️  Could not install numpy for Windows:")
        print(f"    {numpy_result.stderr.strip()[-200:]}")
        print(f"    numpy may need to be installed manually on Windows.")
    else:
        print(f"  ✓ numpy installed")

    # Install remaining pure-Python transitive deps
    for dep in WIN_TRANSITIVE_DEPS:
        subprocess.run([
            sys.executable, "-m", "pip", "install",
            "--target", dest,
            "--platform", platform_tag,
            "--python-version", python_version,
            "--only-binary", ":all:",
            "--no-deps",
            dep,
        ], capture_output=True)  # Non-fatal if already installed

    n_removed = strip_pycache(dest)
    if n_removed:
        print(f"  🧹 Stripped {n_removed} __pycache__ dirs from deps-win64")

    print(f"  ✅ deps-win64 — Flask + rank_bm25 + numpy (Windows amd64)")

    # If cross-compile partially failed, note it for manual build
    if result.returncode != 0:
        print(f"⚠️  Could not install all Windows deps from macOS:")
        print(f"    {result.stderr.strip()[-200:]}")
        print(f"    You may need to run 'pip install --target {dest} flask rank_bm25 numpy'")
        print(f"    on an actual Windows machine with Python {python_version}.")

    return result.returncode == 0


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Bundle Python deps for SHTF USB (Flask + rank_bm25)"
    )
    parser.add_argument(
        "--output", required=True,
        help="Build output directory (e.g. build/output)"
    )
    parser.add_argument(
        "--platform",
        choices=["mac", "win64", "all"],
        default="mac",
        help="Platform to bundle deps for (default: mac)",
    )
    args = parser.parse_args()

    arch = detect_arch()
    python_version = detect_python_version()

    print(f"🖥️  Host: {arch} | Python {python_version}")
    print(f"📂 Output: {args.output}")
    print(f"📦 Packages: {', '.join(PACKAGES)}")

    os.makedirs(args.output, exist_ok=True)

    # ── Step 1: Native install for current arch ──────────────────────────
    if args.platform in ("mac", "all"):
        native_target = "deps-arm64" if arch == "arm64" else "deps-x64"
        native_dir = os.path.join(args.output, native_target)
        os.makedirs(native_dir, exist_ok=True)

        if not pip_install(native_dir, PACKAGES):
            print(f"❌ Native install failed for {native_target}. Aborting.")
            sys.exit(1)

        n_removed = strip_pycache(native_dir)
        if n_removed:
            print(f"🧹 Stripped {n_removed} __pycache__ dirs from {native_target}")

        # ── Step 2: Cross-compile for the OTHER arch ─────────────────────
        if arch in CROSS_PLATFORM_MAP:
            cross_cfg = CROSS_PLATFORM_MAP[arch]
            cross_dir = os.path.join(args.output, cross_cfg["target"])
            os.makedirs(cross_dir, exist_ok=True)

            print(f"\n🔄 Cross-compiling for {cross_cfg['name']} ({cross_cfg['platform']})...")

            if pip_install(cross_dir, PACKAGES, platform_tag=cross_cfg["platform"]):
                n_removed = strip_pycache(cross_dir)
                if n_removed:
                    print(f"🧹 Stripped {n_removed} __pycache__ dirs from {cross_cfg['target']}")
                print(f"✅ Cross-compile {cross_cfg['name']} OK")
            else:
                print(f"⚠️  Cross-compile for {cross_cfg['name']} failed.")
                print("   USB will still work on the current architecture only.")
                # Clean up failed partial install so we don't ship broken deps
                if os.path.exists(cross_dir):
                    shutil.rmtree(cross_dir, ignore_errors=True)

    # ── Step 3: Windows deps ─────────────────────────────────────────────
    if args.platform in ("win64", "all"):
        bundle_win_deps(args.output)

    print("\n✅ bundle_deps.py complete.")


if __name__ == "__main__":
    main()
