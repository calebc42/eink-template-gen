
# Table of Contents

1.  [Feature: Decorative Cover Pages](#orgea89d5e)
    1.  [Title Text & Framing](#org7ec8eca)
    2.  [Title Positioning](#orgeb17103)


<a id="orgea89d5e"></a>

# Feature: Decorative Cover Pages

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

:SUMMARY: Click to see Screenshot Gallery: Title Pages

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
<td class="org-left"><img src="src/assets/screenshots/manta/title_truchet_filled.png" alt="title_truchet_filled.png" /></td>
<td class="org-left"><img src="src/assets/screenshots/manta/title_diagonal_truchet.png" alt="title_diagonal_truchet.png" /></td>
<td class="org-left"><img src="src/assets/screenshots/manta/title_hexagonal_truchet.png" alt="title_hexagonal_truchet.png" /></td>
</tr>

<tr>
<td class="org-left"><b>10 Print</b></td>
<td class="org-left"><b>Koch Snowflake</b></td>
<td class="org-left"><b>Plant Fractal</b></td>
</tr>

<tr>
<td class="org-left"><img src="src/assets/screenshots/manta/title_ten_print.png" alt="title_ten_print.png" /></td>
<td class="org-left"><img src="src/assets/screenshots/manta/title_lsystem_koch.png" alt="title_lsystem_koch.png" /></td>
<td class="org-left"><img src="src/assets/screenshots/manta/title_lsystem_plant.png" alt="title_lsystem_plant.png" /></td>
</tr>

<tr>
<td class="org-left"><b>Contour Lines</b></td>
<td class="org-left"><b>Noise Field</b></td>
<td class="org-left"><b>Title w/ Frame</b></td>
</tr>

<tr>
<td class="org-left"><img src="src/assets/screenshots/manta/title_contour_lines.png" alt="title_contour_lines.png" /></td>
<td class="org-left"><img src="src/assets/screenshots/manta/title_noise_field.png" alt="title_noise_field.png" /></td>
<td class="org-left"><img src="src/assets/screenshots/manta/title_with_frame.png" alt="title_with_frame.png" /></td>
</tr>
</tbody>
</table>

:END:


<a id="org7ec8eca"></a>

## Title Text & Framing

All title pages support a powerful set of arguments for adding and styling a title block:

-   `--title-text "My Notes"`: The text to display.
-   `--title-frame-shape rounded-rectangle`: Shape of the frame (rectangle, ellipse, etc.).
-   `--title-border-style dashed`: Border style (solid, dashed, dotted, double, ornate).
-   `--title-font-size 32`: Font size in points.
-   `--title-font-family Sans`: Font family (Serif, Sans, Monospace).
-   `--title-fill-grey 15`: Frame fill color (0-15, 15=white).
-   `--title-no-frame`: Disables the frame entirely.


<a id="orgeb17103"></a>

## Title Positioning

By default, the title is placed in the top-third of the page. You can override this:

-   `--title-v-align center`: Vertical alignment (top, center, bottom).
-   `--title-y-center 1000`: Set an exact vertical position in pixels.
-   `--title-h-align left`: Horizontal alignment (left, center, right).
-   `--title-x-center 500`: Set an exact horizontal position in pixels. [cite: org1㓡

