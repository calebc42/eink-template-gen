#!/usr/bin/env python3
"""
Supernote Template Generator - CLI Entry Point
"""
import argparse
import sys

from eink_template_gen.actions import (
    handle_cover_generation,
    handle_json_generation,
    handle_list_devices,
    handle_list_templates,
    handle_multi_template_generation,
    handle_set_default_device,
    handle_set_default_margin,
    handle_show_spacing_info,
    handle_single_template_generation,
)
from eink_template_gen.config import get_default_margin
from eink_template_gen.covers import COVER_REGISTRY
from eink_template_gen.devices import list_devices
from eink_template_gen.separators import SEPARATOR_STYLES
from eink_template_gen.templates import TEMPLATE_REGISTRY


def create_common_parser():
    """
    Creates a parent parser with arguments common to all template generation.
    """
    # --- Get config defaults BEFORE parsing ---
    global_default_margin = get_default_margin()

    parent_parser = argparse.ArgumentParser(add_help=False)

    # --- GLOBAL TEMPLATE CONFIGURATION ---
    config_group = parent_parser.add_argument_group("Global Configuration")
    config_group.add_argument(
        "--device", choices=list_devices(), help="Target device (overrides default or JSON value)"
    )

    config_group.add_argument(
        "--spacing",
        type=str,
        default="6",
        help="Global spacing for lines/dots/tiles. " 'Use "6mm", "71px", or "6". Default: 6mm',
    )

    config_group.add_argument(
        "--true-scale",
        action="store_true",
        help="Use true-scale mm spacing. Disables pixel-perfect rounding (may cause blur).",
    )

    config_group.add_argument(
        "--margin",
        type=float,
        default=None,
        metavar="MM",
        help=f"Margin in mm. Overrides device-specific default. "
        f"(Global fallback is {global_default_margin}mm)",
    )

    config_group.add_argument(
        "--enforce-margins",
        action="store_true",
        help="Allow fractional pixel spacing when using --lines (may cause slight blur)",
    )

    # Add dry-run mode
    config_group.add_argument(
        "--preview", action="store_true", help="Preview settings without generating files"
    )

    # --- Line Count Mode ---
    config_group.add_argument(
        "--lines",
        type=str,
        help='Exact number of lines to fit (e.g., "40" or "40x30" for grids). '
        "Overrides --spacing. By default uses 0 margins; use --margin to specify margins.",
    )

    # --- Styling Kwargs ---
    style_group = parent_parser.add_argument_group("Global Styling")
    valid_sep_styles = [s for s in SEPARATOR_STYLES if s is not None]
    style_group.add_argument(
        "--header",
        type=str,
        metavar="STYLE",
        help=f'Header separator style. Available: {", ".join(valid_sep_styles)}. '
        f'Use "style" or "style(param=value,param=value)" format.',
    )

    style_group.add_argument(
        "--footer",
        type=str,
        metavar="STYLE",
        help=f'Footer separator style. Available: {", ".join(valid_sep_styles)}. '
        f'Use "style" or "style(param=value,param=value)" format.',
    )

    # --- Corner Ornaments ---
    corner_group = parent_parser.add_argument_group("Corner Ornaments")
    corner_group.add_argument(
        "--corner-style",
        type=str,
        metavar="STYLE",
        help="Corner ornament style. Available: bracket, circuit-corner, crosshair, "
        "geometric-frame, tech-marker, diagonal-stripes, corner-node, pixel-art",
    )

    corner_group.add_argument(
        "--corner-size",
        type=float,
        default=20.0,
        help="Size of corner ornaments in pixels (default: 20)",
    )

    corner_group.add_argument(
        "--corner-grey",
        type=int,
        default=0,
        help="Greyscale level for corners 0-15 (default: 0 = black)",
    )

    corner_group.add_argument(
        "--corner-inset",
        type=float,
        default=0.618,
        metavar="RATIO",
        help="Ratio of corner extending into content (0.0=all in margin, 1.0=all in content, default: 0.618)",
    )

    # --- File Output Kwargs ---
    output_group = parent_parser.add_argument_group("File Output")
    output_group.add_argument("--output-dir", default="out", help="Output directory (default: out)")

    output_group.add_argument("--filename", help="Custom filename (default: auto-generated)")

    return parent_parser


def _add_line_numbering_args(parser_group):
    """Adds all line-numbering arguments to a given parser group."""
    parser_group.add_argument(
        "--line-numbers",
        nargs="?",
        type=int,
        const=5,  # Default interval if flag is present without a value
        default=None,  # Value if flag is not present
        dest="line_numbers_interval",  # Use this new destination
        metavar="INTERVAL",
        help="Enable line numbering. Optionally provide an interval (e.g., '--line-numbers' for default 5, '--line-numbers 10' for 10).",
    )
    parser_group.add_argument(
        "--line-numbers-side",
        choices=["left", "right"],
        default="left",
        help="Side (default: left)",
    )
    parser_group.add_argument(
        "--line-numbers-margin-px",
        type=int,
        default=40,
        help="Distance from page edge in pixels (default: 40)",
    )
    parser_group.add_argument(
        "--line-numbers-font-size", type=int, default=18, help="Font size (default: 18)"
    )
    parser_group.add_argument(
        "--line-numbers-grey",
        type=int,
        default=8,
        help="Greyscale level 0-15 (default: 8 = #808080)",
    )


def _add_cell_label_args(parser_group):
    """Adds all cell-labeling arguments to a given parser group."""
    # The main "--cell-labels" flag is defined in the parser itself.
    # This function just adds the configuration options.
    parser_group.add_argument(
        "--cell-labels-y-side",
        choices=["left", "right"],
        default="left",
        help="Side for Y-axis labels ('1, 2, 3...') (default: left)",
    )
    parser_group.add_argument(
        "--cell-labels-y-padding-px",
        type=int,
        default=10,
        help="Padding from left/right grid edge (default: 10)",
    )
    parser_group.add_argument(
        "--cell-labels-x-side",
        choices=["top", "bottom"],
        default="bottom",
        help="Side for X-axis labels ('A, B, C...') (default: bottom)",
    )
    parser_group.add_argument(
        "--cell-labels-x-padding-px",
        type=int,
        default=10,
        help="Padding from top/bottom grid edge (default: 10)",
    )
    parser_group.add_argument(
        "--cell-labels-font-size", type=int, default=16, help="Font size (default: 16)"
    )
    parser_group.add_argument(
        "--cell-labels-grey",
        type=int,
        default=10,
        help="Greyscale level 0-15 (default: 10 = #a0a0a0)",
    )


def _add_axis_label_args(parser_group):
    """Adds all axis-labeling arguments to a given parser group."""
    # The main "--axis-labels" flag is defined in the parser itself.
    # This function just adds the configuration options.
    parser_group.add_argument(
        "--axis-labels-origin",
        choices=["topLeft", "bottomLeft"],
        default="topLeft",
        help="Set the (0,0) origin (default: topLeft)",
    )
    parser_group.add_argument(
        "--axis-labels-interval",
        type=int,
        default=5,
        help="Number every Nth grid line (default: 5)",
    )
    parser_group.add_argument(
        "--axis-labels-y-side",
        choices=["left", "right"],
        default="left",
        help="Side for Y-axis numbers (default: left)",
    )
    parser_group.add_argument(
        "--axis-labels-y-padding-px",
        type=int,
        default=10,
        help="Padding from left/right grid edge (default: 10)",
    )
    parser_group.add_argument(
        "--axis-labels-x-side",
        choices=["top", "bottom"],
        default="bottom",
        help="Side for X-axis numbers (default: bottom)",
    )
    parser_group.add_argument(
        "--axis-labels-x-padding-px",
        type=int,
        default=10,
        help="Padding from top/bottom grid edge (default: 10)",
    )
    parser_group.add_argument(
        "--axis-labels-font-size", type=int, default=16, help="Font size (default: 16)"
    )
    parser_group.add_argument(
        "--axis-labels-grey",
        type=int,
        default=10,
        help="Greyscale level 0-15 (default: 10 = #a0a0a0)",
    )


def configure_util_parser(subparsers):
    """
    Configures the `util` command and its own sub-commands.
    """
    util_parser = subparsers.add_parser("util", help="Utility commands for managing the tool")
    util_subparsers = util_parser.add_subparsers(
        title="Utility Commands", dest="util_command", required=True
    )

    # --- util list-devices ---
    list_dev_parser = util_subparsers.add_parser(
        "list-devices", help="List all available devices and exit"
    )
    list_dev_parser.set_defaults(func=handle_list_devices)

    # --- util list-templates ---
    list_tpl_parser = util_subparsers.add_parser(
        "list-templates", help="List all available templates and cover patterns and exit"
    )
    list_tpl_parser.set_defaults(func=handle_list_templates)

    # --- util set-default-device ---
    set_dev_parser = util_subparsers.add_parser(
        "set-default-device", help="Set the default device for future runs"
    )
    set_dev_parser.add_argument(
        "device", choices=list_devices(), help="Device ID to set as default"
    )
    set_dev_parser.set_defaults(func=handle_set_default_device)

    # --- util set-default-margin ---
    set_margin_parser = util_subparsers.add_parser(
        "set-default-margin", help="Set the default margin in mm for future runs"
    )
    set_margin_parser.add_argument(
        "margin_mm", type=float, metavar="MM", help="Margin in mm to set as default"
    )
    set_margin_parser.set_defaults(func=handle_set_default_margin)

    # --- util info ---
    info_parser = util_subparsers.add_parser(
        "info", help="Show detailed spacing analysis for a device"
    )
    info_parser.add_argument(
        "spacing", type=str, metavar="SPACING", help='Spacing to analyze (e..g., "6mm" or "71px")'
    )
    info_parser.add_argument(
        "--device", choices=list_devices(), help="Target device (optional, uses default if not set)"
    )
    info_parser.set_defaults(func=handle_show_spacing_info)


def configure_cover_parser(subparsers, common_parser):
    """
    Configures the `cover` command for generating cover pages.
    """
    cover_parser = subparsers.add_parser(
        "cover",
        parents=[common_parser],
        help="Generate a decorative cover page pattern",
        description="Generate a decorative cover page pattern (e.g., Truchet tiles, fractals, noise patterns).",
    )
    cover_parser.set_defaults(func=handle_cover_generation)

    cover_parser.add_argument(
        "--type",
        choices=list(COVER_REGISTRY.keys()),
        required=True,
        dest="cover",  # Explicitly set dest to 'cover' to match original args
        help="Cover page pattern type",
    )

    # --- Common Style Args ---
    cover_parser.add_argument(
        "--line-width-px", type=float, default=0.5, help="Line width in pixels (default: 0.5)"
    )

    # --- Cover Pattern Options ---
    pattern_group = cover_parser.add_argument_group("Cover Pattern Options")
    pattern_group.add_argument(
        "--truchet-seed",
        type=int,
        help="Random seed for Truchet tile pattern (for reproducible designs)",
    )
    pattern_group.add_argument(
        "--truchet-fill-grey",
        type=int,
        default=None,
        help="Greyscale 0-15 to fill Truchet tiles (default: None = outline only)",
    )
    pattern_group.add_argument(
        "--diag-fill-grey1",
        type=int,
        default=0,
        help="Greyscale 0-15 for 1st triangle in diagonal pattern (default: 0 = black)",
    )
    pattern_group.add_argument(
        "--diag-fill-grey2",
        type=int,
        default=15,
        help="Greyscale 0-15 for 2nd triangle in diagonal pattern (default: 15 = white)",
    )
    pattern_group.add_argument(
        "--truchet-variant",
        choices=["classic", "cross", "triangle", "wave", "mixed"],
        default="classic",
        help="Truchet tile variant style (default: classic)",
    )
    pattern_group.add_argument(
        "--decorative-border",
        choices=["simple", "double", "ornate", "geometric"],
        help="Add decorative border around pattern (optional)",
    )
    pattern_group.add_argument(
        "--lsystem-iterations",
        type=int,
        default=4,
        help="Number of iterations for L-Systems (default: 4)",
    )
    pattern_group.add_argument(
        "--noise-scale",
        type=float,
        default=0.02,
        help="Noise frequency scale (0.01-0.05, smaller = larger features). Default: 0.02",
    )
    pattern_group.add_argument(
        "--noise-octaves",
        type=int,
        default=4,
        help="Number of noise octaves for detail (1-6, more = more detail). Default: 4",
    )
    pattern_group.add_argument(
        "--noise-seed",
        type=int,
        help="Random seed for noise generation (for reproducible patterns)",
    )
    pattern_group.add_argument(
        "--noise-style",
        choices=["smooth", "turbulent", "simple"],
        default="smooth",
        help="Noise style: smooth (terrain-like), turbulent (marble), simple (basic). Default: smooth",
    )
    pattern_group.add_argument(
        "--contour-interval",
        type=float,
        default=0.1,
        help="Elevation between contour lines (0.05-0.2, smaller = denser). Default: 0.1",
    )
    pattern_group.add_argument(
        "--greyscale-levels",
        type=int,
        default=16,
        help="Number of greyscale levels for noise_field pattern (1-16). Default: 16",
    )

    # --- Title Text & Frame Options ---
    frame_group = cover_parser.add_argument_group("Title Text & Frame Options")
    frame_group.add_argument(
        "--title-text",
        type=str,
        help="Text to display on the cover page (optional - leave blank to handwrite)",
    )
    frame_group.add_argument(
        "--title-no-frame", action="store_true", help="Disable frame around title text"
    )
    frame_group.add_argument(
        "--title-frame-shape",
        choices=["rectangle", "rounded-rectangle", "ellipse", "circle"],
        default="rounded-rectangle",
        help="Shape of title frame (default: rounded-rectangle)",
    )
    frame_group.add_argument(
        "--title-border-style",
        choices=["solid", "dashed", "dotted", "double", "ornate"],
        default="solid",
        help="Style of frame border (default: solid)",
    )
    frame_group.add_argument(
        "--title-border-width",
        type=float,
        default=2.0,
        help="Width of frame border in pixels (default: 2.0)",
    )
    frame_group.add_argument(
        "--title-border-grey",
        type=int,
        default=0,
        help="Border greyscale 0-15 (default: 0 = black)",
    )
    frame_group.add_argument(
        "--title-fill-grey",
        type=int,
        default=15,
        help="Frame fill greyscale 0-15 (default: 15 = white)",
    )
    frame_group.add_argument(
        "--title-corner-radius",
        type=int,
        default=10,
        help="Corner radius for rounded rectangles (default: 10)",
    )
    frame_group.add_argument(
        "--title-font-family",
        type=str,
        default="Serif",
        help="Font family: Serif, Sans, Monospace (default: Serif)",
    )
    frame_group.add_argument(
        "--title-font-size", type=int, default=48, help="Font size in points (default: 48)"
    )
    frame_group.add_argument(
        "--title-font-weight",
        choices=["normal", "bold"],
        default="bold",
        help="Font weight (default: bold)",
    )
    frame_group.add_argument(
        "--title-font-slant",
        choices=["normal", "italic", "oblique"],
        default="normal",
        help="Font slant (default: normal)",
    )
    frame_group.add_argument(
        "--title-text-grey", type=int, default=0, help="Text greyscale 0-15 (default: 0 = black)"
    )
    frame_group.add_argument(
        "--title-letter-spacing",
        type=int,
        default=0,
        help="Extra spacing between letters in pixels (default: 0)",
    )
    frame_group.add_argument(
        "--title-h-align",
        choices=["left", "center", "right"],
        default="center",
        help="Horizontal alignment (default: center)",
    )
    frame_group.add_argument(
        "--title-v-align",
        choices=["top", "center", "bottom"],
        default="top",
        help="Vertical alignment (default: top)",
    )
    frame_group.add_argument(
        "--title-x-center",
        type=float,
        help="Horizontal center for the title frame (in pixels). Default: page center.",
    )
    frame_group.add_argument(
        "--title-y-center",
        type=float,
        help="Vertical center for the title frame (in pixels). Default: top third of page.",
    )
    frame_group.add_argument(
        "--title-frame-width",
        type=float,
        help="Width of the title frame (in pixels). Default: 60%% of page width.",
    )
    frame_group.add_argument(
        "--title-frame-height",
        type=float,
        help="Height of the title frame (in pixels). Default: 20%% of page height.",
    )


def configure_layout_parser(subparsers, common_parser):
    """
    Configures the `layout` command for generating from JSON.
    """
    layout_parser = subparsers.add_parser(
        "layout",
        parents=[common_parser],
        help="Generate a complex, ratio-based template from a JSON file",
        description="Generate a complex, ratio-based template from a JSON layout file.",
    )
    layout_parser.set_defaults(func=handle_json_generation)

    layout_parser.add_argument(
        "--file",
        type=str,
        required=True,
        dest="layout",  # Match original 'args.layout'
        help="Path to the JSON layout configuration file.",
    )

    layout_parser.add_argument(
        "--force-major-alignment",
        action="store_true",
        help="Force grid to end on major lines by adjusting margins (requires --major_every in JSON)",
    )


def configure_multi_parser(subparsers, common_parser):
    """
    Configures the `multi` command for all grid-based layouts.
    """
    multi_parser = subparsers.add_parser(
        "multi",
        parents=[common_parser],
        help="Generate a multi-cell grid template (uniform or mixed types)",
        description="Generate a grid of templates, either all the same type or a mix of different types.",
    )
    multi_parser.set_defaults(func=handle_multi_template_generation)

    # --- Required Grid Args ---
    multi_parser.add_argument("--rows", type=int, required=True, help="Number of rows")
    multi_parser.add_argument("--columns", type=int, required=True, help="Number of columns")

    # --- Grid Type (Uniform or Mixed) ---
    type_group = multi_parser.add_mutually_exclusive_group(required=True)
    type_group.add_argument(
        "--type",
        dest="template",  # Match original 'args.template'
        choices=list(TEMPLATE_REGISTRY.keys()),
        help="Template type for a UNIFORM grid (all cells are this type)",
    )
    type_group.add_argument(
        "--cell-types",
        type=str,
        help='Comma-separated list of template types for a MIXED grid (e.g., "lined,dotgrid,grid,lined")',
    )

    # --- Layout Args ---
    layout_group = multi_parser.add_argument_group("Grid Layout")
    layout_group.add_argument(
        "--section-gap-cols",
        type=float,
        metavar="MM",
        help="Gap between columns in mm (defaults to same as --spacing)",
    )
    layout_group.add_argument(
        "--section-gap-rows",
        type=float,
        metavar="MM",
        help="Gap between rows in mm (defaults to same as --spacing)",
    )
    layout_group.add_argument(
        "--orientation",
        choices=["horizontal", "vertical"],
        default="horizontal",
        help="Orientation of ruling lines: horizontal (default) or vertical (rotated 90°)",
    )

    # --- Style Args (for child templates) ---
    # We must add all possible child-template args here
    style_group = multi_parser.add_argument_group("Child Template Styling (used by cells)")
    style_group.add_argument(
        "--line-width-px", type=float, default=0.5, help="Line width (for lined, grid, etc.)"
    )
    style_group.add_argument(
        "--dot-radius-px", type=float, default=1.5, help="Dot radius (for dotgrid)"
    )
    style_group.add_argument(
        "--major-every", type=int, help="Make every Nth line thicker (for grid, lined)"
    )
    style_group.add_argument(
        "--major-width-add-px", type=float, default=1.5, help="Added width for major lines"
    )
    style_group.add_argument(
        "--crosshair-size", type=int, default=4, help="Size of cross-hairs (for grid)"
    )
    style_group.add_argument("--no-crosshairs", action="store_true", help="Disable cross-hairs")
    style_group.add_argument(
        "--midline-style",
        choices=["dashed", "dotted"],
        default="dashed",
        help="Style for manuscript midline",
    )
    style_group.add_argument(
        "--ascender-opacity", type=float, default=0.3, help="Opacity for manuscript ascender line"
    )
    style_group.add_argument(
        "--staff-gap-mm", type=float, default=10, help="Gap between music staves"
    )
    style_group.add_argument(
        "--split-ratio",
        type=float,
        default=0.6,
        help="Split ratio for hybrid templates (default: 0.6)",
    )
    style_group.add_argument(
        "--section-gap-mm", type=float, help="Gap between sections in hybrid templates in mm"
    )

    # --- Line Numbering Group (for child 'lined') ---
    num_group = multi_parser.add_argument_group('Line Numbering (for child "lined" cells)')
    _add_line_numbering_args(num_group)

    # --- Cell Labeling Group (for child 'grid') ---
    cell_label_group = multi_parser.add_argument_group('Cell Labeling (for child "grid" cells)')
    _add_cell_label_args(cell_label_group)

    # --- Axis Labeling Group (for child 'grid') ---
    axis_label_group = multi_parser.add_argument_group('Axis Labeling (for child "grid" cells)')
    _add_axis_label_args(axis_label_group)


def configure_template_parsers(subparsers, common_parser):
    """
    Configures individual sub-parsers for each single template type.
    """

    # --- 'lined' Template ---
    lined_parser = subparsers.add_parser(
        "lined",
        parents=[common_parser],
        help="Generate a simple lined template",
        description="Generate a full-page lined template.",
    )
    lined_parser.set_defaults(func=handle_single_template_generation, template_type="lined")

    spec_group = lined_parser.add_argument_group("Lined Template Options")
    spec_group.add_argument(
        "--line-width-px", type=float, default=0.5, help="Line width in pixels (default: 0.5)"
    )
    spec_group.add_argument("--major-every", type=int, help="Make every Nth line thicker")
    spec_group.add_argument(
        "--major-width-add-px", type=float, default=1.5, help="Added width for major lines"
    )

    num_group = lined_parser.add_argument_group("Line Numbering Options")
    _add_line_numbering_args(num_group)

    # --- 'dotgrid' Template ---
    dotgrid_parser = subparsers.add_parser(
        "dotgrid",
        parents=[common_parser],
        help="Generate a dot grid template",
        description="Generate a full-page dot grid template.",
    )
    dotgrid_parser.set_defaults(func=handle_single_template_generation, template_type="dotgrid")

    spec_group = dotgrid_parser.add_argument_group("Dotgrid Template Options")
    spec_group.add_argument(
        "--dot-radius-px", type=float, default=1.5, help="Dot radius in pixels (default: 1.5)"
    )
    spec_group.add_argument("--major-every", type=int, help="Make every Nth dot/line a crosshair")
    spec_group.add_argument(
        "--crosshair-size",
        type=int,
        default=4,
        help="Size of cross-hair extensions in pixels (default: 4)",
    )
    spec_group.add_argument(
        "--force-major-alignment",
        action="store_true",
        help="Force grid to end on major lines by adjusting margins",
    )

    # --- 'grid' Template ---
    grid_parser = subparsers.add_parser(
        "grid",
        parents=[common_parser],
        help="Generate a full graph paper grid template",
        description="Generate a full-page graph paper grid template.",
    )
    grid_parser.set_defaults(func=handle_single_template_generation, template_type="grid")

    spec_group = grid_parser.add_argument_group("Grid Template Options")
    spec_group.add_argument(
        "--line-width-px", type=float, default=0.5, help="Line width in pixels (default: 0.5)"
    )
    spec_group.add_argument("--major-every", type=int, help="Make every Nth line thicker")
    spec_group.add_argument(
        "--major-width-add-px",
        type=float,
        default=1.5,
        help="Added width for major lines (default: 1.5)",
    )
    spec_group.add_argument(
        "--crosshair-size",
        type=int,
        default=4,
        help="Size of cross-hair extensions in pixels (default: 4)",
    )
    spec_group.add_argument(
        "--no-crosshairs", action="store_true", help="Disable cross-hairs at major intersections"
    )
    spec_group.add_argument(
        "--force-major-alignment",
        action="store_true",
        help="Force grid to end on major lines by adjusting margins",
    )

    label_group = grid_parser.add_mutually_exclusive_group()
    label_group.add_argument(
        "--cell-labels", action="store_true", help="Enable 'A, B, C...' style labeling"
    )
    label_group.add_argument(
        "--axis-labels", action="store_true", help="Enable '0, 5, 10...' style axis numbering"
    )

    cell_label_group = grid_parser.add_argument_group("Cell Labeling (if --cell-labels)")
    _add_cell_label_args(cell_label_group)

    axis_label_group = grid_parser.add_argument_group("Axis Labeling (if --axis-labels)")
    _add_axis_label_args(axis_label_group)

    # --- 'manuscript' Template ---
    manuscript_parser = subparsers.add_parser(
        "manuscript",
        parents=[common_parser],
        help="Generate a manuscript (4-line) handwriting template",
        description="Generate a full-page manuscript (4-line) handwriting template.",
    )
    manuscript_parser.set_defaults(
        func=handle_single_template_generation, template_type="manuscript"
    )

    spec_group = manuscript_parser.add_argument_group("Manuscript Template Options")
    spec_group.add_argument(
        "--line-width-px", type=float, default=0.5, help="Line width in pixels (default: 0.5)"
    )
    spec_group.add_argument(
        "--midline-style",
        choices=["dashed", "dotted"],
        default="dashed",
        help="Style for manuscript midline (default: dashed)",
    )
    spec_group.add_argument(
        "--ascender-opacity",
        type=float,
        default=0.3,
        help="Opacity for manuscript ascender line (default: 0.3)",
    )

    # --- 'french_ruled' Template ---
    french_parser = subparsers.add_parser(
        "french-ruled",
        parents=[common_parser],
        help="Generate a French ruled (Seyès) template",
        description="Generate a full-page French ruled (Seyès) template.",
    )
    french_parser.set_defaults(func=handle_single_template_generation, template_type="french-ruled")

    spec_group = french_parser.add_argument_group("French Ruled Options")
    spec_group.add_argument(
        "--line-width-px", type=float, default=0.5, help="Line width in pixels (default: 0.5)"
    )

    # --- 'music_staff' Template ---
    music_parser = subparsers.add_parser(
        "music-staff",
        parents=[common_parser],
        help="Generate a music staff template",
        description="Generate a full-page music staff template.",
    )
    music_parser.set_defaults(func=handle_single_template_generation, template_type="music-staff")

    spec_group = music_parser.add_argument_group("Music Staff Options")
    spec_group.add_argument(
        "--line-width-px", type=float, default=0.5, help="Line width in pixels (default: 0.5)"
    )
    spec_group.add_argument(
        "--staff-gap-mm",
        type=float,
        default=10,
        help="Gap between music staves in mm (default: 10)",
    )

    # --- 'hybrid_lined_dotgrid' Template ---
    hybrid_parser = subparsers.add_parser(
        "hybrid-lined-dotgrid",
        parents=[common_parser],
        help="Generate a hybrid Lined/Dotgrid template",
        description="Generate a full-page hybrid template with lined on one side and dotgrid on the other.",
    )
    hybrid_parser.set_defaults(
        func=handle_single_template_generation, template_type="hybrid-lined-dotgrid"
    )

    spec_group = hybrid_parser.add_argument_group("Hybrid Template Options")
    spec_group.add_argument(
        "--line-width-px",
        type=float,
        default=0.5,
        help="Line width for lined section (default: 0.5)",
    )
    spec_group.add_argument(
        "--dot-radius-px",
        type=float,
        default=1.5,
        help="Dot radius for dotgrid section (default: 1.5)",
    )
    spec_group.add_argument(
        "--split-ratio", type=float, default=0.6, help="Split ratio (default: 0.6)"
    )
    spec_group.add_argument(
        "--section-gap-mm",
        type=float,
        help="Gap between sections in mm (defaults to same as --spacing)",
    )

    # --- 'isometric' Template ---
    iso_parser = subparsers.add_parser(
        "isometric",
        parents=[common_parser],
        help="Generate an isometric grid template",
        description="Generate a full-page isometric grid template.",
    )
    iso_parser.set_defaults(func=handle_single_template_generation, template_type="isometric")

    spec_group = iso_parser.add_argument_group("Isometric Template Options")
    spec_group.add_argument(
        "--line-width-px", type=float, default=0.5, help="Line width in pixels (default: 0.5)"
    )

    # --- 'hexgrid' Template ---
    hex_parser = subparsers.add_parser(
        "hexgrid",
        parents=[common_parser],
        help="Generate a hexagonal grid template",
        description="Generate a full-page hexagonal grid template.",
    )
    hex_parser.set_defaults(func=handle_single_template_generation, template_type="hexgrid")

    spec_group = hex_parser.add_argument_group("Hexagonal Template Options")
    spec_group.add_argument(
        "--line-width-px", type=float, default=0.5, help="Line width in pixels (default: 0.5)"
    )


def main():
    parser = argparse.ArgumentParser(
        prog="eink-template-gen",
        description="Generate custom templates for e-ink devices",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:

  # --- Utility ---
  eink-template-gen util list-devices
  eink-template-gen util set-default-device manta
  eink-template-gen util info 6mm --device a5x

  # --- Single Templates ---
  eink-template-gen lined --spacing 7 --line-numbers
  eink-template-gen grid --spacing 5 --major-every 5 --axis-labels
  eink-template-gen manuscript --spacing 8

  # --- Multi-Cell Grids ---
  eink-template-gen multi --rows 2 --columns 2 --type dotgrid --spacing 5
  eink-template-gen multi --rows 1 --columns 2 --cell-types lined,grid

  # --- Cover Pages ---
  eink-template-gen cover --type truchet --spacing 10 --truchet-seed 42
  eink-template-gen cover --type contour-lines --noise-scale 0.03 --title-text "My Notebook"

  # --- JSON Layouts ---
  eink-template-gen layout --file my_cornell_layout.json
        """,
    )

    parser.add_argument(
        "--wizard", action="store_true", help="Launch interactive wizard for template creation"
    )

    # --- Create the common parser ---
    common_parser = create_common_parser()

    # --- Create main sub-parser ---
    subparsers = parser.add_subparsers(
        title="Commands", dest="command", required=True, metavar="<command>"
    )

    # --- Register all the sub-parsers ---
    configure_util_parser(subparsers)
    configure_cover_parser(subparsers, common_parser)
    configure_layout_parser(subparsers, common_parser)
    configure_multi_parser(subparsers, common_parser)
    configure_template_parsers(subparsers, common_parser)  # For 'lined', 'grid', etc.

    # --- Parse and dispatch ---
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    # Check for wizard flag before subcommand parsing
    if "--wizard" in sys.argv:
        from .wizard import run_wizard_and_generate

        run_wizard_and_generate()
        sys.exit(0)

    args = parser.parse_args()

    # Call the function assigned by set_defaults()
    try:
        # This single call now handles all commands, including 'util'
        args.func(args)

    except Exception as e:
        print("\n--- ERROR ---", file=sys.stderr)
        print(f"{e}", file=sys.stderr)
        import traceback

        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
