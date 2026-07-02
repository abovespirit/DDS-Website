import re
from pathlib import Path

root = Path(__file__).resolve().parent.parent
for path in sorted(root.glob("*.html")):
    text = path.read_text(encoding="utf-8")
    for m in re.finditer(r"<img[^>]+>", text):
        tag = m.group(0)
        if "logo-img" in tag or 'width="39"' in tag:
            continue
        start = m.start()
        before = text[max(0, start - 500) : start]
        if "sponsors-grid" in before or "sponsor-logo" in before.split("<img")[-1]:
            continue
        if "framed-image" not in before:
            print(f"{path.name}: {tag[:90]}")
