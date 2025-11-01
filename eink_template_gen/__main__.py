#!/usr/bin/env python3
"""
Supernote Template Generator - CLI Entry Point
"""
import sys
import argparse
from eink_template_gen.templates import TEMPLATE_REGISTRY
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
    handle_set_default_margin
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

  # Generate a complex, ratio-based layout from a JSON file (NEW)
  python cli.py --layout my_cornell_layout.json

  # Set default device and margin
  python cli.py --set-default-device manta
  python cli.py --set-default-margin 8.5
        """
    )
    
    # --- Get config defaults BEFORE parsing ---
    global_default_margin = get_default_margin()

    # --- Utility/Management Commands ---
    parser.add_argument('--show-spacing-info',
                        type=str,
                        metavar='SPACING',
                        help='Show detailed spacing analysis (e.g., "6mm" or "71px")')
    
    parser.add_argument('--set-default-device',
                       choices=list_devices(),
                       help='Set the default device for future runs')
    
    parser.add_argument('--set-default-margin',
                       type=float,
                       metavar='MM',
                       help='Set the default margin in mm for future runs')
    
    parser.add_argument('--list-devices',
                       action='store_true',
                       help='List all available devices and exit')
    
    parser.add_argument('--list-templates',
                       action='store_true',
                       help='List all available templates and exit')
    
    # --- Device Selection ---
    parser.add_argument('--device',
                       choices=list_devices(), # <-- This will now include 'nomad'
                       help='Target device (overrides default or JSON value)')
    
    # --- TEMPLATE SELECTION ---
    template_group = parser.add_mutually_exclusive_group()
    template_group.add_argument('--template',
                       choices=list(TEMPLATE_REGISTRY.keys()),
                       help='Template type (for single or uniform-grid layouts)')
    
    template_group.add_argument('--cell_types',
                       type=str,
                       help='Comma-separated list of template types for a grid, from left-to-right, '
                            'top-to-bottom. Requires --rows and --columns. '
                            'Example: --cell_types lined,dotgrid,grid,manuscript')
    
    template_group.add_argument('--layout',
                       type=str,
                       help='Path to a JSON layout configuration file for complex, ratio-based templates.')
    
    # --- GLOBAL TEMPLATE CONFIGURATION ---
    parser.add_argument('--spacing',
                        type=str,
                        default='6',
                        help='Global spacing for lines/dots (for --template or --cell_types). '
                             'Use "6mm", "71px", or "6". Default: 6mm')

    parser.add_argument('--no-auto-adjust',
                        action='store_true',
                        help='Disable automatic spacing adjustment (only affects mm mode)')
    
    parser.add_argument('--margin',
                       type=float,
                       default=None, # <-- Set default to None
                       help=f'Margin in mm. Overrides device-specific default. '
                            f'(Global fallback is {global_default_margin}mm)')
    
    # --- Styling Kwargs ---
    parser.add_argument('--line_width_px',
                       type=float,
                       default=0.5,
                       help='Line width in pixels (default: 0.5)')
    
    parser.add_argument('--dot_radius_px',
                       type=float,
                       default=1.5,
                       help='Dot radius in pixels (default: 1.5)')
    
    # --- Separator Kwargs ---
    valid_sep_styles = [s for s in SEPARATOR_STYLES if s is not None]
    parser.add_argument('--header-sep',
                       choices=valid_sep_styles,
                       help=f'Header separator style (options: {", ".join(valid_sep_styles)})')
    
    parser.add_argument('--footer-sep',
                       choices=valid_sep_styles,
                       help=f'Footer separator style (options: {", ".join(valid_sep_styles)})')

    # --- File Output Kwargs ---
    parser.add_argument('--output-dir',
                       default='out',
                       help='Output directory (default: out)')
    
    parser.add_argument('--filename',
                       help='Custom filename (default: auto-generated)')

    # --- Layout Kwargs (Grid/Column/Hybrid) ---
    parser.add_argument('--orientation',
                       choices=['horizontal', 'vertical'],
                       default='horizontal',
                       help='Orientation of ruling lines: horizontal (default) or vertical (rotated 90°)')

    parser.add_argument('--columns',
                       type=int,
                       help='Number of columns (for --template or --cell_types)')

    parser.add_argument('--rows',
                       type=int,
                       help='Number of rows (for --template or --cell_types)')

    parser.add_argument('--section-gap-cols',
                       type=float,
                       help='Gap between columns in mm (defaults to same as --spacing)')

    parser.add_argument('--section-gap-rows',
                       type=float,
                       help='Gap between rows in mm (defaults to same as --spacing)')

    parser.add_argument('--split-ratio',
                       type=float,
                       default=0.6,
                       help='Split ratio for hybrid templates (default: 0.6)')
    
    parser.add_argument('--section_gap_mm',
                       type=float,
                       help='Gap between sections in hybrid templates in mm (defaults to same as --spacing)')

    # --- Template-Specific Kwargs ---
    parser.add_argument('--major_every',
                       type=int,
                       help='Make every Nth line thicker (graph paper style)')
    
    parser.add_argument('--major_width_add_px',
                       type=float,
                       default=1.5,
                       help='Added width for major line thickness (default: 1.5)')

    parser.add_argument('--crosshair_size',
                       type=int,
                       default=4,
                       help='Size of cross-hair extensions at major intersections in pixels (default: 3)')
    
    parser.add_argument('--no_crosshairs',
                       action='store_true',
                       help='Disable cross-hairs at major intersections')

    parser.add_argument('--midline_style',
                       choices=['dashed', 'dotted'],
                       default='dashed',
                       help='Style for manuscript midline (default: dashed)')
    
    parser.add_argument('--ascender_opacity',
                       type=float,
                       default=0.3,
                       help='Opacity for manuscript ascender line (default: 0.3)')
                       
    parser.add_argument('--staff_gap_mm',
                       type=float,
                       default=10,
                       help='Gap between music staves in mm (default: 10)')

    # Add this with the other styling kwargs (around line 85)
    parser.add_argument('--force-major-alignment',
                        action='store_true',
                        help='Force grid to end on major lines by adjusting margins (requires --major_every)')
    
    args = parser.parse_args()
    
    # --- Argument Routing logic ---
    
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
    
    if args.layout:
        # 1. New JSON Layout Mode
        handle_json_generation(
            args.layout, 
            args.device, 
            args.no_auto_adjust, 
            args.force_major_alignment
        )
        sys.exit(0)

    elif args.template or args.cell_types:
        # 2. Existing CLI Generation Mode
        if args.cell_types and (not args.rows or not args.columns):
            parser.error("--rows and --columns are required when using --cell_types")
        
        # 3. Check for grid layout without template
        if (args.rows or args.columns) and not args.template and not args.cell_types:
             parser.error("--template is required when using --rows or --columns")
        
        handle_cli_generation(args) # Pass all other args
        sys.exit(0)

    else:
        # 4. No generation command given
        parser.error("No generation command specified. Use --template, --cell_types, or --layout.")

if __name__ == '__main__':
    main()
