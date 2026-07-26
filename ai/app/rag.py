#!/usr/bin/env python3
"""
SHTF USB — Retrieval-Augmented Generation (RAG) module.

Loads a pre-built BM25 search index (search_index.json), rebuilds the
BM25Okapi ranker in memory, and exposes a Searcher class for server.py.

Also provides a needs_reindex() check and a CLI mode (--rebuild /
--rebuild-if-older) that imports build_search_index to rebuild the index
from source content directories.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import List, Optional, Tuple

from rank_bm25 import BM25Okapi

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

_WORD_RE = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> List[str]:
    """Lower-case → split on non-alphanumeric → drop empties."""
    return _WORD_RE.findall(text.lower())


# ---------------------------------------------------------------------------
# Searcher
# ---------------------------------------------------------------------------

class Searcher:
    """BM25 search over Outback Safe + user markdown chunks."""

    def __init__(self, index_path: str):
        """Load *index_path* (JSON) and rebuild the BM25Okapi ranker.

        If the file is missing or malformed the Searcher starts empty
        (``search()`` will return ``[]``).
        """
        self._chunks: List[str] = []
        self._sources: List[dict] = []
        self._chunk_source_map: List[int] = []
        self._bm25: Optional[BM25Okapi] = None
        self._corpus: List[List[str]] = []

        try:
            raw = Path(index_path).read_text(encoding="utf-8")
        except (FileNotFoundError, OSError):
            sys.stderr.write(f"[rag] WARNING – index not found: {index_path}\n")
            return

        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            sys.stderr.write(f"[rag] WARNING – invalid JSON in {index_path}: {exc}\n")
            return

        chunks_cfg = data.get("chunks", [])
        sources_raw = data.get("sources", [])

        if not chunks_cfg:
            sys.stderr.write(f"[rag] WARNING – index has no chunks: {index_path}\n")
            return

        # Collect text + source_idx mapping (filter empty-text chunks).
        texts: List[str] = []
        source_map: List[int] = []
        for idx, c in enumerate(chunks_cfg):
            if isinstance(c, str):
                # Flat string format from build_search_index.py
                text = c.strip()
                source_idx = idx if idx < len(sources_raw) else 0
            else:
                # Object format: {"text": "...", "source_idx": N}
                text = (c.get("text") or "").strip()
                source_idx = c.get("source_idx", 0)
            if not text:
                continue
            texts.append(text)
            source_map.append(source_idx)

        self._chunks = texts
        self._chunk_source_map = source_map
        self._corpus = [tokenize(t) for t in self._chunks]

        # Keep sources aligned with chunk -> source_idx references.
        self._sources = sources_raw

        if self._corpus:
            self._bm25 = BM25Okapi(self._corpus)
            print(
                f"[rag] Loaded index: {len(self._chunks)} chunks "
                f"from {len(sources_raw)} sources"
            )

    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, dict]]:
        """Return up to *top_k* ``(chunk_text, source_dict)`` pairs.

        Chunks with a BM25 score ≤ 0 are dropped.  If the index is
        empty an empty list is returned.
        """
        if self._bm25 is None or not self._corpus or not query.strip():
            return []

        tokens = tokenize(query)
        scores = self._bm25.get_scores(tokens)

        # Zip, filter, sort, slice top_k — keep it readable.
        hits = []
        for idx, score in enumerate(scores):
            if score <= 0:
                continue
            source = (
                self._sources[self._get_source_idx(idx)]
                if self._sources
                else {}
            )
            hits.append((score, self._chunks[idx], source))

        hits.sort(key=lambda x: x[0], reverse=True)
        return [(chunk, src) for _, chunk, src in hits[:top_k]]

    # ------------------------------------------------------------------ helpers

    def _get_source_idx(self, chunk_idx: int) -> int:
        """Return the source index for a chunk, clamped to valid range."""
        if 0 <= chunk_idx < len(self._chunk_source_map):
            src_idx = self._chunk_source_map[chunk_idx]
            if 0 <= src_idx < len(self._sources):
                return src_idx
        return 0


# ---------------------------------------------------------------------------
# needs_reindex
# ---------------------------------------------------------------------------

def needs_reindex(user_content_dir: str, index_path: str) -> bool:
    """Return ``True`` if the BM25 index is stale or missing.

    An index is considered stale when **any** ``.md`` file in
    *user_content_dir* has an mtime newer than the index file's mtime.

    If *user_content_dir* does not exist it is treated as empty (no
    user files → staleness is driven by the index existence alone).
    """
    if not os.path.isfile(index_path):
        return True

    try:
        index_mtime = os.path.getmtime(index_path)
    except OSError:
        return True

    user_dir = Path(user_content_dir)
    if not user_dir.is_dir():
        # No user content to trigger a rebuild.
        return False

    try:
        for md_file in user_dir.rglob("*.md"):
            try:
                if md_file.stat().st_mtime > index_mtime:
                    return True
            except OSError:
                pass
    except OSError:
        pass

    return False


# ---------------------------------------------------------------------------
# CLI  (python3 rag.py --rebuild | --rebuild-if-older …)
# ---------------------------------------------------------------------------

def _rebuild(content_dir: str, user_content_dir: str, index_path: str) -> None:
    """Import build_search_index and rebuild the JSON index."""
    try:
        import build_search_index  # type: ignore[import-not-found]
    except ImportError:
        sys.exit(
            "ERROR – cannot import build_search_index. "
            "Make sure build_search_index.py is in the same directory "
            f"({Path(__file__).parent})."
        )

    if not hasattr(build_search_index, "build_index"):
        sys.exit(
            "ERROR – build_search_index module has no build_index() function."
        )

    print(f"[rag] Rebuilding index → {index_path}")
    build_search_index.build_index(
        content=content_dir,
        user_content=user_content_dir,
        index_path=index_path,
        chunk_size=500,
        chunk_overlap=50,
    )

    # Quick verification — re-load and print stats.
    try:
        data = json.loads(Path(index_path).read_text(encoding="utf-8"))
        n_chunks = len(data.get("chunks", []))
        n_sources = len(data.get("sources", []))
        print(f"✅ Re-indexed {n_chunks} chunks from {n_sources} sources")
    except Exception:
        print("✅ Re-index complete (could not verify stats)")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="RAG CLI — search index load / rebuild helper"
    )
    parser.add_argument(
        "--content",
        default="outback-safe/",
        help="Path to Outback Safe content directory (default: outback-safe/)",
    )
    parser.add_argument(
        "--user-content",
        default="content/",
        help="Path to user .md content directory (default: content/)",
    )
    parser.add_argument(
        "--index",
        default="search_index.json",
        help="Path to search index JSON file (default: search_index.json)",
    )

    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--rebuild",
        action="store_true",
        help="Force rebuild the search index.",
    )
    mode.add_argument(
        "--rebuild-if-older",
        action="store_true",
        help="Rebuild only if user content is newer than the index.",
    )

    args = parser.parse_args()

    if args.rebuild:
        _rebuild(args.content, args.user_content, args.index)
    elif args.rebuild_if_older:
        if needs_reindex(args.user_content, args.index):
            _rebuild(args.content, args.user_content, args.index)
        else:
            print("[rag] Index is up-to-date — nothing to do.")
    else:
        # No mode specified — just verify the index can load.
        searcher = Searcher(args.index)
        if searcher._bm25 is not None:
            print(
                f"[rag] Index is valid ({len(searcher._chunks)} chunks). "
                f"Use --rebuild to force rebuild, --rebuild-if-older for "
                f"conditional rebuild."
            )
        else:
            print("[rag] Index is empty or missing. Use --rebuild to create it.")


if __name__ == "__main__":
    main()
