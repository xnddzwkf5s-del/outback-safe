#!/usr/bin/env python3
"""
preprocess.py — Preprocess Obsidian vault to flat HTML for SHTF USB.

Reads .md files with +++ TOML frontmatter and Zola shortcodes
(warning, steps, info, tip, materials), outputs flat .html files
with dark mode, responsive viewport, navigation, and disclaimer footer.

Usage:
    python3 preprocess.py --source "VAULT_PATH" --output "OUTPUT_DIR"
"""

import os
import re
import sys
import argparse
import shutil
from pathlib import Path

# ---------------------------------------------------------------------------
# Regex patterns
# ---------------------------------------------------------------------------

# Close-tag checked BEFORE open-tag so {% end %} is not captured as a
# shortcode name.
SHORTCODE_CLOSE_RE = re.compile(r'\{%\s*end\s*%\}')

# Matches {% warning() %}, {% warning %}, {% steps() %}, {% steps %}, etc.
SHORTCODE_OPEN_RE = re.compile(
    r'\{%\s*(warning|steps|info|tip|materials)\s*(?:\(\))?\s*%\}'
)

# +++ TOML frontmatter block
FRONTMATTER_RE = re.compile(
    r'^\+\+\+\s*\n(.*?)\n\+\+\+\s*\n', re.DOTALL
)

# Block-level patterns for markdown conversion
TABLE_SEPARATOR_RE = re.compile(r'^\|[\s\-:|]+\|$')
HEADING_RE = re.compile(r'^(#{1,6})\s+(.*?)$')
HR_RE = re.compile(r'^[-*_]{3,}\s*$')
UL_ITEM_RE = re.compile(r'^(\s*)[-*+]\s+(.*?)$')
OL_ITEM_RE = re.compile(r'^(\s*)\d+\.\s+(.*?)$')

# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def escape_html(text):
    """Escape HTML special characters in plain text."""
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def parse_frontmatter(text):
    """Parse minimal TOML frontmatter from +++ delimited block.

    Returns (metadata_dict, body_without_frontmatter).
    Handles: key = "value", key = 1, key = true/false, key = None
    """
    metadata = {}
    fm_match = FRONTMATTER_RE.match(text)
    if not fm_match:
        return metadata, text

    fm_text = fm_match.group(1)
    body = text[fm_match.end():]

    for line in fm_text.strip().split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        # key = "value"
        m = re.match(r'^(\w[\w_-]*)\s*=\s*"(.*)"\s*$', line)
        if m:
            metadata[m.group(1)] = m.group(2)
            continue
        # key = number
        m = re.match(r'^(\w[\w_-]*)\s*=\s*(-?\d+(?:\.\d+)?)\s*$', line)
        if m:
            metadata[m.group(1)] = float(m.group(2)) if '.' in m.group(2) else int(m.group(2))
            continue
        # key = true/false
        m = re.match(r'^(\w[\w_-]*)\s*=\s*(true|false)\s*$', line)
        if m:
            metadata[m.group(1)] = m.group(2) == 'true'
            continue

    return metadata, body


def rewrite_link(url):
    """Rewrite Obsidian internal links to flat HTML structure.

    - External URLs (http/https) are returned as-is.
    - Image paths (images/…) are kept as-is (images are copied to output).
    - Internal page links get flattened: dir/dir/page → page.html
    """
    if not url:
        return url
    if url.startswith('http://') or url.startswith('https://'):
        return url
    # Keep image paths unmodified
    if url.startswith('images/'):
        return url
    # Remove anchors / query strings
    fragment = ''
    if '#' in url:
        url, fragment = url.split('#', 1)
        fragment = '#' + fragment
    # Internal page link — flatten to just the page name
    base = url.rsplit('/', 1)[-1] if '/' in url else url
    if base:
        return f'{base}.html{fragment}'
    return url


# ---------------------------------------------------------------------------
# Inline markdown processing
# ---------------------------------------------------------------------------

def process_inline(text):
    """Apply inline markdown formatting to already-HTML-escaped text."""
    # Images — must be before links (distinguished by leading !)
    text = re.sub(
        r'!\[([^\]]*)\]\(([^)]+)\)',
        lambda m: f'<img src="{rewrite_link(m.group(2))}" alt="{m.group(1)}">',
        text,
    )
    # Links
    text = re.sub(
        r'\[([^\]]*)\]\(([^)]+)\)',
        lambda m: f'<a href="{rewrite_link(m.group(2))}">{m.group(1)}</a>',
        text,
    )
    # Bold  **text**
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # Italic  *text*  (single asterisks, not double)
    text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<em>\1</em>', text)
    # Inline code  `code`
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    return text


# ---------------------------------------------------------------------------
# Table rendering
# ---------------------------------------------------------------------------

def render_table(lines):
    """Render a GFM table from a list of |…| lines (including header)."""
    if len(lines) < 2:
        return escape_html(lines[0]) if lines else ''

    # Header
    headers = [c.strip() for c in lines[0].strip('|').split('|')]
    # Alignments from separator line
    aligns = []
    sep_cells = [c.strip() for c in lines[1].strip('|').split('|')]
    for cell in sep_cells:
        if cell.startswith(':') and cell.endswith(':'):
            aligns.append('center')
        elif cell.endswith(':'):
            aligns.append('right')
        else:
            aligns.append('left')

    # Build thead
    thead_cells = ''.join(
        f'<th>{escape_html(h).strip()}</th>' for h in headers
    )
    thead = f'<thead><tr>{thead_cells}</tr></thead>'

    # Build tbody
    tbody_rows = []
    for line in lines[2:]:
        cells = [c.strip() for c in line.strip('|').split('|')]
        # Pad to match header count
        while len(cells) < len(headers):
            cells.append('')
        row_cells = ''.join(
            f'<td>{process_inline(escape_html(c))}</td>' for c in cells[:len(headers)]
        )
        tbody_rows.append(f'<tr>{row_cells}</tr>')
    tbody = f'<tbody>{"".join(tbody_rows)}</tbody>'

    return f'<table>{thead}{tbody}</table>'


# ---------------------------------------------------------------------------
# Markdown block → HTML
# ---------------------------------------------------------------------------

def md_to_html(text):
    """Convert markdown text to HTML.

    Handles: code blocks, tables, headings, horizontal rules, blockquotes,
    unordered lists, ordered lists, paragraphs, and inline formatting
    (bold, italic, code, links, images).
    """
    lines = text.split('\n')
    result = []
    i = 0
    n = len(lines)

    while i < n:
        stripped = lines[i].strip()

        # Blank line
        if not stripped:
            i += 1
            continue

        # Fenced code block ```
        if stripped.startswith('```'):
            code_lines = []
            i += 1
            while i < n and not lines[i].strip().startswith('```'):
                code_lines.append(lines[i])
                i += 1
            lang = stripped[3:].strip() or ''
            code_text = '\n'.join(code_lines)
            result.append(
                f'<pre><code class="language-{escape_html(lang)}">'
                f'{escape_html(code_text)}</code></pre>'
            )
            i += 1  # skip closing ```
            continue

        # Table — current line has | and next is separator
        if '|' in stripped and i + 1 < n:
            if TABLE_SEPARATOR_RE.match(lines[i + 1].strip()):
                table_lines = []
                while i < n and '|' in lines[i].strip():
                    table_lines.append(lines[i].strip())
                    i += 1
                result.append(render_table(table_lines))
                continue

        # Heading  # … #
        m = HEADING_RE.match(stripped)
        if m:
            level = len(m.group(1))
            content = process_inline(escape_html(m.group(2)))
            result.append(f'<h{level}>{content}</h{level}>')
            i += 1
            continue

        # Horizontal rule
        if HR_RE.match(stripped):
            result.append('<hr>')
            i += 1
            continue

        # Blockquote
        if stripped.startswith('>'):
            bq_lines = []
            while i < n and lines[i].strip().startswith('>'):
                bq_lines.append(lines[i].strip()[1:].strip())
                i += 1
            bq_text = ' '.join(bq_lines)
            result.append(f'<blockquote>{process_inline(escape_html(bq_text))}</blockquote>')
            continue

        # Unordered list
        ul_m = UL_ITEM_RE.match(lines[i])
        if ul_m:
            ul_lines = []
            indent = len(ul_m.group(1))
            while i < n:
                m = UL_ITEM_RE.match(lines[i])
                if m and len(m.group(1)) == indent:
                    ul_lines.append(m.group(2))
                    i += 1
                else:
                    break
            items = ''.join(
                f'<li>{process_inline(escape_html(item))}</li>'
                for item in ul_lines
            )
            result.append(f'<ul>{items}</ul>')
            continue

        # Ordered list
        ol_m = OL_ITEM_RE.match(lines[i])
        if ol_m:
            ol_lines = []
            indent = len(ol_m.group(1))
            while i < n:
                m = OL_ITEM_RE.match(lines[i])
                if m and len(m.group(1)) == indent:
                    ol_lines.append(m.group(2))
                    i += 1
                else:
                    break
            items = ''.join(
                f'<li>{process_inline(escape_html(item))}</li>'
                for item in ol_lines
            )
            result.append(f'<ol>{items}</ol>')
            continue

        # Paragraph — collect until blank or next block element
        p_lines = [stripped]
        i += 1
        while i < n and lines[i].strip():
            ls = lines[i].strip()
            # Stop if next line starts a block
            if (ls.startswith('#') or ls.startswith('```') or
                ls.startswith('>') or ls.startswith('- ') or
                ls.startswith('* ') or ls.startswith('+ ') or
                re.match(r'^\d+\.\s', ls) or HR_RE.match(ls) or
                (i + 1 < n and '|' in ls and
                 TABLE_SEPARATOR_RE.match(lines[i + 1].strip()))):
                break
            p_lines.append(ls)
            i += 1

        p_text = ' '.join(p_lines)
        result.append(f'<p>{process_inline(escape_html(p_text))}</p>')

    return '\n'.join(result)


# ---------------------------------------------------------------------------
# Shortcode rendering
# ---------------------------------------------------------------------------

def render_shortcode(name, content):
    """Render a single shortcode block to HTML.

    name  — one of: warning, steps, info, tip, materials
    content — raw text between the open and close tags
    """
    name = name.lower().strip()

    if name == 'steps':
        # Split by semicolons; filter empty items
        steps = [s.strip() for s in content.split(';') if s.strip()]
        items = '\n'.join(
            f'<li>{process_inline(escape_html(step))}</li>'
            for step in steps
        )
        return f'<div class="procedure steps">\n<ol>\n{items}\n</ol>\n</div>'

    # warning, info, tip, materials — convert inner markdown
    inner_html = md_to_html(content.strip())
    css_class = {
        'warning': 'callout warning',
        'info': 'callout info',
        'tip': 'callout tip',
        'materials': 'callout materials',
    }.get(name, 'callout')

    return f'<div class="{css_class}">\n{inner_html}\n</div>'


# Sentinel for placeholder substitution — must be text that cannot
# appear in real markdown content.
_PLACEHOLDER_PREFIX = '\x00SHTF_SC_'
_PLACEHOLDER_SUFFIX = '\x00'


def process_shortcodes(body):
    """Replace all Zola shortcodes in *body* with HTML.

    Close-tag regex is checked before open-tag, preventing {% end %}
    from being mistaken for a shortcode name.

    Uses a placeholder strategy: shortcode blocks are replaced with
    sentinel tokens before markdown conversion, then swapped back
    afterwards.  This prevents shortcode-rendered HTML from being
    double-escaped or re-wrapped by the markdown converter.
    """
    placeholders = {}  # placeholder_id → rendered HTML
    counter = 0

    while True:
        # Locate the first close-tag
        close_m = SHORTCODE_CLOSE_RE.search(body)
        if not close_m:
            break

        # Find the *last* open-tag before this close
        prefix = body[:close_m.start()]
        open_matches = list(SHORTCODE_OPEN_RE.finditer(prefix))
        if not open_matches:
            sys.stderr.write(
                'WARNING: {% end %} without matching open shortcode\n'
            )
            # Remove stray {% end %} to avoid infinite loop
            body = body[:close_m.start()] + body[close_m.end():]
            continue

        last_open = open_matches[-1]
        sc_name = last_open.group(1)

        # Extract inner content (may contain markdown or plain text)
        inner = body[last_open.end():close_m.start()]

        # Render the shortcode block to final HTML
        rendered = render_shortcode(sc_name, inner)

        # Store rendered HTML under a unique placeholder
        pid = f'{_PLACEHOLDER_PREFIX}{counter}{_PLACEHOLDER_SUFFIX}'
        placeholders[pid] = rendered
        counter += 1

        # Splice out the old block, insert placeholder
        body = body[:last_open.start()] + pid + body[close_m.end():]

    # Now substitute all placeholders into the final body
    # (after the caller runs md_to_html on the placeholder-studded text)
    return body, placeholders


# ---------------------------------------------------------------------------
# File name helper
# ---------------------------------------------------------------------------

def output_filename(rel_path_str, source_root):
    """Determine the flat output .html filename for a .md file.

    - index / _index files use their parent directory name.
    - Regular files use their stem.
    - Collisions are avoided by adding a parent-dir prefix.
    """
    rel = Path(rel_path_str)
    stem = rel.stem
    parent = rel.parent.name if rel.parent.name else None

    if stem in ('_index', 'index'):
        if parent:
            return f'{parent}.html'
        return 'index.html'

    return f'{stem}.html'


def resolve_collisions(md_files, source_root):
    """Assign a unique output name to every .md file, resolving collisions.

    Returns dict: {Path(md_path): 'output_name.html'}

    Strategy: first occurrence gets the default name; later collisions get
    the parent directory prepended (e.g. safety.html → firearms-safety.html).
    """
    names = {}    # output_name → first source path (for diagnostics)
    resolved = {}  # source path → output name

    for md_path in sorted(md_files):
        rel_str = str(md_path.relative_to(source_root)).replace(os.sep, '/')
        candidate = output_filename(rel_str, source_root)

        if candidate not in names:
            names[candidate] = md_path
            resolved[md_path] = candidate
        else:
            # Collision — prepend the immediate parent directory name
            parent = md_path.parent.name
            disambiguated = f'{parent}-{candidate}'
            attempt = 1
            while disambiguated in names:
                # Very rare: even parent-prefixed name collides
                gparent = md_path.parent.parent.name
                disambiguated = f'{gparent}-{parent}-{candidate}'
                attempt += 1
                if attempt > 3:
                    # Defensive — use a counter
                    disambiguated = f'{parent}-{attempt}-{candidate}'
                    break
            names[disambiguated] = md_path
            resolved[md_path] = disambiguated

    return resolved


# ---------------------------------------------------------------------------
# Image copier
# ---------------------------------------------------------------------------

def copy_images(source_root, output_dir):
    """Copy the entire images/ tree from source vault to output/images/."""
    src_images = Path(source_root) / 'images'
    if not src_images.is_dir():
        print(f'No images directory at {src_images}, skipping.')
        return

    dst_images = Path(output_dir) / 'images'
    if dst_images.exists():
        shutil.rmtree(dst_images)

    shutil.copytree(src_images, dst_images)
    count = sum(1 for _ in dst_images.rglob('*') if _.is_file())
    print(f'Copied {count} images to {dst_images}')


# ---------------------------------------------------------------------------
# Single-file processor
# ---------------------------------------------------------------------------

def process_file(md_path):
    """Process one .md file and return an HTML string."""
    with open(md_path, 'r', encoding='utf-8') as fh:
        raw = fh.read()

    # 1. Split frontmatter
    metadata, body = parse_frontmatter(raw)

    title = metadata.get('title', 'Untitled')
    description = metadata.get('description', '')

    # 2. Process shortcodes — extract & render, replace with placeholders
    body, placeholders = process_shortcodes(body)

    # 3. Convert remaining markdown → HTML (placeholders pass through
    #    safely because they contain \x00 bytes, never appearing in
    #    real markdown text).
    html_body = md_to_html(body)

    # 4. Swap placeholders back to rendered shortcode HTML
    for pid, rendered in placeholders.items():
        html_body = html_body.replace(pid, rendered)

    # 4b. Remove <p> wrappers that md_to_html added around block-level
    #     shortcode divs (callout, procedure) — these are standalone
    #     blocks and must not be inline inside paragraphs.
    html_body = re.sub(
        r'<p>\s*(<div class="(?:callout|procedure)[^"]*">.+?</div>)\s*</p>',
        r'\1',
        html_body,
        flags=re.DOTALL,
    )

    # 5. Assemble full page
    page = f'''<!DOCTYPE html>
<html lang="en-AU">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{escape_html(title)} — Outback Safe</title>
<meta name="description" content="{escape_html(description)}">
<link rel="stylesheet" href="style.css">
</head>
<body>
<nav class="site-nav">
  <a href="index.html" class="back-link">&larr; Outback Safe</a>
</nav>
<main class="content">
<article>
{html_body}
</article>
</main>
<footer class="site-footer">
  <p><strong>Disclaimer:</strong> This information is for educational purposes only.
  It is not a substitute for professional medical advice, diagnosis, or treatment.
  In a life-threatening emergency, activate your PLB or call 000 (Australia) immediately.
  Always seek the advice of qualified health providers.</p>
  <p>Outback Safe — Offline Survival Reference</p>
</footer>
</body>
</html>'''
    return page


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description='Preprocess Obsidian vault to flat HTML for SHTF USB.'
    )
    parser.add_argument(
        '--source', required=True,
        help='Path to Obsidian vault root (contains .md files with +++ frontmatter).'
    )
    parser.add_argument(
        '--output', required=True,
        help='Output directory for flat HTML files.'
    )
    args = parser.parse_args()

    source_root = Path(args.source).resolve()
    output_dir = Path(args.output).resolve()

    if not source_root.is_dir():
        sys.stderr.write(f'ERROR: Source directory not found: {source_root}\n')
        sys.exit(1)

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Discover .md files (recursive)
    md_files = sorted(source_root.rglob('*.md'))
    if not md_files:
        sys.stderr.write(f'WARNING: No .md files found under {source_root}\n')
        # Still copy images if present
        copy_images(source_root, output_dir)
        return

    # Resolve output filenames (collision-safe)
    file_names = resolve_collisions(md_files, source_root)

    processed = 0

    for md_path in md_files:
        rel = md_path.relative_to(source_root)
        rel_str = str(rel).replace(os.sep, '/')

        out_name = file_names[md_path]
        out_path = output_dir / out_name

        try:
            html = process_file(md_path)
        except Exception as exc:
            sys.stderr.write(
                f'ERROR processing {rel_str}: {exc}\n'
            )
            continue

        with open(out_path, 'w', encoding='utf-8') as fh:
            fh.write(html)

        processed += 1
        print(f'  {rel_str}  →  {out_name}')

    # Copy images
    copy_images(source_root, output_dir)

    print(f'\nDone. {processed} pages written to {output_dir}')


if __name__ == '__main__':
    main()
