#!/usr/bin/env python3
"""Fix UTF-8 mojibake introduced by PowerShell Set-Content."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Mojibake sequences created when UTF-8 bytes were read as cp1252, then saved as UTF-8
REPLACEMENTS = {
    "\u00e2\u20ac\u201d": "\u2014",  # —
    "\u00e2\u20ac\u201c": "\u2013",  # –
    "\u00e2\u20ac\u2122": "\u2019",  # '
    "\u00e2\u20ac\u0153": "\u201c",  # "
    "\u00e2\u20ac\u009d": "\u201d",  # "
    "\u00c2\u00b7": "\u00b7",        # ·
    "\u00c3\u00a9": "\u00e9",        # é
    "\u00c2\u00a0": "\u00a0",        # nbsp if mangled
}


def main() -> None:
    updated = 0
    for path in sorted(ROOT.glob("*.html")):
        text = path.read_text(encoding="utf-8")
        original = text
        for bad, good in REPLACEMENTS.items():
            text = text.replace(bad, good)
        if text != original:
            path.write_text(text, encoding="utf-8", newline="\n")
            updated += 1
            print(f"Fixed {path.name}")
    print(f"Done: {updated} files")

    text = (ROOT / "index.html").read_text(encoding="utf-8")
    line = [l for l in text.splitlines() if "Welcome to Dance Dimensions of SWFL" in l][0]
    i = line.index("SWFL") + 5
    print("codepoints after SWFL:", [hex(ord(c)) for c in line[i : i + 3]])


if __name__ == "__main__":
    main()
