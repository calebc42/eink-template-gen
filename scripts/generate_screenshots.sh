#!/bin/bash

# This script generates all the example images for the README.
# Assumes 'eink-template-gen' is in your system's PATH.
# Run this script from the project root directory.

OUTPUT_DIR="../src/assets/screenshots"
BEFORE_DIR="$OUTPUT_DIR/before"
mkdir -p "$OUTPUT_DIR"
mkdir -p "$BEFORE_DIR"

echo "=== E-INK TEMPLATE GENERATOR SCREENSHOTS ==="
echo "Saving images to $OUTPUT_DIR/"

# --- 1. Core Problem (The "Why") ---
echo "Generating: 1. Core Problem (Before & After)"

# "Before" - Blurry, fractional pixel lines
eink-template-gen lined --spacing 6mm --no-auto-adjust --device manta \
  --output-dir "$BEFORE_DIR" --filename "problem_before_blurry_lines.png"

# "After" - Crisp, pixel-perfect lines
eink-template-gen lined --spacing 6mm --device manta \
  --output-dir "$OUTPUT_DIR" --filename "problem_after_pixel_perfect_lined.png"

# "Before" - Default grid alignment (awkward edge)
eink-template-gen grid --spacing 5mm --major_every 5 --device manta \
  --output-dir "$BEFORE_DIR" --filename "problem_before_grid_alignment.png"

# "After" - Force-aligned grid
eink-template-gen grid --spacing 5mm --major_every 5 --force-major-alignment --device manta \
  --output-dir "$OUTPUT_DIR" --filename "problem_after_grid_alignment.png"


# --- 2. Template Type Gallery ---
echo "Generating: 2. Template Type Gallery"
eink-template-gen lined --spacing 7mm --line-numbers --device manta --output-dir "$OUTPUT_DIR" --filename "gallery_lined_with_numbers.png"
eink-template-gen dotgrid --spacing 5mm --major_every 5 --device manta --output-dir "$OUTPUT_DIR" --filename "gallery_dotgrid_with_crosshairs.png"
eink-template-gen grid --spacing 5mm --major_every 5 --axis-labels --device manta --output-dir "$OUTPUT_DIR" --filename "gallery_grid_with_axis_labels.png"
eink-template-gen grid --spacing 5mm --cell-labels --device manta --output-dir "$OUTPUT_DIR" --filename "gallery_grid_with_cell_labels.png"
eink-template-gen manuscript --spacing 8mm --device manta --output-dir "$OUTPUT_DIR" --filename "gallery_manuscript.png"
eink-template-gen french_ruled --spacing 2mm --device manta --output-dir "$OUTPUT_DIR" --filename "gallery_french_ruled.png"
eink-template-gen music_staff --spacing 2mm --device manta --output-dir "$OUTPUT_DIR" --filename "gallery_music_staff.png"
eink-template-gen isometric --spacing 5mm --device manta --output-dir "$OUTPUT_DIR" --filename "gallery_isometric.png"
eink-template-gen hexgrid --spacing 5mm --device manta --output-dir "$OUTPUT_DIR" --filename "gallery_hexgrid.png"
eink-template-gen hybrid_lined_dotgrid --spacing 6mm --device manta --output-dir "$OUTPUT_DIR" --filename "gallery_hybrid.png"


# --- 3. Flexible Layouts ---
echo "Generating: 3. Flexible Layouts"
eink-template-gen multi --rows 2 --columns 2 --type dotgrid --device manta --output-dir "$OUTPUT_DIR" --filename "layout_multi_uniform.png"
eink-template-gen multi --rows 3 --columns 1 --type lined --orientation vertical --device manta --output-dir "$OUTPUT_DIR" --filename "layout_multi_vertical.png"
eink-template-gen multi --rows 2 --columns 2 --cell_types lined,grid,dotgrid,manuscript --device manta --output-dir "$OUTPUT_DIR" --filename "layout_multi_mixed.png"

# Note: This command assumes 'cornell_layout.json' exists in the current directory.
if [ -f "cornell_layout.json" ]; then
    eink-template-gen layout --file cornell_layout.json --output-dir "$OUTPUT_DIR" --filename "layout_json_cornell.png"
else
    echo "Skipping JSON layout (cornell_layout.json not found)"
fi


# --- 4. Customization Features ---
echo "Generating: 4. Customization Features"
eink-template-gen lined --spacing 7mm --header-sep wavy --footer-sep double --device manta --output-dir "$OUTPUT_DIR" --filename "custom_separators.png"


# --- 5. Decorative Title Pages ---
echo "Generating: 5. Decorative Title Pages"
eink-template-gen title --type truchet --truchet-variant classic --device manta --output-dir "$OUTPUT_DIR" --filename "title_truchet_classic.png"
eink-template-gen title --type truchet --truchet-variant mixed --truchet-fill-grey 12 --device manta --output-dir "$OUTPUT_DIR" --filename "title_truchet_filled.png"
eink-template-gen title --type diagonal_truchet --device manta --output-dir "$OUTPUT_DIR" --filename "title_diagonal_truchet.png"
eink-template-gen title --type hexagonal_truchet --device manta --output-dir "$OUTPUT_DIR" --filename "title_hexagonal_truchet.png"
eink-template-gen title --type ten_print --device manta --output-dir "$OUTPUT_DIR" --filename "title_ten_print.png"
eink-template-gen title --type contour_lines --noise-style turbulent --device manta --output-dir "$OUTPUT_DIR" --filename "title_contour_lines.png"
eink-template-gen title --type noise_field --device manta --output-dir "$OUTPUT_DIR" --filename "title_noise_field.png"
eink-template-gen title --type hilbert_curve --device manta --output-dir "$OUTPUT_DIR" --filename "title_lsystem_hilbert.png"
eink-template-gen title --type koch_snowflake --device manta --output-dir "$OUTPUT_DIR" --filename "title_lsystem_koch.png"
eink-template-gen title --type plant_fractal --device manta --output-dir "$OUTPUT_DIR" --filename "title_lsystem_plant.png"
eink-template-gen title --type koch_snowflake --lsystem-iterations 5 --decorative-border ornate --title-text "Fractals" --device manta --output-dir "$OUTPUT_DIR" --filename "title_with_frame.png"


echo "=== Generation Complete ==="
echo "All images saved to $OUTPUT_DIR and $BEFORE_DIR"
