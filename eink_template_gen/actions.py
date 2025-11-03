# In template_gen/actions.py

import os
import inspect
import json
from pathlib import Path
from .templates import (
    TEMPLATE_REGISTRY, 
    create_column_template, 
    create_cell_grid_template,
    create_json_layout_template
)
from .devices import get_device, list_devices
from .config import set_default_device, get_default_device, set_default_margin, get_default_margin # <-- FIXED IMPORT
from .utils import (
    generate_filename, 
    parse_spacing, 
    format_spacing_summary, 
    print_spacing_info
)
from .titles import TITLE_REGISTRY

# --- Action 1: Utility Commands ---

def handle_list_devices():
    print("Available devices:")
    default_device = get_default_device()
    for device_id in list_devices():
        config = get_device(device_id)
        marker = " (DEFAULT)" if device_id == default_device else ""
        print(f"  {device_id:10s} - {config['name']} ({config['width']}×{config['height']}px @ {config['dpi']}dpi){marker}")

def handle_set_default_device(device_id):
    if set_default_device(device_id):
        device_config = get_device(device_id)
        print(f"✓ Default device set to: {device_config['name']}")
        print(f"  You can now run commands without --device flag")
    else:
        print("✗ Failed to set default device")

def handle_set_default_margin(margin_mm):
    if set_default_margin(margin_mm):
        print(f"✓ Default margin set to: {margin_mm}mm")
    else:
        print("✗ Failed to set default margin")

def handle_list_templates():
    print("Available templates:")
    for template_name in TEMPLATE_REGISTRY.keys():
        print(f"  {template_name}")

def handle_show_spacing_info(device_id_arg, spacing_str):
    device_id = device_id_arg
    if not device_id:
        device_id = get_default_device()
        if not device_id:
            print("Error: No device specified and no default device set. Use --device DEVICE")
            return
    
    try:
        device_config = get_device(device_id)
    except ValueError as e:
        print(f"Error: {e}")
        return
        
    print_spacing_info(spacing_str, device_config['dpi'], device_config['name'])

# --- Action 2: NEW JSON Layout Generation ---

def handle_json_generation(layout_file_path, cli_device_override, cli_no_auto_adjust, cli_force_major_alignment):
    """
    Handles generation from a JSON layout file.
    """
    print(f"Loading layout from: {layout_file_path}")
    
    # 1. Read and Parse JSON
    try:
        with open(layout_file_path, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"Error: Layout file not found at '{layout_file_path}'")
        return
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in layout file. {e}")
        return
    except Exception as e:
        print(f"Error reading file: {e}")
        return
        
    # 2. Validate and Get Device
    try:
        # --device flag overrides device in JSON
        if cli_device_override:
            config['device'] = cli_device_override
            print(f"Note: Using device from --device flag: {cli_device_override}")

        if 'device' not in config:
            # --- FALLBACK: Check for default device ---
            default_dev = get_default_device()
            if default_dev:
                config['device'] = default_dev
                print(f"Note: Using default device: {default_dev}")
            else:
                print("Error: JSON config must specify a 'device' (or set a default).")
                return
            
        device_config = get_device(config['device'])
    except ValueError as e:
        print(f"Error: {e}")
        return

    # 3. Determine Margin
    if 'margin_mm' in config:
        # 1. Use margin from JSON file if specified
        margin_mm_to_use = config['margin_mm']
        margin_source = f"JSON file ({margin_mm_to_use}mm)"
    elif 'default_margin_mm' in device_config:
        # 2. Use device-specific margin
        margin_mm_to_use = device_config['default_margin_mm']
        margin_source = f"{device_config['name']} default ({margin_mm_to_use}mm)"
    else:
        # 3. Use global config margin
        margin_mm_to_use = get_default_margin()
        margin_source = f"global default ({margin_mm_to_use}mm)"

    # 4a. Auto-Adjust
    #    Priority: CLI -> JSON -> Default (True)
    json_auto_adjust = config.get('auto_adjust_spacing', True)
    
    if cli_no_auto_adjust:
        final_auto_adjust = False # CLI flag wins
        print("Note: Using --no-auto-adjust from CLI flag.")
    else:
        final_auto_adjust = json_auto_adjust # Use JSON value (or its default)
        if not final_auto_adjust:
            print("Note: Using 'auto_adjust_spacing: false' from JSON.")

    # 4b. Force Major Alignment
    #    Priority: CLI -> JSON -> Default (False)
    json_force_align = config.get('force_major_alignment', False)
    
    if cli_force_major_alignment:
        final_force_align = True # CLI flag wins
        print("Note: Using --force-major-alignment from CLI flag.")
    else:
        final_force_align = json_force_align # Use JSON value (or its default)
        if final_force_align:
            print("Note: Using 'force_major_alignment: true' from JSON.")
        
    # 5. Call the Generator
    try:
        surface = create_json_layout_template(config, device_config, margin_mm_to_use, final_auto_adjust, final_force_align) # <-- Pass margin in
    except Exception as e:
        print(f"\n--- ERROR DURING TEMPLATE GENERATION ---")
        print(f"{e}")
        import traceback
        traceback.print_exc()
        return

    # 5. Save File
    output_dir = config.get('output_dir', 'out')
    
    # Default filename is based on the JSON filename
    default_filename = Path(layout_file_path).stem + ".png"
    filename = config.get('output_filename', default_filename)
    
    device_dir = os.path.join(output_dir, config['device'])
    os.makedirs(device_dir, exist_ok=True)
    
    filepath = os.path.join(device_dir, filename)
    surface.write_to_png(filepath)
    
    # 6. Print Summary
    print(f"\n✓ Template written to {filepath}")
    print(f"  - Layout: {layout_file_path}")
    print(f"  - Device: {device_config['name']} ({device_config['width']}×{device_config['height']}px @ {device_config['dpi']}dpi)")
    print(f"  - Margin: {margin_source}")
    print(f"  - Master Spacing: {config.get('master_spacing_mm', 'N/A')}mm")


# --- Action 3: Existing CLI-based Generation ---

def handle_cli_generation(args):
    """
    This is the main application logic, moved from cli.py
    """
    
    # --- 1. Device Setup ---
    device_id = args.device
    if not device_id:
        device_id = get_default_device()
        if not device_id:
            print("Error: No device specified and no default device set. Use --device DEVICE or --set-default-device DEVICE")
            return

    try:
        device_config = get_device(device_id)
    except ValueError as e:
        print(f"Error: {e}")
        return

    # --- 2. MODE DETECTION: Line Count vs Spacing Mode ---
    using_line_count_mode = hasattr(args, 'lines') and args.lines is not None
    
    if using_line_count_mode:
        # ============================================
        # LINE COUNT MODE
        # ============================================
        from .utils import (
            parse_line_count_spec, 
            calculate_spacing_from_line_count,
            calculate_spacing_from_line_count_with_margins
        )
        
        try:
            h_lines, v_lines = parse_line_count_spec(args.lines)
        except ValueError as e:
            print(f"Error: {e}")
            return
        
        # --- Determine margin to use ---
        # Priority: CLI --margin flag > default to 0 for line count mode
        if args.margin is not None:
            # User explicitly specified a margin
            margin_mm_to_use = args.margin
            use_margins = margin_mm_to_use > 0
            if use_margins:
                print(f"Using specified margin: {margin_mm_to_use}mm")
            else:
                print(f"Using specified margin: 0mm (full page)")
        else:
            # Default to 0 margins for line count mode
            margin_mm_to_use = 0
            use_margins = False
            print(f"Using margin: 0mm (full page) - specify --margin to use margins with --lines")
        
        mm2px = device_config['dpi'] / 25.4
        margin_px = round(margin_mm_to_use * mm2px)
        
        # Calculate spacing based on whether margins are used
        enforce_exact = getattr(args, 'enforce_exact_spacing', False)
        
        if use_margins:
            # Calculate spacing with margins
            h_spacing_px, h_is_fractional, content_height = calculate_spacing_from_line_count_with_margins(
                device_config['height'], h_lines, margin_px, enforce_exact=enforce_exact
            )
            
            if v_lines:
                v_spacing_px, v_is_fractional, content_width = calculate_spacing_from_line_count_with_margins(
                    device_config['width'], v_lines, margin_px, enforce_exact=enforce_exact
                )
                is_fractional = h_is_fractional or v_is_fractional
            else:
                v_spacing_px = None
                content_width = None
                is_fractional = h_is_fractional
        else:
            # Calculate spacing without margins (full page)
            content_height = device_config['height']
            content_width = device_config['width']
            
            h_spacing_px, h_is_fractional = calculate_spacing_from_line_count(
                content_height, h_lines, enforce_exact=enforce_exact
            )
            
            if v_lines:
                v_spacing_px, v_is_fractional = calculate_spacing_from_line_count(
                    content_width, v_lines, enforce_exact=enforce_exact
                )
                is_fractional = h_is_fractional or v_is_fractional
            else:
                v_spacing_px = None
                is_fractional = h_is_fractional
        
        # Set spacing values
        spacing_px = h_spacing_px
        spacing_mm_to_use = h_spacing_px / mm2px
        
        # Set flags for summary
        spacing_mode = 'px'
        was_adjusted = False
        original_mm = spacing_mm_to_use
        adjusted_mm = spacing_mm_to_use
        
        # Print line count mode summary
        print(f"LINE COUNT MODE: Fitting exactly {h_lines} lines" + 
              (f" × {v_lines} columns" if v_lines else ""))
        if use_margins:
            print(f"  Content area: {content_height}px" + 
                  (f" × {content_width}px" if v_lines else "") + 
                  f" (after {margin_mm_to_use}mm margins)")
        print(f"  Calculated spacing: {h_spacing_px:.3f}px" +
              (f" × {v_spacing_px:.3f}px" if v_lines else ""))
        if is_fractional:
            if enforce_exact:
                print(f"  ⚠️  Using fractional spacing (may cause slight rendering blur)")
            else:
                print(f"  ℹ️  Rounded to nearest pixel (add --enforce-exact-spacing for fractional)")
        
    else:
        # ============================================
        # NORMAL SPACING MODE
        # ============================================
        
        # --- 2a. Margin Setup ---
        if args.margin is not None:
            margin_mm_to_use = args.margin
            print(f"Using specified margin: {margin_mm_to_use}mm")
        elif 'default_margin_mm' in device_config:
            margin_mm_to_use = device_config['default_margin_mm']
            print(f"Using default margin for {device_config['name']}: {margin_mm_to_use}mm")
        else:
            margin_mm_to_use = get_default_margin()
            print(f"Using global default margin: {margin_mm_to_use}mm")

        # --- 2b. Spacing Setup ---
        spacing_px, original_mm, adjusted_mm, was_adjusted, spacing_mode = parse_spacing(
            args.spacing,
            device_config['dpi'],
            auto_adjust=not args.no_auto_adjust
        )
        
        if was_adjusted and spacing_mode == 'mm':
            print(f"Note: Adjusted spacing from {original_mm}mm to {adjusted_mm:.3f}mm ({int(spacing_px)}px) for pixel-perfect alignment")
        elif spacing_mode == 'px':
            print(f"Using exact pixel spacing: {int(spacing_px)}px (≈{original_mm:.2f}mm)")
        
        spacing_mm_to_use = adjusted_mm
        
        # Initialize these for normal mode (not used but avoids undefined variable errors)
        h_lines = None
        v_lines = None
        h_spacing_px = spacing_px
        v_spacing_px = None
        is_fractional = False

    # --- 3. Gather Shared Kwargs ---
    cli_args = vars(args)
    template_kwargs = {}
    
    base_kwargs = {
        'width': device_config['width'],
        'height': device_config['height'],
        'dpi': device_config['dpi'],
        'spacing_mm': spacing_mm_to_use,
        'margin_mm': margin_mm_to_use,
        'auto_adjust_spacing': False if using_line_count_mode else not args.no_auto_adjust,
        'header_separator': args.header_sep,
        'footer_separator': args.footer_sep,
        'force_major_alignment': args.force_major_alignment,
    }

    # --- 4. Generation Logic Branching ---
    num_columns = args.columns if args.columns else 1
    num_rows = args.rows if args.rows else 1
    is_grid_layout = num_columns > 1 or num_rows > 1
    
    if args.cell_types:
        print(f"Generating {num_rows}x{num_columns} multi-type grid for {device_config['name']}...")
        template_func = create_cell_grid_template
        
        cell_type_list = args.cell_types.split(',')
        
        if len(cell_type_list) != (num_columns * num_rows):
            print(f"Error: --cell_types list has {len(cell_type_list)} items, but grid is {num_rows}x{num_columns} ({num_rows*num_columns} items required)")
            return

        # Build kwargs for each cell type
        cell_definitions = []
        idx = 0
        for r in range(num_rows):
            row_defs = []
            for c in range(num_columns):
                cell_type = cell_type_list[idx].strip()
                if cell_type not in TEMPLATE_REGISTRY:
                    print(f"Error: Unknown template type in --cell_types: '{cell_type}'")
                    return
                
                # --- START OF BUG FIX 2 (Passing spacing) ---
                cell_kwargs = _build_template_kwargs(cell_type, args, spacing_mm_to_use)
                # --- END OF BUG FIX 2 ---
                row_defs.append({'type': cell_type, 'kwargs': cell_kwargs})
                idx += 1
            cell_definitions.append(row_defs)
        
        base_kwargs['cell_definitions'] = cell_definitions
        base_kwargs['column_gap_mm'] = args.section_gap_cols if args.section_gap_cols is not None else spacing_mm_to_use
        base_kwargs['row_gap_mm'] = args.section_gap_rows if args.section_gap_rows is not None else spacing_mm_to_use

    elif is_grid_layout:
        if not args.template:
             print("Error: --template is required when using --rows or --columns")
             return
             
        print(f"Generating {num_rows}x{num_columns} uniform {args.template} grid for {device_config['name']}...")
        template_func = create_column_template
        base_kwargs['num_columns'] = num_columns
        base_kwargs['num_rows'] = num_rows
        base_kwargs['column_gap_mm'] = args.section_gap_cols if args.section_gap_cols is not None else spacing_mm_to_use
        base_kwargs['row_gap_mm'] = args.section_gap_rows if args.section_gap_rows is not None else spacing_mm_to_use
        base_kwargs['base_template'] = args.template
        
        # --- START OF BUG FIX 2 (Passing spacing) ---
        template_kwargs = _build_template_kwargs(args.template, args, spacing_mm_to_use)
        # --- END OF BUG FIX 2 ---
        base_kwargs['template_kwargs'] = template_kwargs

    else:
        if not args.template:
             print("Error: --template is required for a single-page layout")
             return
             
        print(f"Generating single {args.template} template for {device_config['name']}...")
        template_func = TEMPLATE_REGISTRY[args.template]
        
        template_kwargs = _build_template_kwargs(args.template, args, spacing_mm_to_use)
        base_kwargs.update(template_kwargs)

    # --- 5. Generate Surface ---
    surface = template_func(**base_kwargs)
    
    # --- 6. Save File ---
    # Determine base directory
    base_device_dir = os.path.join(args.output_dir, device_id)
    
    # Add 'true-scale' subdirectory if auto-adjust is disabled
    if args.no_auto_adjust:
        device_dir = os.path.join(base_device_dir, 'true-scale')
        print("Note: Saving to 'true-scale' directory as --no-auto-adjust was specified.")
    else:
        device_dir = base_device_dir
    os.makedirs(device_dir, exist_ok=True)
    
    if args.filename:
        filename = args.filename if args.filename.endswith('.png') else f"{args.filename}.png"
    elif args.cell_types:
        spacing_str = f"{int(spacing_px)}px" if spacing_mode == 'px' else f"{original_mm}mm"
        filename = f"{num_rows}x{num_columns}_multi_grid_{spacing_str.replace('.', '_')}.png"
    else:
        # Use the existing, detailed auto-namer
        filename_kwargs = {}
        if is_grid_layout:
            if num_columns > 1: filename_kwargs['columns'] = num_columns
            if num_rows > 1: filename_kwargs['rows'] = num_rows
            if args.orientation == 'vertical': filename_kwargs['orientation'] = 'vertical'
        
        if args.template == 'hybrid_lined_dotgrid':
            filename_kwargs['split_ratio'] = f"{int(args.split_ratio * 100)}-{int((1 - args.split_ratio) * 100)}"
            filename_kwargs['orientation'] = 'vertical'
        
        filename_kwargs['spacing_mode'] = spacing_mode
        if args.header_sep: filename_kwargs['header_separator'] = args.header_sep
        if args.footer_sep: filename_kwargs['footer_separator'] = args.footer_sep
            
        if args.template in ['lined', 'grid','manuscript', 'french_ruled', 'music_staff', 'isometric', 'hexgrid']:
            filename_kwargs['line_width_px'] = args.line_width_px
        elif args.template == 'dotgrid':
            filename_kwargs['dot_radius_px'] = args.dot_radius_px
        elif args.template == 'hybrid_lined_dotgrid':
            filename_kwargs['line_width_px'] = args.line_width_px
            filename_kwargs['dot_radius_px'] = args.dot_radius_px
        
        filename_spacing_val = original_mm if spacing_mode == 'mm' else int(spacing_px)
        filename = generate_filename(args.template, filename_spacing_val, **filename_kwargs)
    
    filepath = os.path.join(device_dir, filename)
    surface.write_to_png(filepath)
    
    # --- 7. Print Summary ---
    if using_line_count_mode:
        # Line count mode summary
        from .utils import format_line_count_summary
        spacing_display = format_line_count_summary(
            h_lines, v_lines, h_spacing_px, v_spacing_px, is_fractional
        )
    else:
        # Normal mode summary
        spacing_display = format_spacing_summary(spacing_px, original_mm, adjusted_mm, was_adjusted, spacing_mode)
    
    print(f"✓ Template written to {filepath}")
    print(f"  - Device: {device_config['name']} ({device_config['width']}×{device_config['height']}px @ {device_config['dpi']}dpi)")
    if args.cell_types: print(f"  - Template: Multi-Type Grid")
    else: print(f"  - Template: {args.template}")
    print(f"  - Spacing: {spacing_display}")
    
    # Calculate mm2px and base_margin_px for both modes (needed for margin display)
    mm2px = device_config['dpi'] / 25.4
    base_margin_px = round(margin_mm_to_use * mm2px)
    
    # Show margin info
    if using_line_count_mode:
        # Line count mode margin display
        if margin_mm_to_use > 0:
            print(f"  - Margin: {margin_mm_to_use}mm (specified with --margin)")
        else:
            print(f"  - Margin: 0mm (full page fit)")
    else:
        # Normal mode margin display with adjustment info
        # Check if force_major_alignment was used
        if args.force_major_alignment and args.major_every and args.template in ['grid', 'dotgrid']:
            # Calculate the actual adjusted margins
            from .utils import calculate_major_aligned_margins, calculate_major_aligned_margins_x
            content_height = device_config['height'] - (2 * base_margin_px)
            content_width = device_config['width'] - (2 * base_margin_px)
        
            m_top, m_bottom, _ = calculate_major_aligned_margins(content_height, spacing_px, base_margin_px, args.major_every)
            m_left, m_right, _ = calculate_major_aligned_margins_x(content_width, spacing_px, base_margin_px, args.major_every)
        
            # Convert back to mm
            m_top_mm = m_top / mm2px
            m_bottom_mm = m_bottom / mm2px
            m_left_mm = m_left / mm2px
            m_right_mm = m_right / mm2px
        
            print(f"  - Margin: {margin_mm_to_use}mm (adjusted for major alignment: "
                  f"T:{m_top_mm:.2f}mm, B:{m_bottom_mm:.2f}mm, L:{m_left_mm:.2f}mm, R:{m_right_mm:.2f}mm)")
        elif not is_grid_layout and args.template not in ['hybrid_lined_dotgrid']:
            # For single templates, show the actual adjusted margins
            from .utils import calculate_adjusted_margins, calculate_adjusted_margins_x
            content_height = device_config['height'] - (2 * base_margin_px)
            content_width = device_config['width'] - (2 * base_margin_px)
        
            m_top, m_bottom = calculate_adjusted_margins(content_height, spacing_px, base_margin_px)
            m_left, m_right = calculate_adjusted_margins_x(content_width, spacing_px, base_margin_px)
        
            # Convert back to mm
            m_top_mm = m_top / mm2px
            m_bottom_mm = m_bottom / mm2px
            m_left_mm = m_left / mm2px
            m_right_mm = m_right / mm2px
        
            # Check if margins were adjusted
            margin_adjusted = (abs(m_top - base_margin_px) > 0.5 or 
                               abs(m_bottom - base_margin_px) > 0.5 or
                               abs(m_left - base_margin_px) > 0.5 or
                               abs(m_right - base_margin_px) > 0.5)
        
            if margin_adjusted:
                print(f"  - Margin: {margin_mm_to_use}mm (adjusted for pixel-perfect: "
                      f"T:{m_top_mm:.2f}mm, B:{m_bottom_mm:.2f}mm, L:{m_left_mm:.2f}mm, R:{m_right_mm:.2f}mm)")
            else:
                print(f"  - Margin: {margin_mm_to_use}mm")
        else:
            # For grid layouts or hybrid, just show base margin
            print(f"  - Margin: {margin_mm_to_use}mm")
    
    # Rest of summary (layout info, etc.)
    if is_grid_layout or args.cell_types:
        print(f"  - Layout: {num_columns} column(s) × {num_rows} row(s)")
        if args.orientation == 'vertical': print(f"  - Content orientation: vertical (rotated 90°)")
        
        if args.header_sep: print(f"  - Header separator: {args.header_sep}")
        if args.footer_sep: print(f"  - Footer separator: {args.footer_sep}")
    
        if args.template == 'hybrid_lined_dotgrid':
            section_gap = args.section_gap_mm if args.section_gap_mm is not None else spacing_mm_to_use
            print(f"  - Split: {int(args.split_ratio * 100)}% / {int((1 - args.split_ratio) * 100)}%")
            print(f"  - Section gap: {section_gap}mm")

def _build_template_kwargs(template_type, args, spacing_mm_default=None):
    """
    Build appropriate kwargs dict for a specific template type.
    Only includes parameters that are relevant to that template.
    
    Args:
        template_type: Type of template (e.g., 'lined', 'dotgrid')
        args: Parsed command-line arguments
        spacing_mm_default: The default spacing (in mm) to use as a fallback
        
    Returns:
        Dictionary of kwargs appropriate for the template type
    """
    kwargs = {}
    
    # Common parameters for most templates
    if template_type in ['lined', 'grid', 'manuscript', 'french_ruled', 'music_staff', 'isometric', 'hexgrid']:
        kwargs['line_width_px'] = args.line_width_px
    
    if template_type == 'dotgrid':
        kwargs['dot_radius_px'] = args.dot_radius_px
    
    if template_type == 'hybrid_lined_dotgrid':
        kwargs['line_width_px'] = args.line_width_px
        kwargs['dot_radius_px'] = args.dot_radius_px
        kwargs['split_ratio'] = args.split_ratio
        
        if args.section_gap_mm is not None:
            kwargs['section_gap_mm'] = args.section_gap_mm
        else:
            kwargs['section_gap_mm'] = spacing_mm_default
    
    # Grid-specific parameters
    if template_type in ['grid', 'dotgrid']:
        if args.major_every is not None:
            kwargs['major_every'] = args.major_every
            kwargs['major_width_add_px'] = args.major_width_add_px
        if template_type == 'grid':
            kwargs['crosshair_size'] = 0 if args.no_crosshairs else args.crosshair_size
    
    # Lined template with major lines
    if template_type == 'lined' and args.major_every is not None:
        kwargs['major_every'] = args.major_every
        kwargs['major_width_add_px'] = args.major_width_add_px
    
    # Manuscript-specific parameters
    if template_type == 'manuscript':
        kwargs['midline_style'] = args.midline_style
        kwargs['ascender_opacity'] = args.ascender_opacity
    
    # Music staff-specific parameters
    if template_type == 'music_staff':
        kwargs['staff_gap_mm'] = args.staff_gap_mm
    
    # French ruled-specific parameters  
    if template_type == 'french_ruled':
        # Add any french_ruled specific kwargs here
        pass
        
# --- Line Numbering Config ---
    if template_type == 'lined' and args.line_numbers:
        kwargs['line_number_config'] = {
            "side": args.line_numbers_side,
            "interval": args.line_numbers_interval_val,
            "margin_px": args.line_numbers_margin_px,
            "font_size": args.line_numbers_font_size,
            "grey": args.line_numbers_grey
        }
        
    # --- MODIFIED: Cell Labeling Config ---
    if template_type == 'grid' and args.cell_labels:
        kwargs['cell_label_config'] = {
            "y_axis_side": args.cell_labels_y_side,
            "y_axis_padding_px": args.cell_labels_y_padding_px, # Renamed
            "x_axis_side": args.cell_labels_x_side,
            "x_axis_padding_px": args.cell_labels_x_padding_px, # Renamed
            "font_size": args.cell_labels_font_size,
            "grey": args.cell_labels_grey
        }
        
    # --- MODIFIED: Axis Labeling Config ---
    if template_type == 'grid' and args.axis_labels:
        kwargs['axis_label_config'] = {
            "origin": args.axis_labels_origin,
            "interval": args.axis_labels_interval,
            "y_axis_side": args.axis_labels_y_side,
            "y_axis_padding_px": args.axis_labels_y_padding_px, # Renamed
            "x_axis_side": args.axis_labels_x_side,
            "x_axis_padding_px": args.axis_labels_x_padding_px, # Renamed
            "font_size": args.axis_labels_font_size,
            "grey": args.axis_labels_grey
        }
    
    return kwargs

# Modify handle_list_templates function:
def handle_list_templates():
    print("Available templates:")
    for template_name in TEMPLATE_REGISTRY.keys():
        print(f"  {template_name}")
    
    print("\nAvailable title patterns:")
    for title_name in TITLE_REGISTRY.keys():
        print(f"  {title_name}")

# Add new function for title generation:
def handle_title_generation(args):
    """
    Handle generation of title page patterns
    """
    
    # --- 1. Device Setup ---
    device_id = args.device
    if not device_id:
        device_id = get_default_device()
        if not device_id:
            print("Error: No device specified and no default device set. Use --device DEVICE or --set-default-device DEVICE")
            return

    try:
        device_config = get_device(device_id)
    except ValueError as e:
        print(f"Error: {e}")
        return

    # --- 2a. Margin Setup ---
    if args.margin is not None:
        margin_mm_to_use = args.margin
        print(f"Using specified margin: {margin_mm_to_use}mm")
    elif 'default_margin_mm' in device_config:
        margin_mm_to_use = device_config['default_margin_mm']
        print(f"Using default margin for {device_config['name']}: {margin_mm_to_use}mm")
    else:
        margin_mm_to_use = get_default_margin()
        print(f"Using global default margin: {margin_mm_to_use}mm")

    # --- 2b. Spacing Setup ---
    spacing_px, original_mm, adjusted_mm, was_adjusted, spacing_mode = parse_spacing(
        args.spacing,
        device_config['dpi'],
        auto_adjust=not args.no_auto_adjust
    )
    
    if was_adjusted and spacing_mode == 'mm':
        print(f"Note: Adjusted spacing from {original_mm}mm to {adjusted_mm:.3f}mm ({int(spacing_px)}px) for pixel-perfect alignment")
    elif spacing_mode == 'px':
        print(f"Using exact pixel spacing: {int(spacing_px)}px (≈{original_mm:.2f}mm)")
    
    spacing_mm_to_use = adjusted_mm

    # --- 3. Gather Title-Specific Kwargs ---
    title_kwargs = {
        'width': device_config['width'],
        'height': device_config['height'],
        'dpi': device_config['dpi'],
        'spacing_mm': spacing_mm_to_use,
        'margin_mm': margin_mm_to_use,
        'line_width_px': args.line_width_px,
        'auto_adjust_spacing': not args.no_auto_adjust,
        'header_separator': args.header_sep,
        'footer_separator': args.footer_sep,
    }
    
    # Add title-specific parameters
    if args.title in ['truchet', 'diagonal_truchet', 'hexagonal_truchet', 'ten_print']:
        if hasattr(args, 'truchet_seed') and args.truchet_seed is not None:
            title_kwargs['rotation_seed'] = args.truchet_seed
        
        if args.title == 'truchet':
            if hasattr(args, 'truchet_fill_grey') and args.truchet_fill_grey is not None:
                title_kwargs['truchet_fill_grey'] = args.truchet_fill_grey
        
        elif args.title == 'diagonal_truchet':
            if hasattr(args, 'diag_fill_grey1'):
                title_kwargs['diagonal_fill_grey_1'] = args.diag_fill_grey1
            if hasattr(args, 'diag_fill_grey2'):
                title_kwargs['diagonal_fill_grey_2'] = args.diag_fill_grey2

    if hasattr(args, 'decorative_border') and args.decorative_border is not None:
        title_kwargs['decorative_border'] = args.decorative_border

    elif args.title in ['hilbert_curve', 'dragon_curve']:
        # Pass L-System params
        if hasattr(args, 'lsystem_iterations'):
            title_kwargs['lsystem_iterations'] = args.lsystem_iterations
        # if hasattr(args, 'lsystem_step_px'):
        #     title_kwargs['lsystem_step_px'] = args.lsystem_step_px

    elif args.title in ['contour_lines', 'noise_field']:
        # Common noise parameters
        if hasattr(args, 'noise_scale') and args.noise_scale is not None:
            title_kwargs['noise_scale'] = args.noise_scale
        
        if hasattr(args, 'noise_octaves') and args.noise_octaves is not None:
            title_kwargs['octaves'] = args.noise_octaves
        
        if hasattr(args, 'noise_seed') and args.noise_seed is not None:
            if args.title == 'contour_lines':
                title_kwargs['contour_seed'] = args.noise_seed
            else:  # noise_field
                title_kwargs['noise_seed'] = args.noise_seed
        
        if hasattr(args, 'noise_style') and args.noise_style is not None:
            if args.title == 'contour_lines':
                title_kwargs['contour_style'] = args.noise_style
            else:  # noise_field
                title_kwargs['noise_style'] = args.noise_style
        
        # Contour-specific parameters
        if args.title == 'contour_lines':
            if hasattr(args, 'contour_interval') and args.contour_interval is not None:
                title_kwargs['contour_interval'] = args.contour_interval
        
        # Noise field-specific parameters
        if args.title == 'noise_field':
            if hasattr(args, 'greyscale_levels') and args.greyscale_levels is not None:
                title_kwargs['greyscale_levels'] = args.greyscale_levels
    
    # Build title_config - always create it for the frame
    # Text is optional (user might want to handwrite it)
    title_config = {
        'show_frame': not getattr(args, 'title_no_frame', False),
        'frame_shape': getattr(args, 'title_frame_shape', 'rounded-rectangle'),
        'border_style': getattr(args, 'title_border_style', 'solid'),
        'border_width': getattr(args, 'title_border_width', 2.0),
        'border_grey': getattr(args, 'title_border_grey', 0),
        'fill_grey': getattr(args, 'title_fill_grey', 15),
        'corner_radius': getattr(args, 'title_corner_radius', 10),
        'font_family': getattr(args, 'title_font_family', 'Serif'),
        'font_size': getattr(args, 'title_font_size', 48),
        'font_weight': getattr(args, 'title_font_weight', 'bold'),
        'font_slant': getattr(args, 'title_font_slant', 'normal'),
        'text_grey': getattr(args, 'title_text_grey', 0),
        'letter_spacing': getattr(args, 'title_letter_spacing', 0),
        'h_align': getattr(args, 'title_h_align', 'center'),
        'v_align': getattr(args, 'title_v_align', 'top'),
    }
    
    # Add text only if provided and non-empty
    if hasattr(args, 'title_text') and args.title_text and args.title_text.strip():
        title_config['text'] = args.title_text
    
    # Optional positioning
    if hasattr(args, 'title_x_center') and args.title_x_center is not None:
        title_config['x_center'] = args.title_x_center
    if hasattr(args, 'title_y_center') and args.title_y_center is not None:
        title_config['y_center'] = args.title_y_center
    if hasattr(args, 'title_frame_width') and args.title_frame_width is not None:
        title_config['frame_width'] = args.title_frame_width
    if hasattr(args, 'title_frame_height') and args.title_frame_height is not None:
        title_config['frame_height'] = args.title_frame_height
    
    title_kwargs['title_config'] = title_config

    # --- 4. Generate Surface ---
    print(f"Generating '{args.title}' title page for {device_config['name']}...")
    
    if args.title not in TITLE_REGISTRY:
        print(f"Error: Unknown title pattern '{args.title}'")
        return
        
    title_func = TITLE_REGISTRY[args.title]
    surface = title_func(**title_kwargs)
    
    # --- 5. Save File ---
    base_device_dir = os.path.join(args.output_dir, device_id)
    
    # Add 'true-scale' subdirectory if auto-adjust is disabled
    if args.no_auto_adjust:
        device_dir = os.path.join(base_device_dir, 'true-scale')
        print("Note: Saving to 'true-scale' directory as --no-auto-adjust was specified.")
    else:
        device_dir = base_device_dir
    os.makedirs(device_dir, exist_ok=True)
    
    if args.filename:
        filename = args.filename if args.filename.endswith('.png') else f"{args.filename}.png"
    else:
        # Auto-generate filename
        spacing_str = f"{int(spacing_px)}px" if spacing_mode == 'px' else f"{original_mm}mm"
        filename = f"title_{args.title}_{spacing_str.replace('.', '_')}"
        
        # Add seed to filename if specified
        if args.title == 'truchet' and hasattr(args, 'truchet_seed') and args.truchet_seed is not None:
            filename += f"_seed{args.truchet_seed}"
        
        if args.header_sep:
            filename += f"_h-{args.header_sep}"
        if args.footer_sep:
            filename += f"_f-{args.footer_sep}"
            
        filename += ".png"
    
    filepath = os.path.join(device_dir, filename)
    surface.write_to_png(filepath)
    
    # --- 6. Print Summary ---
    spacing_display = format_spacing_summary(spacing_px, original_mm, adjusted_mm, was_adjusted, spacing_mode)
    print(f"✓ Title page written to {filepath}")
    print(f"  - Device: {device_config['name']} ({device_config['width']}×{device_config['height']}px @ {device_config['dpi']}dpi)")
    print(f"  - Pattern: {args.title}")
    print(f"  - Tile Size: {spacing_display}")
    print(f"  - Margin: {margin_mm_to_use}mm")
    
    if args.title == 'truchet' and hasattr(args, 'truchet_seed') and args.truchet_seed is not None:
        print(f"  - Seed: {args.truchet_seed} (reproducible)")

    if args.title == 'truchet':
        if hasattr(args, 'truchet_variant'):
            print(f"  - Variant: {args.truchet_variant}")
    
    # Add border info for all patterns
    if hasattr(args, 'decorative_border') and args.decorative_border:
        print(f"  - Border: {args.decorative_border}")

    if args.title in ['contour_lines', 'noise_field']:
        print(f"  - Noise scale: {title_kwargs.get('noise_scale', 0.02)}")
        print(f"  - Octaves: {title_kwargs.get('octaves', 4)}")
        print(f"  - Style: {title_kwargs.get('contour_style' if args.title == 'contour_lines' else 'noise_style', 'smooth')}")
        
        if args.title == 'contour_lines':
            print(f"  - Contour interval: {title_kwargs.get('contour_interval', 0.1)}")
        
        if args.title == 'noise_field':
            print(f"  - Greyscale levels: {title_kwargs.get('greyscale_levels', 16)}")
        
        if hasattr(args, 'noise_seed') and args.noise_seed is not None:
            print(f"  - Seed: {args.noise_seed} (reproducible)")
