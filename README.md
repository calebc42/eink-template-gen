
# Table of Contents

1.  [Table of Contents](#org88a00db)
2.  [Badges](#orgbbe7e4a)
3.  [About](#orgc0cd1a8)
4.  [Why This Tool?](#org69c405e)
5.  [What this tool is NOT](#org7fc3e75)
6.  [Features](#org2b5b705)
7.  [Installation](#org597bf4d)
8.  [Quick Start (Wizard)](#org147e5c4)
9.  [Full Documentation](#org27a38ee)
10. [Supported Devices](#org3c734ed)
11. [Configuration](#org217ca64)
12. [Usage Examples](#org539e9c8)
    1.  [Basic Templates](#org1db95cb)
13. [Output](#org9f78a14)
14. [AI-Assisted Development (ai-wizard-prompt.org)](#org49c4688)
15. [Contributing](#org6f3df60)
    1.  [Development Setup](#org26a70a4)
16. [License](#orge183f49)
17. [Credits](#org4a90d11)


<a id="org88a00db"></a>

# Table of Contents


<a id="orgbbe7e4a"></a>

# Badges

![Python CI](https://github.com/calebc42/eink-template-gen/actions/workflows/ci.yml/badge.svg)
![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-GPLv3-green)


<a id="orgc0cd1a8"></a>

# About

A device-agnostic command-line tool for generating mathematically balanced, pixel-perfect page templates for e-ink devices. Developed with the Supernote Manta, this tool supports millimeter or pixel specifications for human-readable, technically-precise, or true-scale template configurations.


<a id="org69c405e"></a>

# Why This Tool?

This tool was born from the frustration of online generators that fail to handle "half-lines" or pixel alignment, resulting in uneven, blurry, or aliased lines on high-DPI e-ink screens. This generator calculates exact pixel-perfect margins and spacing based on your device's specific resolution and DPI, ensuring every line is crisp and uniform.

**Problem: Blurry Lines (Fractional Pixels)**
"The image on the left (using `--true-scale`) shows blurry, aliased lines caused by fractional pixels. The image on the right (default) shows the tool's pixel-perfect rounding, which ensures every line is crisp."

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

**Problem: Toolbar/Overlay**
The image on the left (built-in template) shows the file name and page count overlays displaying over the template. The image on the right shows the lines being automatically adjusted to render within the margins.

<table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">


<colgroup>
<col  class="org-left" />

<col  class="org-left" />
</colgroup>
<thead>
<tr>
<th scope="col" class="org-left">"Before" (OEM Template)</th>
<th scope="col" class="org-left">"After" (Pixel-Perfect)</th>
</tr>
</thead>
<tbody>
<tr>
<td class="org-left"><img src="src/assets/screenshots/before/manta/built-in_9mm.png" alt="built-in_9mm.png" /></td>
<td class="org-left"><img src="src/assets/screenshots/manta/pixel_perfect_9mm.png" alt="pixel_perfect_9mm.png" /></td>
</tr>
</tbody>
</table>

**Problem: Half-Spaced Lines and Cells**
The image on the left (using `--enforce-margins`) shows lines and cells being cut off abruptly at the exact margin. The image on the right (default) shows the tool's smart grid-centering, which automatically pads the margins to prevent 'half-cells' and create a cleaner, more balanced page.

<table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">


<colgroup>
<col  class="org-left" />

<col  class="org-left" />
</colgroup>
<thead>
<tr>
<th scope="col" class="org-left">"Before" (cut-off cells)</th>
<th scope="col" class="org-left">"After" (Pixel-Perfect)</th>
</tr>
</thead>
<tbody>
<tr>
<td class="org-left"><img src="src/assets/screenshots/before/manta/before_half_cells.png" alt="before_half_cells.png" /></td>
<td class="org-left"><img src="src/assets/screenshots/manta/after_adjusted_margins.png" alt="after_adjusted_margins.png" /></td>
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


<a id="org7fc3e75"></a>

# What this tool is NOT

-   Calendar/Schedule Generator
-   Task/To Do list Generator
-   Color e-ink Template Generator (yet)
-   Real-Time GUI Editor
-   Monetized or Paywalled Tool


<a id="org2b5b705"></a>

# Features

-   **Interactive Wizard:** A guided, step-by-step terminal wizard to create complex templates without needing to memorize flags. Just run `eink-template-gen --wizard`.
-   **Pixel-Perfect Alignment:** Automatically adjusts margins and spacing to eliminate blurry lines and aliasing artifacts.
-   **Multiple Template Types:** Generate lined, dotgrid, grid, manuscript, french ruled, music staff, isometric, hexgrid, and hybrid pages.
-   **Flexible Layouts:** Create single pages, uniform N x M grids, mixed-type grids, and complex, ratio-based layouts using JSON.
-   **Decorative Title Pages:** Generate artistic cover pages using Truchet tiles, L-System fractals, noise fields, and more.
-   **Powerful Customization:** Add major/minor lines, decorative separators, line numbers, and axis labels.
-   **Flexible Spacing:** Define layouts using millimeters (default), exact pixels, or by fitting an exact line count.


<a id="org597bf4d"></a>

# Installation

    pip install eink-template-gen


<a id="org147e5c4"></a>

# Quick Start (Wizard)

For the easiest experience, use the interactive wizard.

1.  Install the tool (if you haven't already):
    
        pip install eink-template-gen

2.  Run the wizard:
    
        eink-template-gen --wizard

This will guide you step-by-step through selecting a device, template, and all the relevant options, then generate the file for you.


<a id="org27a38ee"></a>

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


<a id="org3c734ed"></a>

# Supported Devices

Built-in device profiles:

-   Supernote Manta (10.7", 1920x2560, 300 DPI)
-   Supernote A5 X (10.3", 1404x1872, 226 DPI)
-   Supernote A6 X (7.8", 1404x1872, 300 DPI)
-   Supernote Nomad (7.8", 1404x1872, 300 DPI)


<a id="org217ca64"></a>

# Configuration

Set a default device to avoid specifying `--device` every time:

    eink-template-gen util set-default-device manta
    eink-template-gen util set-default-margin 10

Configuration is stored locally in `config.json`.


<a id="org539e9c8"></a>

# Usage Examples


<a id="org1db95cb"></a>

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


<a id="org9f78a14"></a>

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


<a id="org49c4688"></a>

# AI-Assisted Development (ai-wizard-prompt.org)

This project includes a file named `ai-wizard-prompt.org` (and `.md`). This file is **not** used by the Python code.

It is a comprehensive "system prompt" or context file that defines the **entire** logic of the wizard as a persona for a Large Language Model (AI).

****When to use it:****

-   **Prototyping:** Quickly test new or complex feature combinations without writing Python code for the wizard.
-   **Assistance:** If you are unsure of the flags, you can have an AI act as the complete wizard to guide you and generate the final command or JSON file.

****How to use it:****

1.  Open `ai-wizard-prompt.org` or `ai-wizard-prompt.md`.
2.  Copy the **entire** contents of the file.
3.  Paste the contents into a **new chat session** with a capable LLM (like Gemini, Claude, or ChatGPT).
4.  On a new line after the pasted text, type: `Okay, you are the eink-template-gen Wizard. Start.`
5.  The AI will then take on the persona of the wizard and begin asking you questions, one at a time, to build your template.


<a id="org6f3df60"></a>

# Contributing

Contributions are welcome! This project uses:

-   Cairo for high-quality 2D graphics rendering
-   Python 3.8+
-   Pure Python implementation (no external dependencies for noise/fractals)


<a id="org26a70a4"></a>

## Development Setup

To set up a development environment:

    # Clone the repo
    git clone https://github.com/calebc42/eink-template-gen.git
    cd eink-template-gen
    
    # Install in editable mode with dev/test dependencies
    pip install -e .[dev,test]


<a id="orge183f49"></a>

# License

This project is licensed under the **GNU General Public License v3.0**. See the `LICENSE` file for details.


<a id="org4a90d11"></a>

# Credits

Developed for the Supernote community with love for pixel-perfect templates.

