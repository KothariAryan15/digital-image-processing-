"""
HSI Image Filtering Practical
Implements RGB <-> HSI conversion and the six spatial filters visible
in the reference repository:
averaging, gaussian, maximum, median, minimum, weighted_average.

Run from this folder:
    pip install -r requirements.txt
    python hsi_filters.py
"""
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "input" / "input.jpg"
OUTPUT = ROOT / "output"
OUTPUT.mkdir(exist_ok=True)

def rgb_to_hsi(rgb):
    """Convert an RGB uint8 image to H, S, I float arrays.
    H is in radians [0, 2*pi), S and I are in [0, 1].
    """
    x = np.asarray(rgb, dtype=np.float32) / 255.0
    r, g, b = x[..., 0], x[..., 1], x[..., 2]
    intensity = (r + g + b) / 3.0

    minimum = np.minimum(np.minimum(r, g), b)
    saturation = np.zeros_like(intensity)
    nonzero_i = intensity > 1e-8
    saturation[nonzero_i] = 1.0 - minimum[nonzero_i] / intensity[nonzero_i]

    numerator = 0.5 * ((r - g) + (r - b))
    denominator = np.sqrt((r - g)**2 + (r - b) * (g - b))
    ratio = np.zeros_like(intensity)
    valid = denominator > 1e-8
    ratio[valid] = np.clip(numerator[valid] / denominator[valid], -1.0, 1.0)
    theta = np.arccos(ratio)
    hue = np.where(b <= g, theta, 2.0 * np.pi - theta)
    hue[saturation <= 1e-8] = 0.0
    return hue, saturation, intensity

def hsi_to_rgb(hue, saturation, intensity):
    """Convert HSI arrays back to an RGB uint8 image."""
    h = np.mod(hue, 2.0 * np.pi)
    s = np.clip(saturation, 0.0, 1.0)
    i = np.clip(intensity, 0.0, 1.0)
    r = np.zeros_like(i)
    g = np.zeros_like(i)
    b = np.zeros_like(i)

    m1 = h < 2.0 * np.pi / 3.0
    hm = h[m1]
    b[m1] = i[m1] * (1.0 - s[m1])
    r[m1] = i[m1] * (1.0 + s[m1] * np.cos(hm) / np.maximum(np.cos(np.pi/3.0 - hm), 1e-8))
    g[m1] = 3.0 * i[m1] - (r[m1] + b[m1])

    m2 = (h >= 2.0 * np.pi / 3.0) & (h < 4.0 * np.pi / 3.0)
    hm = h[m2] - 2.0 * np.pi / 3.0
    r[m2] = i[m2] * (1.0 - s[m2])
    g[m2] = i[m2] * (1.0 + s[m2] * np.cos(hm) / np.maximum(np.cos(np.pi/3.0 - hm), 1e-8))
    b[m2] = 3.0 * i[m2] - (r[m2] + g[m2])

    m3 = h >= 4.0 * np.pi / 3.0
    hm = h[m3] - 4.0 * np.pi / 3.0
    g[m3] = i[m3] * (1.0 - s[m3])
    b[m3] = i[m3] * (1.0 + s[m3] * np.cos(hm) / np.maximum(np.cos(np.pi/3.0 - hm), 1e-8))
    r[m3] = 3.0 * i[m3] - (g[m3] + b[m3])

    out = np.stack((r, g, b), axis=-1)
    return Image.fromarray(np.clip(out * 255.0, 0, 255).astype(np.uint8), "RGB")

def neighbourhoods(channel, size=3):
    """Return all size x size neighbourhoods using edge padding."""
    pad = size // 2
    p = np.pad(channel, ((pad, pad), (pad, pad)), mode="edge")
    h, w = channel.shape
    return np.stack(
        [p[y:y+h, x:x+w] for y in range(size) for x in range(size)],
        axis=0
    )

def apply_spatial_filter(channel, name):
    n = neighbourhoods(channel, 3)
    if name == "averaging":
        result = np.mean(n, axis=0)
    elif name == "gaussian":
        kernel = np.array([[1, 2, 1], [2, 4, 2], [1, 2, 1]], dtype=np.float32) / 16.0
        result = sum(kernel[y, x] * n[y*3+x] for y in range(3) for x in range(3))
    elif name == "maximum":
        result = np.max(n, axis=0)
    elif name == "median":
        result = np.median(n, axis=0)
    elif name == "minimum":
        result = np.min(n, axis=0)
    elif name == "weighted_average":
        kernel = np.array([[1, 2, 1], [2, 4, 2], [1, 2, 1]], dtype=np.float32) / 16.0
        result = sum(kernel[y, x] * n[y*3+x] for y in range(3) for x in range(3))
    else:
        raise ValueError(f"Unknown filter: {name}")
    return np.clip(result, 0.0, 1.0)

def main():
    original = Image.open(INPUT).convert("RGB")
    original.save(OUTPUT / "original.png")

    # Convert to HSI, filter only the intensity plane, then convert back to RGB.
    hue, saturation, intensity = rgb_to_hsi(original)
    filters = [
        "averaging", "gaussian", "maximum",
        "median", "minimum", "weighted_average"
    ]
    results = []
    for name in filters:
        filtered_i = apply_spatial_filter(intensity, name)
        result = hsi_to_rgb(hue, saturation, filtered_i)
        result.save(OUTPUT / f"{name}.png")
        results.append((name, result.copy()))

    # Comparison image: original + the six repository-listed filter outputs.
    tile_w, tile_h = 300, 230
    labels = [("original", original)] + results
    cols = 2
    rows = (len(labels) + cols - 1) // cols
    comparison = Image.new("RGB", (cols * tile_w, rows * tile_h), "white")
    draw = ImageDraw.Draw(comparison)
    for idx, (label, picture) in enumerate(labels):
        thumb = picture.copy()
        thumb.thumbnail((tile_w - 16, tile_h - 38))
        x = (idx % cols) * tile_w
        y = (idx // cols) * tile_h
        comparison.paste(thumb, (x + (tile_w-thumb.width)//2, y + 5))
        draw.text((x + 10, y + tile_h - 25), label, fill="black")
    comparison.save(OUTPUT / "all_filters_comparison.png")
    print("Completed: HSI conversion and six spatial filters.")
    print(f"Results saved in: {OUTPUT}")

if __name__ == "__main__":
    main()
