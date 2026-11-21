"""HSI filtering practical: six spatial filters on the intensity channel."""
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / 'input' / 'input.jpg'
OUTPUT = ROOT / 'output'
OUTPUT.mkdir(exist_ok=True)


def rgb_to_hsi(im):
    a = np.asarray(im.convert('RGB'), dtype=np.float32) / 255.0
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    intensity = (r + g + b) / 3.0
    minimum = np.minimum(np.minimum(r, g), b)
    saturation = np.zeros_like(intensity)
    nz = intensity > 1e-8
    saturation[nz] = 1 - minimum[nz] / intensity[nz]
    numerator = 0.5 * ((r - g) + (r - b))
    denominator = np.sqrt((r - g) ** 2 + (r - b) * (g - b))
    ratio = np.zeros_like(intensity)
    valid = denominator > 1e-8
    ratio[valid] = np.clip(numerator[valid] / denominator[valid], -1, 1)
    hue = np.arccos(ratio)
    hue = np.where(b <= g, hue, 2 * np.pi - hue)
    hue[saturation <= 1e-8] = 0
    return hue, saturation, intensity


def hsi_to_rgb(hue, saturation, intensity):
    hue = np.mod(hue, 2 * np.pi)
    saturation = np.clip(saturation, 0, 1)
    intensity = np.clip(intensity, 0, 1)
    r = np.zeros_like(intensity)
    g = np.zeros_like(intensity)
    b = np.zeros_like(intensity)
    m = hue < 2 * np.pi / 3
    x = hue[m]
    b[m] = intensity[m] * (1 - saturation[m])
    r[m] = intensity[m] * (1 + saturation[m] * np.cos(x) / np.maximum(np.cos(np.pi / 3 - x), 1e-8))
    g[m] = 3 * intensity[m] - r[m] - b[m]
    m = (hue >= 2 * np.pi / 3) & (hue < 4 * np.pi / 3)
    x = hue[m] - 2 * np.pi / 3
    r[m] = intensity[m] * (1 - saturation[m])
    g[m] = intensity[m] * (1 + saturation[m] * np.cos(x) / np.maximum(np.cos(np.pi / 3 - x), 1e-8))
    b[m] = 3 * intensity[m] - r[m] - g[m]
    m = hue >= 4 * np.pi / 3
    x = hue[m] - 4 * np.pi / 3
    g[m] = intensity[m] * (1 - saturation[m])
    b[m] = intensity[m] * (1 + saturation[m] * np.cos(x) / np.maximum(np.cos(np.pi / 3 - x), 1e-8))
    r[m] = 3 * intensity[m] - g[m] - b[m]
    pixels = np.uint8(np.clip(np.stack((r, g, b), axis=-1) * 255, 0, 255))
    return Image.fromarray(pixels)


def filter2d(array, name):
    padded = np.pad(array, 1, mode='edge')
    height, width = array.shape
    windows = [padded[y:y + height, x:x + width] for y in range(3) for x in range(3)]
    if name == 'averaging':
        result = np.mean(windows, axis=0)
    elif name == 'median':
        result = np.median(windows, axis=0)
    elif name == 'maximum':
        result = np.max(windows, axis=0)
    elif name == 'minimum':
        result = np.min(windows, axis=0)
    else:
        kernel = np.array([[1, 2, 1], [2, 4, 2], [1, 2, 1]], dtype=float) / 16
        result = sum(kernel[y, x] * windows[3 * y + x] for y in range(3) for x in range(3))
    return np.clip(result, 0, 1)


def main():
    if not INPUT.exists():
        raise FileNotFoundError(f'Input image not found: {INPUT}. Place your image at input/input.jpg.')
    original = Image.open(INPUT).convert('RGB')
    original.save(OUTPUT / 'original.png')
    hue, saturation, intensity = rgb_to_hsi(original)
    names = ['averaging', 'gaussian', 'maximum', 'median', 'minimum', 'weighted_average']
    results = []
    for name in names:
        filtered = hsi_to_rgb(hue, saturation, filter2d(intensity, name))
        filtered.save(OUTPUT / f'{name}.png')
        results.append((name, filtered.copy()))
    cell_w, cell_h = 306, 235
    sheet = Image.new('RGB', (cell_w * 2, cell_h * 4), (245, 245, 245))
    draw = ImageDraw.Draw(sheet)
    for index, (name, picture) in enumerate([('original', original)] + results):
        x, y = (index % 2) * cell_w, (index // 2) * cell_h
        picture.thumbnail((cell_w - 16, cell_h - 38))
        sheet.paste(picture, (x + 8, y + 26))
        draw.text((x + 8, y + 7), name.replace('_', ' ').title(), fill=(20, 20, 20))
    sheet.save(OUTPUT / 'all_filters_comparison.png')
    print('Generated six filter outputs and comparison sheet.')


if __name__ == '__main__':
    main()
