
# Table of Contents

1.  [About](#org7298b01)
2.  [Why This Tool?](#orgcfe5b81)
3.  [What this tool is NOT](#orgcda8fdc)
4.  [Features](#orgdabc90f)
    1.  [Pixel-Perfect Alignment](#orge7a2f16)
    2.  [Template Types](#org38b6c47)
    3.  [Flexible Layouts](#org4606b13)
        1.  [Single Page Templates](#org87f6111)
        2.  [Uniform Multi-Cell Grids](#org30f6eb1)
        3.  [Mixed Multi-Type Grids](#orgc1210b6)
        4.  [JSON Layout Engine](#orgfe9ab78)
    4.  [Decorative Title Pages](#orga9f0496)
        1.  [Title Text & Framing](#org59794e3)
        2.  [Title Positioning](#org910609b)
5.  [Customization Options](#orgcb5b9b2)
    1.  [Major/Minor Lines](#org7d3f22e)
    2.  [Custom Separators](#org04773e4)
    3.  [Margin Labels](#org7bedd04)
6.  [Spacing Modes](#orgf21e2b2)
    1.  [Millimeter Mode (Default)](#org86fa987)
    2.  [Pixel Mode](#org4a40690)
    3.  [Line Count Mode](#orgf99ca66)
7.  [Installation](#org01e7dd3)
8.  [Supported Devices](#org6e34d90)
9.  [Configuration](#orgcc5cd6b)
10. [Usage Examples](#orgfd53644)
    1.  [Basic Templates](#org395b85c)
    2.  [Advanced Layouts](#orga5ca6d0)
    3.  [Title Pages](#org642120a)
    4.  [Utility Commands](#orgef6260c)
11. [Output](#org42fc764)
12. [Technical Details](#orgdf1f62f)
    1.  [Pixel-Perfect Algorithm](#org3a8ba9a)
    2.  [E-ink Greyscale Palette](#org837a16b)
13. [Command Reference](#org8fbaa12)
    1.  [Global Options](#org8a42ae4)
    2.  [Commands](#org67016c3)
14. [Contributing](#org2e75524)
15. [License](#org229c976)
16. [Credits](#org700c5f6)



<a id="org7298b01"></a>

# About

A device-agnostic command-line tool for generating mathematically balanced, pixel-perfect page templates for e-ink devices. Developed with the Supernote Manta, this tool supports millimeter or pixel specifications for human-readable, technically-precise, or true-scale template configurations.


<a id="orgcfe5b81"></a>

# Why This Tool?

This tool was born from the frustration of online generators that fail to handle "half-lines" or pixel alignment, resulting in uneven, blurry, or aliased lines on high-DPI e-ink screens. This generator calculates exact pixel-perfect margins and spacing based on your device's specific resolution and DPI, ensuring every line is crisp and uniform.

<div class="DETAILS" id="org964501a">
<div class="SUMMARY" id="orgc2e4d62">
<p>
Click to see Visual Comparison: The "Why"
</p>

</div>

<p>
<b><b>Problem: Blurry Lines (Fractional Pixels)</b></b>
The image on the left (<code>--no-auto-adjust</code>) shows blurry, anti-aliased lines. The image on the right (default) shows the pixel-perfect, crisp lines this tool creates.
</p>

<table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">


<colgroup>
<col  class="org-left" />

<col  class="org-left" />
</colgroup>
<thead>
<tr>
<th scope="col" class="org-left">"Before" (Blurry)</th>
<th scope="col" class="org-left">"After" (Pixel-Perfect)</th>
</tr>
</thead>
<tbody>
<tr>
<td class="org-left"><img src="src/assets/screenshots/before/problem_before_blurry_lines.png" alt="problem_before_blurry_lines.png" /></td>
<td class="org-left"><img src="src/assets/screenshots/problem_after_pixel_perfect_lined.png" alt="problem_after_pixel_perfect_lined.png" /></td>
</tr>
</tbody>
</table>

<p>
<b><b>Problem: Grid Misalignment</b></b>
The image on the left (default) shows a grid being awkwardly cut off. The image on the right (<code>--force-major-alignment</code>) shows the margins being automatically adjusted to end perfectly on a major grid line.
</p>

<table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">


<colgroup>
<col  class="org-left" />

<col  class="org-left" />
</colgroup>
<thead>
<tr>
<th scope="col" class="org-left">"Before" (Misaligned)</th>
<th scope="col" class="org-left">"After" (Force-Aligned)</th>
</tr>
</thead>
<tbody>
<tr>
<td class="org-left"><img src="src/assets/screenshots/before/problem_before_grid_alignment.png" alt="problem_before_grid_alignment.png" /></td>
<td class="org-left"><img src="src/assets/screenshots/problem_after_grid_alignment.png" alt="problem_after_grid_alignment.png" /></td>
</tr>
</tbody>
</table>

</div>


<a id="orgcda8fdc"></a>

# What this tool is NOT

-   Calendar/Schedule Generator
-   Task/To Do list Generator
-   Color e-ink Template Generator (yet)
-   Real-Time GUI Editor
-   Monetized or Paywalled Tool


<a id="orgdabc90f"></a>

# Features


<a id="orge7a2f16"></a>

## Pixel-Perfect Alignment

-   Automatically adjusts margins and spacing to ensure precise sub-pixel placement
-   Eliminates blurry lines and aliasing artifacts
-   Handles fractional pixel calculations with configurable rounding strategies
-   Optional `--lines` mode to fit an exact number of lines with automatic spacing calculation


<a id="org38b6c47"></a>

## Template Types

Generate a wide variety of template patterns:

-   `lined` - Horizontal ruled lines with optional line numbering
-   `dotgrid` - Dot grid with optional major crosshairs
-   `grid` - Full graph paper with major/minor lines and crosshairs
-   `manuscript` - 4-line handwriting guides (baseline, midline, ascender, descender)
-   `french_ruled` - Seyès ruling with vertical guides
-   `music_staff` - 5-line musical notation staves
-   `isometric` - 60° triangular isometric grid
-   `hexgrid` - Flat-top hexagonal grid
-   `hybrid_lined_dotgrid` - Split layout with lined on one side, dotgrid on the other

<div class="DETAILS" id="org7725dcc">
<div class="SUMMARY" id="orgc684029">
<p>
Click to see Screenshot Gallery: Template Types
</p>

</div>

<table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">


<colgroup>
<col  class="org-left" />

<col  class="org-left" />

<col  class="org-left" />
</colgroup>
<thead>
<tr>
<th scope="col" class="org-left">Lined (w/ Numbers)</th>
<th scope="col" class="org-left">Dotgrid (w/ Crosshairs)</th>
<th scope="col" class="org-left">Grid (w/ Axis Labels)</th>
</tr>
</thead>
<tbody>
<tr>
<td class="org-left"><img src="src/assets/screenshots/gallery_lined_with_numbers.png" alt="gallery_lined_with_numbers.png" /></td>
<td class="org-left"><img src="src/assets/screenshots/gallery_dotgrid_with_crosshairs.png" alt="gallery_dotgrid_with_crosshairs.png" /></td>
<td class="org-left"><img src="src/assets/screenshots/gallery_grid_with_axis_labels.png" alt="gallery_grid_with_axis_labels.png" /></td>
</tr>

<tr>
<td class="org-left"><b>Manuscript</b></td>
<td class="org-left"><b>French Ruled</b></td>
<td class="org-left"><b>Music Staff</b></td>
</tr>

<tr>
<td class="org-left"><img src="src/assets/screenshots/gallery_manuscript.png" alt="gallery_manuscript.png" /></td>
<td class="org-left"><img src="src/assets/screenshots/gallery_french_ruled.png" alt="gallery_french_ruled.png" /></td>
<td class="org-left"><img src="src/assets/screenshots/gallery_music_staff.png" alt="gallery_music_staff.png" /></td>
</tr>

<tr>
<td class="org-left"><b>Isometric</b></td>
<td class="org-left"><b>Hex Grid</b></td>
<td class="org-left"><b>Hybrid</b></td>
</tr>

<tr>
<td class="org-left"><img src="src/assets/screenshots/gallery_isometric.png" alt="gallery_isometric.png" /></td>
<td class="org-left"><img src="src/assets/screenshots/gallery_hexgrid.png" alt="gallery_hexgrid.png" /></td>
<td class="org-left"><img src="src/assets/screenshots/gallery_hybrid.png" alt="gallery_hybrid.png" /></td>
</tr>
</tbody>
</table>

</div>


<a id="org4606b13"></a>

## Flexible Layouts


<a id="org87f6111"></a>

### Single Page Templates

    eink-template-gen lined --spacing 7mm --margin 10
    eink-template-gen grid --spacing 5mm --major_every 5 --axis-labels


<a id="org30f6eb1"></a>

### Uniform Multi-Cell Grids

Create N × M grids where all cells use the same template:

    # 2x2 grid of dotgrid
    eink-template-gen multi --rows 2 --columns 2 --type dotgrid --spacing 5mm
    # 2 stacked (vertical) sections of lined paper
    eink-template-gen multi --rows 2 --columns 1 --type lined --spacing 7mm --orientation vertical

The `multi` command also supports an `--orientation` flag (`horizontal` or `vertical`) which determines the layout flow.


<a id="orgc1210b6"></a>

### Mixed Multi-Type Grids

Create N × M grids where each cell can be a different template type:

    eink-template-gen multi --rows 2 --columns 2 \
      --cell_types lined,grid,dotgrid,manuscript --spacing 6mm


<a id="orgfe9ab78"></a>

### JSON Layout Engine

Design complex, ratio-based layouts (like Cornell notes) using JSON:

    eink-template-gen layout --file cornell_layout.json

Example JSON structure for Cornell Notes with a Title:

    {
      "device": "manta",
      "master_spacing_mm": 7,
      "margin_mm": 12,
      "header_separator": {
        "style": "wavy",
        "amplitude": 10.0,
        "wavelength": 100.0
      },
      "page_layout": [
        {
          "name": "Cue Column",
          "region_rect": [0, 0.1, 0.3, 0.75],
          "template": "dotgrid",
          "spacing_mm": 5,
          "kwargs": {"dot_size_px": 1}
        },
        {
          "name": "Notes Section",
          "region_rect": [0.3, 0.1, 0.7, 0.75],
          "template": "lined",
          "kwargs": {"line_width_px": 0.75}
        },
        {
          "name": "Summary Section",
          "region_rect": [0, 0.85, 1.0, 0.15],
          "template": "grid",
          "kwargs": {"line_width_px": 0.5}
        }
      ],
      "title_element": {
        "text": "Lecture Notes",
        "region_rect": [0, 0, 1.0, 0.1],
        "font_size": 32,
        "font_weight": "bold",
        "v_align": "center",
        "show_frame": false
      }
    }

**Note: When using JSON, separators can be defined as simple strings (e.g., "bold") or as objects with specific parameters to customize their appearance.**

<div class="DETAILS" id="org07e63ee">
<div class="SUMMARY" id="org6a7c9f2">
<p>
Click to see Screenshot Gallery: Flexible Layouts
</p>

</div>

<table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">


<colgroup>
<col  class="org-left" />

<col  class="org-left" />

<col  class="org-left" />

<col  class="org-left" />
</colgroup>
<thead>
<tr>
<th scope="col" class="org-left">Uniform 2x2 Grid</th>
<th scope="col" class="org-left">Vertical Stacked</th>
<th scope="col" class="org-left">Mixed-Type Grid</th>
<th scope="col" class="org-left">JSON (Cornell)</th>
</tr>
</thead>
<tbody>
<tr>
<td class="org-left"><img src="src/assets/screenshots/layout_multi_uniform.png" alt="layout_multi_uniform.png" /></td>
<td class="org-left"><img src="src/assets/screenshots/layout_multi_vertical.png" alt="layout_multi_vertical.png" /></td>
<td class="org-left"><img src="src/assets/screenshots/layout_multi_mixed.png" alt="layout_multi_mixed.png" /></td>
<td class="org-left"><img src="src/assets/screenshots/layout_json_cornell.png" alt="layout_json_cornell.png" /></td>
</tr>
</tbody>
</table>

</div>


<a id="orga9f0496"></a>

## Decorative Title Pages

Generate artistic cover pages with multiple pattern types:

-   `truchet` - Classic Truchet tiles with variants (classic, cross, triangle, wave, mixed)
-   `diagonal_truchet` - Diagonal split tiles
-   `hexagonal_truchet` - Truchet patterns on hexagonal grid
-   `ten_print` - Random diagonal maze pattern
-   L-System Fractals:
    -   `hilbert_curve` - Space-filling Hilbert curve
    -   `dragon_curve` - Classic dragon fractal
    -   `koch_snowflake` - 6-fold symmetric snowflake
    -   `sierpinski_triangle` - Recursive triangle pattern
    -   `plant_fractal` - Organic branching pattern
    -   `gosper_curve` - Hexagonal space-filling curve
    -   `levy_c_curve` - Elegant symmetric fractal
-   `contour_lines` - Topographic-style contour maps using Perlin-like noise
-   `noise_field` - Greyscale texture patterns

All title pages support:

-   Optional decorative borders (simple, double, ornate, geometric)
-   Custom title text with configurable frames
-   Reproducible patterns via seed values

<div class="DETAILS" id="org6ec891c">
<div class="SUMMARY" id="orgf776945">
<p>
Click to see Screenshot Gallery: Title Pages
</p>

</div>

<table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">


<colgroup>
<col  class="org-left" />

<col  class="org-left" />

<col  class="org-left" />
</colgroup>
<thead>
<tr>
<th scope="col" class="org-left">Truchet (Filled)</th>
<th scope="col" class="org-left">Diagonal Truchet</th>
<th scope="col" class="org-left">Hexagonal Truchet</th>
</tr>
</thead>
<tbody>
<tr>
<td class="org-left"><img src="src/assets/screenshots/title_truchet_filled.png" alt="title_truchet_filled.png" /></td>
<td class="org-left"><img src="src/assets/screenshots/title_diagonal_truchet.png" alt="title_diagonal_truchet.png" /></td>
<td class="org-left"><img src="src/assets/screenshots/title_hexagonal_truchet.png" alt="title_hexagonal_truchet.png" /></td>
</tr>

<tr>
<td class="org-left"><b>10 Print</b></td>
<td class="org-left"><b>Koch Snowflake</b></td>
<td class="org-left"><b>Plant Fractal</b></td>
</tr>

<tr>
<td class="org-left"><img src="src/assets/screenshots/title_ten_print.png" alt="title_ten_print.png" /></td>
<td class="org-left"><img src="src/assets/screenshots/title_lsystem_koch.png" alt="title_lsystem_koch.png" /></td>
<td class="org-left"><img src="src/assets/screenshots/title_lsystem_plant.png" alt="title_lsystem_plant.png" /></td>
</tr>

<tr>
<td class="org-left"><b>Contour Lines</b></td>
<td class="org-left"><b>Noise Field</b></td>
<td class="org-left"><b>Title w/ Frame</b></td>
</tr>

<tr>
<td class="org-left"><img src="srcA/assets/screenshots/title_contour_lines.png" alt="title_contour_lines.png" /></td>
<td class="org-left"><img src="src/assets/screenshots/title_noise_field.png" alt="title_noise_field.png" /></td>
<td class="org-left"><img src="src/assets/screenshots/title_with_frame.png" alt="title_with_frame.png" /></td>
</tr>
</tbody>
</table>

</div>


<a id="org59794e3"></a>

### Title Text & Framing

All title pages support a powerful set of arguments for adding and styling a title block:

-   ****`--title-text "My Notes"`**:** The text to display.
-   ****`--title-frame-shape rounded-rectangle`**:** Shape of the frame (rectangle, ellipse, etc.).
-   ****`--title-border-style dashed`**:** Border style (solid, dashed, dotted, double, ornate).
-   ****`--title-font-size 32`**:** Font size in points.
-   ****`--title-font-family Sans`**:** Font family (Serif, Sans, Monospace).
-   ****`--title-fill-grey 15`**:** Frame fill color (0-15, 15=white).
-   ****`--title-no-frame`**:** Disables the frame entirely.


<a id="org910609b"></a>

### Title Positioning

By default, the title is placed in the top-third of the page. You can override this:

-   ****`--title-v-align center`**:** Vertical alignment (top, center, bottom).
-   ****`--title-y-center 1000`**:** Set an exact vertical position in pixels.
-   ****`--title-h-align left`**:** Horizontal alignment (left, center, right).
-   ****`--title-x-center 500`**:** Set an exact horizontal position in pixels.


<a id="orgcb5b9b2"></a>

# Customization Options


<a id="org7d3f22e"></a>

## Major/Minor Lines

-   Major Lines: Every Nth line can be thicker (e.g., `--major_every 5`)
-   Crosshairs: Automatic crosshair markers at major intersections
-   Force Alignment: `--force-major-alignment` adjusts margins to ensure grids end on major lines


<a id="org04773e4"></a>

## Custom Separators

Add decorative header/footer separators:

    eink-template-gen lined --spacing 7mm \
      --header-sep wavy --footer-sep double

Available styles: bold, double, wavy, dashed, thick<sub>thin</sub>, zig-zag, scalloped, castellated, dotted, dash-dot, barber-stripe, stitch

<div class="DETAILS" id="org728f907">
<div class="SUMMARY" id="orgd1e8e39">
<p>
Click to see Screenshot: Custom Separators
</p>

</div>

<p>
Example of 'wavy' and 'double' separators.
<img src="src/assets/screenshots/custom_separators.png" alt="custom_separators.png" />
</p>

</div>


<a id="org7bedd04"></a>

## Margin Labels

-   Line Numbers: `--line-numbers` with configurable side, interval, and styling
-   Cell Labels: `--cell-labels` for grid cells (A, B, C&#x2026; / 1, 2, 3&#x2026;)
-   Axis Labels: `--axis-labels` for plot-style numbering (0, 5, 10&#x2026;)

**Note: For the `grid` command, you may use either `--cell-labels` or `--axis-labels`, but not both at the same time.**

    # Lined paper with line numbers
    eink-template-gen lined --spacing 7mm --line-numbers \
      --line-numbers-interval 5 --line-numbers-side left
    
    # Grid with A, B, C... / 1, 2, 3... labels
    eink-template-gen grid --spacing 5mm --cell-labels
    
    # Grid with axis labels
    eink-template-gen grid --spacing 5mm --major_every 5 --axis-labels \
      --axis-labels-interval 5 --axis-labels-origin bottomLeft


<a id="orgf21e2b2"></a>

# Spacing Modes


<a id="org86fa987"></a>

## Millimeter Mode (Default)

Human-readable spacing with automatic pixel-perfect adjustment:

    eink-template-gen lined --spacing 6mm
    # Note: Adjusted spacing from 6mm to 6.011mm (71px) for pixel-perfect alignment

Disable auto-adjustment for true-scale (may cause slight blur):

    eink-template-gen lined --spacing 6mm --no-auto-adjust


<a id="org4a40690"></a>

## Pixel Mode

Exact pixel control:

    eink-template-gen lined --spacing 71px


<a id="orgf99ca66"></a>

## Line Count Mode

Fit an exact number of lines by automatically calculating spacing:

    # Fit exactly 40 lines with default 0mm margins
    eink-template-gen lined --lines 40
    # Fit exactly 40 lines with 10mm margins
    eink-template-gen lined --lines 40 --margin 10
    # Grid with specific dimensions
    eink-template-gen grid --lines 40x30 --margin 10

Use `--enforce-exact-spacing` to allow fractional pixel spacing (may cause
slight blur but ensures exact fit).


<a id="org01e7dd3"></a>

# Installation

    pip install eink-template-gen


<a id="org6e34d90"></a>

# Supported Devices

Built-in device profiles:

-   Supernote Manta (10.7", 1920×2560, 300 DPI)
-   Supernote A5 X (10.3", 1404×1872, 226 DPI)
-   Supernote A6 X (7.8", 1404×1872, 300 DPI)
-   Supernote Nomad (7.8", 1404×1872, 300 DPI)


<a id="orgcc5cd6b"></a>

# Configuration

Set a default device to avoid specifying `--device` every time:

    eink-template-gen util set-default-device manta
    eink-template-gen util set-default-margin 10

Configuration is stored locally in `config.json`.


<a id="orgfd53644"></a>

# Usage Examples


<a id="org395b85c"></a>

## Basic Templates

    # Simple lined paper
    eink-template-gen lined --spacing 7mm
    # Dot grid with major crosshairs
    eink-template-gen dotgrid --spacing 5mm --major_every 5
    # Graph paper with axis labels
    eink-template-gen grid --spacing 5mm --major_every 5 --axis-labels
    # Manuscript paper for handwriting practice
    eink-template-gen manuscript --spacing 8mm


<a id="orga5ca6d0"></a>

## Advanced Layouts

    # 2×2 grid of different templates
    eink-template-gen multi --rows 2 --columns 2 \
      --cell_types lined,grid,dotgrid,manuscript --spacing 6mm
    
    # Cornell notes from JSON
    eink-template-gen layout --file cornell_layout.json
    
    # Split page: lined + dotgrid
    eink-template-gen hybrid_lined_dotgrid --spacing 6mm --split-ratio 0.6
    
    # Advanced multi: 2x1 grid of lined paper with line numbers
    eink-template-gen multi --rows 2 --columns 1 --type lined \
      --spacing 7mm --line-numbers --line-numbers-interval 1


<a id="org642120a"></a>

## Title Pages

    # Truchet pattern with a *filled* background and custom title
    eink-template-gen title --type truchet --spacing 10mm \
      --truchet-fill-grey 12 --truchet-variant mixed \
      --title-text "Lab Notebook" --title-font-size 40
    
    # L-System fractal with 5 iterations and a decorative border
    eink-template-gen title --type koch_snowflake --spacing 1mm \
      --lsystem-iterations 5 --decorative-border ornate \
      --title-text "Fractals"
    
    # Organic contour map using turbulent noise and a custom seed
    eink-template-gen title --type contour_lines --noise-style turbulent \
      --noise-scale 0.02 --octaves 6 --noise-seed 1234 \
      --title-text "Field Notes" --title-y-center 1800


<a id="orgef6260c"></a>

## Utility Commands

    # List available devices
    eink-template-gen util list-devices
    # List all template types
    eink-template-gen util list-templates
    # Analyze spacing for a device
    eink-template-gen util info 6mm --device a5x
    # Set defaults
    eink-template-gen util set-default-device manta
    eink-template-gen util set-default-margin 10


<a id="org42fc764"></a>

# Output

Templates are saved to `out/<device_id>/` by default:

    out/
    ├── manta/
    │   ├── lined_7mm_0_5px.png
    │   ├── grid_5mm_0_5px_h-wavy.png
    │   └── title_truchet_10mm_seed42.png
    └── a5x/
        └── lined_6mm_71px.png

Use `--output-dir` and `--filename` to customize output location.


<a id="orgdf1f62f"></a>

# Technical Details


<a id="org3a8ba9a"></a>

## Pixel-Perfect Algorithm

-   Calculate ideal spacing in pixels from mm input
-   Round to nearest integer pixel value
-   Calculate actual mm value of rounded pixels
-   Adjust top/bottom (and left/right for grids) margins to center content
-   Ensure no partial lines/dots at boundaries


<a id="org837a16b"></a>

## E-ink Greyscale Palette

The tool uses the native 16-level greyscale palette (0-15) used by Supernote devices:

-   0 = #000000 (black)
-   8 = #808080 (medium grey)
-   15 = #ffffff (white)

All greyscale values are automatically snapped to the nearest palette level for optimal e-ink rendering.


<a id="org8fbaa12"></a>

# Command Reference


<a id="org8a42ae4"></a>

## Global Options

-   `--device DEVICE` - Target device (overrides default)
-   `--spacing SPACING` - Line/dot spacing (e.g., 6mm, 71px, or 6)
-   `--no-auto-adjust` - Disable automatic spacing adjustment
-   `--margin MM` - Page margin in mm (overrides device default)
-   `--lines SPEC` - Fit exact number of lines (e.g., 40 or 40x30)
-   `--output-dir DIR` - Output directory (default: out)
-   `--filename NAME` - Custom filename


<a id="org67016c3"></a>

## Commands

-   `lined` - Generate lined template
-   `dotgrid` - Generate dot grid template
-   `grid` - Generate graph paper grid
-   `manuscript` - Generate manuscript template
-   `french_ruled` - Generate Seyès ruling
-   `music_staff` - Generate music staff
-   `isometric` - Generate isometric grid
-   `hexgrid` - Generate hexagonal grid
-   `hybrid_lined_dotgrid` - Generate hybrid template
-   `multi` - Generate multi-cell grid
-   `layout` - Generate from JSON layout
-   `title` - Generate decorative title page
-   `util` - Utility commands (list-devices, set-default-device, etc.)

For detailed options for each command, run:

    eink-template-gen <command> --help


<a id="org2e75524"></a>

# Contributing

Contributions are welcome! This project uses:

-   Cairo for high-quality 2D graphics rendering
-   Python 3.8+
-   Pure Python implementation (no external dependencies for noise/fractals)


<a id="org229c976"></a>

# License

This project is licensed under the *GNU General Public License v3.0*. See the `LICENSE` file for details.


<a id="org700c5f6"></a>

# Credits

Developed for the Supernote community with love for pixel-perfect templates.

