#!/usr/bin/env python3
"""Convert filled pink silhouettes to smooth SVG + high-res PNG outlines."""

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
from skimage.measure import find_contours

ROOT = Path(__file__).resolve().parent.parent
ABOUT = ROOT / "images" / "about"
PINK = "#ec3a8b"
PINK_RGBA = (236, 58, 139, 255)
STROKE_WIDTH = 16
PAD = 90
PNG_SIZE = 1800


def foreground_mask(img: Image.Image) -> np.ndarray:
    arr = np.array(img.convert("RGBA"))
    rgb = arr[:, :, :3].astype(np.int16)
    alpha = arr[:, :, 3]
    near_white = (rgb[:, :, 0] > 245) & (rgb[:, :, 1] > 245) & (rgb[:, :, 2] > 245)
    return (~near_white) & (alpha > 20)


def label_components(mask: np.ndarray) -> tuple[np.ndarray, list[int]]:
    labeled, count = ndimage.label(mask)
    if count == 0:
        return labeled, []
    sizes = ndimage.sum(mask, labeled, index=range(1, count + 1))
    ordered = sorted(range(1, count + 1), key=lambda i: sizes[i - 1], reverse=True)
    return labeled, ordered


def pick_component(labels: np.ndarray, ordered: list[int], strategy: str) -> np.ndarray:
    if not ordered:
        return labels > 0
    sizes = {lab: int((labels == lab).sum()) for lab in ordered}
    meaningful = [lab for lab in ordered if sizes[lab] >= 2000] or ordered[:1]

    if strategy == "left":
        best, best_x = meaningful[0], 1e9
        for lab in meaningful:
            xs = np.where(labels == lab)[1]
            cx = float(xs.mean())
            if cx < best_x:
                best, best_x = lab, cx
        return labels == best
    if strategy == "center":
        mid = labels.shape[1] / 2
        best, best_dist = meaningful[0], 1e9
        for lab in meaningful:
            xs = np.where(labels == lab)[1]
            dist = abs(float(xs.mean()) - mid)
            if dist < best_dist:
                best, best_dist = lab, dist
        return labels == best
    return labels == meaningful[0]


def clean_mask(mask: np.ndarray) -> np.ndarray:
    m = ndimage.binary_closing(mask, iterations=3)
    m = ndimage.binary_fill_holes(m)
    soft = ndimage.gaussian_filter(m.astype(np.float32), sigma=1.8)
    return soft > 0.5


def chaikin_closed(pts: np.ndarray, iterations: int = 3) -> np.ndarray:
    """Smooth a closed polyline with Chaikin corner-cutting."""
    pts = pts.copy()
    if np.allclose(pts[0], pts[-1]):
        pts = pts[:-1]
    for _ in range(iterations):
        n = len(pts)
        new_pts = []
        for i in range(n):
            p0 = pts[i]
            p1 = pts[(i + 1) % n]
            new_pts.append(0.75 * p0 + 0.25 * p1)
            new_pts.append(0.25 * p0 + 0.75 * p1)
        pts = np.asarray(new_pts, dtype=np.float64)
    return pts


def resample_closed(pts: np.ndarray, spacing: float = 2.5) -> np.ndarray:
    """Evenly resample a closed path."""
    if np.allclose(pts[0], pts[-1]):
        pts = pts[:-1]
    diffs = np.diff(pts, axis=0, append=pts[:1])
    seg_len = np.hypot(diffs[:, 0], diffs[:, 1])
    total = float(seg_len.sum())
    if total < 1:
        return pts
    n = max(32, int(total / spacing))
    cum = np.concatenate([[0.0], np.cumsum(seg_len)])
    samples = np.linspace(0, total, n, endpoint=False)
    out = []
    j = 0
    for s in samples:
        while j < len(seg_len) - 1 and cum[j + 1] < s:
            j += 1
        t = 0 if seg_len[j] == 0 else (s - cum[j]) / seg_len[j]
        out.append(pts[j] * (1 - t) + pts[(j + 1) % len(pts)] * t)
    return np.asarray(out, dtype=np.float64)


def extract_paths(mask: np.ndarray) -> list[np.ndarray]:
    h, w = mask.shape
    up = Image.fromarray((mask.astype(np.uint8) * 255), "L")
    up = up.resize((w * 3, h * 3), Image.Resampling.LANCZOS)
    soft = ndimage.gaussian_filter(np.array(up).astype(np.float32) / 255.0, sigma=1.6)
    contours = find_contours(soft, 0.5)
    if not contours:
        return []

    contours = sorted(contours, key=len, reverse=True)
    min_len = max(120, int(0.015 * (h * 3 + w * 3)))
    paths = []
    for contour in contours[:2]:
        if len(contour) < min_len:
            continue
        pts = np.column_stack([contour[:, 1], contour[:, 0]]).astype(np.float64)
        # Keep a modest number of samples, then smooth into flowing curves
        stride = max(1, len(pts) // 180)
        pts = pts[::stride]
        pts = chaikin_closed(pts, iterations=5)
        pts = resample_closed(pts, spacing=max(4.0, (pts.max(axis=0) - pts.min(axis=0)).max() / 120))
        paths.append(pts)
        break  # outer silhouette only
    return paths


def normalize_paths(paths: list[np.ndarray]) -> tuple[list[np.ndarray], float]:
    all_pts = np.vstack(paths)
    min_x, min_y = all_pts.min(axis=0)
    max_x, max_y = all_pts.max(axis=0)
    width = max_x - min_x
    height = max_y - min_y
    side = max(width, height) + PAD * 2
    ox = (side - width) / 2 - min_x
    oy = (side - height) / 2 - min_y
    out = [np.column_stack([p[:, 0] + ox, p[:, 1] + oy]) for p in paths]
    return out, side


def points_to_smooth_svg_path(pts: np.ndarray) -> str:
    """Build a cubic-bezier SVG path through points (midpoint smoothing)."""
    if np.allclose(pts[0], pts[-1]):
        pts = pts[:-1]
    n = len(pts)
    mid = lambda i, j: (pts[i] + pts[j]) / 2.0

    # Start at midpoint between last and first for continuity
    start = mid(n - 1, 0)
    d = [f"M {start[0]:.3f},{start[1]:.3f}"]
    for i in range(n):
        p = pts[i]
        nxt = mid(i, (i + 1) % n)
        d.append(f"Q {p[0]:.3f},{p[1]:.3f} {nxt[0]:.3f},{nxt[1]:.3f}")
    d.append("Z")
    return " ".join(d)


def paths_to_svg(paths: list[np.ndarray], side: float) -> str:
    parts = []
    for pts in paths:
        d = points_to_smooth_svg_path(pts)
        parts.append(
            f'<path d="{d}" fill="none" stroke="{PINK}" '
            f'stroke-width="{STROKE_WIDTH}" stroke-linejoin="round" '
            f'stroke-linecap="round" stroke-miterlimit="1"/>'
        )
    body = "\n  ".join(parts)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {side:.2f} {side:.2f}" '
        f'width="100%" height="100%" role="img">\n'
        f'  <rect width="100%" height="100%" fill="#ffffff"/>\n'
        f"  {body}\n"
        f"</svg>\n"
    )


def render_png_from_paths(paths: list[np.ndarray], side: float, size: int = PNG_SIZE) -> Image.Image:
    supersample = 4
    big = size * supersample
    canvas = Image.new("RGBA", (big, big), (255, 255, 255, 255))
    draw = ImageDraw.Draw(canvas)
    scale = (big - 80) / side
    stroke = max(10, int(STROKE_WIDTH * scale))
    margin = 40

    for pts in paths:
        coords = [((x * scale) + margin, (y * scale) + margin) for x, y in pts]
        if coords[0] != coords[-1]:
            coords.append(coords[0])
        draw.line(coords, fill=PINK_RGBA, width=stroke, joint="curve")
        r = stroke / 2
        for x, y in coords[:: max(1, len(coords) // 200)]:
            draw.ellipse((x - r, y - r, x + r, y + r), fill=PINK_RGBA)

    return canvas.resize((size, size), Image.Resampling.LANCZOS)


def convert_file(src_name: str, dest_stem: str, strategy: str) -> None:
    img = Image.open(ABOUT / src_name)
    mask = foreground_mask(img)
    labels, ordered = label_components(mask)
    print(f"{src_name}: {len(ordered)} component(s), strategy={strategy}")
    single = clean_mask(pick_component(labels, ordered, strategy))
    paths = extract_paths(single)
    if not paths:
        raise RuntimeError(f"No contour found for {src_name}")

    norm_paths, side = normalize_paths(paths)
    svg_path = ABOUT / f"{dest_stem}.svg"
    svg_path.write_text(paths_to_svg(norm_paths, side), encoding="utf-8")

    png = render_png_from_paths(norm_paths, side)
    png_path = ABOUT / f"{dest_stem}.png"
    png.save(png_path, "PNG", optimize=True)
    print(f"  -> {svg_path.name}, {png_path.name} ({png.size[0]}x{png.size[1]})")


def main() -> None:
    convert_file("dance-floor.png", "dance-floor-outline", "largest")
    convert_file("small-class.png", "small-class-outline", "left")
    convert_file("recital.png", "recital-outline", "center")


if __name__ == "__main__":
    main()
