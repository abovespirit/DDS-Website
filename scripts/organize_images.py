#!/usr/bin/env python3
"""Organize images into category folders and update all HTML/CSS references."""

from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parent.parent
IMAGES = ROOT / "images"

# filename -> subfolder/new-filename (relative to images/)
# Keep filenames unique; rename cryptic Wix IDs to friendlier names where clear.
MOVES: dict[str, str] = {
    # Brand
    "logo-wide-crop.png": "brand/logo-wide-crop.png",
    "logo-20th-anniversary.png": "brand/logo-20th-anniversary.png",
    "icon-facebook.png": "brand/icon-facebook.png",
    "icon-instagram.png": "brand/icon-instagram.png",
    "icon-email.png": "brand/icon-email.png",
    "affiliation-dance-masters.png": "brand/affiliation-dance-masters.png",
    "5d8739_a79d7aff7efa4c00b22397d6f02da09f~mv2.gif": "brand/affiliation-dance-educators.gif",
    "de0b44_15be272868af43e890951a77fabab569.jpg": "brand/affiliation-cape-coral.jpg",

    # Heroes
    "hero-1.jpg": "heroes/hero-1.jpg",
    "hero-2.jpg": "heroes/hero-2.jpg",
    "hero-3.jpg": "heroes/hero-3.jpg",

    # Home
    "5d8739_31e96ce3490d427cac0a33a7a806fa4a.jpg": "home/welcome-dancers.jpg",
    "5d8739_b5450b14e17d42bbb0b79d996d72a408.jpeg": "home/class-dancers.jpeg",
    "5d8739_42b076124749491d81a536142f34ffdd.jpg": "home/show-troupe.jpg",
    "5d8739_ae1304e39b9449718483c9ead166f34a.jpg": "home/studio-class.jpg",
    "5d8739_df50e004f8eb486f8ab0678adbe43db9.jpg": "home/recital.jpg",

    # Classes
    "5d8739_e34b3b7057e047dfa2bf3591b786bafc.png": "classes/summer-stepping-stones.png",
    "5d8739_9e91701359e04bc499fe96427e65e512.png": "classes/summer-fairytale.png",
    "5d8739_b951fbe370e54606867aa30ad507f9f9.png": "classes/summer-silly-goose.png",
    "5d8739_f5a4f080636546acb24ef260f11e3a80.png": "classes/summer-bring-the-hype.png",
    "group-preschool.png": "classes/group-preschool.png",
    "group-elementary.png": "classes/group-elementary.png",
    "group-teens.png": "classes/group-teens.png",
    "5d8739_e60e4b83228b4f07aef04b758767055f.jpg": "classes/dance-with-me.jpg",
    "5d8739_f85d9ed52bf84db294e7dd0d7352e010.jpg": "classes/creative-dance.jpg",
    "5d8739_7eea7a6cea6840baa204c3f88268e02a.jpg": "classes/kinder.jpg",
    "5d8739_953b42159eea48308d08c6b4f4cddcd2.jpg": "classes/primary-teen.jpg",
    "5d8739_040bdc45980c458c81da97e8251fe11f.jpg": "classes/teen-jazz.jpg",
    "5d8739_cf3cf74c727f46aeba50554e013ec7b1.jpg": "classes/studio-dancers.jpg",
    "5d8739_17cd05146cb44bb6b22671c5fcd0aa7c.jpg": "classes/primary.jpg",
    "5d8739_543b783392ed4f95adbb8de7807c0d42.jpg": "classes/dress-code-preschool.jpg",
    "5d8739_d3771d086ed9487b8bc1c389da74f711.jpg": "classes/dress-code-upper.jpg",

    # About
    "about-dance-floor.png": "about/dance-floor.png",
    "about-small-class.png": "about/small-class.png",
    "about-recital.png": "about/recital.png",
    "attention-line-art.png": "about/attention-line-art.png",
    "5d8739_26122e833aac4bc79104c3daf3aadd9b.png": "about/feature-icon.png",

    # Gallery
    "file.jpeg": "gallery/video-thumb.jpeg",
    "5d8739_61cbdd17c2a148f8b95cfc33d0ac475a.jpeg": "gallery/dancers.jpeg",

    # Show Troupe
    "5d8739_9f31f4a4090c41f7b3233a34466dcf30.jpg": "show-troupe/performance-1.jpg",
    "5d8739_e292f4705d684da0853827a7507c7098.jpg": "show-troupe/performance-2.jpg",
    "5d8739_e5ffc2af9ad242acaefc62658d9ddf77.jpg": "show-troupe/performance-3.jpg",

    # Recital
    "5d8739_03320e921748457eba094375d41925db.jpg": "recital/banner.jpg",
    "5d8739_a3443a81c49c4852a57f55a2d770b387.png": "recital/rehearsal-schedule.png",
    "5d8739_b83d317b326f4f38927329251dcd2c20.png": "recital/important-dates.png",
    "5d8739_a8ee1531c80e4a14b31ee39c9e157bd1.png": "recital/gift-trophy-1.png",
    "5d8739_e07fec9859f04c6b9342d5d5874a12c7.png": "recital/gift-medal-1.png",
    "5d8739_0ebf47f0b106496e884904d90b254a21.png": "recital/gift-trophy-2.png",
    "5d8739_a285dff01e12444d9107e3574ab16068.png": "recital/gift-medal-2.png",
    "recital-line-art.png": "recital/line-art.png",

    # Sponsors
    "5d8739_68751d17357c4bc5a86fa40ecad6eb21.png": "sponsors/oasis.png",
    "5d8739_4c10813ea26647919e0c8c67b3e54772.png": "sponsors/infinite-air.png",
    "5d8739_1d31cce095b44ddc8536ef68c34f7d52.png": "sponsors/united-lawn.png",
    "5d8739_835a249939324f02bd511164232bb903.png": "sponsors/boxed-in.png",
    "5d8739_7a9eaab35acc4b7180bb9166fb3e2387.jpg": "sponsors/surfside.jpg",
    "5d8739_284b16cbbec242ef9f759a67513e5d17.jpg": "sponsors/sharper-things.jpg",
    "5d8739_1a44e2269f7841a5b1cf2d8389b26961.png": "sponsors/ryan-and-ryan.png",
    "5d8739_f9925c5311184e9ba1163c60ea0276c9.jpg": "sponsors/lusk.jpg",
    "5d8739_bf34fd5a98274159bc889956019e392e.png": "sponsors/signs-by-sophia.png",
    "5d8739_f099d8397ce64a4d99461b7d93829bf6.png": "sponsors/all-perfect.png",
    "5d8739_f60f46e0f5f54b2c9b6c0bbbe48c9de1.jpg": "sponsors/diamond-fence.jpg",
    "5d8739_90019ca8544b4fd7b62e528db1a7f1f2.png": "sponsors/orthodontics.png",
    "5d8739_9a6ab492c0644d73a75b53687d137ca9.png": "sponsors/belle.png",
}


def find_source(name: str) -> Path | None:
    """Find a file by name anywhere under images/."""
    direct = IMAGES / name
    if direct.is_file():
        return direct
    matches = list(IMAGES.rglob(name))
    return matches[0] if matches else None


def main() -> None:
    # Move / rename files
    moved = 0
    missing = []
    for old_name, new_rel in MOVES.items():
        src = find_source(old_name)
        dest = IMAGES / new_rel
        if src is None:
            missing.append(old_name)
            continue
        if src.resolve() == dest.resolve():
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            # Already organized
            if src != dest and src.is_file():
                # Keep dest, remove duplicate source if different path
                pass
            continue
        shutil.move(str(src), str(dest))
        print(f"Moved {old_name} -> images/{new_rel}")
        moved += 1

    # Also move any leftover unused files into misc/
    for f in list(IMAGES.glob("*")):
        if f.is_file() and f.name not in MOVES:
            # Check if already accounted for via rename
            dest_misc = IMAGES / "misc" / f.name
            dest_misc.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(f), str(dest_misc))
            print(f"Moved leftover {f.name} -> images/misc/{f.name}")

    # Build replacement map: old path fragment -> new path
    # Replace longest old names first to avoid partial matches
    replacements: list[tuple[str, str]] = []
    for old_name, new_rel in MOVES.items():
        # Paths that may appear in files
        replacements.append((f"images/{old_name}", f"images/{new_rel}"))

    replacements.sort(key=lambda x: len(x[0]), reverse=True)

    updated_files = 0
    for path in list(ROOT.glob("*.html")) + list(ROOT.glob("*.css")):
        text = path.read_text(encoding="utf-8")
        original = text
        for old, new in replacements:
            text = text.replace(old, new)
        if text != original:
            path.write_text(text, encoding="utf-8")
            print(f"Updated {path.name}")
            updated_files += 1

    print(f"\nDone: moved {moved} files, updated {updated_files} pages")
    if missing:
        print("Missing source files (skipped):")
        for m in missing:
            print(f"  - {m}")

    # Verify references
    pattern = re.compile(r"images/[a-zA-Z0-9._~/-]+\.(?:png|jpe?g|gif|webp|svg)", re.I)
    broken = []
    for path in list(ROOT.glob("*.html")) + list(ROOT.glob("*.css")):
        for ref in pattern.findall(path.read_text(encoding="utf-8")):
            if not (ROOT / ref).exists():
                broken.append((path.name, ref))
    if broken:
        print("\nBROKEN REFERENCES:")
        for page, ref in broken:
            print(f"  {page}: {ref}")
    else:
        print("\nAll image references resolve.")


if __name__ == "__main__":
    main()
