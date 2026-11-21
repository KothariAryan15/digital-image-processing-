# HSI Filter Practical

This practical contains the six filter names shown in the supplied screenshot of the reference project:

- averaging
- gaussian
- maximum
- median
- minimum
- weighted_average

It also converts the input RGB image to HSI, applies each spatial filter to the intensity (I) component, and converts the result back to RGB.

## Run in VS Code

1. Put your image in `input/input.jpg`.
2. Open a terminal in this folder.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run:

```bash
python hsi_filters.py
```

The six processed images and the original copy are saved in `output/`.

## Note on implementation

The screenshot confirms the filter names but does not expose the original source code or exact kernels. The script uses standard 3x3 implementations. Gaussian and weighted_average use the common 3x3 weighted kernel.
