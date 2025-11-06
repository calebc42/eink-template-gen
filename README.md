
# Table of Contents

1.  [About](#orgc6243ee)
2.  [Why This Tool?](#orgeda4cdd)
3.  [What this tool is NOT](#orgf2ba7c1)
4.  [Features](#org70cf0ad)
5.  [Installation](#org8544504)
    1.  [Development Version](#org7af9cde)
6.  [Full Documentation](#org7d50f0b)
7.  [Supported Devices](#org4fb1b4c)
8.  [Configuration](#org657c333)
9.  [Usage Examples](#org4422797)
    1.  [Basic Templates](#orga689170)
10. [Output](#org44399c6)
11. [Contributing](#org704ebfb)
12. [License](#org2de9852)
13. [Credits](#org274ed63)


<a id="orgc6243ee"></a>

# About

A device-agnostic command-line tool for generating mathematically balanced, pixel-perfect page templates for e-ink devices. Developed with the Supernote Manta, this tool supports millimeter or pixel specifications for human-readable, technically-precise, or true-scale template configurations.


<a id="orgeda4cdd"></a>

# Why This Tool?

This tool was born from the frustration of online generators that fail to handle "half-lines" or pixel alignment, resulting in uneven, blurry, or aliased lines on high-DPI e-ink screens. This generator calculates exact pixel-perfect margins and spacing based on your device's specific resolution and DPI, ensuring every line is crisp and uniform.

:SUMMARY: Click to see Visual Comparison: The "Why"

**Problem: Blurry Lines (Fractional Pixels)**
The image on the left (`--no-auto-adjust`) shows blurry, anti-aliased lines. The image on the right (default) shows the pixel-perfect, crisp lines this tool creates.

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
<td class="org-left"><img src="src/assets/screenshots/before/manta/true-scale/before_pixel_perfect.png" alt="before_pixel_perfect.png" /></td>
<td class="org-left"><img src="src/assets/screenshots/manta/after_pixel_perfect.png" alt="after_pixel_perfect.png" /></td>
</tr>
</tbody>
</table>

**Problem: Grid Misalignment**
The image on the left (default) shows a grid being awkwardly cut off. The image on the right (`--force-major-alignment`) shows the margins being automatically adjusted to end perfectly on a major grid line.

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
<td class="org-left"><img src="src/assets/screenshots/before/manta/problem_before_grid_alignment.png" alt="problem_before_grid_alignment.png" /></td>
<td class="org-left"><img src="src/assets/screenshots/manta/problem_after_grid_alignment.png" alt="problem_after_grid_alignment.png" /></td>
</tr>
</tbody>
</table>

:END:


<a id="orgf2ba7c1"></a>

# What this tool is NOT

-   Calendar/Schedule Generator
-   Task/To Do list Generator
-   Color e-ink Template Generator (yet)
-   Real-Time GUI Editor
-   Monetized or Paywalled Tool


<a id="org70cf0ad"></a>

# Features

-   **Pixel-Perfect Alignment:** Automatically adjusts margins and spacing to eliminate blurry lines and aliasing artifacts.
-   **Multiple Template Types:** Generate lined, dotgrid, grid, manuscript, french ruled, music staff, isometric, hexgrid, and hybrid pages.
-   **Flexible Layouts:** Create single pages, uniform N x M grids, mixed-type grids, and complex, ratio-based layouts using JSON.
-   **Decorative Title Pages:** Generate artistic cover pages using Truchet tiles, L-System fractals, noise fields, and more.
-   **Powerful Customization:** Add major/minor lines, decorative separators, line numbers, and axis labels.
-   **Flexible Spacing:** Define layouts using millimeters (default), exact pixels, or by fitting an exact line count.


<a id="org8544504"></a>

# Installation

    pip install eink-template-gen


<a id="org7af9cde"></a>

## Development Version

If you want the latest unreleased features or want to contribute to development, you can install the package directly from this repository.

Clone the repository:

    git clone [https://github.com/calebc42/eink-template-gen.git](https://github.com/calebc42/eink-template-gen.git)
    cd eink-template-gen

Create and activate a virtual environment:

    # On macOS/Linux
    python3 -m venv .venv
    source .venv/bin/activate
    
    # On Windows
    python -m venv .venv
    .\.venv\Scripts\activate

Install in editable mode: This links the command eink-template-gen to your local source code, so any changes you make are immediately reflected.

    pip install -e .


<a id="org7d50f0b"></a>

# Full Documentation

For detailed guides, feature deep-dives, and advanced examples, please see the `docs/` directory:

-   **Features**
    -   [Template Types](docs/features/template-types.md)
    -   [Flexible Layouts](docs/features/layouts.md)
    -   [Decorative Title Pages](docs/features/title-pages.md)
-   **Guides**
    -   [Customization Options (Separators, Labels, etc.)](docs/guides/customization.md)
    -   [Spacing Modes (mm, px, line count)](docs/guides/spacing-modes.md)
-   **Examples**
    -   [Advanced Usage Examples](docs/advanced-examples.md)
-   **Reference**
    -   [Command Reference (All Flags)](docs/reference/command-reference.md)
    -   [Technical Details (Algorithm, Palette)](docs/reference/technical-details.md)


<a id="org4fb1b4c"></a>

# Supported Devices

Built-in device profiles:

-   Supernote Manta (10.7", 1920x2560, 300 DPI)
-   Supernote A5 X (10.3", 1404x1872, 226 DPI)
-   Supernote A6 X (7.8", 1404x1872, 300 DPI)
-   Supernote Nomad (7.8", 1404x1872, 300 DPI)


<a id="org657c333"></a>

# Configuration

Set a default device to avoid specifying `--device` every time:

    eink-template-gen util set-default-device manta
    eink-template-gen util set-default-margin 10

Configuration is stored locally in `config.json`.


<a id="org4422797"></a>

# Usage Examples


<a id="orga689170"></a>

## Basic Templates

    # Simple lined paper
    eink-template-gen lined --spacing 7mm
    
    # Dot grid with major crosshairs
    eink-template-gen dotgrid --spacing 5mm --major_every 5
    
    # Graph paper with axis labels
    eink-template-gen grid --spacing 5mm --major_every 5 --axis-labels
    
    # Manuscript paper for handwriting practice
    eink-template-gen manuscript --spacing 8mm

For more complex examples, including `multi`, `layout`, and `title` commands, see the [Advanced Usage Examples](docs/advanced-examples.md) documentation.


<a id="org44399c6"></a>

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


<a id="org704ebfb"></a>

# Contributing

Contributions are welcome! This project uses:

-   Cairo for high-quality 2D graphics rendering
-   Python 3.8+
-   Pure Python implementation (no external dependencies for noise/fractals)


<a id="org2de9852"></a>

# License

This project is licensed under the **GNU General Public License v3.0**. See the `LICENSE` file for details.


<a id="org274ed63"></a>

# Credits

Developed for the Supernote community with love for pixel-perfect templates.

