#!/usr/bin/env python3
"""Download remote images and rewrite HTML/CSS to use local images/ paths."""

import re
import urllib.request
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent
IMAGES_DIR = ROOT / "images"
EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".avif", ".svg"}

URL_PATTERN = re.compile(
    r"https?://[^\s\"')>]+",
    re.IGNORECASE,
)

MEDIA_ID_PATTERN = re.compile(r"/media/([^/]+~mv2\.[a-z0-9]+)/", re.IGNORECASE)
WIDTH_PATTERN = re.compile(r"/w_(\d+),")

FRIENDLY_NAMES = {
    "5d8739_6bf04846151a447c8e40756c32d0f9f5~mv2.png": "logo-wide-crop.png",
    "5d8739_9f20a0f96a8d4f2f91eca561b54e0688~mv2.png": "icon-facebook.png",
    "5d8739_7bf2613ae3274ee08f1af872db3f01d0~mv2.png": "icon-instagram.png",
    "5d8739_1e0dd61194ae46cf9a065642f7041c68~mv2.png": "icon-email.png",
    "5d8739_dab71dfff2874d2998ab1b4ac9483a0d~mv2.jpg": "hero-1.jpg",
    "5d8739_86b6d0c9836f4b779307e8d381f00677~mv2.jpg": "hero-2.jpg",
    "5d8739_a74c99f2d8dd4e77b8f45f46f406ebde~mv2.jpg": "hero-3.jpg",
    "5d8739_82068a75234c44718eae6d22eac19ba3~mv2.png": "logo-20th-anniversary.png",
    "5d8739_1f2da603921a42f7be1d8dc25218fa90~mv2.png": "affiliation-dance-masters.png",
    "de0b44_15be272868af43e890951a77fabab569.jpg": "affiliation-cape-coral.jpg",
    "5d8739_a79d7aff7efa4c00b22397d6f02da09f~mv2.gif": "affiliation-dance-educators.gif",
}


def is_image_url(url: str) -> bool:
    lower = url.lower()
    if "wixstatic.com" in lower or "unsplash.com" in lower:
        return True
    return any(lower.split("?")[0].endswith(ext) for ext in EXTENSIONS)


def url_width(url: str) -> int:
    match = WIDTH_PATTERN.search(url)
    return int(match.group(1)) if match else 0


def media_key(url: str) -> str | None:
    match = MEDIA_ID_PATTERN.search(url)
    return match.group(1) if match else None


def local_name_for_key(key: str) -> str:
    if key in FRIENDLY_NAMES:
        return FRIENDLY_NAMES[key]
    base = key.replace("~mv2.", ".")
    return re.sub(r"[^a-zA-Z0-9._-]", "_", base)


def unsplash_name(url: str) -> str:
    slug = url.split("/")[-1].split("?")[0] or "photo"
    return f"unsplash-{slug}.jpg"


def collect_urls() -> set[str]:
    urls: set[str] = set()
    for path in list(ROOT.glob("*.html")) + list(ROOT.glob("*.css")):
        text = path.read_text(encoding="utf-8")
        for match in URL_PATTERN.findall(text):
            url = match.rstrip(".,;")
            if is_image_url(url):
                urls.add(url)
    return urls


def build_download_plan(urls: set[str]) -> dict[str, str]:
    """Map every remote URL to a local images/ path."""
    url_to_local: dict[str, str] = {}
    groups: dict[str, list[str]] = defaultdict(list)

    for url in urls:
        key = media_key(url)
        if key:
            groups[key].append(url)
        elif "unsplash.com" in url:
            local = f"images/{unsplash_name(url)}"
            url_to_local[url] = local
        else:
            name = url.split("/")[-1].split("?")[0] or "image"
            url_to_local[url] = f"images/{name}"

    for key, group_urls in groups.items():
        best = max(group_urls, key=url_width)
        local = f"images/{local_name_for_key(key)}"
        for url in group_urls:
            url_to_local[url] = local

    return url_to_local


def download_file(url: str, dest: Path) -> bool:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0:
        return True
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            dest.write_bytes(response.read())
        print(f"Downloaded {dest.name}")
        return True
    except Exception as exc:
        print(f"Failed {dest.name}: {exc}")
        return False


def main() -> None:
    urls = collect_urls()
    url_to_local = build_download_plan(urls)

    # Download each unique local file — try all source URLs until one succeeds
    local_to_urls: dict[str, list[str]] = defaultdict(list)
    for url, local in url_to_local.items():
        local_to_urls[local].append(url)

    for local, group_urls in sorted(local_to_urls.items()):
        dest = ROOT / local
        if dest.exists() and dest.stat().st_size > 0:
            continue
        ordered = sorted(group_urls, key=url_width, reverse=True)
        for url in ordered:
            if download_file(url, dest):
                break

    # Rewrite project files — longest URLs first to avoid partial replacements
    replacements = sorted(url_to_local.items(), key=lambda item: len(item[0]), reverse=True)
    for path in list(ROOT.glob("*.html")) + list(ROOT.glob("*.css")):
        text = path.read_text(encoding="utf-8")
        original = text
        for remote, local in replacements:
            text = text.replace(remote, local)
        if text != original:
            path.write_text(text, encoding="utf-8")
            print(f"Updated {path.name}")

    print(f"\nDone: {len(local_to_urls)} images in images/")


if __name__ == "__main__":
    main()
