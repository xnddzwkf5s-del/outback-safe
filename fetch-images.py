#!/usr/bin/env python3
"""
Fetch plant images from Wikimedia Commons for Survival Wiki.
Uses Wikipedia API to find article images, then downloads from Commons.
"""
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

OUTDIR = os.path.expanduser("~/Survival-Wiki/static/images/plants")
os.makedirs(OUTDIR, exist_ok=True)

# Plants to fetch: (output_filename, wikipedia_search_term, fallback_commons_search)
PLANTS = [
    # === Arid Outback Plants ===
    ("eremophila.jpg", "Eremophila maculata", "Eremophila maculata flower"),
    ("acacia-aneura.jpg", "Acacia aneura", "Acacia aneura tree"),
    ("santalum-spicatum.jpg", "Santalum spicatum", "Santalum spicatum tree"),
    ("duboisia-hopwoodii.jpg", "Duboisia hopwoodii", "Duboisia hopwoodii"),
    ("dodonaea-viscosa.jpg", "Dodonaea viscosa", "Dodonaea viscosa flower"),
    ("eucalyptus-camaldulensis.jpg", "Eucalyptus camaldulensis", "Eucalyptus camaldulensis tree"),
    # Extra arid
    ("sarcostemma-australe.jpg", "Sarcostemma australe", "Sarcostemma australe"),
    ("senna-artemisioides.jpg", "Senna artemisioides", "Senna artemisioides flower"),
    ("pterocaulon-sphacelatum.jpg", "Pterocaulon sphacelatum", "Pterocaulon sphacelatum"),
    ("eremophila-duttonii.jpg", "Eremophila duttonii", "Eremophila duttonii"),
    # === Tropical Outback Plants ===
    ("melaleuca-alternifolia.jpg", "Melaleuca alternifolia", "Melaleuca alternifolia flower"),
    ("melaleuca-quinquenervia.jpg", "Melaleuca quinquenervia", "Melaleuca quinquenervia bark"),
    ("alstonia-constricta.jpg", "Alstonia constricta", "Alstonia constricta"),
    ("centipeda.jpg", "Centipeda cunninghamii", "Centipeda cunninghamii"),
    ("pandanus-spiralis.jpg", "Pandanus spiralis", "Pandanus spiralis fruit"),
    # Extra tropical
    ("terminalia-ferdinandiana.jpg", "Terminalia ferdinandiana", "Terminalia ferdinandiana fruit"),
    ("carpentaria-acuminata.jpg", "Carpentaria acuminata", "Carpentaria acuminata"),
    ("buchanania-obovata.jpg", "Buchanania obovata", "Buchanania obovata"),
    ("ficus-opposita.jpg", "Ficus opposita", "Ficus opposita leaf"),
    ("acacia-holosericea.jpg", "Acacia holosericea", "Acacia holosericea"),
    ("eucalyptus-globulus.jpg", "Eucalyptus globulus", "Eucalyptus globulus bark"),
    # === Deadly Look-Alikes ===
    ("duboisia-myoporoides.jpg", "Duboisia myoporoides", "Duboisia myoporoides"),
    ("euphorbia-hirta.jpg", "Euphorbia hirta", "Euphorbia hirta flower"),
    ("ricinus-communis.jpg", "Ricinus communis", "Ricinus communis plant"),
    ("datura-stramonium.jpg", "Datura stramonium", "Datura stramonium flower"),
    ("dendrocnide-moroides.jpg", "Dendrocnide moroides", "Dendrocnide moroides leaf"),
]

USER_AGENT = "SurvivalWiki/1.0 (educational project; vwoo@outlook.com.au)"
HEADERS = {"User-Agent": USER_AGENT}


def md5_path(filename):
    """Compute the Commons hash-based subdirectory path."""
    m = hashlib.md5(filename.encode("utf-8")).hexdigest()
    return f"{m[0]}/{m[:2]}"


def download_from_url(url, outpath):
    """Download a file, return True on success."""
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
        # Check if we got an image or error HTML
        if data[:6] == b"<html>" or data[:5] == b"<!DOC":
            return False
        with open(outpath, "wb") as f:
            f.write(data)
        return True
    except Exception:
        return False


def find_image_on_wikipedia(search_term):
    """Use Wikipedia API to find the main image for an article."""
    params = {
        "action": "query",
        "prop": "pageimages|images",
        "titles": search_term,
        "format": "json",
        "pithumbsize": 800,
        "imlimit": 10,
    }
    url = "https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
    except Exception as e:
        print(f"    API error: {e}")
        return None

    pages = data.get("query", {}).get("pages", {})
    for page_id, page in pages.items():
        # Try pageimage first
        if "pageimage" in page:
            return page["pageimage"]
        # Try images list
        if "images" in page:
            for img in page["images"]:
                title = img.get("title", "")
                if title.startswith("File:"):
                    fn = title[5:]
                    ext = fn.lower().rsplit(".", 1)[-1] if "." in fn else ""
                    if ext in ("jpg", "jpeg", "png", "gif", "webp"):
                        return fn
    return None


def find_on_commons_direct(search_term):
    """Use Commons API directly as fallback."""
    params = {
        "action": "query",
        "list": "search",
        "srsearch": search_term,
        "srnamespace": 6,
        "format": "json",
        "srlimit": 10,
    }
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
    except Exception as e:
        print(f"    Commons API error: {e}")
        return None

    for page in data.get("query", {}).get("search", []):
        title = page.get("title", "")
        if title.startswith("File:"):
            fn = title[5:]
            ext = fn.lower().rsplit(".", 1)[-1] if "." in fn else ""
            if ext in ("jpg", "jpeg", "png", "gif", "webp"):
                # Skip PDFs, svgs, etc by checking the "size" field
                wordcount = page.get("wordcount", 0)
                if wordcount > 50 and not any(
                    bad in fn.lower()
                    for bad in ["flag", "icon", "diagram", "graph", "map", "logo", "symbol"]
                ):
                    return fn
    # Fallback: just return the first JPG
    for page in data.get("query", {}).get("search", []):
        title = page.get("title", "")
        if title.startswith("File:") and title.lower().endswith(".jpg"):
            return title[5:]
    return None


def download_plant_image(out_name, search_wiki, search_commons):
    """Find and download a plant image from Wikipedia/Commons."""
    outpath = os.path.join(OUTDIR, out_name)

    # Skip if already have a valid image
    if os.path.exists(outpath) and os.path.getsize(outpath) > 500:
        print(f"  ✅ Already have {out_name}")
        return True

    print(f"\n  Searching: {search_wiki}")

    # Step 1: Try Wikipedia API
    filename = find_image_on_wikipedia(search_wiki)
    if filename:
        print(f"    Found on Wikipedia: {filename}")
    else:
        # Step 2: Try Commons search directly
        print(f"    Not on Wikipedia, searching Commons: {search_commons}")
        filename = find_on_commons_direct(search_commons)

    if not filename:
        print(f"    ❌ No image found for {search_wiki}")
        return False

    # Build the correct download URL
    path_prefix = md5_path(filename)
    url = f"https://upload.wikimedia.org/wikipedia/commons/{path_prefix}/{filename}"
    thumb_url = f"https://upload.wikimedia.org/wikipedia/commons/thumb/{path_prefix}/{filename}/800px-{filename}"

    print(f"    Downloading: {filename}")

    # Try direct download first
    if download_from_url(url, outpath):
        size = os.path.getsize(outpath)
        print(f"    ✅ {out_name} ({size:,} bytes)")
        return True

    # Try thumbnail
    if download_from_url(thumb_url, outpath):
        size = os.path.getsize(outpath)
        print(f"    ✅ {out_name} (thumb, {size:,} bytes)")
        return True

    print(f"    ❌ Failed to download {filename}")
    return False


def main():
    print("=" * 60)
    print("Fetching Plant Images from Wikimedia Commons")
    print("=" * 60)

    success = 0
    failed = 0

    for out_name, search_wiki, search_commons in PLANTS:
        # Be polite: delay between requests
        time.sleep(1.5)
        if download_plant_image(out_name, search_wiki, search_commons):
            success += 1
        else:
            failed += 1

    print()
    print("=" * 60)
    print(f"Results: {success} downloaded, {failed} failed, {success+failed} total")
    print(f"Images in: {OUTDIR}")
    print("=" * 60)

    # List files
    for f in sorted(os.listdir(OUTDIR)):
        fpath = os.path.join(OUTDIR, f)
        size = os.path.getsize(fpath)
        print(f"  {f:45s} {size:>8,} bytes")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
