
# Table of Contents

1.  [Feature: Flexible Layouts](#org2af0683)
    1.  [Single Page Templates](#org7131567)
    2.  [Uniform Multi-Cell Grids](#org6cd5269)
    3.  [Mixed Multi-Type Grids](#org23f148f)
    4.  [JSON Layout Engine](#orgc5e3569)


<a id="org2af0683"></a>

# Feature: Flexible Layouts


<a id="org7131567"></a>

## Single Page Templates

    eink-template-gen lined --spacing 7mm --margin 10
    eink-template-gen grid --spacing 5mm --major_every 5 --axis-labels


<a id="org6cd5269"></a>

## Uniform Multi-Cell Grids

Create N × M grids where all cells use the same template:

    # 2x2 grid of dotgrid
    eink-template-gen multi --rows 2 --columns 2 --type dotgrid --spacing 5mm
    # 2 stacked (vertical) sections of lined paper
    eink-template-gen multi --rows 2 --columns 1 --type lined --spacing 7mm --orientation vertical

The `multi` command also supports an `--orientation` flag (`horizontal` or `vertical`) which determines the layout flow.


<a id="org23f148f"></a>

## Mixed Multi-Type Grids

Create N × M grids where each cell can be a different template type:

    eink-template-gen multi --rows 2 --columns 2 \
      --cell_types lined,grid,dotgrid,manuscript --spacing 6mm


<a id="orgc5e3569"></a>

## JSON Layout Engine

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

:SUMMARY: Click to see Screenshot Gallery: Flexible Layouts

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
<td class="org-left"><img src="src/assets/screenshots/manta/layout_multi_uniform.png" alt="layout_multi_uniform.png" /></td>
<td class="org-left"><img src="src/assets/screenshots/manta/layout_multi_vertical.png" alt="layout_multi_vertical.png" /></td>
<td class="org-left"><img src="src/assets/screenshots/manta/layout_multi_mixed.png" alt="layout_multi_mixed.png" /></td>
<td class="org-left"><img src="src/assets/screenshots/manta/layout_json_cornell.png" alt="layout_json_cornell.png" /></td>
</tr>
</tbody>
</table>

:END:

