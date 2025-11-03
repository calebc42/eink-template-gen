#!/usr/bin/env python3
"""
Supernote Template Generator - CLI Entry Point
"""
import sys
import argparse
from eink_template_gen.templates import TEMPLATE_REGISTRY
from eink_template_gen.titles import TITLE_REGISTRY
from eink_template_gen.devices import list_devices
from eink_template_gen.separators import SEPARATOR_STYLES
from eink_template_gen.config import get_default_margin

# Import the new action handlers
from eink_template_gen.actions import (
    handle_list_devices,
    handle_set_default_device,
    handle_list_templates,
    handle_show_spacing_info,
    handle_cli_generation,
    handle_json_generation,
    handle_set_default_margin,
    handle_title_generation
)

def main():
    parser = argparse.ArgumentParser(
        description='Generate custom templates for e-ink devices',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate a simple lined template
  python cli.py --template lined --spacing 6
  
  # Generate a 2x2 multi-type grid
  python cli.py --rows 2 --columns 2 --spacing 6 \
    --cell_types lined,dotgrid,manuscript,grid
    
  # Generate a lined template with line numbers
  python cli.py --template lined --spacing 7 --line-numbers --line-numbers-interval 1

  # Generate a grid with spreadsheet-style labels (Y-axis on right)
  python cli.py --template grid --spacing 5 --cell-labels --cell-labels-y-side right

  # Generate a grid with math-style axis numbering (X-axis on top)
  python cli.py --template grid --spacing 10 --axis-labels --axis-labels-x-side top

  # Generate a Truchet tile title page with text
  python cli.py --title truchet --spacing 10 --truchet-seed 42 --title-text "My Notebook"
  
  # Generate a Truchet tile title page without text (for handwriting)
  python cli.py --title truchet --spacing 10

  # Generate topographic contour lines (smooth terrain)
  python cli.py --title contour_lines --spacing 5 --noise-scale 0.03 --contour-interval 0.1

  # Generate dense, detailed contour map with seed
  python cli.py --title contour_lines --spacing 5 --contour-interval 0.05 \
    --noise-octaves 6 --noise-seed 42

  # Generate marble-like turbulent pattern
  python cli.py --title contour_lines --spacing 5 --noise-style turbulent \
    --title-text "Lab Notebook" --title-v-align center

  # Generate greyscale noise texture background
  python cli.py --title noise_field --spacing 5 --noise-scale 0.02 \
    --noise-octaves 5 --greyscale-levels 8

  # Generate a complex, ratio-based layout from a JSON file
  python cli.py --layout my_cornell_layout.json

  # Set default device and margin
  python cli.py --set-default-device manta
  python cli.py --set-default-margin 8.5

  # Generate Truchet variants
  python cli.py --title truchet --spacing 10 --truchet-variant cross

  # Generate mixed Truchet tiles with ornate border
  python cli.py --title truchet --spacing 10 --truchet-variant mixed \
    --decorative-border ornate --title-text "Notebook"

  # Generate new L-system fractals
  python cli.py --title koch_snowflake --spacing 5 --lsystem-iterations 4
  python cli.py --title plant_fractal --spacing 5 --lsystem-iterations 5
  python cli.py --title sierpinski_triangle --spacing 5 --lsystem-iterations 6
        """
    )
    
    # --- Get config defaults BEFORE parsing ---
    global_default_margin = get_default_margin()

    # --- Utility/Management Commands ---
    util_group = parser.add_argument_group('Utility Commands')
    util_group.add_argument('--show-spacing-info',
                        type=str,
                        metavar='SPACING',
                        help='Show detailed spacing analysis (e.g., "6mm" or "71px")')
    
    util_group.add_argument('--set-default-device',
                       choices=list_devices(),
                       help='Set the default device for future runs')
    
    util_group.add_argument('--set-default-margin',
                       type=float,
                       metavar='MM',
                       help='Set the default margin in mm for future runs')
    
    util_group.add_argument('--list-devices',
                       action='store_true',
                       help='List all available devices and exit')
    
    util_group.add_argument('--list-templates',
                       action='store_true',
                       help='List all available templates and title patterns and exit')
    
    # --- TEMPLATE/TITLE SELECTION (Mutually Exclusive) ---
    template_group = parser.add_mutually_exclusive_group(required=True)
    template_group.add_argument('--template',
                       choices=list(TEMPLATE_REGISTRY.keys()),
                       help='Template type (for single or uniform-grid layouts)')
    
    template_group.add_argument('--title',
                       choices=list(TITLE_REGISTRY.keys()),
                       help='Title page pattern type (decorative covers)')
    
    template_group.add_argument('--cell_types',
                       type=str,
                       help='Comma-separated list of template types for a grid, from left-to-right, '
                            'top-to-bottom. Requires --rows and --columns. '
                            'Example: --cell_types lined,dotgrid,grid,manuscript')
    
    template_group.add_argument('--layout',
                       type=str,
                       help='Path to a JSON layout configuration file for complex, ratio-based templates.')
    
    # Add dummy entries for utility commands to satisfy 'required=True'
    # This allows running --list-devices without specifying a template
    template_group.add_argument('--list-devices-dummy', action='store_true', help=argparse.SUPPRESS)
    template_group.add_argument('--list-templates-dummy', action='store_true', help=argparse.SUPPRESS)
    template_group.add_argument('--set-default-device-dummy', action='store_true', help=argparse.SUPPRESS)
    template_group.add_argument('--set-default-margin-dummy', action='store_true', help=argparse.SUPPRESS)
    template_group.add_argument('--show-spacing-info-dummy', action='store_true', help=argparse.SUPPRESS)


    # --- GLOBAL TEMPLATE CONFIGURATION ---
    config_group = parser.add_argument_group('Global Configuration')
    config_group.add_argument('--device',
                       choices=list_devices(),
                       help='Target device (overrides default or JSON value)')
    
    config_group.add_argument('--spacing',
                        type=str,
                        default='6',
                        help='Global spacing for lines/dots/tiles (for --template, --title, or --cell_types). '
                             'Use "6mm", "71px", or "6". Default: 6mm')

    config_group.add_argument('--no-auto-adjust',
                        action='store_true',
                        help='Disable automatic spacing adjustment (only affects mm mode)')
    
    config_group.add_argument('--margin',
                       type=float,
                       default=None,
                       help=f'Margin in mm. Overrides device-specific default. '
                            f'(Global fallback is {global_default_margin}mm)')
    
    config_group.add_argument('--force-major-alignment',
                        action='store_true',
                        help='Force grid to end on major lines by adjusting margins (requires --major_every)')

    # In config_group:
    config_group.add_argument('--lines',
                        type=str,
                        help='Exact number of lines to fit (e.g., "40" or "40x30" for grids). '
                        'Overrides --spacing. By default uses 0 margins; use --margin to specify margins.')

    config_group.add_argument('--enforce-exact-spacing',
                        action='store_true',
                        help='Allow fractional pixel spacing when using --lines (may cause slight blur)')

    # --- Styling Kwargs ---
    style_group = parser.add_argument_group('Global Styling')
    style_group.add_argument('--line_width_px',
                       type=float,
                       default=0.5,
                       help='Line width in pixels (default: 0.5)')
    
    style_group.add_argument('--dot_radius_px',
                       type=float,
                       default=1.5,
                       help='Dot radius in pixels (default: 1.5)')
    
    valid_sep_styles = [s for s in SEPARATOR_STYLES if s is not None]
    style_group.add_argument('--header-sep',
                       choices=valid_sep_styles,
                       help=f'Header separator style (options: {", ".join(valid_sep_styles)})')
    
    style_group.add_argument('--footer-sep',
                       choices=valid_sep_styles,
                       help=f'Footer separator style (options: {", ".join(valid_sep_styles)})')

    # --- File Output Kwargs ---
    output_group = parser.add_argument_group('File Output')
    output_group.add_argument('--output-dir',
                       default='out',
                       help='Output directory (default: out)')
    
    output_group.add_argument('--filename',
                       help='Custom filename (default: auto-generated)')

    # --- Layout Kwargs (Grid/Column/Hybrid) ---
    layout_group = parser.add_argument_group('Grid & Layout')
    layout_group.add_argument('--orientation',
                       choices=['horizontal', 'vertical'],
                       default='horizontal',
                       help='Orientation of ruling lines: horizontal (default) or vertical (rotated 90°)')

    layout_group.add_argument('--columns',
                       type=int,
                       help='Number of columns (for --template or --cell_types)')

    layout_group.add_argument('--rows',
                       type=int,
                       help='Number of rows (for --template or --cell_types)')

    layout_group.add_argument('--section-gap-cols',
                       type=float,
                       help='Gap between columns in mm (defaults to same as --spacing)')

    layout_group.add_argument('--section-gap-rows',
                       type=float,
                       help='Gap between rows in mm (defaults to same as --spacing)')

    layout_group.add_argument('--split-ratio',
                       type=float,
                       default=0.6,
                       help='Split ratio for hybrid templates (default: 0.6)')
    
    layout_group.add_argument('--section_gap_mm',
                       type=float,
                       help='Gap between sections in hybrid templates in mm (defaults to same as --spacing)')

    # --- Template-Specific Kwargs ---
    template_spec_group = parser.add_argument_group('Template-Specific')
    template_spec_group.add_argument('--major_every',
                       type=int,
                       help='Make every Nth line thicker (graph paper style)')
    
    template_spec_group.add_argument('--major_width_add_px',
                       type=float,
                       default=1.5,
                       help='Added width for major line thickness (default: 1.5)')

    template_spec_group.add_argument('--crosshair_size',
                       type=int,
                       default=4,
                       help='Size of cross-hair extensions at major intersections in pixels (default: 3)')
    
    template_spec_group.add_argument('--no_crosshairs',
                       action='store_true',
                       help='Disable cross-hairs at major intersections')

    template_spec_group.add_argument('--midline_style',
                       choices=['dashed', 'dotted'],
                       default='dashed',
                       help='Style for manuscript midline (default: dashed)')
    
    template_spec_group.add_argument('--ascender_opacity',
                       type=float,
                       default=0.3,
                       help='Opacity for manuscript ascender line (default: 0.3)')
                       
    template_spec_group.add_argument('--staff_gap_mm',
                       type=float,
                       default=10,
                       help='Gap between music staves in mm (default: 10)')
    
    # --- Title Pattern Options ---
    title_group = parser.add_argument_group('Title Pattern Options')
    title_group.add_argument('--truchet-seed',
                   type=int,
                   help='Random seed for Truchet tile pattern (for reproducible designs)')

    title_group.add_argument('--truchet-fill-grey',
                   type=int,
                   default=None,
                   help='Greyscale 0-15 to fill Truchet tiles (default: None = outline only)')

    title_group.add_argument('--diag-fill-grey1',
                   type=int,
                   default=0,
                   help='Greyscale 0-15 for 1st triangle in diagonal pattern (default: 0 = black)')
                   
    title_group.add_argument('--diag-fill-grey2',
                   type=int,
                   default=15,
                   help='Greyscale 0-15 for 2nd triangle in diagonal pattern (default: 15 = white)')

    # Truchet variant options
    title_group.add_argument('--truchet-variant',
                   choices=['classic', 'cross', 'triangle', 'wave', 'mixed'],
                   default='classic',
                   help='Truchet tile variant style (default: classic)')
    
    # Decorative border option (works with all patterns)
    title_group.add_argument('--decorative-border',
                   choices=['simple', 'double', 'ornate', 'geometric'],
                   help='Add decorative border around pattern (optional)')

    title_group.add_argument('--lsystem-iterations',
                   type=int,
                   default=4,
                   help='Number of iterations for L-Systems (default: 4)')
                   
    # title_group.add_argument('--lsystem-step-px',
    #                type=int,
    #                default=10,
    #                help='Step length in pixels for L-System turtle (default: 10)')

    title_group.add_argument('--noise-scale',
                   type=float,
                   default=0.02,
                   help='Noise frequency scale (0.01-0.05, smaller = larger features). Default: 0.02')
    
    title_group.add_argument('--noise-octaves',
                   type=int,
                   default=4,
                   help='Number of noise octaves for detail (1-6, more = more detail). Default: 4')
    
    title_group.add_argument('--noise-seed',
                   type=int,
                   help='Random seed for noise generation (for reproducible patterns)')
    
    title_group.add_argument('--noise-style',
                   choices=['smooth', 'turbulent', 'simple'],
                   default='smooth',
                   help='Noise style: smooth (terrain-like), turbulent (marble), simple (basic). Default: smooth')
    
    # Contour-specific options
    title_group.add_argument('--contour-interval',
                   type=float,
                   default=0.1,
                   help='Elevation between contour lines (0.05-0.2, smaller = denser). Default: 0.1')
    
    # Noise field-specific options
    title_group.add_argument('--greyscale-levels',
                   type=int,
                   default=16,
                   help='Number of greyscale levels for noise_field pattern (1-16). Default: 16')
    
    # Title text and frame options
    title_group.add_argument('--title-text',
                   type=str,
                   help='Text to display on the title page (optional - leave blank to handwrite)')
    
    title_group.add_argument('--title-no-frame',
                   action='store_true',
                   help='Disable frame around title text')
    
    title_group.add_argument('--title-frame-shape',
                   choices=['rectangle', 'rounded-rectangle', 'ellipse', 'circle'],
                   default='rounded-rectangle',
                   help='Shape of title frame (default: rounded-rectangle)')
    
    title_group.add_argument('--title-border-style',
                   choices=['solid', 'dashed', 'dotted', 'double', 'ornate'],
                   default='solid',
                   help='Style of frame border (default: solid)')
    
    title_group.add_argument('--title-border-width',
                   type=float,
                   default=2.0,
                   help='Width of frame border in pixels (default: 2.0)')
    
    title_group.add_argument('--title-border-grey',
                   type=int,
                   default=0,
                   help='Border greyscale 0-15 (default: 0 = black)')
    
    title_group.add_argument('--title-fill-grey',
                   type=int,
                   default=15,
                   help='Frame fill greyscale 0-15 (default: 15 = white)')
    
    title_group.add_argument('--title-corner-radius',
                   type=int,
                   default=10,
                   help='Corner radius for rounded rectangles (default: 10)')
    
    title_group.add_argument('--title-font-family',
                   type=str,
                   default='Serif',
                   help='Font family: Serif, Sans, Monospace (default: Serif)')
    
    title_group.add_argument('--title-font-size',
                   type=int,
                   default=48,
                   help='Font size in points (default: 48)')
    
    title_group.add_argument('--title-font-weight',
                   choices=['normal', 'bold'],
                   default='bold',
                   help='Font weight (default: bold)')
    
    title_group.add_argument('--title-font-slant',
                   choices=['normal', 'italic', 'oblique'],
                   default='normal',
                   help='Font slant (default: normal)')
    
    title_group.add_argument('--title-text-grey',
                   type=int,
                   default=0,
                   help='Text greyscale 0-15 (default: 0 = black)')
    
    title_group.add_argument('--title-letter-spacing',
                   type=int,
                   default=0,
                   help='Extra spacing between letters in pixels (default: 0)')

    title_group.add_argument('--title-h-align',
                   choices=['left', 'center', 'right'],
                   default='center',
                   help='Horizontal alignment (default: center)')
    
    title_group.add_argument('--title-v-align',
                   choices=['top', 'center', 'bottom'],
                   default='top',
                   help='Vertical alignment (default: top)')
    
    # --- MODIFIED: Added Title Positioning & Sizing ---
    title_group.add_argument('--title-x-center',
                   type=float,
                   help='Horizontal center for the title frame (in pixels). Default: page center.')
    
    title_group.add_argument('--title-y-center',
                   type=float,
                   help='Vertical center for the title frame (in pixels). Default: top third of page.')
    
    title_group.add_argument('--title-frame-width',
                   type=float,
                   help='Width of the title frame (in pixels). Default: 60%% of page width.')
    
    title_group.add_argument('--title-frame-height',
                   type=float,
                   help='Height of the title frame (in pixels). Default: 20%% of page height.')
    
    # --- Line Numbering Group (for 'lined') ---
    num_group = parser.add_argument_group('Line Numbering (for --template lined)')
    num_group.add_argument('--line-numbers',
                           action='store_true',
                           help="Enable line numbering for 'lined' templates.")
    num_group.add_argument('--line-numbers-side',
                           choices=['left', 'right'],
                           default='left',
                           help="Side to place line numbers (default: left)")
    num_group.add_argument('--line-numbers-interval',
                           type=int,
                           default=5,
                           dest='line_numbers_interval_val',
                           help="Number every Nth line (default: 5)")
    num_group.add_argument('--line-numbers-margin-px',
                           type=int,
                           default=40,
                           help="Horizontal distance from page edge in pixels (default: 40)")
    num_group.add_argument('--line-numbers-font-size',
                           type=int,
                           default=18,
                           help="Font size for line numbers (default: 18)")
    num_group.add_argument('--line-numbers-grey',
                           type=int,
                           default=8,
                           help="Greyscale level 0-15 (default: 8 = #808080)")

    # --- Cell Labeling Group (for 'grid') ---
    cell_label_group = parser.add_argument_group('Cell Labeling (for --template grid)')
    cell_label_group.add_argument('--cell-labels',
                                 action='store_true',
                                 help="Enable 'A, B, C...' style labeling in the margins for 'grid' templates.")
    cell_label_group.add_argument('--cell-labels-y-side',
                                 choices=['left', 'right'],
                                 default='left',
                                 help="Side for Y-axis labels ('1, 2, 3...') (default: left)")
    cell_label_group.add_argument('--cell-labels-y-padding-px',
                                 type=int,
                                 default=10,
                                 help="Padding from left/right grid edge (default: 10)")
    cell_label_group.add_argument('--cell-labels-x-side',
                                 choices=['top', 'bottom'],
                                 default='bottom',
                                 help="Side for X-axis labels ('A, B, C...') (default: bottom)")
    cell_label_group.add_argument('--cell-labels-x-padding-px',
                                 type=int,
                                 default=10,
                                 help="Padding from top/bottom grid edge (default: 10)")
    cell_label_group.add_argument('--cell-labels-font-size',
                                 type=int,
                                 default=16,
                                 help="Font size for cell labels (default: 16)")
    cell_label_group.add_argument('--cell-labels-grey',
                                 type=int,
                                 default=10,
                                 help="Greyscale level 0-15 (default: 10 = #a0a0a0)")

    # --- Axis Labeling Group (for 'grid') ---
    axis_label_group = parser.add_argument_group('Axis Labeling (for --template grid)')
    axis_label_group.add_argument('--axis-labels',
                                 action='store_true',
                                 help="Enable '0, 5, 10...' style axis plot numbering for 'grid' templates.")
    axis_label_group.add_argument('--axis-labels-origin',
                                 choices=['topLeft', 'bottomLeft'],
                                 default='topLeft',
                                 help="Set the (0,0) origin (default: topLeft)")
    axis_label_group.add_argument('--axis-labels-interval',
                                 type=int,
                                 default=5,
                                 help="Number every Nth grid line (default: 5)")
    axis_label_group.add_argument('--axis-labels-y-side',
                                 choices=['left', 'right'],
                                 default='left',
                                 help="Side for Y-axis numbers (default: left)")
    axis_label_group.add_argument('--axis-labels-y-padding-px',
                                 type=int,
                                 default=10,
                                 help="Padding from left/right grid edge (default: 10)")
    axis_label_group.add_argument('--axis-labels-x-side',
                                 choices=['top', 'bottom'],
                                 default='bottom',
                                 help="Side for X-axis numbers (default: bottom)")
    axis_label_group.add_argument('--axis-labels-x-padding-px',
                                 type=int,
                                 default=10,
                                 help="Padding from top/bottom grid edge (default: 10)")
    axis_label_group.add_argument('--axis-labels-font-size',
                                 type=int,
                                 default=16,
                                 help="Font size for axis labels (default: 16)")
    axis_label_group.add_argument('--axis-labels-grey',
                                 type=int,
                                 default=10,
                                 help="Greyscale level 0-15 (default: 10 = #a0a0a0)")
    
    args = parser.parse_args()
    
    # --- Argument Routing logic ---
    
    # Handle utility commands first
    if args.set_default_device:
        handle_set_default_device(args.set_default_device)
        sys.exit(0)
    
    if args.set_default_margin is not None:
        handle_set_default_margin(args.set_default_margin)
        sys.exit(0)
    
    if args.list_devices:
        handle_list_devices()
        sys.exit(0)
    
    if args.list_templates:
        handle_list_templates()
        sys.exit(0)

    if args.show_spacing_info:
        # Note: --device is optional for this command
        handle_show_spacing_info(args.device, args.show_spacing_info)
        sys.exit(0)
    
    # --- Generation Logic ---
    
    # Check if a real generation command was given
    is_gen_command = args.layout or args.template or args.cell_types or args.title
    if not is_gen_command:
        parser.error("No generation command specified. Use --template, --title, --cell_types, or --layout. Use -h for help.")
    
    # --- Validation Check ---
    if args.cell_labels and args.axis_labels:
        parser.error("argument --axis-labels: not allowed with argument --cell-labels")

    if args.layout:
        # 1. JSON Layout Mode
        handle_json_generation(
            args.layout, 
            args.device, 
            args.no_auto_adjust, 
            args.force_major_alignment
        )
        sys.exit(0)

    elif args.title:
        # 2. Title Pattern Mode
        handle_title_generation(args)
        sys.exit(0)

    elif args.template or args.cell_types:
        # 3. Existing CLI Generation Mode
        if args.cell_types and (not args.rows or not args.columns):
            parser.error("--rows and --columns are required when using --cell_types")
        
        # Check for grid layout without template
        if (args.rows or args.columns) and not args.template and not args.cell_types:
             parser.error("--template is required when using --rows or --columns")
        
        handle_cli_generation(args)
        sys.exit(0)

    else:
        # 4. No generation command given (should be caught above, but as a fallback)
        parser.error("No generation command specified. Use --template, --title, --cell_types, or --layout.")

if __name__ == '__main__':
    main()
