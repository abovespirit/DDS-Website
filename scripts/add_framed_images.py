#!/usr/bin/env python3
"""Wrap content photos in framed-image--photo markup site-wide."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SKIP_IMG = re.compile(
    r'class="logo-img"|width="39"|class="sponsor-logo"|footer-social',
    re.I,
)


def wrap_recital_banners(text: str) -> str:
    pattern = re.compile(
        r'(<div class="recital-banner">\s*<div class="container">)\s*'
        r'(<img[^>]+>)\s*'
        r'(</div>\s*</div>)',
        re.S,
    )
    return pattern.sub(
        r'\1\n            <div class="framed-image framed-image--photo recital-banner-photo">\n                \2\n            </div>\n        \3',
        text,
    )


def wrap_about_image_block(text: str) -> str:
    pattern = re.compile(
        r'(<div class="about-image-block">)\s*(<img[^>]+>)\s*(</div>)',
        re.S,
    )
    return pattern.sub(
        r'\1\n                <div class="framed-image framed-image--photo">\n                    \2\n                </div>\n            \3',
        text,
    )


def wrap_current_images(text: str) -> str:
    pattern = re.compile(
        r'(<div class="current-img[^"]*">)\s*(<img[^>]+>)',
        re.S,
    )
    return pattern.sub(
        r'\1\n                    <div class="framed-image framed-image--photo">\n                        \2\n                    </div>',
        text,
    )


def wrap_recital_flyer(text: str) -> str:
    pattern = re.compile(
        r'(<div class="recital-flyer">)\s*(<img[^>]+>)\s*(</div>)',
        re.S,
    )
    return pattern.sub(
        r'\1\n                <div class="framed-image framed-image--photo">\n                    \2\n                </div>\n            \3',
        text,
    )


def wrap_class_gallery_imgs(text: str) -> str:
    def wrap_block(match: re.Match) -> str:
        opening, inner, closing = match.group(1), match.group(2), match.group(3)
        if "framed-image" in inner:
            return match.group(0)
        wrapped = re.sub(
            r"<img([^>]+)>",
            r'<div class="framed-image framed-image--photo"><img\1></div>',
            inner,
        )
        return f"{opening}{wrapped}{closing}"

    return re.sub(
        r'(<div class="class-gallery[^"]*">)(.*?)(</div>)',
        wrap_block,
        text,
        flags=re.S,
    )


def add_classes(text: str, old: str, new: str) -> str:
    return text.replace(old, new)


def main() -> None:
    for path in sorted(ROOT.glob("*.html")):
        original = path.read_text(encoding="utf-8")
        text = original

        text = add_classes(text, 'class="class-strip-img"', 'class="class-strip-img framed-image framed-image--photo"')
        text = add_classes(text, 'class="philosophy-feature-img"', 'class="philosophy-feature-img framed-image framed-image--photo"')
        text = add_classes(text, 'class="gallery-item"', 'class="gallery-item framed-image framed-image--photo"')
        text = add_classes(text, 'class="group-visual"', 'class="group-visual framed-image framed-image--photo"')
        text = add_classes(text, 'class="video-card-thumb"', 'class="video-card-thumb framed-image framed-image--photo"')

        text = wrap_recital_banners(text)
        text = wrap_about_image_block(text)
        text = wrap_current_images(text)
        text = wrap_recital_flyer(text)
        text = wrap_class_gallery_imgs(text)

        if text != original:
            path.write_text(text, encoding="utf-8")
            print(f"Updated {path.name}")


if __name__ == "__main__":
    main()
