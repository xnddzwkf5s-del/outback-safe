#!/usr/bin/env python3
"""Outback Safe — EPUB 2.0.1 Builder"""
import sys, os, re, zipfile, shutil, tempfile, markdown
from pathlib import Path
from html import escape

ROOT = Path("/Users/pang/Survival-Wiki")
CONTENT = ROOT / "content"
STATIC = ROOT / "static"
OUTPUT = ROOT / "Outback Safe.epub"
SITE_COPY = ROOT / "site" / "Outback Safe.epub"

# ─── Frontmatter ───────────────────────────────────────────────────
def parse_frontmatter(text):
    if not text.startswith("+++"): return {}, text
    parts = text.split("+++\n", 2)
    if len(parts) < 3: return {}, text
    fm = {}
    for line in parts[1].split("\n"):
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s: continue
        if "[" in s and "]" in s: continue
        k, v = s.split("=", 1)
        fm[k.strip()] = v.strip().strip('"').strip("'")
    return fm, parts[2]

# ─── Shortcodes ────────────────────────────────────────────────────
def render_shortcodes(text):
    text = re.sub(r'\{%\s*warning\(\)\s*%\}(.*?)\{%\s*end\s*%\}',
        lambda m: '<div class="admonition warning"><div class="admonition-title">Warning</div><div class="admonition-body">' +
                  m.group(1).strip() + '</div></div>', text, flags=re.DOTALL)
    text = re.sub(r'\{%\s*info\(\)\s*%\}(.*?)\{%\s*end\s*%\}',
        lambda m: '<div class="admonition info"><div class="admonition-title">Information</div><div class="admonition-body">' +
                  m.group(1).strip() + '</div></div>', text, flags=re.DOTALL)
    text = re.sub(r'\{%\s*materials\(\)\s*%\}(.*?)\{%\s*end\s*%\}',
        lambda m: '<div class="materials-box"><div class="materials-title">Materials</div><ul class="materials-list">' +
                  ''.join('<li>' + i.strip() + '</li>' for i in m.group(1).split(';') if i.strip()) + '</ul></div>',
        text, flags=re.DOTALL)
    text = re.sub(r'\{%\s*steps\(\)\s*%\}(.*?)\{%\s*end\s*%\}',
        lambda m: '<ol class="steps-list">' +
                  ''.join('<li><span>' + l.strip().lstrip("- ") + '</span></li>'
                          for l in m.group(1).strip().split('\n') if l.strip()) + '</ol>',
        text, flags=re.DOTALL)
    return text

# ─── File naming ───────────────────────────────────────────────────
def compute_flat_name(md_path):
    rel = md_path.relative_to(CONTENT)
    parts = list(rel.parts)
    if parts[-1] in ("_index.md", "index.md"):
        parts = parts[:-1]
    elif parts[-1].endswith(".md"):
        parts[-1] = parts[-1][:-3]
    if not parts:
        return "index.xhtml"
    return "-".join(parts) + ".xhtml"

def build_file_map():
    """Build mapping from content-root path to flat xhtml filename."""
    mapping = {}
    for md_file in sorted(CONTENT.rglob("*.md")):
        flat_name = compute_flat_name(md_file)
        rel = md_file.relative_to(CONTENT)
        path_no_ext = str(rel.with_suffix(""))
        mapping[path_no_ext] = flat_name
        if rel.name in ("_index.md", "index.md"):
            mapping[str(rel.parent)] = flat_name
            # Also map with /index and /_index suffixes
            mapping[str(rel.parent) + "/index"] = flat_name
    return mapping

# ─── Slug generation (consistent) ──────────────────────────────────
def make_slug(text):
    """Generate a valid XML id from heading text."""
    slug = re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')
    # Ensure valid XML: must start with letter or underscore
    if slug and not slug[0].isalpha() and slug[0] != '_':
        slug = 'h-' + slug
    return slug

# ─── Link resolution ───────────────────────────────────────────────
def resolve_content_root(clean, current_dir):
    """Resolve a potentially relative path to an absolute content-root path."""
    cur_parts = [p for p in current_dir.split("/") if p]
    if clean.startswith("../"):
        rel_parts = clean.split("/")
        up = sum(1 for p in rel_parts if p == "..")
        new_cur = cur_parts[:-up] if up <= len(cur_parts) else []
        remaining = [p for p in rel_parts if p != ".."]
        return "/".join(new_cur + remaining)
    else:
        return "/".join(cur_parts + [clean])

def resolve_epub_link(url, current_dir, page_map):
    """Convert markdown URL to flat xhtml path or proper image path."""
    # Images
    if url.startswith("/images/"):
        return url[1:]
    if url.startswith("/maps/"):
        return "images/maps/" + url[6:]
    # External / anchor / mailto
    if url.startswith(("http://", "https://", "#", "mailto:")):
        return url

    base = url.split("#")[0]
    # Keep fragment for anchors to pages
    frag = url[len(base):] if len(base) < len(url) else ""
    clean = base.rstrip("/")

    # Try resolving
    target = None

    # Strategy 1: treat as content-root path (for content like 02-stabilise/...)
    if re.match(r'^\d{2}-', clean) or '/' in clean:
        target = page_map.get(clean)
        if target is None:
            target = page_map.get(clean + "/_index")
        if target is None:
            # Try resolving relative to current directory
            resolved = resolve_content_root(clean, current_dir)
            target = page_map.get(resolved)
            if target is None:
                target = page_map.get(resolved + "/_index")

    # Strategy 2: single word, relative to current dir
    if target is None:
        resolved = resolve_content_root(clean, current_dir)
        target = page_map.get(resolved)
        if target is None:
            target = page_map.get(resolved + "/_index")

    if target:
        return target + frag
    return url  # fallback

# ─── Content conversion ────────────────────────────────────────────
def extract_toc(html):
    """Extract h2 headings for page-level TOC. Returns (toc_html, slugs_list)."""
    headings = re.findall(r'<h2[^>]*>(.*?)</h2>', html)
    # Don't generate TOC for pages with fewer than 3 headings
    if len(headings) < 3:
        return "", []
    slugs = []
    toc_parts = ['<div class="page-toc"><p class="toc-title"><strong>Contents</strong></p><ul>']
    for h in headings:
        # Decode any HTML entities for slug generation
        plain = h.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"')
        slug = make_slug(plain)
        slugs.append((h, slug))
        # Use the heading text as-is in the link text (entities preserved)
        toc_parts.append(f'<li><a href="#{escape(slug)}">{h}</a></li>')
    toc_parts.append('</ul></div>')
    return '\n'.join(toc_parts) + '\n', slugs

def add_anchors(html, slugs):
    """Add id attributes to h2 elements using the generated slugs."""
    for h, slug in slugs:
        # Replace <h2>heading text</h2> with <h2 id="slug">heading text</h2>
        # Need exact match to avoid replacing partial matches
        old = f'<h2>{h}</h2>'
        new = f'<h2 id="{escape(slug)}">{h}</h2>'
        html = html.replace(old, new, 1)
    return html

def build_page_list_epub(section_dir, page_map, current_dir):
    """Build a page grid for a section's child pages."""
    parts = []
    try:
        subs = sorted([d for d in section_dir.iterdir() if d.is_dir() and (d / "_index.md").exists()])
        if subs:
            items = []
            for s in subs:
                with open(s / "_index.md") as f:
                    fm, _ = parse_frontmatter(f.read())
                stitle = fm.get("title", s.name.replace("-", " ").title())
                sdesc = fm.get("description", "")
                resolved = resolve_epub_link(s.name + "/", current_dir, page_map)
                items.append(f'<li><a href="{escape(resolved)}">{escape(stitle)}</a>'
                             f'{"<p>" + escape(sdesc) + "</p>" if sdesc else ""}</li>')
            if items:
                parts.append('<h2>Sections</h2><ul class="page-grid">' + ''.join(items) + '</ul>')
    except Exception:
        pass
    try:
        pages = sorted([p for p in section_dir.iterdir() if p.suffix == ".md" and p.name != "_index.md"])
        if pages:
            items = []
            for p in pages:
                with open(p) as f:
                    fm, _ = parse_frontmatter(f.read())
                ptitle = fm.get("title", p.stem.replace("-", " ").title())
                pdesc = fm.get("description", "")
                resolved = resolve_epub_link(p.stem, current_dir, page_map)
                items.append(f'<li><a href="{escape(resolved)}">{escape(ptitle)}</a>'
                             f'{"<p>" + escape(pdesc) + "</p>" if pdesc else ""}</li>')
            if items:
                parts.append('<h2>Pages</h2><ul class="page-grid">' + ''.join(items) + '</ul>')
    except Exception:
        pass
    return '\n'.join(parts)

def convert_md(md_path, page_map):
    """Convert markdown file to EPUB body HTML."""
    with open(md_path) as f:
        text = f.read()
    fm, body = parse_frontmatter(text)
    title = fm.get("title", md_path.stem.replace("-", " ").title())

    body = render_shortcodes(body)

    # Resolve links and images in markdown
    rel_dir = str(md_path.parent.relative_to(CONTENT)) if md_path.parent != CONTENT else ""
    def link_replacer(m):
        prefix = m.group(1)
        alt = m.group(2)
        url = m.group(3)
        resolved = resolve_epub_link(url, rel_dir, page_map)
        return f'{prefix}[{alt}]({resolved})'
    body = re.sub(r'(!?)\[([^\]]*)\]\(([^)]+)\)', link_replacer, body)

    # Convert markdown to HTML
    md_conv = markdown.Markdown(extensions=["tables", "fenced_code", "codehilite"])
    html = md_conv.convert(body)
    md_conv.reset()

    # Remove self-referencing EPUB download link
    html = re.sub(r'<a[^>]*href="[^"]*Outback Safe\.epub[^"]*"[^>]*>.*?</a>', '', html)

    # Extract TOC and add anchors
    toc, slugs = extract_toc(html)
    html = toc + add_anchors(html, slugs)

    # Build page grid for _index files
    if md_path.name == "_index.md" and md_path.parent != CONTENT:
        html += build_page_list_epub(md_path.parent, page_map, rel_dir)

    # Fix any remaining image paths in HTML
    html = re.sub(r'src="/images/', 'src="images/', html)
    html = re.sub(r'src="/maps/', 'src="images/maps/', html)

    # Fix href with broken paths - remove non-xhtml references
    html = re.sub(r'href="([^"]*?)\.epub"', '', html)

    return title, html

# ─── EPUB structure ────────────────────────────────────────────────
XHTML_HEADER = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<title>%s</title>
<link rel="stylesheet" type="text/css" href="css/style.css"/>
</head>
<body>
<div class="content">
'''

XHTML_FOOTER = '''
</div>
</body>
</html>'''

def make_xhtml(title, body):
    return XHTML_HEADER % escape(title) + body + XHTML_FOOTER

CSS = """/* Outback Safe EPUB CSS - all var() resolved */
*,*::before,*::after{box-sizing:border-box}
body{font-family:"Inter",-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;font-size:1rem;line-height:1.7;color:#1a1a2e;background:#f8f6f1;margin:0;padding:16px}
h1,h2,h3,h4,h5,h6{font-family:"Playfair Display",Georgia,"Times New Roman",serif;font-weight:600;line-height:1.2;color:#1a1a2e;margin:0 0 .75rem}
h1{font-size:2.2rem}h2{font-size:1.5rem}h3{font-size:1.25rem}h4{font-size:1.1rem}
p{margin:0 0 1rem;font-size:.95rem}
a{color:#b8945a;text-decoration:none}
strong,b{font-weight:600}
.content h2{margin-top:2.5rem;padding-bottom:.4rem;border-bottom:2px solid #c9a96e}
.content h3{margin-top:2rem}
.content p{margin:.9rem 0;font-size:1rem}
.content img{max-width:100%;height:auto;border-radius:12px;margin:1rem 0}
.content blockquote{margin:1.5rem 0;padding:1rem 1.5rem;border-left:4px solid #c9a96e;background:#fff;border-radius:0 4px 4px 0;font-style:italic;color:#6b7280}
.content blockquote p{margin:0}
.content code{font-family:monospace;background:rgba(26,26,46,.06);padding:.15rem .4rem;border-radius:4px;font-size:.9em;color:#1a1a2e}
.content pre{margin:1.5rem 0;border-radius:12px;overflow:hidden}
.content pre code{display:block;overflow-x:auto;padding:1.25rem 1.5rem;background:#1e1e2e;color:#e0e0e0;border-radius:12px;font-size:.88rem;line-height:1.6}
.content hr{border:none;border-top:1px solid #e8e4dd;margin:2.5rem 0}
.content table{width:100%;border-collapse:collapse;margin:1.5rem 0;font-size:.95rem;border-radius:12px;overflow:hidden}
.content table th{background:#1a1a2e;color:#fff;font-weight:600;text-align:left;padding:.75rem 1rem;font-size:.9rem;text-transform:uppercase;letter-spacing:.05em}
.content table td{padding:.7rem 1rem;border-bottom:1px solid #e8e4dd;background:#fff}
.content table td img{max-width:120px;height:auto;border-radius:4px}
.content table tr:nth-child(even) td{background:#f8f6f1}
.admonition{border:1px solid;border-radius:12px;padding:1rem 1.25rem;margin:1.5rem 0;position:relative;overflow:hidden}
.admonition::before{content:"";position:absolute;top:0;left:0;bottom:0;width:4px}
.admonition.warning{background:#fff6e8;border-color:#d4a017}
.admonition.warning::before{background:#d4a017}
.admonition.warning .admonition-title{color:#d4a017}
.admonition.info{background:#eaf4fb;border-color:#3a7bbf}
.admonition.info::before{background:#b8945a}
.admonition.info .admonition-title{color:#b8945a}
.admonition-title{font-weight:700;margin:0 0 .5rem;font-family:"Playfair Display",Georgia,"Times New Roman",serif;font-size:1rem}
.admonition-body{font-size:.95rem;line-height:1.65}
.admonition-body p:first-child{margin-top:0}
.admonition-body p:last-child{margin-bottom:0}
.materials-box{background:#f2f7ed;border:1px solid #6b8e4e;border-left:4px solid #6b8e4e;border-radius:12px;padding:1rem 1.25rem;margin:1.5rem 0}
.materials-title{font-weight:700;margin:0 0 .5rem;font-family:"Playfair Display",Georgia,"Times New Roman",serif;font-size:1rem}
.materials-list{margin:0;padding-left:1.5rem}
.materials-list li{font-size:.95rem;margin-bottom:.35rem;list-style-type:disc}
.materials-list li:last-child{margin-bottom:0}
.steps-list{list-style:none;padding:0;counter-reset:step-counter}
.steps-list li{counter-increment:step-counter;margin:.5rem 0;padding:.75rem 1rem;background:#fff;border-radius:4px;border:1px solid #e8e4dd}
.steps-list li span{display:block}
.page-grid{list-style:none;padding:0;margin:1.5rem 0}
.page-grid li{background:#fff;border:1px solid #e8e4dd;border-radius:12px;padding:1.25rem;margin-bottom:.75rem}
.page-grid li a{font-weight:600;font-family:"Playfair Display",Georgia,"Times New Roman",serif;font-size:1.05rem;display:block;margin-bottom:.25rem}
.page-grid li p{font-size:.85rem;color:#6b7280;margin:.25rem 0 0}
.page-toc{background:#fff;border:1px solid #e8e4dd;border-radius:12px;padding:.75rem 1.25rem;margin:1.5rem 0}
.page-toc .toc-title{font-family:"Playfair Display",Georgia,"Times New Roman",serif;margin:0 0 .3rem}
.page-toc ul{margin:.3rem 0 0;padding-left:1.5rem;font-size:.9rem}
"""

def make_container():
    return """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>"""

def make_opf(pages, all_images):
    manifest = ['  <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>']
    spine = []
    manifest.append('  <item id="css" href="css/style.css" media-type="text/css"/>')
    for i, (flat_name, title) in enumerate(pages):
        mid = f"p{i:03d}"
        manifest.append(f'  <item id="{mid}" href="{flat_name}" media-type="application/xhtml+xml"/>')
        spine.append(f'  <itemref idref="{mid}"/>')

    for img_path in sorted(all_images):
        ext = os.path.splitext(img_path)[1].lower().lstrip(".")
        mt = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png",
              "gif": "image/gif", "svg": "image/svg+xml", "webp": "image/webp"}.get(ext, "image/jpeg")
        img_id = "i-" + re.sub(r'[^a-z0-9]', '-', img_path.lower())
        manifest.append(f'  <item id="{img_id}" href="{img_path}" media-type="{mt}"/>')

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<package version="2.0" xmlns="http://www.idpf.org/2007/opf" unique-identifier="bookid">
  <metadata>
    <dc:identifier id="bookid" xmlns:dc="http://purl.org/dc/elements/1.1/">Outback-Safe-2026-07-23</dc:identifier>
    <dc:title xmlns:dc="http://purl.org/dc/elements/1.1/">Outback Safe</dc:title>
    <dc:creator xmlns:dc="http://purl.org/dc/elements/1.1/">Outback Safe Contributors</dc:creator>
    <dc:language xmlns:dc="http://purl.org/dc/elements/1.1/">en-AU</dc:language>
    <dc:date xmlns:dc="http://purl.org/dc/elements/1.1/">2026-07-23</dc:date>
    <dc:publisher xmlns:dc="http://purl.org/dc/elements/1.1/">Outback Safe</dc:publisher>
    <dc:rights xmlns:dc="http://purl.org/dc/elements/1.1/">CC BY-SA 4.0</dc:rights>
    <dc:description xmlns:dc="http://purl.org/dc/elements/1.1/">Australian Remote Travel Reference - offline, open source</dc:description>
    <meta name="cover" content="p000"/>
  </metadata>
  <manifest>
{chr(10).join(manifest)}
  </manifest>
  <spine toc="ncx">
{chr(10).join(spine)}
  </spine>
  <guide>
    <reference type="toc" title="Table of Contents" href="toc.xhtml"/>
  </guide>
</package>"""

def make_ncx(pages):
    navpoints = []
    for i, (flat_name, title) in enumerate(pages):
        navpoints.append(f"""    <navPoint id="n{i:03d}" playOrder="{i+1}">
      <navLabel>
        <text>{escape(title)}</text>
      </navLabel>
      <content src="{flat_name}"/>
    </navPoint>""")
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head>
    <meta name="dtb:uid" content="Outback-Safe-2026-07-23"/>
    <meta name="dtb:depth" content="1"/>
    <meta name="dtb:totalPageCount" content="0"/>
    <meta name="dtb:maxPageNumber" content="0"/>
  </head>
  <docTitle>
    <text>Outback Safe</text>
  </docTitle>
  <docAuthor>
    <text>Outback Safe Contributors</text>
  </docAuthor>
  <navMap>
{chr(10).join(navpoints)}
  </navMap>
</ncx>"""

def collect_images():
    images = []
    src_img = STATIC / "images"
    if src_img.exists():
        for f in sorted(src_img.rglob("*")):
            if f.is_file() and f.suffix.lower() in (".jpg", ".jpeg", ".png", ".gif", ".webp"):
                images.append(str(f.relative_to(STATIC)))
    # Add map SVGs to images/maps/
    src_maps = STATIC / "maps"
    if src_maps.exists():
        for f in sorted(src_maps.glob("*.svg")):
            images.append("images/maps/" + f.name)
    return images

# ─── Main build ────────────────────────────────────────────────────
def build_epub():
    print("Building EPUB...")
    page_map = build_file_map()
    print(f"  Page map: {len(page_map)} entries")

    all_md = sorted(CONTENT.rglob("*.md"))
    print(f"  Markdown files: {len(all_md)}")

    processed = []
    for md_file in all_md:
        rel = md_file.relative_to(CONTENT)
        flat_name = compute_flat_name(md_file)
        title, body = convert_md(md_file, page_map)
        xhtml = make_xhtml(title, body)
        processed.append((flat_name, title, xhtml))
        print(f"    {str(rel):45s} -> {flat_name}")

    # Build TOC page (first in spine)
    toc_links = []
    for flat_name, title, _ in processed:
        toc_links.append(f'<li><a href="{escape(flat_name)}">{escape(title)}</a></li>')
    toc_body = '<h1>Outback Safe</h1><p>Australian Remote Travel Reference</p><h2>Contents</h2><ul class="page-grid">' + ''.join(toc_links) + '</ul>'
    processed.insert(0, ("toc.xhtml", "Table of Contents", make_xhtml("Table of Contents", toc_body)))

    all_images = collect_images()
    print(f"  Images in EPUB: {len(all_images)}")

    opf_content = make_opf([(f, t) for f, t, _ in processed], all_images)
    ncx_content = make_ncx([(f, t) for f, t, _ in processed])

    # Build EPUB in temp dir
    tmpdir = Path(tempfile.mkdtemp())
    oebps = tmpdir / "OEBPS"
    oebps.mkdir(parents=True)
    (tmpdir / "META-INF").mkdir()

    (tmpdir / "mimetype").write_text("application/epub+zip")
    (tmpdir / "META-INF" / "container.xml").write_text(make_container())
    (oebps / "content.opf").write_text(opf_content)
    (oebps / "toc.ncx").write_text(ncx_content)

    (oebps / "css").mkdir()
    (oebps / "css" / "style.css").write_text(CSS)

    for flat_name, title, xhtml in processed:
        (oebps / flat_name).write_text(xhtml)

    # Copy images
    src_img = STATIC / "images"
    if src_img.exists():
        for f in src_img.rglob("*"):
            if f.is_file():
                rel = f.relative_to(STATIC)
                target = oebps / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, target)

    # Copy map SVGs
    maps_dir = oebps / "images" / "maps"
    maps_dir.mkdir(parents=True, exist_ok=True)
    src_maps = STATIC / "maps"
    if src_maps.exists():
        for f in src_maps.glob("*.svg"):
            shutil.copy2(f, maps_dir / f.name)

    # Write EPUB
    if OUTPUT.exists():
        os.remove(OUTPUT)
    with zipfile.ZipFile(OUTPUT, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(tmpdir / "mimetype", "mimetype", compress_type=zipfile.ZIP_STORED)
        zf.write(tmpdir / "META-INF/container.xml", "META-INF/container.xml", compress_type=zipfile.ZIP_DEFLATED)
        for f in sorted(oebps.rglob("*")):
            if f.is_file():
                zf.write(f, str(f.relative_to(tmpdir)), compress_type=zipfile.ZIP_DEFLATED)

    shutil.rmtree(tmpdir)
    print(f"\nEPUB: {OUTPUT}")
    SITE_COPY.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(OUTPUT, SITE_COPY)
    print(f"Copy: {SITE_COPY}")
    verify_epub(OUTPUT)
    return True

def verify_epub(epub_path):
    print("\n=== Verify ===")
    try:
        with zipfile.ZipFile(epub_path, "r") as zf:
            names = zf.namelist()
            print(f"  Entries: {len(names)}, first: {names[0]}")
            assert names[0] == "mimetype", "mimetype not first!"
            info = zf.getinfo("mimetype")
            assert info.compress_type == zipfile.ZIP_STORED, "mimetype compressed!"
            print("  mimetype: OK")

            xhtml_files = [n for n in names if n.endswith(".xhtml")]
            epub_set = set(names)
            img_refs = set()
            missing = 0
            for xf in xhtml_files:
                content = zf.read(xf).decode("utf-8")
                for img_src in re.findall(r'src="([^"]+\.(?:jpg|png|gif|svg|webp))"', content, re.IGNORECASE):
                    ref = "OEBPS/" + img_src
                    img_refs.add(img_src)
                    if ref not in epub_set:
                        missing += 1
                        if missing <= 10:
                            print(f"  MISSING: {ref}")
            print(f"  Image refs: {len(img_refs)}, missing: {missing}")

            for r in ["OEBPS/content.opf", "OEBPS/toc.ncx", "OEBPS/css/style.css"]:
                print(f"  {'OK' if r in names else 'MISS'}: {r}")

            ncx = zf.read("OEBPS/toc.ncx").decode("utf-8")
            print(f"  NCX navPoints: {len(re.findall(r'<navPoint', ncx))}")
            print(f"  Size: {os.path.getsize(epub_path)/1024:.0f} KB")
    except Exception as e:
        print(f"  Error: {e}")

if __name__ == "__main__":
    build_epub()
