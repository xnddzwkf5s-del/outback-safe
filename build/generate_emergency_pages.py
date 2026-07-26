#!/usr/bin/env python3
"""
generate_emergency_pages.py — Generate the emergency landing page for SHTF USB.

Creates index.html with 6 colour-coded tiles linking to critical
survival pages.  Designed for urgent access in an emergency — large
touch targets, high contrast, fast visual scanning.

Usage:
    python3 generate_emergency_pages.py --source "HTML_DIR" --output "HTML_DIR/index.html"
"""

import os
import argparse
from pathlib import Path
from textwrap import dedent

# ---------------------------------------------------------------------------
# Emergency tile definitions
# ---------------------------------------------------------------------------

EMERGENCY_TILES = [
    {
        'id': 'snake-bite',
        'emoji': '\U0001F40D',   # 🐍
        'label': 'Snake Bite',
        'color': '#dc2626',       # red-600
        'link': 'snake-bite.html',
        'desc': 'Pressure immobilisation bandage, ID guide, collapse management.',
    },
    {
        'id': 'cpr',
        'emoji': '\u2764\uFE0F',  # ❤️
        'label': 'CPR',
        'color': '#dc2626',
        'link': 'cpr.html',
        'desc': 'Compression-only CPR, airway, recovery position.',
    },
    {
        'id': 'bleeding',
        'emoji': '\U0001FA78',    # 🩸
        'label': 'Bleeding',
        'color': '#dc2626',
        'link': 'severe-bleeding.html',
        'desc': 'Tourniquets, wound packing, direct pressure.',
    },
    {
        'id': 'heat-stroke',
        'emoji': '\U0001F321\uFE0F',  # 🌡️
        'label': 'Heat Stroke',
        'color': '#ea580c',       # orange-600
        'link': 'heat-survival.html',
        'desc': 'Cooling, hydration, shade, heat illness stages.',
    },
    {
        'id': 'spider-bites',
        'emoji': '\U0001F577\uFE0F',  # 🕷️
        'label': 'Spider Bite',
        'color': '#ea580c',
        'link': 'spider-bites.html',
        'desc': 'Funnel-web PIB, redback, white-tail treatment.',
    },
    {
        'id': 'vehicle-fire',
        'emoji': '\U0001F525',    # 🔥
        'label': 'Fire',
        'color': '#ca8a04',       # yellow-600
        'link': 'grab-bag.html',
        'desc': 'Vehicle fire timeline, grab bag contents, evacuation.',
    },
]


# ---------------------------------------------------------------------------
# HTML template
# ---------------------------------------------------------------------------

def build_tile_html(tile):
    """Return the <a> tile element for one emergency tile."""
    return dedent(f'''\
    <a href="{tile['link']}" class="tile" id="tile-{tile['id']}"
       style="--tile-color: {tile['color']}">
      <span class="tile-emoji">{tile['emoji']}</span>
      <span class="tile-label">{tile['label']}</span>
      <span class="tile-desc">{tile['desc']}</span>
    </a>''')


def build_index_html():
    """Build the complete index.html string."""
    tiles_html = '\n'.join(build_tile_html(t) for t in EMERGENCY_TILES)

    return dedent(f'''\
    <!DOCTYPE html>
    <html lang="en-AU">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Outback Safe — Emergency Reference</title>
    <meta name="description" content="Offline emergency survival reference. Snake bite, CPR, bleeding, heat stroke, spider bites, vehicle fire.">
    <link rel="stylesheet" href="style.css">
    <style>
      /* Critical inline styles — rendered before style.css loads */
      :root {{
        --bg: #0f172a;
        --text: #e2e8f0;
        --muted: #94a3b8;
        --surface: #1e293b;
        --border: #334155;
      }}
      *, *::before, *::after {{
        box-sizing: border-box;
        margin: 0;
        padding: 0;
      }}
      html {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                     "Helvetica Neue", Arial, sans-serif;
        font-size: 16px;
        line-height: 1.6;
        color: var(--text);
        background: var(--bg);
        -webkit-font-smoothing: antialiased;
      }}
      body {{
        min-height: 100dvh;
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 2rem 1rem 4rem;
      }}

      /* Header */
      .hero {{
        text-align: center;
        margin-bottom: 2.5rem;
        max-width: 36rem;
      }}
      .hero h1 {{
        font-size: 2rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        color: #f8fafc;
        margin-bottom: 0.5rem;
      }}
      .hero p {{
        color: var(--muted);
        font-size: 1rem;
      }}

      /* Tile grid */
      .grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 1.25rem;
        width: 100%;
        max-width: 64rem;
      }}

      /* Tiles */
      .tile {{
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
        padding: 1.5rem;
        border-radius: 0.75rem;
        background: var(--surface);
        border: 2px solid var(--border);
        text-decoration: none;
        color: inherit;
        transition: border-color 0.15s, transform 0.1s;
        touch-action: manipulation;
        -webkit-tap-highlight-color: transparent;
      }}
      .tile:hover, .tile:active {{
        border-color: var(--tile-color);
        transform: translateY(-2px);
      }}
      .tile:focus-visible {{
        outline: 3px solid var(--tile-color);
        outline-offset: 2px;
      }}

      .tile-emoji {{
        font-size: 2.25rem;
        line-height: 1;
        margin-bottom: 0.25rem;
      }}
      .tile-label {{
        font-size: 1.25rem;
        font-weight: 700;
        color: var(--tile-color);
        letter-spacing: -0.01em;
      }}
      .tile-desc {{
        font-size: 0.875rem;
        color: var(--muted);
        line-height: 1.5;
      }}

      /* Color accent bars */
      .tile::before {{
        content: "";
        display: block;
        height: 3px;
        width: 2.5rem;
        background: var(--tile-color);
        border-radius: 2px;
        margin-bottom: 0.5rem;
      }}

      /* Footer */
      .footer {{
        margin-top: 3rem;
        text-align: center;
        color: var(--muted);
        font-size: 0.8rem;
        max-width: 36rem;
      }}
      .footer p + p {{
        margin-top: 0.5rem;
      }}

      /* Mobile tweaks */
      @media (max-width: 480px) {{
        body {{
          padding: 1.25rem 0.75rem 3rem;
        }}
        .hero h1 {{
          font-size: 1.5rem;
        }}
        .grid {{
          grid-template-columns: 1fr;
          gap: 1rem;
        }}
        .tile {{
          padding: 1.25rem;
          flex-direction: row;
          flex-wrap: wrap;
          align-items: center;
          gap: 0.25rem 0.75rem;
        }}
        .tile-emoji {{
          font-size: 1.75rem;
          margin-bottom: 0;
        }}
        .tile-label {{
          font-size: 1.1rem;
        }}
        .tile-desc {{
          width: 100%;
        }}
        .tile::before {{
          display: none;
        }}
      }}
    </style>
    </head>
    <body>
    <header class="hero">
      <h1>\u26A0\uFE0F Emergency Reference</h1>
      <p>Offline survival reference. Tap a tile for step-by-step instructions.
      All pages load instantly — no internet required.</p>
    </header>

    <div class="grid">
    {tiles_html}
    </div>

    <footer class="footer">
      <p><strong>Disclaimer:</strong> This information is for educational
      purposes only. It is not a substitute for professional medical advice,
      diagnosis, or treatment. In a life-threatening emergency, activate your
      PLB or call 000 (Australia) immediately.</p>
      <p>Outback Safe — Offline Survival Reference</p>
    </footer>
    </body>
    </html>''')


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description='Generate emergency landing page for SHTF USB.'
    )
    parser.add_argument(
        '--source', required=True,
        help='Directory containing preprocessed .html files.'
    )
    parser.add_argument(
        '--output', required=True,
        help='Path for the generated index.html (e.g. HTML_DIR/index.html).'
    )
    args = parser.parse_args()

    source_dir = Path(args.source).resolve()
    output_path = Path(args.output).resolve()

    if not source_dir.is_dir():
        print(f'ERROR: Source directory not found: {source_dir}', file=__import__('sys').stderr)
        __import__('sys').exit(1)

    # Verify that key pages exist
    missing = []
    for tile in EMERGENCY_TILES:
        target = source_dir / tile['link']
        if not target.is_file():
            missing.append(tile['link'])
    if missing:
        print(f'WARNING: {len(missing)} linked page(s) not found in {source_dir}:')
        for m in missing:
            print(f'  - {m}')

    # Build and write
    html = build_index_html()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as fh:
        fh.write(html)

    print(f'Wrote emergency landing page → {output_path}')
    print(f'  {len(EMERGENCY_TILES)} tiles, {len(missing)} missing link(s)')


if __name__ == '__main__':
    main()
