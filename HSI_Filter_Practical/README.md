# HSI Image Filtering Practical

This project follows the filter names visible in the supplied screenshot of the reference repository's `filters/HSI_Filter_Practical` folder.

## Included operations
- RGB to HSI and HSI to RGB conversion
- averaging
- gaussian
- maximum
- median
- minimum
- weighted_average

The filters are applied to the HSI intensity (I) component, then converted back to RGB. No additional filter types have been added.

## Files
- `hsi_filters.py` — implementation
- `input/input.jpg` — your supplied birds image
- `output/` — generated results
- `requirements.txt` — dependencies

## Run in VS Code
```bash
pip install -r requirements.txt
python hsi_filters.py
```

## Accuracy note
The screenshot confirms the six filter names and that the practical includes HSI conversion. It does not show the original Python source or exact kernels. This implementation uses standard 3x3 definitions; `gaussian` and `weighted_average` are represented with the common 3x3 weighted kernel. It is therefore based on the visible repository contents, but is not a byte-for-byte reproduction of your friend's source code.
