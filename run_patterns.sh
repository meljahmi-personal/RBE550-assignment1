#!/bin/bash

# Victor Sierra Pattern Runner
echo "Victor Sierra Pattern Runner"
echo "================================"

# Run each pattern script
echo "Running zigzag pattern..."
python3 zigzag_pattern.py

echo "Running linear pattern..."
python3 linear_pattern.py

echo "Running radial pattern..."
python3 radial_pattern.py

# Convert EPS to PNG using Python instead of ImageMagick
echo "Converting EPS files to PNG using Python..."
python3 -c "
try:
    from PIL import Image
    for pattern in ['zigzag', 'linear', 'radial']:
        eps_file = f'victor_sierra_{pattern}.eps'
        png_file = f'victor_sierra_{pattern}.png'
        try:
            img = Image.open(eps_file)
            img.save(png_file, 'PNG')
            print(f'Converted {eps_file} to {png_file}')
        except Exception as e:
            print(f'Failed to convert {eps_file}: {e}')
except ImportError:
    print('PIL not installed. Install with: pip install Pillow')
    print('Or convert manually using an image editor')
"

# Show results
echo ""
echo "Files created:"
ls -la victor_sierra_*.*
