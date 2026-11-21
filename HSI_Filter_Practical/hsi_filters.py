"""HSI filtering practical: averaging, gaussian, maximum, median, minimum,
and weighted_average. Place the source image at input/input.jpg, then run:
    pip install -r requirements.txt
    python hsi_filters.py
"""
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "input" / "input.jpg"
OUTPUT = ROOT / "output"
OUTPUT.mkdir(exist_ok=True)

def rgb_to_hsi(image):
    a = np.asarray(image.convert("RGB"), dtype=np.float32) / 255.0
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    intensity = (r + g + b) / 3.0
    mn = np.minimum(np.minimum(r, g), b)
    saturation = np.zeros_like(intensity)
    nz = intensity > 1e-8
    saturation[nz] = 1.0 - mn[nz] / intensity[nz]
    num = 0.5 * ((r-g) + (r-b))
    den = np.sqrt((r-g)**2 + (r-b)*(g-b))
    ratio = np.zeros_like(intensity)
    valid = den > 1e-8
    ratio[valid] = np.clip(num[valid] / den[valid], -1, 1)
    theta = np.arccos(ratio)
    hue = np.where(b <= g, theta, 2*np.pi-theta)
    hue[saturation <= 1e-8] = 0
    return hue, saturation, intensity

def hsi_to_rgb(h, s, i):
    h = np.mod(h, 2*np.pi)
    s, i = np.clip(s, 0, 1), np.clip(i, 0, 1)
    r, g, b = np.zeros_like(i), np.zeros_like(i), np.zeros_like(i)
    m = h < 2*np.pi/3
    x = h[m]
    b[m] = i[m]*(1-s[m])
    r[m] = i[m]*(1+s[m]*np.cos(x)/np.maximum(np.cos(np.pi/3-x), 1e-8))
    g[m] = 3*i[m]-r[m]-b[m]
    m = (h >= 2*np.pi/3) & (h < 4*np.pi/3)
    x = h[m]-2*np.pi/3
    r[m] = i[m]*(1-s[m])
    g[m] = i[m]*(1+s[m]*np.cos(x)/np.maximum(np.cos(np.pi/3-x), 1e-8))
    b[m] = 3*i[m]-r[m]-g[m]
    m = h >= 4*np.pi/3
    x = h[m]-4*np.pi/3
    g[m] = i[m]*(1-s[m])
    b[m] = i[m]*(1+s[m]*np.cos(x)/np.maximum(np.cos(np.pi/3-x), 1e-8))
    r[m] = 3*i[m]-g[m]-b[m]
    out = np.stack((r, g, b), axis=-1)
    return Image.fromarray(np.uint8(np.clip(out*255, 0, 255)))

def windows(a):
    p = np.pad(a, 1, mode="edge")
    h, w = a.shape
    return [p[y:y+h, x:x+w] for y in range(3) for x in range(3)]

def spatial_filter(a, name):
    n = windows(a)
    if name == "averaging":
        out = np.mean(n, axis=0)
    elif name == "gaussian":
        k = np.array([[1,2,1],[2,4,2],[1,2,1]], dtype=float)/16
        out = sum(k[y,x]*n[3*y+x] for y in range(3) for x in range(3))
    elif name == "maximum":
        out = np.max(n, axis=0)
    elif name == "median":
        out = np.median(n, axis=0)
    elif name == "minimum":
        out = np.min(n, axis=0)
    elif name == "weighted_average":
        k = np.array([[1,2,1],[2,4,2],[1,2,1]], dtype=float)/16
        out = sum(k[y,x]*n[3*y+x] for y in range(3) for x in range(3))
    else:
        raise ValueError("Unknown filter: " + name)
    return np.clip(out, 0, 1)

def main():
    if not INPUT.exists():
        raise FileNotFoundError(f"Put your image at: {INPUT}")
    original = Image.open(INPUT).convert("RGB")
    original.save(OUTPUT / "original.png")
    hue, sat, intensity = rgb_to_hsi(original)
    names = ["averaging", "gaussian", "maximum", "median", "minimum", "weighted_average"]
    for name in names:
        filtered = spatial_filter(intensity, name)
        hsi_to_rgb(hue, sat, filtered).save(OUTPUT / f"{name}.png")
        print("Saved", name)
    print("All six HSI filter outputs are in the output folder.")

if __name__ == "__main__":
    main()
