#!/usr/bin/env python3
"""
build_search_index.py — BM25 search index builder for SHTF USB offline knowledge base.

Phase 1 build script. Runs during build (Mac mini) and at runtime (USB re-index).
Self-contained: only depends on stdlib + rank_bm25.

Inputs:
  - HTML directory (preprocessed outback-safe pages)
  - Optional user-content directory (.md files with +++ frontmatter)

Output:
  - search_index.json with chunks, tokenized chunks, source metadata, and stats.
"""

import argparse
import hashlib
import json
import os
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Optional, Dict, List, Tuple

# ---------------------------------------------------------------------------
# HTML text extraction
# ---------------------------------------------------------------------------

class MainTextExtractor(HTMLParser):
    """Extract visible text from a specific HTML tag (default: <main>)."""

    def __init__(self, target_tag="main"):
        super().__init__()
        self.target_tag = target_tag.lower()
        self._depth = 0
        self._collecting = False
        self._parts = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == self.target_tag:
            self._collecting = True
            self._depth += 1
        elif self._collecting:
            self._depth += 1

    def handle_endtag(self, tag):
        if self._collecting:
            self._depth -= 1
            if tag.lower() == self.target_tag and self._depth <= 0:
                self._collecting = False
                self._depth = 0

    def handle_data(self, data):
        if self._collecting:
            self._parts.append(data)

    def get_text(self) -> str:
        return " ".join(self._parts).strip()


def extract_html_text(filepath: str) -> str:
    """Extract readable text from an HTML file, preferring <main> then <body>."""
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        raw = f.read()

    # Try <main> first
    extractor = MainTextExtractor("main")
    extractor.feed(raw)
    text = extractor.get_text()
    if text:
        return text

    # Fallback: <body>
    extractor = MainTextExtractor("body")
    extractor.feed(raw)
    text = extractor.get_text()
    if text:
        return text

    # Last resort: strip all tags
    return _strip_all_tags(raw)


def _strip_all_tags(html: str) -> str:
    """Brute-force tag stripping as last-resort fallback."""
    cleaner = re.compile(r"<[^>]+>")
    text = cleaner.sub(" ", html)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# ---------------------------------------------------------------------------
# Markdown parsing
# ---------------------------------------------------------------------------

_FRONTMATTER_RE = re.compile(r"^\+\+\+\s*\n(.*?)\+\+\+\s*\n", re.DOTALL)


def parse_md_file(filepath: str) -> Tuple[str, Optional[str]]:
    """Parse a .md file, returning (body_text, title_or_None).

    Strips +++ frontmatter. If frontmatter contains a 'title:' line, it is
    extracted as the page title.
    """
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        raw = f.read()

    title = None
    body = raw
    m = _FRONTMATTER_RE.match(raw)
    if m:
        fm = m.group(1)
        body = raw[m.end():]  # everything after frontmatter
        # Extract title from frontmatter
        for line in fm.splitlines():
            line = line.strip()
            if line.lower().startswith("title:"):
                title = line.split(":", 1)[1].strip().strip('"').strip("'")
                break

    return body.strip(), title


# ---------------------------------------------------------------------------
# Tokenization
# ---------------------------------------------------------------------------

# Split on non-alphanumeric (preserves CJK etc. but works for English-centric index)
_TOKEN_RE = re.compile(r"[^\w]+", re.UNICODE)


def tokenize(text: str) -> list[str]:
    """Lowercase, split on non-word chars, drop empty tokens."""
    lowered = text.lower()
    tokens = [t for t in _TOKEN_RE.split(lowered) if t]
    return tokens


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------

_HEADING_RE = re.compile(r"^#{1,3}\s+", re.MULTILINE)


def chunk_text(
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> list[str]:
    """Split text into chunks suitable for BM25 indexing.

    Strategy:
      1. Split on ## / ### headings (preserving heading as contextual prefix).
      2. For each heading-section, if it's longer than chunk_size words,
         break into overlapping sliding windows.
    """
    # Step 1: split on markdown headings (## or ###)
    sections = _split_by_headings(text)

    # Step 2: sub-chunk long sections
    chunks = []
    for section in sections:
        words = section.split()
        if len(words) <= chunk_size:
            if words:
                chunks.append(" ".join(words))
        else:
            # Sliding window
            step = chunk_size - chunk_overlap
            if step <= 0:
                step = 1  # safety: avoid infinite loop on bad params
            for i in range(0, len(words), step):
                window = words[i:i + chunk_size]
                if len(window) < 20:  # skip tiny trailing fragments
                    continue
                chunks.append(" ".join(window))
    return chunks


def _split_by_headings(text: str) -> list[str]:
    """Split text at ## and ### markdown headings.

    Each heading becomes the start of a new section. The heading line is
    included at the front of the section text for context.
    """
    # Find all heading positions
    positions = []
    for m in _HEADING_RE.finditer(text):
        positions.append(m.start())

    if not positions:
        return [text] if text.strip() else []

    sections = []
    for i, pos in enumerate(positions):
        start = pos
        end = positions[i + 1] if i + 1 < len(positions) else len(text)
        section = text[start:end].strip()
        if section:
            sections.append(section)

    # Also include text before the first heading if non-trivial
    if positions and positions[0] > 0:
        prefix = text[:positions[0]].strip()
        if prefix and len(prefix.split()) >= 20:
            sections.insert(0, prefix)

    return sections


# ---------------------------------------------------------------------------
# Source title extraction
# ---------------------------------------------------------------------------

def _title_from_html(filepath: str) -> Optional[str]:
    """Try to extract an <h1> or <title> from an HTML file."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            raw = f.read()
    except Exception:
        return None

    # <title> tag
    m = re.search(r"<title[^>]*>(.*?)</title>", raw, re.IGNORECASE | re.DOTALL)
    if m:
        title = _strip_all_tags(m.group(1)).strip()
        if title:
            return title

    # First <h1>
    m = re.search(r"<h1[^>]*>(.*?)</h1>", raw, re.IGNORECASE | re.DOTALL)
    if m:
        title = _strip_all_tags(m.group(1)).strip()
        if title:
            return title

    return None


def _source_title(filepath: str, is_md: bool = False, md_title: Optional[str] = None) -> str:
    """Determine a human-readable title for a source file."""
    if md_title:
        return md_title
    if is_md:
        # MD file without frontmatter title → use filename stem
        return Path(filepath).stem.replace("-", " ").replace("_", " ").title()
    # HTML: try <h1>/<title>, else filename stem
    html_title = _title_from_html(filepath)
    if html_title:
        return html_title
    return Path(filepath).stem.replace("-", " ").replace("_", " ").title()


def _source_url(filepath: str, base_dir: str) -> str:
    """Convert absolute filepath to a relative URL."""
    rel = os.path.relpath(filepath, base_dir)
    return rel


# ---------------------------------------------------------------------------
# Main index-building logic
# ---------------------------------------------------------------------------

def build_index(
    content_dir: str,
    user_content_dir: Optional[str],
    chunk_size: int,
    chunk_overlap: int,
) -> dict:
    """Build the complete search index from HTML and optional MD sources.

    Returns a dict suitable for JSON serialization.
    """
    chunks: list[str] = []          # raw text chunks
    tokenized_chunks: list[list[str]] = []  # tokenized for BM25 reconstruction
    sources: list[dict] = []         # per-chunk metadata
    seen_files: set[str] = set()     # dedupe by filename

    # --- Process HTML directory ---
    html_dir = Path(content_dir)
    if html_dir.is_dir():
        html_files = sorted(html_dir.rglob("*.html"))
        for fp in html_files:
            fname = fp.name.lower()
            # Skip index.html files (self-referential)
            if fname == "index.html" or fp.name.lower().startswith("index."):
                continue
            if fp.name in seen_files:
                continue
            seen_files.add(fp.name)

            text = extract_html_text(str(fp))
            if not text or len(text.split()) < 20:
                continue

            section_chunks = chunk_text(text, chunk_size, chunk_overlap)
            title = _source_title(str(fp), is_md=False)
            url = _source_url(str(fp), content_dir)

            for ch in section_chunks:
                chunks.append(ch)
                tokenized_chunks.append(tokenize(ch))
                sources.append({
                    "title": title,
                    "url": url,
                    "source_type": "html",
                })

    # --- Process user-content directory ---
    if user_content_dir:
        md_dir = Path(user_content_dir)
        if md_dir.is_dir():
            md_files = sorted(md_dir.rglob("*.md"))
            for fp in md_files:
                if fp.name in seen_files:
                    continue
                seen_files.add(fp.name)

                body, md_title = parse_md_file(str(fp))
                if not body or len(body.split()) < 20:
                    continue

                section_chunks = chunk_text(body, chunk_size, chunk_overlap)
                title = _source_title(str(fp), is_md=True, md_title=md_title)
                url = _source_url(str(fp), user_content_dir)

                for ch in section_chunks:
                    chunks.append(ch)
                    tokenized_chunks.append(tokenize(ch))
                    sources.append({
                        "title": title,
                        "url": url,
                        "source_type": "user",
                    })

    # --- Compute unique pages ---
    unique_pages = set()
    for src in sources:
        unique_pages.add((src["title"], src["url"], src["source_type"]))

    index = {
        "chunks": chunks,
        "tokenized_chunks": tokenized_chunks,
        "sources": sources,
        "total_pages": len(unique_pages),
        "total_chunks": len(chunks),
    }

    # --- Build BM25Okapi model and embed its parameters ---
    if tokenized_chunks:
        from rank_bm25 import BM25Okapi
        bm25 = BM25Okapi(tokenized_chunks)

        # Serialize the BM25 state so search code can reconstruct it without
        # recomputing IDF/doc_freqs (important: idf uses float32 keys).
        index["bm25"] = {
            "corpus_size": bm25.corpus_size,
            "avgdl": float(bm25.avgdl),
            "doc_len": [int(dl) for dl in bm25.doc_len],
            "doc_freqs": bm25.doc_freqs,   # dict[str, float]
            "idf": {k: float(v) for k, v in bm25.idf.items()},  # dict[str, float]
            "k1": float(bm25.k1),
            "b": float(bm25.b),
            "epsilon": float(bm25.epsilon),
        }
    else:
        index["bm25"] = {
            "corpus_size": 0,
            "avgdl": 0.0,
            "doc_len": [],
            "doc_freqs": {},
            "idf": {},
            "k1": 1.5,
            "b": 0.75,
            "epsilon": 0.25,
        }

    return index


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Build BM25 search index for offline knowledge base"
    )
    parser.add_argument(
        "--content",
        required=True,
        help="Path to directory containing preprocessed HTML files",
    )
    parser.add_argument(
        "--user-content",
        default=None,
        help="Optional path to directory containing user .md files (+++ frontmatter)",
    )
    parser.add_argument(
        "--output",
        default="search_index.json",
        help="Output path for search_index.json (default: search_index.json)",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=500,
        help="Maximum words per chunk (default: 500)",
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=50,
        help="Overlap between adjacent chunks in words (default: 50)",
    )
    args = parser.parse_args()

    # Validate inputs
    if not os.path.isdir(args.content):
        print(f"Error: --content directory not found: {args.content}", file=sys.stderr)
        sys.exit(1)

    if args.user_content and not os.path.isdir(args.user_content):
        print(f"Warning: --user-content directory not found: {args.user_content} (skipping)", file=sys.stderr)
        args.user_content = None

    if args.chunk_overlap >= args.chunk_size:
        print(f"Error: --chunk-overlap ({args.chunk_overlap}) must be less than --chunk-size ({args.chunk_size})",
              file=sys.stderr)
        sys.exit(1)

    # Build
    print(f"Building BM25 index from: {args.content}")
    if args.user_content:
        print(f"  + user content: {args.user_content}")
    print(f"  chunk_size={args.chunk_size}, overlap={args.chunk_overlap}")

    index = build_index(
        content_dir=args.content,
        user_content_dir=args.user_content,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
    )

    # Write output
    out_path = args.output
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    # Stats
    n_chunks = index["total_chunks"]
    n_pages = index["total_pages"]
    print(f"✅ BM25 index: {n_chunks} chunks from {n_pages} sources")
    print(f"   Output: {os.path.abspath(out_path)} ({os.path.getsize(out_path):,} bytes)")


if __name__ == "__main__":
    main()
