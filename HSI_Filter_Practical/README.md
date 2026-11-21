# HSI Image Filtering Practical

This project uses the supplied birds-and-flowers image (`input/input.jpg`) and applies the six spatial filters named in the reference repository: averaging, gaussian, maximum, median, minimum, and weighted_average.

The image is converted from RGB to HSI. Each filter is applied to the intensity (I) component, then the result is converted back to RGB. Individual results and a labeled comparison sheet are saved in `output/`.

## Run in VS Code

```bash
pip install -r requirements.txt
python hsi_filters.py
```

## Output files

- `original.png`
- `averaging.png`
- `gaussian.png`
- `maximum.png`
- `median.png`
- `minimum.png`
- `weighted_average.png`
- `all_filters_comparison.png`

## Implementation note

The reference screenshot exposed the six filter names and HSI workflow, but not the friend's complete source code or exact kernels. This project therefore uses standard 3x3 spatial-filter implementations. Gaussian and weighted_average use the common 3x3 weighted kernel.
