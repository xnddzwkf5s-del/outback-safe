import zipfile, re, os, shutil
from pathlib import Path
from html import escape

SITE = Path('/Users/pang/Survival-Wiki/site')
EPUB_SRC = Path('/Users/pang/Survival-Wiki/Outback Safe.epub')
OUT = Path('/Users/pang/Survival-Wiki/Outback Safe.epub')

# Backup original
shutil.copy(EPUB_SRC, str(EPUB_SRC) + '.bak')

CSS = 'body{font-family:-apple-system,sans-serif;font-size:16px;line-height:1.6;color:#1a1a2e;margin:1em}h1{font-size:1.8em;margin:.5em 0}h2{font-size:1.4em;margin:1.5em 0 .5em;border-bottom:2px solid #c9a96e;padding-bottom:.3em}h3{font-size:1.2em;margin:1em 0 .5em}p{margin:.8em 0}a{color:#b8945a}table{width:100%;border-collapse:collapse;margin:1em 0;font-size:.9em}th{background:#1a1a2e;color:#fff;padding:.5em;text-align:left}td{padding:.5em;border-bottom:1px solid #e8e4dd}tr:nth-child(even) td{background:#f8f6f1}img{max-width:100%;height:auto}.admonition{border:1px solid #d4a017;background:#fff6e8;padding:.8em;margin:1em 0;border-radius:4px}.admonition-title{font-weight:bold;margin-bottom:.3em}.toc{background:#f8f6f1;padding:.8em;margin:1em 0;border:1px solid #e8e4dd}'

pages = []

for html_file in sorted(SITE.rglob('*.html')):
    if 'static' in str(html_file) or html_file.name == '404.html': continue
    content = html_file.read_text()
    title_m = re.search(r'<title>(.*?)</title>', content)
    title = title_m.group(1) if title_m else html_file.stem.replace('-',' ').title()
    main_m = re.search(r'<main>(.*?)</main>', content, re.DOTALL)
    body = main_m.group(1) if main_m else ''
    body = re.sub(r'<header>.*?</header>', '', body, flags=re.DOTALL)
    body = re.sub(r'<footer>.*?</footer>', '', body, flags=re.DOTALL)
    body = re.sub(r'<nav.*?</nav>', '', body, flags=re.DOTALL)
    
    # FIX: Convert relative paths to EPUB-internal paths
    # From site/XX/YY/page.html, images are at ../../static/images/...
    # In EPUB, pages are at OEBPS/page.html, images at OEBPS/static/images/...
    body = re.sub(r'src="(?:\.\./)+static/(images|maps)/', r'src="static/\1/', body)
    
    # Remove link hrefs (EPUB can't do cross-page links easily)
    body = re.sub(r'href="([^"]+)"', 'href="#"', body)
    
    # Fix XHTML entities - only escape bare & not part of an entity
    body = re.sub(r'&(?!(amp|lt|gt|quot|apos|#\d+|#x[0-9a-fA-F]+);)', '&amp;', body)
    
    rel = str(html_file.relative_to(SITE))
    name = rel.replace('/','_')
    display_title = title.replace(' — Outback Safe','')
    
    # Proper XHTML with DOCTYPE
    clean = f'<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE html>\n<html xmlns="http://www.w3.org/1999/xhtml">\n<head><title>{escape(display_title)}</title>\n<style type="text/css">\n{CSS}\n</style>\n</head>\n<body>\n<h1>{escape(display_title)}</h1>\n{body}\n</body>\n</html>'
    
    pages.append((name, display_title, clean))

# Build EPUB 2.0 compatible
with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as z:
    # mimetype MUST be first, stored, with no extra field
    z.writestr('mimetype', 'application/epub+zip', compress_type=zipfile.ZIP_STORED)
    
    z.writestr('META-INF/container.xml', '<?xml version="1.0" encoding="UTF-8"?><container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>')
    
    manifest_items = '<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>\n'
    spine_items = ''
    ncx_navmap = ''
    toc_items = ''
    
    for i, (name, title, body_html) in enumerate(pages):
        iid = f'page{i}'
        manifest_items += f'<item id="{iid}" href="{name}" media-type="application/xhtml+xml"/>\n'
        spine_items += f'<itemref idref="{iid}"/>\n'
        ncx_navmap += f'<navPoint id="nav{i}" playOrder="{i+1}"><navLabel><text>{escape(title)}</text></navLabel><content src="{name}"/></navPoint>\n'
        toc_items += f'<li><a href="{name}">{title}</a></li>\n'
        z.writestr(f'OEBPS/{name}', body_html)
    
    # Images - copy from site/static, fix the double-static path issue
    img_count = 0
    for img_file in sorted(SITE.rglob('*')):
        if img_file.is_file() and 'static/images/' in str(img_file):
            rel = str(img_file.relative_to(SITE))
            # rel is like "static/images/fire/bow-drill.jpg"
            zb_path = f'OEBPS/{rel}'
            iid = f'img{img_count}'
            ext = img_file.suffix.lower()
            mt = 'image/jpeg' if ext in ('.jpg','.jpeg') else 'image/png' if ext == '.png' else 'image/svg+xml'
            manifest_items += f'<item id="{iid}" href="{rel}" media-type="{mt}"/>\n'
            z.write(img_file, zb_path)
            img_count += 1
    
    for img_file in sorted(SITE.rglob('*')):
        if img_file.is_file() and 'static/maps/' in str(img_file):
            rel = str(img_file.relative_to(SITE))
            zb_path = f'OEBPS/{rel}'
            iid = f'img{img_count}'
            ext = img_file.suffix.lower()
            mt = 'image/jpeg' if ext in ('.jpg','.jpeg') else 'image/png' if ext == '.png' else 'image/svg+xml'
            manifest_items += f'<item id="{iid}" href="{rel}" media-type="{mt}"/>\n'
            z.write(img_file, zb_path)
            img_count += 1
    
    # OPF with dc:identifier
    opf = f'<?xml version="1.0" encoding="UTF-8"?>\n<package xmlns="http://www.idpf.org/2007/opf" version="2.0" unique-identifier="book-id">\n  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">\n    <dc:title>Outback Safe</dc:title>\n    <dc:creator>Outback Safe</dc:creator>\n    <dc:description>Australian Remote Travel Reference — 4WD survival, bush medicine, maps, first aid</dc:description>\n    <dc:language>en</dc:language>\n    <dc:identifier id="book-id">outback-safe-2026</dc:identifier>\n  </metadata>\n  <manifest>\n{manifest_items}  </manifest>\n  <spine toc="ncx">\n{spine_items}  </spine>\n</package>'
    z.writestr('OEBPS/content.opf', opf)
    
    # NCX for EPUB 2.0 compatibility (required for Apple Books)
    ncx = f'<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN" "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">\n<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">\n  <head>\n    <meta name="dtb:uid" content="outback-safe-2026"/>\n  </head>\n  <docTitle><text>Outback Safe</text></docTitle>\n  <navMap>\n{ncx_navmap}  </navMap>\n</ncx>'
    z.writestr('OEBPS/toc.ncx', ncx)
    
    # Nav XHTML
    nav_html = f'<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE html>\n<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">\n<head><title>Contents</title></head>\n<body>\n  <nav epub:type="toc">\n    <h1>Contents</h1>\n    <ol>\n{toc_items}    </ol>\n  </nav>\n</body>\n</html>'
    z.writestr('OEBPS/nav.xhtml', nav_html)

print(f'EPUB: {OUT.stat().st_size/1048576:.1f} MB — {len(pages)} pages, {img_count} images')
