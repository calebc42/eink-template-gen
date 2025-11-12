import json
import os
from pathlib import Path

import cairo

from .config import get_default_device, get_default_margin, set_default_device, set_default_margin
from .corners import draw_page_corners
from .covers import COVER_REGISTRY, create_cover_surface
from .devices import get_device, list_devices
from .templates import (
    TEMPLATE_REGISTRY,
    AlignmentUnits,
    create_cell_grid_template,
    create_column_template,
    create_json_layout_template,
    create_template_surface,
)
from .utils import (
    SpacingResult,
    calculate_page_margins,
    calculate_spacing,
    calculate_spacing_from_line_count,
    calculate_spacing_from_line_count_with_margins,
    format_line_count_summary,
    format_spacing_summary,
    generate_filename,
    parse_line_count_spec,
    print_spacing_info,
)

# --- Generation Helper: 1. Setup ---


def _setup_generation_context(args):
    """
    Handles initial setup:
    1. Gets Device
    2. Gets Base Margin (mm)
    3. Handles "Line Count Mode" vs "Spacing Mode" to get base spacing.

    Returns a 'context' dictionary.
    Full pixel calculations are done in the main handlers.
    """
    context = {}

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
    context["dpi"] = device_config["dpi"]  # Add for convenience
    context["width"] = device_config["width"]
    context["height"] = device_config["height"]

    # 2. Margin Setup
    if hasattr(args, "margin") and args.margin is not None:
        context["margin_mm"] = args.margin
        print(f"Using specified margin: {args.margin}mm")
    elif "default_margin_mm" in device_config:
        context["margin_mm"] = device_config["default_margin_mm"]
        print(f"Using default margin for {device_config['name']}: {context['margin_mm']}mm")
    else:
        context["margin_mm"] = get_default_margin()
        print(f"Using global default margin: {context['margin_mm']}mm")

    # 3. Mode Detection: Line Count vs Spacing
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

        # In line count mode, we must calculate exact spacing now.
        margin_mm = context["margin_mm"]
        margin_px = round(margin_mm * (context["dpi"] / 25.4))

        # Use 0 margin if user didn't specify one
        use_margins = hasattr(args, "margin") and args.margin is not None and args.margin > 0

        if not use_margins:
            margin_px = 0
            print(f"LINE COUNT MODE: Fitting {args.lines} lines with 0mm margin (default).")
        else:
            print(
                f"LINE COUNT MODE: Fitting {args.lines} lines with specified {margin_mm}mm margin."
            )

        enforce_exact = getattr(args, "enforce_margins", False)
        v_spacing_px = None
        v_is_fractional = False

        if use_margins:
            h_spacing_px, h_is_fractional, _ = calculate_spacing_from_line_count_with_margins(
                context["height"], h_lines, margin_px, enforce_exact=enforce_exact
            )
            if v_lines:
                v_spacing_px, v_is_fractional, _ = calculate_spacing_from_line_count_with_margins(
                    context["width"], v_lines, margin_px, enforce_exact=enforce_exact
                )
        else:
            h_spacing_px, h_is_fractional = calculate_spacing_from_line_count(
                context["height"], h_lines, enforce_exact=enforce_exact
            )
            if v_lines:
                v_spacing_px, v_is_fractional = calculate_spacing_from_line_count(
                    context["width"], v_lines, enforce_exact=enforce_exact
                )

        context["is_fractional"] = h_is_fractional or (v_lines and v_is_fractional)

        # Create a SpacingResult object to match the normal mode
        context["spacing_result"] = SpacingResult(
            pixels=h_spacing_px,
            mm=h_spacing_px / (context["dpi"] / 25.4),
            was_adjusted=False,
            original_mm=h_spacing_px / (context["dpi"] / 25.4),
        )
        context["v_spacing_px"] = v_spacing_px  # For grid line count
        context["spacing_str"] = f"{h_spacing_px}px"  # For legacy factory
        context["spacing_mm_to_use"] = context["spacing_result"].mm  # For legacy

    else:
        # ============================================
        # NORMAL SPACING MODE
        # ============================================
        # We just store the user's string. The handler will calculate it.
        context["spacing_str"] = args.spacing
        context["spacing_mm_to_use"] = float(
            str(args.spacing).lower().replace("mm", "").replace("px", "")
        )  # Approx.
        # Note: 'spacing_result' will be added by the handler

    return context


# --- Generation Helper: 2. Build Kwargs ---


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
    interval_val = cli_args.get("line_numbers_interval")
    if interval_val is not None:
        kwargs["line_number_config"] = {
            "side": cli_args["line_numbers_side"],
            "interval": interval_val,
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


# --- Generation Helper: 3. Preview Summary ---


def _build_preview_summary(context, args, template_kwargs=None):
    """
    Build a detailed text preview of what will be generated.
    Returns a formatted string.
    (REFACTORED: Reads from rich context, does no calculation)
    """
    device_config = context["device_config"]
    template_kwargs = template_kwargs or {}
    mm2px = device_config["dpi"] / 25.4

    lines = []
    lines.append("\n" + "=" * 70)
    lines.append("TEMPLATE PREVIEW (Dry-Run)")
    lines.append("=" * 70)

    # Device info
    lines.append(f"\n Device: {device_config['name']}")
    lines.append(f"    Resolution: {device_config['width']}×{device_config['height']}px")
    lines.append(f"    DPI: {device_config['dpi']}")
    if "diagonal_inches" in device_config:
        lines.append(f"    Physical size: {device_config['diagonal_inches']}\" diagonal")

    # Template type
    if args.command == "layout":
        lines.append("\n Template: JSON Layout")
        lines.append(f"    File: {args.layout}")
    elif args.command == "cover":
        lines.append("\n Template: Title Page")
        lines.append(f"    Pattern: {args.cover}")
    elif args.command == "multi":
        if args.template:
            lines.append("\n Template: Multi-Cell Grid (Uniform)")
            lines.append(f"    Type: {args.template}")
        else:
            lines.append("\n Template: Multi-Cell Grid (Mixed)")
        lines.append(f"    Layout: {args.columns} column(s) × {args.rows} row(s)")
    else:
        lines.append(f"\n Template: {args.command}")

    # Spacing
    lines.append("\n Spacing:")
    if context["using_line_count_mode"]:
        spacing_display = format_line_count_summary(
            context["h_lines"],
            context.get("v_lines"),  # Use .get for safety
            context["spacing_result"].pixels,
            context.get("v_spacing_px"),
            context["is_fractional"],
        )
        lines.append(f"    {spacing_display}")
        lines.append("    Mode: Line Count (fitted)")
    else:
        spacing = context["spacing_result"]
        spacing_display = format_spacing_summary(
            spacing.pixels,
            spacing.original_mm,
            spacing.mm,
            spacing.was_adjusted,
            "mm",  # Assume mm mode for this
        )
        lines.append(f"    {spacing_display}")

    # Margins (Reads from context["margins"])
    lines.append("\n Margins:")
    margin_mm = context["margin_mm"]
    margins = context.get("margins")  # Get the PageMargins object

    if not margins:
        # Fallback for handlers not yet refactored (e.g., json)
        lines.append(f"    {margin_mm}mm (Calculation not available in preview)")
    else:
        base_margin_px = round(margin_mm * mm2px)
        m_top = margins.top
        m_bottom = margins.bottom
        m_left = margins.left
        m_right = margins.right

        # Check if adjustment happened
        if abs(m_top - base_margin_px) > 0.5 or abs(m_left - base_margin_px) > 0.5:
            lines.append(f"    Base: {margin_mm}mm")
            # We don't know *why* it adjusted (pixel-perfect vs major-align)
            # so we just show the result.
            lines.append("    Adjusted for alignment:")
            lines.append(f"      Top: {m_top/mm2px:.2f}mm ({m_top}px)")
            lines.append(f"      Bottom: {m_bottom/mm2px:.2f}mm ({m_bottom}px)")
            lines.append(f"      Left: {m_left/mm2px:.2f}mm ({m_left}px)")
            lines.append(f"      Right: {m_right/mm2px:.2f}mm ({m_right}px)")
        else:
            lines.append(f"    {margin_mm}mm (no adjustment needed)")

    # Content Area
    lines.append("\n Content Area:")
    if margins:
        lines.append(f"    {margins.content_width}×{margins.content_height}px")
        lines.append(
            f"    ({margins.content_width/mm2px:.1f}×{margins.content_height/mm2px:.1f}mm)"
        )

        if (
            args.command not in ["layout", "multi", "cover"]
            and not context["using_line_count_mode"]
        ):
            num_h_lines = int(margins.content_height / context["spacing_result"].pixels)
            lines.append(f"    Fits ~{num_h_lines} horizontal lines")
            if args.command in ["grid", "dotgrid"]:
                num_v_lines = int(margins.content_width / context["spacing_result"].pixels)
                lines.append(f"    Fits ~{num_v_lines} vertical lines")
    else:
        lines.append("    (Calculation not available in preview)")

    # Features
    lines.append("\n Features:")
    features = []
    if template_kwargs:
        if template_kwargs.get("major_every"):
            features.append(f"Major lines every {template_kwargs['major_every']}")
        if template_kwargs.get("line_number_config"):
            cfg = template_kwargs["line_number_config"]
            features.append(f"Line numbers (every {cfg['interval']}, {cfg['side']} side)")
        if template_kwargs.get("cell_label_config"):
            features.append("Cell labels (A, B, C... / 1, 2, 3...)")
        if template_kwargs.get("axis_label_config"):
            cfg = template_kwargs["axis_label_config"]
            features.append(f"Axis labels (origin: {cfg['origin']})")
        if template_kwargs.get("no_crosshairs"):
            features.append("Crosshairs disabled")
        elif template_kwargs.get("crosshair_size"):
            features.append(f"Crosshairs ({template_kwargs['crosshair_size']}px)")

    if hasattr(args, "header") and args.header:
        features.append(f"Header separator: {args.header}")
    if hasattr(args, "footer") and args.footer:
        features.append(f"Footer separator: {args.footer}")

    # Corner Ornaments
    if hasattr(args, "corner_style") and args.corner_style:
        lines.append("\n Corner Ornaments:")
        lines.append(f"    Style: {args.corner_style}")
        lines.append(f"    Size: {getattr(args, 'corner_size', 20.0)}px")
        if getattr(args, "corner_grey", 0) != 0:
            lines.append(f"    Grey level: {args.corner_grey}")

    if features:
        for feature in features:
            lines.append(f"    • {feature}")
    else:
        lines.append("    (none)")

    # Output
    lines.append("\n Output (if generated):")
    if args.filename:
        filename = args.filename if args.filename.endswith(".png") else f"{args.filename}.png"
    else:
        filename_kwargs = vars(args).copy()

        if context["using_line_count_mode"]:
            filename_kwargs["spacing"] = context["spacing_result"].pixels
            filename_kwargs["spacing_mode"] = "px"
        else:
            filename_kwargs["spacing"] = context["spacing_result"].original_mm
            filename_kwargs["spacing_mode"] = "mm"

        if args.command == "layout":
            filename = Path(args.layout).stem + ".png"
        elif args.command == "cover":
            filename = generate_filename("cover", **filename_kwargs)
        elif args.command == "multi":
            filename = generate_filename("multi", **filename_kwargs)
        else:
            filename_kwargs.pop("template_type", None)
            filename = generate_filename(args.command, **filename_kwargs)

    output_dir = args.output_dir
    device_id = context["device_id"]
    if args.true_scale:
        output_path = os.path.join(output_dir, device_id, "true-scale", filename)
    else:
        output_path = os.path.join(output_dir, device_id, filename)

    lines.append(f"    {output_path}")

    # Warnings
    warnings = []
    if context.get("is_fractional"):
        warnings.append("⚠️  Fractional pixel spacing may cause slight blur or alignment drift")
    if args.true_scale:
        warnings.append("ℹ️  True-scale mode: may not align perfectly to pixel grid (blurry lines)")

    if warnings:
        lines.append("\n Warnings:")
        for warning in warnings:
            lines.append(f"    {warning}")

    lines.append("\n" + "=" * 70)
    return "\n".join(lines)


# --- Generation Helper: 4. Save & Summarize ---


def _save_and_print_summary(surface, context, args):
    """
    Handles all file saving and summary printing.
    """
    cli_args = vars(args)
    device_id = context["device_id"]
    device_config = context["device_config"]
    mm2px = device_config["dpi"] / 25.4

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
    else:
        # Build filename kwargs from context
        filename_kwargs = vars(args).copy()
        if context["using_line_count_mode"]:
            filename_kwargs["spacing"] = context["spacing_result"].pixels
            filename_kwargs["spacing_mode"] = "px"
        else:
            filename_kwargs["spacing"] = context["spacing_result"].original_mm
            filename_kwargs["spacing_mode"] = "mm"

        if args.command == "layout":
            default_filename = Path(args.layout).stem + ".png"
            filename = cli_args.get("output_filename", default_filename)
            output_dir = device_dir
        elif args.command == "cover":
            filename = generate_filename("cover", **filename_kwargs)
            output_dir = device_dir
        elif args.command == "multi":
            filename = generate_filename("multi", **filename_kwargs)
            output_dir = device_dir
        else:  # Single template command
            template_type = cli_args.get("template_type")
            filename_kwargs.pop("template_type", None)
            filename = generate_filename(template_type, **filename_kwargs)
            output_dir = device_dir

    # 3. Save the file
    filepath = os.path.join(output_dir, filename)
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
        return

    if args.command == "cover":
        print(f"  - Pattern: {args.cover}")
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
            context.get("v_lines"),
            context["spacing_result"].pixels,
            context.get("v_spacing_px"),
            context["is_fractional"],
        )
        print(f"  - Spacing: {spacing_display}")
    else:
        spacing = context["spacing_result"]
        spacing_display = format_spacing_summary(
            spacing.pixels,
            spacing.original_mm,
            spacing.mm,
            spacing.was_adjusted,
            "mm",  # Assume mm mode
        )
        print(f"  - Spacing: {spacing_display}")

    # Margin summary (Reads from context["margins"])
    margin_mm = context["margin_mm"]
    margins = context.get("margins")  # Get the PageMargins object

    if not margins or args.true_scale or cli_args.get("enforce_margins"):
        print(f"  - Margin: {margin_mm}mm")
    else:
        base_margin_px = round(margin_mm * mm2px)
        m_top = margins.top
        m_bottom = margins.bottom
        m_left = margins.left
        m_right = margins.right

        if abs(m_top - base_margin_px) > 0.5 or abs(m_left - base_margin_px) > 0.5:
            # Check *why* it adjusted
            is_major_aligned = getattr(args, "force_major_alignment", False) and cli_args.get(
                "major_every"
            )
            if is_major_aligned and args.command not in ["layout", "multi", "cover"]:
                print(
                    f"  - Margin: {margin_mm}mm (adjusted for major alignment: "
                    f"T:{m_top/mm2px:.2f}, B:{m_bottom/mm2px:.2f}, L:{m_left/mm2px:.2f}, R:{m_right/mm2px:.2f}mm)"
                )
            else:
                print(
                    f"  - Margin: {margin_mm}mm (adjusted for pixel-perfect: "
                    f"T:{m_top/mm2px:.2f}, B:{m_bottom/mm2px:.2f}, L:{m_left/mm2px:.2f}, R:{m_right/mm2px:.2f}mm)"
                )
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
    print("\nAvailable cover patterns:")
    for cover_name in COVER_REGISTRY.keys():
        if not cover_name.startswith("_"):
            print(f"  {cover_name}")
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
        device_id = config.get("device")
        if not device_id:
            device_id = get_default_device()
            if not device_id:
                raise ValueError("JSON config must specify 'device', or set a default.")
            config["device"] = device_id

        device_config = get_device(device_id)
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
    else:
        margin_mm = get_default_margin()
        print(f"Using global default margin: {margin_mm}mm")
        margin_source = f"global default ({margin_mm}mm)"

    # 4. Auto-Adjust
    auto_adjust = not args.true_scale and config.get("auto_adjust_spacing", True)

    # 5. Force Major Alignment
    force_major_alignment = args.force_major_alignment or config.get("force_major_alignment", False)

    # 6. Build Context for Preview/Summary
    master_spacing_mm = config.get("master_spacing_mm", 6)

    # Create a basic context for preview
    context = {
        "device_id": device_id,
        "device_config": device_config,
        "dpi": device_config["dpi"],
        "width": device_config["width"],
        "height": device_config["height"],
        "margin_mm": margin_mm,
        "using_line_count_mode": False,
        "spacing_result": calculate_spacing(master_spacing_mm, device_config["dpi"], auto_adjust),
        # JSON margins are simple, so we can calculate them for the preview
        "margins": calculate_page_margins(
            device_config["width"],
            device_config["height"],
            device_config["dpi"],
            margin_mm,
            v_align_unit_px=1,
            h_align_unit_px=1,  # JSON page margins don't align to grid
        ),
    }

    # 7. *** PREVIEW MODE CHECK ***
    if getattr(args, "preview", False):
        preview = _build_preview_summary(context, args, template_kwargs={})
        print(preview)

        print("  Layout Regions:")
        for i, region in enumerate(config.get("page_layout", [])):
            print(f"    {i+1}. {region.get('name', 'Unnamed')} ({region.get('template', 'blank')})")

        print("\n Preview complete. No files were created.")
        print("  Remove --preview to generate the template.")
        return

    # 8. Call the Generator
    surface = create_json_layout_template(
        config, device_config, margin_mm, auto_adjust, force_major_alignment
    )

    # 8.5. Draw corner ornaments if specified
    if hasattr(args, "corner_style") and args.corner_style:
        ctx = cairo.Context(surface)

        corner_kwargs = {"grey": getattr(args, "corner_grey", 0)}

        draw_page_corners(
            ctx,
            context["margins"],
            context["width"],
            context["height"],
            args.corner_style,
            getattr(args, "corner_size", 20.0),
            margin_inset_ratio=getattr(args, "corner_inset", 0.618),
            **corner_kwargs,
        )

    # 9. Save File and Print Summary
    print(f"  - Margin: {margin_source}")
    print(f"  - Master Spacing: {master_spacing_mm}mm")
    _save_and_print_summary(surface, context, args)


# --- Action 3: Cover Page Generation ---


def handle_cover_generation(args):
    """
    Handle generation of cover page patterns
    """
    # 1. Initial setup
    context = _setup_generation_context(args)
    template_kwargs = _build_template_kwargs(args.cover, args)

    # 2. Calculate Spacing
    if not context["using_line_count_mode"]:
        # Calculate spacing if not in line count mode
        context["spacing_result"] = calculate_spacing(
            context["spacing_mm_to_use"], context["dpi"], not args.true_scale
        )
        # We don't print the adjustment message here, we let the generator do it

    spacing_px = context["spacing_result"].pixels

    # 3. Calculate Margins
    alignment = AlignmentUnits.from_template_config(
        args.cover, spacing_px, context["dpi"], template_kwargs
    )

    margins = calculate_page_margins(
        context["width"],
        context["height"],
        context["dpi"],
        context["margin_mm"],
        alignment.vertical,
        alignment.horizontal,
        template_kwargs.get("major_every"),
        getattr(args, "force_major_alignment", False),  # Covers don't usually major align
    )

    # 4. Enrich context for preview/summary
    context["margins"] = margins

    # 5. *** PREVIEW MODE CHECK ***
    if getattr(args, "preview", False):
        preview = _build_preview_summary(context, args, template_kwargs)
        print(preview)

        # Add title-specific preview details
        if "title_text" in vars(args) and args.title_text:
            print("  Title Element:")
            print(f'    • Text: "{args.title_text}"')
            print(f"    • Frame: {'Enabled' if not args.title_no_frame else 'Disabled'}")

        print("\n Preview complete. No files were created.")
        print("  Remove --preview to generate the template.")
        return

    # 6. Gather ALL kwargs for the generator
    all_kwargs = vars(args).copy()
    all_kwargs.update(template_kwargs)

    # Add the special cover_config dict
    all_kwargs["cover_config"] = {
        "title_no_frame": args.title_no_frame,
        "title_frame_shape": args.title_frame_shape,
        "title_border_style": args.title_border_style,
        "title_border_width": args.title_border_width,
        "title_border_grey": args.title_border_grey,
        "title_fill_grey": args.title_fill_grey,
        "title_corner_radius": args.title_corner_radius,
        "title_font_family": args.title_font_family,
        "title_font_size": args.title_font_size,
        "title_font_weight": args.title_font_weight,
        "title_font_slant": args.title_font_slant,
        "title_text_grey": args.title_text_grey,
        "title_letter_spacing": args.title_letter_spacing,
        "title_h_align": args.title_h_align,
        "title_v_align": args.title_v_align,
    }
    if args.title_text and args.title_text.strip():
        all_kwargs["cover_config"]["title_text"] = args.title_text
    if args.title_x_center is not None:
        all_kwargs["cover_config"]["title_x_center"] = args.title_x_center
    if args.title_y_center is not None:
        all_kwargs["cover_config"]["title_y_center"] = args.title_y_center
    if args.title_frame_width is not None:
        all_kwargs["cover_config"]["title_frame_width"] = args.title_frame_width
    if args.title_frame_height is not None:
        all_kwargs["cover_config"]["title_frame_height"] = args.title_frame_height

    # 7. Generate Surface
    print(f"Generating '{args.cover}' cover page for {context['device_config']['name']}...")
    all_kwargs.pop("spacing", None)
    all_kwargs.pop("cover", None)
    all_kwargs.pop("header", None)
    all_kwargs.pop("footer", None)
    surface = create_cover_surface(
        cover_type=args.cover,
        margins=margins,
        spacing=context["spacing_result"],
        page_width=context["width"],
        page_height=context["height"],
        header=args.header,
        footer=args.footer,
        **all_kwargs,  # Pass all other args as kwargs
    )

    # 7.5. Draw corner ornaments if specified
    if hasattr(args, "corner_style") and args.corner_style:
        ctx = cairo.Context(surface)

        corner_kwargs = {"grey": getattr(args, "corner_grey", 0)}

        draw_page_corners(
            ctx,
            context["margins"],
            context["width"],
            context["height"],
            args.corner_style,
            getattr(args, "corner_size", 20.0),
            margin_inset_ratio=getattr(args, "corner_inset", 0.618),
            **corner_kwargs,
        )

    # 8. Save and Summarize
    _save_and_print_summary(surface, context, args)


# --- Action 4: Single Template Generation  ---


def handle_single_template_generation(args):
    """
    Handles generation of a single, full-page template.
    """
    # 1. Initial setup
    context = _setup_generation_context(args)
    template_type = args.template_type
    template_kwargs = _build_template_kwargs(template_type, args)

    # 2. Calculate Spacing
    if not context["using_line_count_mode"]:
        # Calculate spacing if not in line count mode
        context["spacing_result"] = calculate_spacing(
            context["spacing_mm_to_use"], context["dpi"], not args.true_scale
        )
        # Note: We let the generator print the adjustment message

        # Update legacy value for generator
        context["spacing_str"] = f"{context['spacing_result'].pixels}px"

    spacing_px = context["spacing_result"].pixels

    # 3. Calculate Margins
    alignment = AlignmentUnits.from_template_config(
        template_type, spacing_px, context["dpi"], template_kwargs
    )

    margins = calculate_page_margins(
        context["width"],
        context["height"],
        context["dpi"],
        context["margin_mm"],
        alignment.vertical,
        alignment.horizontal,
        template_kwargs.get("major_every"),
        getattr(args, "force_major_alignment", False) and template_kwargs.get("major_every"),
    )

    # 4. Enrich context for preview/summary
    context["margins"] = margins

    # 5. *** PREVIEW MODE CHECK ***
    if getattr(args, "preview", False):
        preview = _build_preview_summary(context, args, template_kwargs)
        print(preview)
        print("\n Preview complete. No files were created.")
        print("  Remove --preview to generate the template.")
        return

    print(f"Generating single '{template_type}' template for {context['device_config']['name']}...")

    # 6. Call the factory
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

    # 6.5. Draw corner ornaments if specified
    if hasattr(args, "corner_style") and args.corner_style:
        ctx = cairo.Context(surface)

        corner_kwargs = {"grey": getattr(args, "corner_grey", 0)}

        draw_page_corners(
            ctx,
            context["margins"],
            context["width"],
            context["height"],
            args.corner_style,
            getattr(args, "corner_size", 20.0),
            margin_inset_ratio=getattr(args, "corner_inset", 0.618),
            **corner_kwargs,
        )

    # 7. Save and Summarize
    _save_and_print_summary(surface, context, args)


# --- Action 5: Multi-Cell (Grid) Generation ---


def handle_multi_template_generation(args):
    """
    Handles generation of multi-cell grids (uniform or mixed).
    """
    # 1. Initial setup
    context = _setup_generation_context(args)
    num_columns = args.columns
    num_rows = args.rows

    # 2. Calculate Spacing
    if not context["using_line_count_mode"]:
        context["spacing_result"] = calculate_spacing(
            context["spacing_mm_to_use"], context["dpi"], not args.true_scale
        )
        # Note: We let the generator print the adjustment message

        context["spacing_str"] = f"{context['spacing_result'].pixels}px"

    spacing_px = context["spacing_result"].pixels
    spacing_mm = context["spacing_result"].mm

    # 3. Determine master template type & kwargs (for page alignment)
    master_template_type = ""
    preview_template_kwargs = {}
    if args.cell_types:
        master_template_type = args.cell_types.split(",")[0].strip()
        preview_template_kwargs = _build_template_kwargs(master_template_type, args)
    else:
        master_template_type = args.template
        preview_template_kwargs = _build_template_kwargs(master_template_type, args)

    # 4. Calculate Page Margins
    alignment = AlignmentUnits.from_template_config(
        master_template_type, spacing_px, context["dpi"], preview_template_kwargs
    )
    margins = calculate_page_margins(
        context["width"],
        context["height"],
        context["dpi"],
        context["margin_mm"],
        alignment.vertical,
        alignment.horizontal,
        preview_template_kwargs.get("major_every"),
        getattr(args, "force_major_alignment", False)
        and preview_template_kwargs.get("major_every"),
    )

    # 5. Enrich context for preview/summary
    context["margins"] = margins

    # 6. *** PREVIEW MODE CHECK ***
    if getattr(args, "preview", False):
        preview = _build_preview_summary(context, args, template_kwargs=preview_template_kwargs)
        print(preview)

        if args.cell_types:
            lines = args.cell_types.split(",")
            max_len = max(len(line.strip()) for line in lines) + 2
            if max_len < 10:
                max_len = 10

            print("  Cell Layout:")
            for r in range(num_rows):
                row_str = "    "
                for c in range(num_columns):
                    cell_name = lines[r * num_columns + c].strip()
                    row_str += f"[{cell_name:^{max_len}}] "
                print(row_str)

        print("\n Preview complete. No files were created.")
        print("  Remove --preview to generate the template.")
        return

    # 7. Build generation kwargs
    base_kwargs = {
        "width": context["width"],
        "height": context["height"],
        "dpi": context["dpi"],
        "spacing_mm": spacing_mm,  # Use adjusted mm
        "margin_mm": context["margin_mm"],
        "auto_adjust_spacing": not args.true_scale,
        "header": args.header,
        "footer": args.footer,
        "force_major_alignment": getattr(args, "force_major_alignment", False),
        "column_gap_mm": args.section_gap_cols if args.section_gap_cols is not None else spacing_mm,
        "row_gap_mm": args.section_gap_rows if args.section_gap_rows is not None else spacing_mm,
    }

    if args.cell_types:
        print(
            f"Generating {num_rows}x{num_columns} multi-type grid for {context['device_config']['name']}..."
        )
        template_func = create_cell_grid_template

        cell_type_list = args.cell_types.split(",")
        if len(cell_type_list) != (num_columns * num_rows):
            raise ValueError(
                f"Cell types list has {len(cell_type_list)} items, but grid is {num_rows}x{num_columns}"
            )

        cell_definitions = []
        idx = 0
        for r in range(num_rows):
            row_defs = []
            for c in range(num_columns):
                cell_type = cell_type_list[idx].strip()
                if cell_type not in TEMPLATE_REGISTRY and cell_type != "blank":
                    raise ValueError(f"Unknown template type in --cell_types: '{cell_type}'")
                cell_kwargs = _build_template_kwargs(cell_type, args)
                row_defs.append({"type": cell_type, "kwargs": cell_kwargs})
                idx += 1
            cell_definitions.append(row_defs)
        base_kwargs["cell_definitions"] = cell_definitions

    else:
        template_type = args.template
        print(
            f"Generating {num_rows}x{num_columns} uniform '{template_type}' grid for {context['device_config']['name']}..."
        )
        template_func = create_column_template
        base_kwargs["num_columns"] = num_columns
        base_kwargs["num_rows"] = num_rows
        base_kwargs["base_template"] = template_type
        base_kwargs["template_kwargs"] = _build_template_kwargs(template_type, args)  # Build fresh

    # 8. Generate Surface
    surface = template_func(**base_kwargs)

    # 8.5. Draw corner ornaments if specified
    if hasattr(args, "corner_style") and args.corner_style:
        ctx = cairo.Context(surface)

        corner_kwargs = {"grey": getattr(args, "corner_grey", 0)}

        draw_page_corners(
            ctx,
            context["margins"],
            context["width"],
            context["height"],
            args.corner_style,
            getattr(args, "corner_size", 20.0),
            margin_inset_ratio=getattr(args, "corner_inset", 0.618),
            **corner_kwargs,
        )

    # 9. Save and Summarize
    _save_and_print_summary(surface, context, args)
