# In eink_template_gen/actions.py

import json
import os
from pathlib import Path

from .config import get_default_device, get_default_margin, set_default_device, set_default_margin
from .covers import COVER_REGISTRY
from .devices import get_device, list_devices
from .templates import (
    TEMPLATE_REGISTRY,
    create_cell_grid_template,
    create_column_template,
    create_json_layout_template,
    create_template_surface,
)
from .utils import (
    calculate_adjusted_margins,
    calculate_adjusted_margins_x,
    calculate_major_aligned_margins,
    calculate_major_aligned_margins_x,
    calculate_spacing_from_line_count,
    calculate_spacing_from_line_count_with_margins,
    format_line_count_summary,
    format_spacing_summary,
    generate_filename,
    parse_line_count_spec,
    parse_spacing,
    print_spacing_info,
)

# --- Generation Helper: 1. Setup ---


def _setup_generation_context(args):
    """
    Handles all common setup for a generation command:
    1. Gets Device
    2. Gets Margin
    3. Handles "Line Count Mode" vs "Spacing Mode"

    Returns a 'context' dictionary with all calculated values.
    """
    context = {}
    # cli_args = vars(args)

    # 1. Device Setup
    device_id = args.device
    if not device_id:
        device_id = get_default_device()
        if not device_id:
            raise ValueError(
                "No device specified and no default device set. Use --device DEVICE or set a default."
            )

    device_config = get_device(device_id)
    context["device_config"] = device_config
    context["device_id"] = device_id
    mm2px = device_config["dpi"] / 25.4

    # 2. Mode Detection: Line Count vs Spacing
    context["using_line_count_mode"] = hasattr(args, "lines") and args.lines is not None

    if context["using_line_count_mode"]:
        # ============================================
        # LINE COUNT MODE
        # ============================================
        try:
            h_lines, v_lines = parse_line_count_spec(args.lines)
        except ValueError as e:
            raise e

        context["h_lines"] = h_lines
        context["v_lines"] = v_lines

        # Determine margin to use
        if args.margin is not None:
            margin_mm = args.margin
            use_margins = margin_mm > 0
            margin_source = f"specified {margin_mm}mm"
        else:
            margin_mm = 0
            use_margins = False
            margin_source = "0mm (default for line count mode)"

        context["margin_mm"] = margin_mm
        margin_px = round(margin_mm * mm2px)

        enforce_exact = getattr(args, "enforce_margins", False)

        v_spacing_px = None
        v_is_fractional = False

        if use_margins:
            h_spacing_px, h_is_fractional, content_height = (
                calculate_spacing_from_line_count_with_margins(
                    device_config["height"], h_lines, margin_px, enforce_exact=enforce_exact
                )
            )
            if v_lines:
                v_spacing_px, v_is_fractional, content_width = (
                    calculate_spacing_from_line_count_with_margins(
                        device_config["width"], v_lines, margin_px, enforce_exact=enforce_exact
                    )
                )
        else:
            content_height = device_config["height"]
            content_width = device_config["width"]
            h_spacing_px, h_is_fractional = calculate_spacing_from_line_count(
                content_height, h_lines, enforce_exact=enforce_exact
            )
            if v_lines:
                v_spacing_px, v_is_fractional = calculate_spacing_from_line_count(
                    content_width, v_lines, enforce_exact=enforce_exact
                )

        context["is_fractional"] = h_is_fractional or (v_lines and v_is_fractional)
        context["h_spacing_px"] = h_spacing_px
        context["v_spacing_px"] = v_spacing_px

        # Store the primary spacing in the generic 'spacing_px' key
        context["spacing_px"] = h_spacing_px

        # The "spacing_str" for the factory is the *exact pixel value*
        context["spacing_str"] = f"{h_spacing_px}px"
        # Store original mm for summary
        context["original_mm"] = h_spacing_px / mm2px
        context["spacing_mode"] = "px"
        context["was_adjusted"] = False

        # This key is needed by handle_multi_template_generation
        context["spacing_mm_to_use"] = context["original_mm"]

        print(f"LINE COUNT MODE: Fitting {args.lines} lines with {margin_source} margin.")

    else:
        # ============================================
        # NORMAL SPACING MODE
        # ============================================
        if args.margin is not None:
            margin_mm = args.margin
            print(f"Using specified margin: {margin_mm}mm")
        elif "default_margin_mm" in device_config:
            margin_mm = device_config["default_margin_mm"]
            print(f"Using default margin for {device_config['name']}: {margin_mm}mm")
        else:
            margin_mm = get_default_margin()
            print(f"Using global default margin: {margin_mm}mm")

        context["margin_mm"] = margin_mm

        # Spacing setup
        spacing_px, original_mm, adjusted_mm, was_adjusted, spacing_mode = parse_spacing(
            args.spacing, device_config["dpi"], auto_adjust=not args.true_scale
        )

        context["spacing_str"] = args.spacing
        context["spacing_px"] = spacing_px
        context["original_mm"] = original_mm
        context["adjusted_mm"] = adjusted_mm
        context["was_adjusted"] = was_adjusted
        context["spacing_mode"] = spacing_mode
        context["spacing_mm_to_use"] = adjusted_mm

    return context


def _build_template_kwargs(template_type, args):
    """
    Builds the template-specific kwargs dict from the full args.
    """
    kwargs = {}
    cli_args = vars(args)

    # Common
    if cli_args.get("line_width_px") is not None:
        kwargs["line_width_px"] = cli_args["line_width_px"]
    if cli_args.get("dot_radius_px") is not None:
        kwargs["dot_radius_px"] = cli_args["dot_radius_px"]
    if cli_args.get("enforce_margins"):
        kwargs["enforce_margins"] = True

    # Grid/Lined features
    if cli_args.get("major_every") is not None:
        kwargs["major_every"] = cli_args["major_every"]

        # Only add major_width_add_px if it's actually defined for this command
        if "major_width_add_px" in cli_args:
            kwargs["major_width_add_px"] = cli_args["major_width_add_px"]

    # Grid features
    if cli_args.get("crosshair_size") is not None:
        kwargs["crosshair_size"] = cli_args["crosshair_size"]
    if cli_args.get("no_crosshairs") is not None:
        kwargs["no_crosshairs"] = cli_args["no_crosshairs"]

    # Manuscript
    if cli_args.get("midline_style") is not None:
        kwargs["midline_style"] = cli_args["midline_style"]
    if cli_args.get("ascender_opacity") is not None:
        kwargs["ascender_opacity"] = cli_args["ascender_opacity"]

    # Music
    if cli_args.get("staff_gap_mm") is not None:
        kwargs["staff_gap_mm"] = cli_args["staff_gap_mm"]

    # Hybrid
    if cli_args.get("split_ratio") is not None:
        kwargs["split_ratio"] = cli_args["split_ratio"]
    if cli_args.get("section_gap_mm") is not None:
        kwargs["section_gap_mm"] = cli_args["section_gap_mm"]

    # --- Line Numbering Config ---
    if cli_args.get("line_numbers"):
        kwargs["line_number_config"] = {
            "side": cli_args["line_numbers_side"],
            "interval": cli_args["line_numbers_interval_val"],
            "margin_px": cli_args["line_numbers_margin_px"],
            "font_size": cli_args["line_numbers_font_size"],
            "grey": cli_args["line_numbers_grey"],
        }

    # --- Cell Labeling Config ---
    if cli_args.get("cell_labels"):
        kwargs["cell_label_config"] = {
            "y_axis_side": cli_args["cell_labels_y_side"],
            "y_axis_padding_px": cli_args["cell_labels_y_padding_px"],
            "x_axis_side": cli_args["cell_labels_x_side"],
            "x_axis_padding_px": cli_args["cell_labels_x_padding_px"],
            "font_size": cli_args["cell_labels_font_size"],
            "grey": cli_args["cell_labels_grey"],
        }

    # --- Axis Labeling Config ---
    if cli_args.get("axis_labels"):
        kwargs["axis_label_config"] = {
            "origin": cli_args["axis_labels_origin"],
            "interval": cli_args["axis_labels_interval"],
            "y_axis_side": cli_args["axis_labels_y_side"],
            "y_axis_padding_px": cli_args["axis_labels_y_padding_px"],
            "x_axis_side": cli_args["axis_labels_x_side"],
            "x_axis_padding_px": cli_args["axis_labels_x_padding_px"],
            "font_size": cli_args["axis_labels_font_size"],
            "grey": cli_args["axis_labels_grey"],
        }

    return kwargs


# --- Generation Helper: 3. Save & Summarize ---
def _save_and_print_summary(surface, context, args):
    """
    Handles all file saving and summary printing.
    """
    cli_args = vars(args)
    device_id = context["device_id"]
    device_config = context["device_config"]

    # 1. Determine Output Directory
    base_device_dir = os.path.join(args.output_dir, device_id)
    if args.true_scale:
        device_dir = os.path.join(base_device_dir, "true-scale")
        print("Note: Saving to 'true-scale' directory as --true-scale was specified.")
    else:
        device_dir = base_device_dir

    # 2. Determine Filename
    if args.filename:
        filename = args.filename if args.filename.endswith(".png") else f"{args.filename}.png"
        output_dir = device_dir

    elif args.command == "layout":
        default_filename = Path(args.layout).stem + ".png"
        filename = cli_args.get("output_filename", default_filename)  # Check for JSON override
        # Layouts go in the base device_dir
        output_dir = device_dir

    elif args.command == "title":
        filename_kwargs = cli_args.copy()
        filename_kwargs["spacing_mode"] = context["spacing_mode"]

        if context["using_line_count_mode"]:
            filename_kwargs["spacing"] = context["h_spacing_px"]
            filename_kwargs["spacing_mode"] = "px"  # Force px mode for filename

        filename = generate_filename("title", **filename_kwargs)
        # generated filename includes directory (e.g., "title/truchet/...")
        output_dir = device_dir

    elif args.command == "multi":
        filename_kwargs = cli_args.copy()
        filename_kwargs["spacing_mode"] = context["spacing_mode"]

        if context["using_line_count_mode"]:
            filename_kwargs["spacing"] = context["h_spacing_px"]
            filename_kwargs["spacing_mode"] = "px"  # Force px mode for filename

        filename = generate_filename("multi", **filename_kwargs)
        # generated filename includes directory (e.g., "multi/...")
        output_dir = device_dir

    else:  # Single template command
        template_type = cli_args.get("template_type")  # 'lined', 'grid', etc.
        filename_kwargs = cli_args.copy()
        filename_kwargs["spacing_mode"] = context["spacing_mode"]

        if context["using_line_count_mode"]:
            filename_kwargs["spacing"] = context["h_spacing_px"]
            filename_kwargs["spacing_mode"] = "px"  # Force px mode for filename

        # Remove the duplicate key before calling the function
        filename_kwargs.pop("template_type", None)

        filename = generate_filename(template_type, **filename_kwargs)
        # generated filename includes directory (e.g., "lined/...")
        output_dir = device_dir

    # 3. Save the file
    filepath = os.path.join(output_dir, filename)

    # Create directory structure if it doesn't exist
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    surface.write_to_png(filepath)

    # 4. Print Summary
    print(f"\nSuccess: Template written to {filepath}")
    print(
        f"  - Device: {device_config['name']} ({device_config['width']}×{device_config['height']}px @ {device_config['dpi']}dpi)"
    )

    if args.command == "layout":
        print(f"  - Layout: {args.layout}")
        print(f"  - Margin: {context['margin_mm']}mm")
        return  # JSON layout has its own summary logic

    if args.command == "title":
        print(f"  - Pattern: {args.title}")
        print(f"  - Margin: {context['margin_mm']}mm")

    if args.command == "multi":
        if args.template:
            print(f"  - Template: {args.template} (Uniform)")
        else:
            print("  - Template: Multi-Type Grid")
        print(f"  - Layout: {args.columns} column(s) × {args.rows} row(s)")

    if args.command in TEMPLATE_REGISTRY:
        print(f"  - Template: {args.command}")

    # Spacing summary
    if context["using_line_count_mode"]:
        spacing_display = format_line_count_summary(
            context["h_lines"],
            context["v_lines"],
            context["h_spacing_px"],
            context["v_spacing_px"],
            context["is_fractional"],
        )
        print(f"  - Spacing: {spacing_display}")
        print(f"  - Margin: {context['margin_mm']}mm")
    else:
        spacing_display = format_spacing_summary(
            context["spacing_px"],
            context["original_mm"],
            context["adjusted_mm"],
            context["was_adjusted"],
            context["spacing_mode"],
        )
        print(f"  - Spacing: {spacing_display}")

        # Detailed margin summary for non-line-count mode
        margin_mm = context["margin_mm"]
        mm2px = device_config["dpi"] / 25.4
        base_margin_px = round(margin_mm * mm2px)

        # Check if true_scale OR enforce_margins is active
        # If either is true, just print the simple margin and skip all adjustment logic
        if cli_args.get("true_scale", False) or cli_args.get("enforce_margins", False):
            print(f"  - Margin: {margin_mm}mm")
        else:
            content_height = device_config["height"] - (2 * base_margin_px)
            content_width = device_config["width"] - (2 * base_margin_px)
            # We can't show adjusted margins for complex layouts
            is_complex_layout = args.command in ["multi", "hybrid_lined_dotgrid"]
            force_align = cli_args.get("force_major_alignment", False) and cli_args.get(
                "major_every"
            )

            if not is_complex_layout:
                # Recalculate margins just for display
                v_align_unit = context["spacing_px"]

                template_type = args.command  # e.g., 'lined', 'grid'
                config = TEMPLATE_REGISTRY.get(template_type, {})
                h_align_setting = config.get("horizontal_align_unit")

                h_align_unit = context["spacing_px"]  # Default for 'grid', 'dotgrid', etc.

                if h_align_setting == "none":
                    h_align_unit = 1  # For 'lined', 'manuscript'
                elif h_align_setting == "french_ruled":
                    h_align_unit = context["spacing_px"] * 4

                if force_align:
                    m_top, m_bottom, _ = calculate_major_aligned_margins(
                        content_height, v_align_unit, base_margin_px, cli_args.get("major_every", 0)
                    )
                    m_left, m_right, _ = calculate_major_aligned_margins_x(
                        content_width, h_align_unit, base_margin_px, cli_args.get("major_every", 0)
                    )
                else:
                    m_top, m_bottom = calculate_adjusted_margins(
                        content_height, v_align_unit, base_margin_px
                    )
                    m_left, m_right = calculate_adjusted_margins_x(
                        content_width, h_align_unit, base_margin_px
                    )

                margin_adjusted = (
                    abs(m_top - base_margin_px) > 0.5 or abs(m_left - base_margin_px) > 0.5
                )

                if force_align:
                    print(
                        f"  - Margin: {margin_mm}mm (adjusted for major alignment: "
                        f"T:{m_top/mm2px:.2f}, B:{m_bottom/mm2px:.2f}, L:{m_left/mm2px:.2f}, R:{m_right/mm2px:.2f}mm)"
                    )
                elif margin_adjusted:
                    print(
                        f"  - Margin: {margin_mm}mm (adjusted for pixel-perfect: "
                        f"T:{m_top/mm2px:.2f}, B:{m_bottom/mm2px:.2f}, L:{m_left/mm2px:.2f}, R:{m_right/mm2px:.2f}mm)"
                    )
                else:
                    print(f"  - Margin: {margin_mm}mm")
            else:
                print(f"  - Margin: {margin_mm}mm")


# --- Action 1: Utility Commands ---


def handle_list_devices(args=None):
    print("Available devices:")
    default_device = get_default_device()
    for device_id in list_devices():
        config = get_device(device_id)
        marker = " (DEFAULT)" if device_id == default_device else ""
        print(
            f"  {device_id:10s} - {config['name']} ({config['width']}×{config['height']}px @ {config['dpi']}dpi){marker}"
        )


def handle_set_default_device(args):
    device_id = args.device if hasattr(args, "device") else args
    if set_default_device(device_id):
        device_config = get_device(device_id)
        print(f"Success: Default device set to: {device_config['name']}")
    else:
        print("Error: Failed to set default device")


def handle_set_default_margin(args):
    margin_mm = args.margin_mm if hasattr(args, "margin_mm") else args
    if set_default_margin(margin_mm):
        print(f"Success: Default margin set to: {margin_mm}mm")
    else:
        print("Error: Failed to set default margin")


def handle_list_templates(args=None):
    print("Available single templates:")
    for template_name in TEMPLATE_REGISTRY.keys():
        print(f"  {template_name}")

    print("\nAvailable title patterns:")
    for title_name in COVER_REGISTRY.keys():
        print(f"  {title_name}")

    print("\nComplex layout commands:")
    print("  multi")
    print("  layout")


def handle_show_spacing_info(args):
    device_id_arg = args.device if hasattr(args, "device") else args
    spacing_str = args.spacing if hasattr(args, "spacing") else args

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

    print_spacing_info(spacing_str, device_config["dpi"], device_config["name"])


# --- Action 2: JSON Layout Generation ---


def handle_json_generation(args):
    """
    Handles generation from a JSON layout file.
    """
    print(f"Loading layout from: {args.layout}")

    # 1. Read and Parse JSON
    try:
        with open(args.layout, "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"Error: Layout file not found at '{args.layout}'")
        return
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in layout file. {e}")
        return

    # 2. Validate and Get Device
    try:
        if args.device:
            config["device"] = args.device
            print(f"Note: Using device from --device flag: {args.device}")

        if "device" not in config:
            default_dev = get_default_device()
            if default_dev:
                config["device"] = default_dev
                print(f"Note: Using default device: {default_dev}")
            else:
                raise ValueError("JSON config must specify a 'device', or set a default.")

        device_config = get_device(config["device"])
    except ValueError as e:
        print(f"Error: {e}")
        return

    # 3. Determine Margin
    if args.margin is not None:
        margin_mm = args.margin
        margin_source = f"CLI flag ({margin_mm}mm)"
    elif "margin_mm" in config:
        margin_mm = config["margin_mm"]
        margin_source = f"JSON file ({margin_mm}mm)"
    elif "default_margin_mm" in device_config:
        margin_mm = device_config["default_margin_mm"]
        margin_source = f"{device_config['name']} default ({margin_mm}mm)"
    else:
        margin_mm = get_default_margin()
        margin_source = f"global default ({margin_mm}mm)"

    # 4. Auto-Adjust
    json_auto_adjust = config.get("auto_adjust_spacing", True)
    if args.true_scale:
        final_auto_adjust = False
        print("Note: Using --true-scale from CLI flag.")
    else:
        final_auto_adjust = json_auto_adjust

    # 5. Force Major Alignment
    json_force_align = config.get("force_major_alignment", False)
    if args.force_major_alignment:
        final_force_align = True
        print("Note: Using --force-major-alignment from CLI flag.")
    else:
        final_force_align = json_force_align

    # 6. Call the Generator
    surface = create_json_layout_template(
        config, device_config, margin_mm, final_auto_adjust, final_force_align
    )

    # 7. Save File and Print Summary
    # We pass 'args' and a 'context' dict to the summary helper
    context = {
        "device_id": config["device"],
        "device_config": device_config,
        "margin_mm": margin_mm,
    }
    print(f"  - Margin: {margin_source}")
    print(f"  - Master Spacing: {config.get('master_spacing_mm', 'N/A')}mm")
    _save_and_print_summary(surface, context, args)


# --- Action 3: Title Page Generation ---


def handle_cover_generation(args):
    """
    Handle generation of title page patterns
    """
    # 1. Setup device, margin, and spacing
    context = _setup_generation_context(args)

    # 2. Gather Title-Specific Kwargs
    title_kwargs = {
        "width": context["device_config"]["width"],
        "height": context["device_config"]["height"],
        "dpi": context["device_config"]["dpi"],
        "spacing_mm": context["spacing_mm_to_use"],  # from context
        "margin_mm": context["margin_mm"],
        "line_width_px": args.line_width_px,
        "auto_adjust_spacing": not args.true_scale,
        "header": args.header,
        "footer": args.footer,
    }

    # Add title-specific parameters from args
    if args.title in ["truchet", "diagonal_truchet", "hexagonal_truchet", "ten_print"]:
        if args.truchet_seed is not None:
            title_kwargs["rotation_seed"] = args.truchet_seed
        if args.title == "truchet" and args.truchet_fill_grey is not None:
            title_kwargs["truchet_fill_grey"] = args.truchet_fill_grey
        elif args.title == "diagonal_truchet":
            title_kwargs["diagonal_fill_grey_1"] = args.diag_fill_grey1
            title_kwargs["diagonal_fill_grey_2"] = args.diag_fill_grey2

    if args.decorative_border is not None:
        title_kwargs["decorative_border"] = args.decorative_border

    if args.title in [
        "hilbert_curve",
        "dragon_curve",
        "koch_snowflake",
        "plant_fractal",
        "sierpinski_triangle",
    ]:
        title_kwargs["lsystem_iterations"] = args.lsystem_iterations

    if args.title in ["contour_lines", "noise_field"]:
        # Common noise parameters
        title_kwargs["noise_scale"] = args.noise_scale
        title_kwargs["octaves"] = args.noise_octaves

        # Specific seed/style parameters
        if args.noise_seed is not None:
            if args.title == "contour_lines":
                title_kwargs["contour_seed"] = args.noise_seed
            elif args.title == "noise_field":
                title_kwargs["noise_seed"] = args.noise_seed

        if args.noise_style is not None:
            if args.title == "contour_lines":
                title_kwargs["contour_style"] = args.noise_style
            elif args.title == "noise_field":
                title_kwargs["noise_style"] = args.noise_style

        # Specific parameters
        if args.title == "contour_lines":
            title_kwargs["contour_interval"] = args.contour_interval
        if args.title == "noise_field":
            title_kwargs["greyscale_levels"] = args.greyscale_levels

    # Build cover_config
    cover_config = {
        "show_frame": not args.title_no_frame,
        "frame_shape": args.title_frame_shape,
        "border_style": args.title_border_style,
        "border_width": args.title_border_width,
        "border_grey": args.title_border_grey,
        "fill_grey": args.title_fill_grey,
        "corner_radius": args.title_corner_radius,
        "font_family": args.title_font_family,
        "font_size": args.title_font_size,
        "font_weight": args.title_font_weight,
        "font_slant": args.title_font_slant,
        "text_grey": args.title_text_grey,
        "letter_spacing": args.title_letter_spacing,
        "h_align": args.title_h_align,
        "v_align": args.title_v_align,
    }
    if args.title_text and args.title_text.strip():
        cover_config["text"] = args.title_text
    if args.title_x_center is not None:
        cover_config["x_center"] = args.title_x_center
    if args.title_y_center is not None:
        cover_config["y_center"] = args.title_y_center
    if args.title_frame_width is not None:
        cover_config["frame_width"] = args.title_frame_width
    if args.title_frame_height is not None:
        cover_config["frame_height"] = args.title_frame_height

    title_kwargs["cover_config"] = cover_config

    # 3. Generate Surface
    print(f"Generating '{args.title}' title page for {context['device_config']['name']}...")
    title_func = COVER_REGISTRY[args.title]
    surface = title_func(**title_kwargs)

    # 4. Save and Summarize
    _save_and_print_summary(surface, context, args)


# --- Action 4: Single Template Generation ---


def handle_single_template_generation(args):
    """
    Handles generation of a single, full-page template.
    """
    # 1. Setup device, margin, and spacing
    context = _setup_generation_context(args)

    # 2. Get template-specific kwargs
    template_type = args.template_type
    template_kwargs = _build_template_kwargs(template_type, args)

    print(f"Generating single '{template_type}' template for {context['device_config']['name']}...")

    # 3. Call the factory
    surface = create_template_surface(
        template_type=template_type,
        device_config=context["device_config"],
        spacing_str=context["spacing_str"],
        margin_mm=context["margin_mm"],
        auto_adjust_spacing=not args.true_scale,
        force_major_alignment=getattr(args, "force_major_alignment", False),
        header=args.header,
        footer=args.footer,
        template_kwargs=template_kwargs,
    )

    # 4. Save and Summarize
    _save_and_print_summary(surface, context, args)


# --- Action 5: Multi-Cell (Grid) Generation ---


def handle_multi_template_generation(args):
    """
    Handles generation of multi-cell grids (uniform or mixed).
    """
    # 1. Setup device, margin, and spacing
    context = _setup_generation_context(args)

    # 2. Determine grid type and build args
    num_columns = args.columns
    num_rows = args.rows
    spacing_mm = context["spacing_mm_to_use"]  # The adjusted mm value

    base_kwargs = {
        "width": context["device_config"]["width"],
        "height": context["device_config"]["height"],
        "dpi": context["device_config"]["dpi"],
        "spacing_mm": spacing_mm,
        "margin_mm": context["margin_mm"],
        "auto_adjust_spacing": not args.true_scale,
        "header": args.header,
        "footer": args.footer,
        "force_major_alignment": getattr(args, "force_major_alignment", False),
        "column_gap_mm": args.section_gap_cols if args.section_gap_cols is not None else spacing_mm,
        "row_gap_mm": args.section_gap_rows if args.section_gap_rows is not None else spacing_mm,
    }

    if args.cell_types:
        # --- Mixed-Type Grid ---
        print(
            f"Generating {num_rows}x{num_columns} multi-type grid for {context['device_config']['name']}..."
        )
        template_func = create_cell_grid_template

        cell_type_list = args.cell_types.split(",")
        if len(cell_type_list) != (num_columns * num_rows):
            raise ValueError(
                f"--cell_types list has {len(cell_type_list)} items, but grid is {num_rows}x{num_columns}"
            )

        cell_definitions = []
        idx = 0
        for r in range(num_rows):
            row_defs = []
            for c in range(num_columns):
                cell_type = cell_type_list[idx].strip()
                if cell_type not in TEMPLATE_REGISTRY:
                    raise ValueError(f"Unknown template type in --cell_types: '{cell_type}'")

                cell_kwargs = _build_template_kwargs(cell_type, args)
                row_defs.append({"type": cell_type, "kwargs": cell_kwargs})
                idx += 1
            cell_definitions.append(row_defs)

        base_kwargs["cell_definitions"] = cell_definitions

    else:
        # --- Uniform Grid ---
        template_type = args.template
        print(
            f"Generating {num_rows}x{num_columns} uniform '{template_type}' grid for {context['device_config']['name']}..."
        )
        template_func = create_column_template

        base_kwargs["num_columns"] = num_columns
        base_kwargs["num_rows"] = num_rows
        base_kwargs["base_template"] = template_type
        base_kwargs["template_kwargs"] = _build_template_kwargs(template_type, args)

    # 3. Generate Surface
    surface = template_func(**base_kwargs)

    # 4. Save and Summarize
    _save_and_print_summary(surface, context, args)
