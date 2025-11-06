"""
Template creation functions and the new Template Factory
"""

from math import cos, radians, sqrt, tan

import cairo

from . import drawing
from .cover_elements import draw_title_element
from .devices import snap_to_eink_greyscale
from .separator_config import parse_separator_config
from .separators import draw_separator, draw_separator_line
from .utils import (
    calculate_adjusted_margins,
    calculate_adjusted_margins_x,
    calculate_major_aligned_margins,
    calculate_major_aligned_margins_x,
    parse_spacing,
)

# --- Dispatcher Helper for Dotgrid ---
# This helper encapsulates the one tricky bit of logic from the old
# create_dotgrid_template: choosing which draw function to use.


def _draw_dotgrid_dispatcher(
    ctx,
    x_start,
    x_end,
    y_start,
    y_end,
    spacing_px,
    dot_radius,
    skip_first_row,
    skip_last_row,
    major_every=None,
    crosshair_size=4,
    **kwargs,
):
    """
    Dispatches to the correct dotgrid draw function based on whether
    major_every is specified.
    """
    if major_every:
        drawing.draw_dot_grid_with_crosshairs(
            ctx,
            x_start,
            x_end,
            y_start,
            y_end,
            spacing_px,
            dot_radius,
            skip_first_row=skip_first_row,
            skip_last_row=skip_last_row,
            major_every=major_every,
            crosshair_size=crosshair_size,
        )
    else:
        drawing.draw_dot_grid(
            ctx,
            x_start,
            x_end,
            y_start,
            y_end,
            spacing_px,
            dot_radius,
            skip_first_row=skip_first_row,
            skip_last_row=skip_last_row,
        )


# --- Data-Driven Template Registry ---

TEMPLATE_REGISTRY = {
    "lined": {
        "draw_func": drawing.draw_lined_section,
        "horizontal_align_unit": "none",  # Lined templates don't adjust H margin
        "vertical_align_unit": "default",
        "specific_args_map": {
            "line_width_px": "line_width",
            "major_every": "major_every",
            "major_width_add_px": "major_width_add_px",
        },
    },
    "dotgrid": {
        "draw_func": _draw_dotgrid_dispatcher,
        "horizontal_align_unit": "default",  # Uses spacing_px
        "vertical_align_unit": "default",
        "specific_args_map": {
            "dot_radius_px": "dot_radius",
            "major_every": "major_every",
            "crosshair_size": "crosshair_size",
        },
    },
    "grid": {
        "draw_func": drawing.draw_grid,
        "horizontal_align_unit": "default",
        "vertical_align_unit": "default",
        "specific_args_map": {
            "line_width_px": "line_width",
            "major_every": "major_every",
            "major_width_add_px": "major_width_add_px",
            "crosshair_size": "crosshair_size",
        },
    },
    "manuscript": {
        "draw_func": drawing.draw_manuscript_lines,
        "horizontal_align_unit": "none",
        "vertical_align_unit": "default",
        "specific_args_map": {
            "line_width_px": "line_width",
            "midline_style": "midline_style",
            "ascender_opacity": "ascender_opacity",
        },
    },
    "french_ruled": {
        "draw_func": drawing.draw_french_ruled,
        "horizontal_align_unit": "french_ruled",  # Uses spacing_px * 4
        "vertical_align_unit": "default",
        "specific_args_map": {
            "line_width_px": "line_width",
            "margin_line_offset_px": "margin_line_offset_px",  # Not passed from CLI
            "show_vertical_lines": "show_vertical_lines",  # Not passed from CLI
        },
    },
    "music_staff": {
        "draw_func": drawing.draw_music_staff,
        "horizontal_align_unit": "none",
        "vertical_align_unit": "music_staff",  # Uses custom staff_unit_px
        "specific_args_map": {
            "line_width_px": "line_width",
            "staff_gap_mm": "staff_gap_mm",
            # 'staff_spacing_mm' and 'dpi' are handled specially
        },
    },
    "isometric": {
        "draw_func": drawing.draw_isometric_grid,
        "horizontal_align_unit": "isometric",  # Custom alignment
        "vertical_align_unit": "isometric",  # Custom alignment
        "specific_args_map": {
            "line_width_px": "line_width",
            "major_every": "major_every",
            "major_width_add_px": "major_width_add_px",
        },
    },
    "hexgrid": {
        "draw_func": drawing.draw_hex_grid,
        "horizontal_align_unit": "hexgrid",  # Custom alignment
        "vertical_align_unit": "hexgrid",  # Custom alignment
        "specific_args_map": {
            "line_width_px": "line_width",
            "major_every": "major_every",
            "major_width_add_px": "major_width_add_px",
        },
    },
    "hybrid_lined_dotgrid": {
        # Hybrid is a special case and doesn't fit the simple factory.
        # We will keep its original function.
        "draw_func": "hybrid_special_case",
    },
}


# --- The New Template Factory ---


def create_template_surface(
    template_type,
    device_config,
    spacing_str,
    margin_mm,
    auto_adjust_spacing,
    force_major_alignment,
    header_separator,
    footer_separator,
    template_kwargs,
):
    """
    Primary factory for generating single-page templates.
    Reads from TEMPLATE_REGISTRY to configure and draw the template.
    """

    # --- Special Case: Hybrid Template ---
    # The hybrid template is a complex layout, not a simple repeating
    # pattern. We call its original function directly.
    if template_type == "hybrid_lined_dotgrid":
        # NOTE: We need to parse spacing_str to mm for the hybrid func
        # This is a safe assumption for this special case.
        try:
            spacing_mm_val = float(str(spacing_str).lower().replace("mm", "").replace("px", ""))
        except ValueError:
            spacing_mm_val = 6.0  # Fallback

        return create_hybrid_template(
            width=device_config["width"],
            height=device_config["height"],
            dpi=device_config["dpi"],
            spacing_mm=spacing_mm_val,
            margin_mm=margin_mm,
            section_gap_mm=template_kwargs.get("section_gap_mm", spacing_mm_val),
            line_width_px=template_kwargs.get("line_width_px", 0.5),
            dot_radius_px=template_kwargs.get("dot_radius_px", 1.5),
            header_separator=header_separator,
            footer_separator=footer_separator,
            split_ratio=template_kwargs.get("split_ratio", 0.6),
            auto_adjust_spacing=auto_adjust_spacing,
            force_major_alignment=force_major_alignment,
        )

    # --- 1. Look up config ---
    config = TEMPLATE_REGISTRY.get(template_type)
    if not config:
        raise ValueError(f"Unknown template type '{template_type}' in factory.")

    # --- 2. Setup Device & Spacing ---
    width = device_config["width"]
    height = device_config["height"]
    dpi = device_config["dpi"]
    mm2px = dpi / 25.4

    spacing_px, original_mm, adjusted_mm, was_adjusted, mode = parse_spacing(
        spacing_str, dpi, auto_adjust=auto_adjust_spacing
    )

    if mode == "mm" and was_adjusted:
        print(
            f"Note: Adjusted spacing from {original_mm}mm to {adjusted_mm:.3f}mm ({int(spacing_px)}px) for pixel-perfect alignment"
        )
    elif mode == "px":
        print(f"Using exact pixel spacing: {int(spacing_px)}px (≈{original_mm:.2f}mm)")

    # --- 3. Setup Canvas ---
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    ctx = cairo.Context(surface)
    ctx.set_source_rgb(1, 1, 1)  # White background
    ctx.paint()

    # --- 4. Calculate Pixel-Perfect Margins ---
    base_margin = round(margin_mm * mm2px)
    content_height = height - (2 * base_margin)
    content_width = width - (2 * base_margin)

    # Get alignment units based on template type
    v_align_unit_px = spacing_px
    h_align_unit_px = spacing_px

    if config.get("vertical_align_unit") == "music_staff":
        staff_gap_mm = template_kwargs.get("staff_gap_mm", 10)
        staff_gap_px = round(staff_gap_mm * mm2px)
        v_align_unit_px = (spacing_px * 4) + staff_gap_px  # Full staff unit
    elif config.get("vertical_align_unit") == "isometric":
        v_align_unit_px = spacing_px * tan(radians(60))
    elif config.get("vertical_align_unit") == "hexgrid":
        v_align_unit_px = sqrt(3) * spacing_px

    if config.get("horizontal_align_unit") == "none":
        h_align_unit_px = 1  # No adjustment
    elif config.get("horizontal_align_unit") == "french_ruled":
        h_align_unit_px = spacing_px * 4
    elif config.get("horizontal_align_unit") == "isometric":
        h_align_unit_px = spacing_px / cos(radians(30))
    elif config.get("horizontal_align_unit") == "hexgrid":
        h_align_unit_px = 1.5 * spacing_px

    # Calculate final margins
    major_every = template_kwargs.get("major_every")
    if force_major_alignment and major_every and template_type in ["grid", "dotgrid"]:
        m_top, m_bottom, _ = calculate_major_aligned_margins(
            content_height, v_align_unit_px, base_margin, major_every
        )
        m_left, m_right, _ = calculate_major_aligned_margins_x(
            content_width, h_align_unit_px, base_margin, major_every
        )
        print("Note: Force-aligned grid to major lines.")
    else:
        m_top, m_bottom = calculate_adjusted_margins(content_height, v_align_unit_px, base_margin)
        m_left, m_right = calculate_adjusted_margins_x(content_width, h_align_unit_px, base_margin)

    # --- 5. Draw Separators ---
    header_style, header_kwargs = parse_separator_config(header_separator)
    if header_style:
        draw_separator_line(
            ctx, m_left, width - m_right, m_top, style=header_style, **header_kwargs
        )

    footer_style, footer_kwargs = parse_separator_config(footer_separator)
    if footer_style:
        draw_separator_line(
            ctx, m_left, width - m_right, height - m_bottom, style=footer_style, **footer_kwargs
        )

    # --- 6. Prepare and Call Drawing Function ---
    draw_func = config["draw_func"]

    # Base arguments required by all draw functions
    draw_kwargs = {
        "ctx": ctx,
        "x_start": m_left,
        "x_end": width - m_right,
        "y_start": m_top,
        "y_end": height - m_bottom,
        "spacing_px": spacing_px,
    }

    # *** START FIX ***
    # Add skip args *only if* they are relevant
    if template_type in ["lined", "manuscript", "french_ruled"]:
        draw_kwargs["skip_first"] = header_style is not None
        draw_kwargs["skip_last"] = footer_style is not None
    elif template_type in ["grid", "dotgrid"]:
        draw_kwargs["skip_first_row"] = header_style is not None
        draw_kwargs["skip_last_row"] = footer_style is not None
    # *** END FIX ***

    # Translate and filter template_kwargs
    arg_map = config.get("specific_args_map", {})
    for cli_arg, func_arg in arg_map.items():
        if cli_arg in template_kwargs:
            draw_kwargs[func_arg] = template_kwargs[cli_arg]

    # Handle --no_crosshairs
    if "no_crosshairs" in template_kwargs and template_kwargs["no_crosshairs"]:
        draw_kwargs["crosshair_size"] = 0

    # Handle special case for music_staff
    if template_type == "music_staff":
        draw_kwargs["staff_spacing_mm"] = adjusted_mm
        draw_kwargs["dpi"] = dpi
        # Remove args it doesn't understand
        draw_kwargs.pop("spacing_px", None)

    # Call the specific drawing function
    try:
        draw_func(**draw_kwargs)
    except TypeError as e:
        print("\n--- ERROR ---")
        print(f"Argument mismatch calling draw function for '{template_type}'.")
        print(f"Error: {e}")
        print(f"Attempted to call: {draw_func.__name__}")
        print(f"With arguments: {list(draw_kwargs.keys())}")
        raise

    # --- 7. Draw Extras (Line Numbers, Labels) ---
    if "line_number_config" in template_kwargs:
        print("Note: Drawing line numbers...")
        drawing.draw_line_numbering(
            ctx, m_top, height - m_bottom, spacing_px, config=template_kwargs["line_number_config"]
        )

    if "cell_label_config" in template_kwargs:
        print("Note: Drawing cell labels...")
        drawing.draw_cell_labeling(
            ctx,
            m_left,
            width - m_right,
            m_top,
            height - m_bottom,
            spacing_px,
            config=template_kwargs["cell_label_config"],
        )

    if "axis_label_config" in template_kwargs:
        print("Note: Drawing axis labels...")
        drawing.draw_axis_labeling(
            ctx,
            m_left,
            width - m_right,
            m_top,
            height - m_bottom,
            spacing_px,
            config=template_kwargs["axis_label_config"],
        )

    # --- 8. Return Surface ---
    return surface


# --- COMPLEX LAYOUT FACTORIES ---
# These functions are called by `handle_multi_template_generation`
# and `handle_json_generation`. They are already factories,
# so they remain.


def create_hybrid_template(
    width,
    height,
    dpi,
    spacing_mm,
    margin_mm,
    section_gap_mm,
    line_width_px,
    dot_radius_px,
    header_separator=None,
    footer_separator=None,
    split_ratio=0.6,
    auto_adjust_spacing=True,
    force_major_alignment=None,
):  # <-- FIX
    """
    Create a hybrid template with lined section (left) and dot grid (right)
    """
    mm2px = dpi / 25.4

    if auto_adjust_spacing:
        from .utils import snap_spacing_to_clean_pixels

        adjusted_mm, spacing_px, was_adjusted = snap_spacing_to_clean_pixels(spacing_mm, dpi)
        if was_adjusted:
            print(
                f"Note: Adjusted spacing from {spacing_mm}mm to {adjusted_mm:.3f}mm for pixel-perfect alignment"
            )
        spacing_mm = adjusted_mm
    else:
        spacing_px = spacing_mm * mm2px

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    ctx = cairo.Context(surface)

    # white background
    ctx.set_source_rgb(1, 1, 1)
    ctx.paint()

    # calculate base margins
    base_margin = round(margin_mm * mm2px)

    # Calculate adjusted top/bottom margins
    content_height = height - (2 * base_margin)
    m_top, m_bottom = calculate_adjusted_margins(content_height, spacing_px, base_margin)

    # Calculate adjusted left/right margins (based on dotgrid spacing)
    content_width = width - (2 * base_margin)
    m_left, m_right = calculate_adjusted_margins_x(content_width, spacing_px, base_margin)

    # calculate split and gap
    split_x = int(width * split_ratio)
    gap_px = round(section_gap_mm * mm2px)
    half_gap = gap_px // 2

    # --- Parse header separator ---
    header_style, header_kwargs = parse_separator_config(header_separator)
    if header_style:
        draw_separator_line(
            ctx, m_left, width - m_right, m_top, style=header_style, **header_kwargs
        )

    # --- Parse footer separator ---
    footer_style, footer_kwargs = parse_separator_config(footer_separator)
    if footer_style:
        draw_separator_line(
            ctx, m_left, width - m_right, height - m_bottom, style=footer_style, **footer_kwargs
        )

    # --- Update skip logic ---
    skip_first = header_style is not None
    skip_last = footer_style is not None

    # draw lined section (left) with boundary skipping
    drawing.draw_lined_section(
        ctx,
        m_left,
        split_x - half_gap,
        m_top,
        height - m_bottom,
        spacing_px,
        line_width_px,
        skip_first=skip_first,
        skip_last=skip_last,
    )

    # draw dot grid section (right) with boundary skipping
    drawing.draw_dot_grid(
        ctx,
        split_x + half_gap,
        width - m_right,
        m_top,
        height - m_bottom,
        spacing_px,
        dot_radius_px,
        skip_first_row=skip_first,
        skip_last_row=skip_last,
    )

    # --- draw vertical separator with grey ---
    draw_separator(ctx, split_x, m_top, height - m_bottom, grey=5)

    return surface


def create_column_template(
    width,
    height,
    dpi,
    spacing_mm,
    margin_mm,
    num_columns,
    num_rows,
    column_gap_mm,
    row_gap_mm,
    base_template,
    template_kwargs,
    header_separator=None,
    footer_separator=None,
    auto_adjust_spacing=True,
    force_major_alignment=None,
):  # <-- FIX (though not used)
    """
    Create a multi-column, multi-row template with any base template type
    """
    mm2px = dpi / 25.4

    # This import is needed for the margin calculations
    from .utils import snap_spacing_to_clean_pixels

    if auto_adjust_spacing:
        adjusted_mm, spacing_px, was_adjusted = snap_spacing_to_clean_pixels(spacing_mm, dpi)
        if was_adjusted:
            print(
                f"Note: Adjusted spacing from {spacing_mm}mm to {adjusted_mm:.3f}mm for pixel-perfect alignment"
            )
        spacing_mm = adjusted_mm
    else:
        spacing_px = spacing_mm * mm2px

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    ctx = cairo.Context(surface)

    # white background
    ctx.set_source_rgb(1, 1, 1)
    ctx.paint()

    base_margin = round(margin_mm * mm2px)
    col_gap_px = round(column_gap_mm * mm2px)
    row_gap_px = round(row_gap_mm * mm2px)

    # --- Page-level Margin Adjustment ---
    # We adjust the *full page* margins first, based on the base spacing.
    # This ensures separators align with the content grid.

    # Determine the repeating vertical unit for the *whole page*
    # This is complex, as it depends on the template type (e.g., music staff)
    page_adj_y_spacing = spacing_px
    page_adj_x_spacing = spacing_px

    if base_template == "music_staff":
        # Use staff unit for page adjustment
        staff_gap_mm_val = template_kwargs.get("staff_gap_mm", 10)
        staff_gap_px = int(staff_gap_mm_val * mm2px)
        staff_height_px = spacing_px * 4
        page_adj_y_spacing = staff_height_px + staff_gap_px
    elif base_template == "french_ruled":
        page_adj_x_spacing = spacing_px * 4
    elif base_template in ["lined", "manuscript"]:
        page_adj_x_spacing = 1  # No horizontal adjustment

    content_height_page = height - (2 * base_margin)
    m_top_page, m_bottom_page = calculate_adjusted_margins(
        content_height_page, page_adj_y_spacing, base_margin
    )

    content_width_page = width - (2 * base_margin)
    m_left_page, m_right_page = calculate_adjusted_margins_x(
        content_width_page, page_adj_x_spacing, base_margin
    )

    # --- Parse header separator ---
    header_style, header_kwargs = parse_separator_config(header_separator)
    if header_style:
        draw_separator_line(
            ctx, m_left_page, width - m_right_page, m_top_page, style=header_style, **header_kwargs
        )

    # --- Parse footer separator ---
    footer_style, footer_kwargs = parse_separator_config(footer_separator)
    if footer_style:
        draw_separator_line(
            ctx,
            m_left_page,
            width - m_right_page,
            height - m_bottom_page,
            style=footer_style,
            **footer_kwargs,
        )

    # --- Cell Calculation & Drawing ---

    # Calculate cell dimensions based on *adjusted* page content area
    available_width = (width - m_left_page - m_right_page) - ((num_columns - 1) * col_gap_px)
    column_width = available_width // num_columns

    available_height = (height - m_top_page - m_bottom_page) - ((num_rows - 1) * row_gap_px)
    row_height = available_height // num_rows

    # Get the ruling orientation (e.g., vertical lines)
    template_kwargs.pop("orientation", "horizontal")

    for r in range(num_rows):
        y_start_cell = m_top_page + (r * (row_height + row_gap_px))
        y_end_cell = y_start_cell + row_height

        for c in range(num_columns):
            x_start_cell = m_left_page + (c * (column_width + col_gap_px))
            x_end_cell = x_start_cell + column_width

            # --- Internal Margin Adjustment ---
            # Calculate pixel-perfect margins *inside* this cell
            # to fill the space perfectly.

            cell_width = x_end_cell - x_start_cell
            cell_height = y_end_cell - y_start_cell

            # Use the same adjustment spacing as the page
            internal_m_top, internal_m_bottom = calculate_adjusted_margins(
                cell_height, page_adj_y_spacing, 0
            )
            internal_m_left, internal_m_right = calculate_adjusted_margins_x(
                cell_width, page_adj_x_spacing, 0
            )

            # Define the final drawing boundaries *inside* the cell
            draw_x_start = x_start_cell + internal_m_left
            draw_x_end = x_end_cell - internal_m_right
            draw_y_start = y_start_cell + internal_m_top
            draw_y_end = y_end_cell - internal_m_bottom

            # --- Update skip logic ---
            skip_first = (r == 0) and (header_style is not None)
            skip_last = (r == num_rows - 1) and (footer_style is not None)

            # --- Draw content in the cell ---
            if base_template == "lined":
                drawing.draw_lined_section(
                    ctx,
                    draw_x_start,
                    draw_x_end,
                    draw_y_start,
                    draw_y_end,
                    spacing_px,
                    template_kwargs.get("line_width_px", 0.5),
                    skip_first=skip_first,
                    skip_last=skip_last,
                    major_every=template_kwargs.get("major_every"),
                    major_width_add_px=template_kwargs.get("major_width_add_px", 1.5),
                )

            elif base_template == "dotgrid":
                # Use the dispatcher to handle major_every
                _draw_dotgrid_dispatcher(
                    ctx,
                    draw_x_start,
                    draw_x_end,
                    draw_y_start,
                    draw_y_end,
                    spacing_px,
                    dot_radius=template_kwargs.get("dot_radius_px", 1.5),
                    skip_first_row=skip_first,
                    skip_last_row=skip_last,
                    major_every=template_kwargs.get("major_every"),
                    crosshair_size=template_kwargs.get("crosshair_size", 4),
                )

            elif base_template == "grid":
                drawing.draw_grid(
                    ctx,
                    draw_x_start,
                    draw_x_end,
                    draw_y_start,
                    draw_y_end,
                    spacing_px,
                    template_kwargs.get("line_width_px", 0.5),
                    skip_first_row=skip_first,
                    skip_last_row=skip_last,
                    major_every=template_kwargs.get("major_every"),
                    major_width_add_px=template_kwargs.get("major_width_add_px", 1.5),
                    crosshair_size=(
                        0
                        if template_kwargs.get("no_crosshairs")
                        else template_kwargs.get("crosshair_size", 3)
                    ),
                )

            elif base_template == "manuscript":
                drawing.draw_manuscript_lines(
                    ctx,
                    draw_x_start,
                    draw_x_end,
                    draw_y_start,
                    draw_y_end,
                    spacing_px,
                    template_kwargs.get("line_width_px", 0.5),
                    template_kwargs.get("midline_style", "dashed"),
                    template_kwargs.get("ascender_opacity", 0.3),
                )

            elif base_template == "french_ruled":
                # Note: French ruled margin line probably won't work well in columns
                drawing.draw_french_ruled(
                    ctx,
                    draw_x_start,
                    draw_x_end,
                    draw_y_start,
                    draw_y_end,
                    spacing_px,
                    template_kwargs.get("line_width_px", 0.5),
                    margin_line_offset_px=None,  # Disable margin line in columns
                    show_vertical_lines=True,
                )

            elif base_template == "music_staff":
                drawing.draw_music_staff(
                    ctx,
                    draw_x_start,
                    draw_x_end,
                    draw_y_start,
                    draw_y_end,
                    spacing_mm,
                    dpi,
                    template_kwargs.get("line_width_px", 0.5),
                    template_kwargs.get("staff_gap_mm", 10),
                )

            elif base_template == "isometric":
                drawing.draw_isometric_grid(
                    ctx,
                    draw_x_start,
                    draw_x_end,
                    draw_y_start,
                    draw_y_end,
                    spacing_px,
                    template_kwargs.get("line_width_px", 0.5),
                )

            elif base_template == "hexgrid":
                drawing.draw_hex_grid(
                    ctx,
                    draw_x_start,
                    draw_x_end,
                    draw_y_start,
                    draw_y_end,
                    spacing_px,
                    template_kwargs.get("line_width_px", 0.5),
                )

            # --- Draw Column Separator with grey ---
            if c < num_columns - 1:
                sep_x = x_end_cell + (col_gap_px // 2)
                # Draw separator line only in the vertical bounds of the page content
                draw_separator(ctx, sep_x, m_top_page, height - m_bottom_page, grey=5)

        # --- Draw Row Separator with grey ---
        if r < num_rows - 1:
            sep_y = y_end_cell + (row_gap_px // 2)
            ctx.set_line_width(1.0)

            # Use snapped greyscale value instead of opacity
            grey_val = snap_to_eink_greyscale(5)
            ctx.set_source_rgb(grey_val, grey_val, grey_val)

            # Draw separator line only in the horizontal bounds of the page content
            ctx.move_to(m_left_page, sep_y + 0.5)
            ctx.line_to(width - m_right_page, sep_y + 0.5)
            ctx.stroke()

    return surface


def create_cell_grid_template(
    width,
    height,
    dpi,
    spacing_mm,
    margin_mm,
    cell_definitions,  # <-- NEW
    column_gap_mm,
    row_gap_mm,
    header_separator=None,
    footer_separator=None,
    auto_adjust_spacing=True,
    force_major_alignment=None,
):  # <-- FIX (though not used)
    """
    Create a multi-column, multi-row template where each cell can be
    a different template type.
    """
    mm2px = dpi / 25.4
    from .utils import (
        calculate_adjusted_margins,
        calculate_adjusted_margins_x,
        snap_spacing_to_clean_pixels,
    )

    # --- Page-level Margin Adjustment ---
    # This is the trickiest part. How do we align the page?
    # We must "nominate" a template type to govern the page alignment.
    # Let's use the top-left cell as the "master".

    master_template_type = cell_definitions[0][0]["type"]
    master_kwargs = cell_definitions[0][0]["kwargs"]

    if auto_adjust_spacing:
        adjusted_mm, spacing_px, _ = snap_spacing_to_clean_pixels(spacing_mm, dpi)
        spacing_mm = adjusted_mm
    else:
        spacing_px = spacing_mm * mm2px

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    ctx = cairo.Context(surface)
    ctx.set_source_rgb(1, 1, 1)
    ctx.paint()

    base_margin = round(margin_mm * mm2px)
    col_gap_px = round(column_gap_mm * mm2px)
    row_gap_px = round(row_gap_mm * mm2px)

    # --- Page-level Margin Adjustment (using master cell's properties) ---
    page_adj_y_spacing = spacing_px
    page_adj_x_spacing = spacing_px

    if master_template_type == "music_staff":
        staff_gap_mm_val = master_kwargs.get("staff_gap_mm", 10)
        staff_gap_px = int(staff_gap_mm_val * mm2px)
        staff_height_px = spacing_px * 4
        page_adj_y_spacing = staff_height_px + staff_gap_px
    elif master_template_type == "french_ruled":
        page_adj_x_spacing = spacing_px * 4
    elif master_template_type in ["lined", "manuscript"]:
        page_adj_x_spacing = 1  # No horizontal adjustment

    content_height_page = height - (2 * base_margin)
    m_top_page, m_bottom_page = calculate_adjusted_margins(
        content_height_page, page_adj_y_spacing, base_margin
    )
    content_width_page = width - (2 * base_margin)
    m_left_page, m_right_page = calculate_adjusted_margins_x(
        content_width_page, page_adj_x_spacing, base_margin
    )

    # --- Parse header separator ---
    header_style, header_kwargs = parse_separator_config(header_separator)
    if header_style:
        draw_separator_line(
            ctx, m_left_page, width - m_right_page, m_top_page, style=header_style, **header_kwargs
        )

    # --- Parse footer separator ---
    footer_style, footer_kwargs = parse_separator_config(footer_separator)
    if footer_style:
        draw_separator_line(
            ctx,
            m_left_page,
            width - m_right_page,
            height - m_bottom_page,
            style=footer_style,
            **footer_kwargs,
        )

    # --- Cell Calculation & Drawing ---
    num_rows = len(cell_definitions)
    num_columns = len(cell_definitions[0]) if num_rows > 0 else 0

    available_width = (width - m_left_page - m_right_page) - ((num_columns - 1) * col_gap_px)
    column_width = available_width // num_columns
    available_height = (height - m_top_page - m_bottom_page) - ((num_rows - 1) * row_gap_px)
    row_height = available_height // num_rows

    for r in range(num_rows):
        y_start_cell = m_top_page + (r * (row_height + row_gap_px))
        y_end_cell = y_start_cell + row_height

        for c in range(num_columns):
            x_start_cell = m_left_page + (c * (column_width + col_gap_px))
            x_end_cell = x_start_cell + column_width

            # Get this specific cell's definition
            cell_def = cell_definitions[r][c]
            template_type = cell_def["type"]
            template_kwargs = cell_def["kwargs"]

            # Calculate internal margins for *this cell*
            cell_width = x_end_cell - x_start_cell
            cell_height = y_end_cell - y_start_cell

            # --- Internal Alignment ---
            # We use the *master* page alignment for all cells
            # This ensures all internal cell content aligns across separators
            internal_m_top, internal_m_bottom = calculate_adjusted_margins(
                cell_height, page_adj_y_spacing, 0
            )
            internal_m_left, internal_m_right = calculate_adjusted_margins_x(
                cell_width, page_adj_x_spacing, 0
            )

            draw_x_start = x_start_cell + internal_m_left
            draw_x_end = x_end_cell - internal_m_right
            draw_y_start = y_start_cell + internal_m_top
            draw_y_end = y_end_cell - internal_m_bottom

            # --- Update skip logic ---
            skip_first = (r == 0) and (header_style is not None)
            skip_last = (r == num_rows - 1) and (footer_style is not None)

            # --- BIG DISPATCH BLOCK ---
            # This calls the correct draw function based on the cell's type

            if template_type == "lined":
                drawing.draw_lined_section(
                    ctx,
                    draw_x_start,
                    draw_x_end,
                    draw_y_start,
                    draw_y_end,
                    spacing_px,
                    template_kwargs.get("line_width_px", 0.5),
                    skip_first=skip_first,
                    skip_last=skip_last,
                    major_every=template_kwargs.get("major_every"),
                    major_width_add_px=template_kwargs.get("major_width_add_px", 1.5),
                )

                # Check for line numbering (from previous step)
                if "line_number_config" in template_kwargs:
                    from .drawing import draw_line_numbering

                    draw_line_numbering(
                        ctx,
                        draw_y_start,
                        draw_y_end,
                        spacing_px,
                        template_kwargs["line_number_config"],
                    )

            elif template_type == "dotgrid":
                # Use the dispatcher to handle major_every
                _draw_dotgrid_dispatcher(
                    ctx,
                    draw_x_start,
                    draw_x_end,
                    draw_y_start,
                    draw_y_end,
                    spacing_px,
                    dot_radius=template_kwargs.get("dot_radius_px", 1.5),
                    skip_first_row=skip_first,
                    skip_last_row=skip_last,
                    major_every=template_kwargs.get("major_every"),
                    crosshair_size=template_kwargs.get("crosshair_size", 4),
                )

            elif template_type == "grid":
                drawing.draw_grid(
                    ctx,
                    draw_x_start,
                    draw_x_end,
                    draw_y_start,
                    draw_y_end,
                    spacing_px,
                    template_kwargs.get("line_width_px", 0.5),
                    skip_first_row=skip_first,
                    skip_last_row=skip_last,
                    major_every=template_kwargs.get("major_every"),
                    major_width_add_px=template_kwargs.get("major_width_add_px", 1.5),
                    crosshair_size=(
                        0
                        if template_kwargs.get("no_crosshairs")
                        else template_kwargs.get("crosshair_size", 4)
                    ),
                )

                # --- Check for cell labeling ---
                if "cell_label_config" in template_kwargs:
                    from .drawing import draw_cell_labeling

                    draw_cell_labeling(
                        ctx,
                        draw_x_start,
                        draw_x_end,
                        draw_y_start,
                        draw_y_end,
                        spacing_px,
                        template_kwargs["cell_label_config"],
                    )

                # --- Check for axis labeling ---
                if "axis_label_config" in template_kwargs:
                    from .drawing import draw_axis_labeling

                    draw_axis_labeling(
                        ctx,
                        draw_x_start,
                        draw_x_end,
                        draw_y_start,
                        draw_y_end,
                        spacing_px,
                        template_kwargs["axis_label_config"],
                    )

            elif template_type == "manuscript":
                drawing.draw_manuscript_lines(
                    ctx,
                    draw_x_start,
                    draw_x_end,
                    draw_y_start,
                    draw_y_end,
                    spacing_px,
                    template_kwargs.get("line_width_px", 0.5),
                    template_kwargs.get("midline_style", "dashed"),
                    template_kwargs.get("ascender_opacity", 0.3),
                )

            elif template_type == "french_ruled":
                drawing.draw_french_ruled(
                    ctx,
                    draw_x_start,
                    draw_x_end,
                    draw_y_start,
                    draw_y_end,
                    spacing_px,
                    template_kwargs.get("line_width_px", 0.5),
                    margin_line_offset_px=None,
                    show_vertical_lines=True,
                )

            elif template_type == "music_staff":
                drawing.draw_music_staff(
                    ctx,
                    draw_x_start,
                    draw_x_end,
                    draw_y_start,
                    draw_y_end,
                    spacing_mm,
                    dpi,
                    template_kwargs.get("line_width_px", 0.5),
                    template_kwargs.get("staff_gap_mm", 10),
                )

            elif template_type == "isometric":
                drawing.draw_isometric_grid(
                    ctx,
                    draw_x_start,
                    draw_x_end,
                    draw_y_start,
                    draw_y_end,
                    spacing_px,
                    template_kwargs.get("line_width_px", 0.5),
                )

            elif template_type == "hexgrid":
                drawing.draw_hex_grid(
                    ctx,
                    draw_x_start,
                    draw_x_end,
                    draw_y_start,
                    draw_y_end,
                    spacing_px,
                    template_kwargs.get("line_width_px", 0.5),
                )

            # --- Draw Separators with grey ---
            if c < num_columns - 1:
                sep_x = x_end_cell + (col_gap_px // 2)
                draw_separator(ctx, sep_x, m_top_page, height - m_bottom_page, grey=5)

        # --- Draw Row Separator with grey ---
        if r < num_rows - 1:
            sep_y = y_end_cell + (row_gap_px // 2)
            ctx.set_line_width(1.0)

            grey_val = snap_to_eink_greyscale(5)
            ctx.set_source_rgb(grey_val, grey_val, grey_val)

            ctx.move_to(m_left_page, sep_y + 0.5)
            ctx.line_to(width - m_right_page, sep_y + 0.5)
            ctx.stroke()

    return surface


def create_json_layout_template(
    config, device_config, margin_mm, auto_adjust=True, force_major_alignment=False
):
    """
    Create a complex, ratio-based template from a JSON config object.
    This is the main "layout engine".
    """

    # 1. Setup Canvas and Device
    width = device_config["width"]
    height = device_config["height"]
    dpi = device_config["dpi"]
    mm2px = dpi / 25.4

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    ctx = cairo.Context(surface)
    ctx.set_source_rgb(1, 1, 1)  # White background
    ctx.paint()

    # 2. Setup Page Margins and Content Area
    base_margin = round(margin_mm * mm2px)

    # Get master spacing for page alignment
    master_spacing_mm = config.get("master_spacing_mm", 6)
    master_spacing_px, _, _, _, _ = parse_spacing(
        str(master_spacing_mm), dpi, auto_adjust=auto_adjust
    )

    # Calculate pixel-perfect page margins
    content_height_page = height - (2 * base_margin)
    m_top_page, m_bottom_page = calculate_adjusted_margins(
        content_height_page, master_spacing_px, base_margin
    )

    content_width_page = width - (2 * base_margin)
    # Use 1 for x-adj if master spacing is only for Y (most common)
    m_left_page, m_right_page = calculate_adjusted_margins_x(content_width_page, 1, base_margin)

    # Define the pixel-perfect content area
    content_x_start = m_left_page
    content_y_start = m_top_page
    content_width = width - m_left_page - m_right_page
    content_height = height - m_top_page - m_bottom_page

    print(f"Note: Page content area is {content_width}px × {content_height}px")

    # 3. Draw Page-Level Separators (MODIFIED)
    header_style, header_kwargs = parse_separator_config(config.get("header_separator"))
    if header_style:
        draw_separator_line(
            ctx, m_left_page, width - m_right_page, m_top_page, style=header_style, **header_kwargs
        )

    footer_style, footer_kwargs = parse_separator_config(config.get("footer_separator"))
    if footer_style:
        draw_separator_line(
            ctx,
            m_left_page,
            width - m_right_page,
            height - m_bottom_page,
            style=footer_style,
            **footer_kwargs,
        )

    # 4. Draw Layout Regions
    if "page_layout" not in config or not config["page_layout"]:
        raise ValueError("JSON config must contain a 'page_layout' array with at least one region.")

    for region in config["page_layout"]:
        name = region.get("name", "Unnamed Region")
        print(f"  Drawing region: '{name}'")

        # 4a. Calculate Region Pixel Boundaries
        rect_percents = region.get("region_rect")
        if not rect_percents or len(rect_percents) != 4:
            raise ValueError(
                f"Region '{name}' has invalid or missing 'region_rect'. "
                "Must be [x_start_p, y_start_p, width_p, height_p]"
            )

        x_p, y_p, w_p, h_p = rect_percents

        cell_x_start_abs = content_x_start + (x_p * content_width)
        cell_y_start_abs = content_y_start + (y_p * content_height)
        cell_width_abs = w_p * content_width
        cell_height_abs = h_p * content_height
        cell_x_end_abs = cell_x_start_abs + cell_width_abs
        cell_y_end_abs = cell_y_start_abs + cell_height_abs

        # 4b. Get Region-Specific Spacing
        # Default to master spacing
        region_spacing_mm = region.get("spacing_mm", master_spacing_mm)
        region_spacing_px, _, _, _, _ = parse_spacing(
            str(region_spacing_mm), dpi, auto_adjust=auto_adjust
        )

        # 4c. Calculate Internal Pixel-Perfect Margins for this Region
        adj_y_spacing = region_spacing_px
        adj_x_spacing = region_spacing_px

        template_type = region.get("template")
        json_kwargs = region.get("kwargs", {})

        if template_type == "french_ruled":
            adj_x_spacing = region_spacing_px * 4
        elif template_type in ["lined", "manuscript"]:
            adj_x_spacing = 1  # No x-adjustment

        major_every = json_kwargs.get("major_every")

        use_force_align = (
            force_major_alignment and major_every and template_type in ["grid", "dotgrid"]
        )

        if use_force_align:
            print(f"  Note: Applying major-force-alignment to region '{name}'")
            internal_m_top, internal_m_bottom, _ = calculate_major_aligned_margins(
                cell_height_abs, adj_y_spacing, 0, major_every
            )
            internal_m_left, internal_m_right, _ = calculate_major_aligned_margins_x(
                cell_width_abs, adj_x_spacing, 0, major_every
            )
        else:
            internal_m_top, internal_m_bottom = calculate_adjusted_margins(
                cell_height_abs, adj_y_spacing, 0
            )
            internal_m_left, internal_m_right = calculate_adjusted_margins_x(
                cell_width_abs, adj_x_spacing, 0
            )

        # 4d. Define Final Drawing Boundaries
        draw_x_start = cell_x_start_abs + internal_m_left
        draw_x_end = cell_x_end_abs - internal_m_right
        draw_y_start = cell_y_start_abs + internal_m_top
        draw_y_end = cell_y_end_abs - internal_m_bottom

        # Dispatch
        if template_type == "lined":
            # Build clean kwargs
            draw_kwargs = {
                "line_width": json_kwargs.get("line_width_px", 0.5),
                "skip_first": json_kwargs.get("skip_first", False),
                "skip_last": json_kwargs.get("skip_last", False),
                "major_every": json_kwargs.get("major_every"),
                "major_width_add_px": json_kwargs.get("major_width_add_px", 1.5),
            }
            drawing.draw_lined_section(
                ctx,
                draw_x_start,
                draw_x_end,
                draw_y_start,
                draw_y_end,
                region_spacing_px,
                **draw_kwargs,
            )

            # Check for line numbering config in the region
            if "line_number_config" in region:
                from .drawing import draw_line_numbering  # Local import

                cfg = region["line_number_config"]
                print(f"  Note: Drawing line numbers for region '{name}'")
                draw_line_numbering(ctx, draw_y_start, draw_y_end, region_spacing_px, cfg)

        elif template_type == "dotgrid":
            # Use the dispatcher to handle major_every
            _draw_dotgrid_dispatcher(
                ctx,
                draw_x_start,
                draw_x_end,
                draw_y_start,
                draw_y_end,
                region_spacing_px,
                dot_radius=json_kwargs.get("dot_radius_px", 1.5),
                skip_first_row=json_kwargs.get("skip_first_row", False),
                skip_last_row=json_kwargs.get("skip_last_row", False),
                major_every=json_kwargs.get("major_every"),
                crosshair_size=json_kwargs.get("crosshair_size", 4),
            )

        elif template_type == "grid":
            # Build clean kwargs
            draw_kwargs = {
                "line_width": json_kwargs.get("line_width_px", 0.5),
                "skip_first_row": json_kwargs.get("skip_first_row", False),
                "skip_last_row": json_kwargs.get("skip_last_row", False),
                "major_every": json_kwargs.get("major_every"),
                "major_width_add_px": json_kwargs.get("major_width_add_px", 1.5),
                "crosshair_size": json_kwargs.get("crosshair_size", 4),
            }
            drawing.draw_grid(
                ctx,
                draw_x_start,
                draw_x_end,
                draw_y_start,
                draw_y_end,
                region_spacing_px,
                **draw_kwargs,
            )

            if "cell_label_config" in region:
                from .drawing import draw_cell_labeling  # Local import

                cfg = region["cell_label_config"]
                print(f"  Note: Drawing cell labels for region '{name}'")
                # We pass the full page height/width to the drawing function
                # so it can correctly place labels at the 'bottom' or 'right'
                draw_cell_labeling(
                    ctx, draw_x_start, draw_x_end, draw_y_start, draw_y_end, region_spacing_px, cfg
                )

            if "axis_label_config" in region:
                from .drawing import draw_axis_labeling  # Local import

                cfg = region["axis_label_config"]
                print(f"  Note: Drawing axis labels for region '{name}'")
                draw_axis_labeling(
                    ctx, draw_x_start, draw_x_end, draw_y_start, draw_y_end, region_spacing_px, cfg
                )

        elif template_type == "manuscript":
            # Build clean kwargs
            draw_kwargs = {
                "line_width": json_kwargs.get("line_width_px", 0.5),
                "midline_style": json_kwargs.get("midline_style", "dashed"),
                "ascender_opacity": json_kwargs.get("ascender_opacity", 0.3),
            }
            drawing.draw_manuscript_lines(
                ctx,
                draw_x_start,
                draw_x_end,
                draw_y_start,
                draw_y_end,
                region_spacing_px,
                **draw_kwargs,
            )

        elif template_type == "french_ruled":
            # Build clean kwargs
            draw_kwargs = {
                "line_width": json_kwargs.get("line_width_px", 0.5),
                "margin_line_offset_px": json_kwargs.get(
                    "margin_line_offset_px"
                ),  # None by default
                "show_vertical_lines": json_kwargs.get("show_vertical_lines", True),
            }
            drawing.draw_french_ruled(
                ctx,
                draw_x_start,
                draw_x_end,
                draw_y_start,
                draw_y_end,
                region_spacing_px,
                **draw_kwargs,
            )

        elif template_type == "music_staff":
            # Build clean kwargs
            draw_kwargs = {
                "line_width": json_kwargs.get("line_width_px", 0.5),
                "staff_gap_mm": json_kwargs.get("staff_gap_mm", 10),
                "staff_spacing_mm": region_spacing_mm,  # Pass mm
                "dpi": dpi,
            }
            drawing.draw_music_staff(
                ctx, draw_x_start, draw_x_end, draw_y_start, draw_y_end, **draw_kwargs
            )

        elif template_type == "isometric":
            # Build clean kwargs
            draw_kwargs = {
                "line_width": json_kwargs.get("line_width_px", 0.5),
                "major_every": json_kwargs.get("major_every"),
                "major_width_add_px": json_kwargs.get("major_width_add_px", 1.5),
            }
            drawing.draw_isometric_grid(
                ctx,
                draw_x_start,
                draw_x_end,
                draw_y_start,
                draw_y_end,
                region_spacing_px,
                **draw_kwargs,
            )

        elif template_type == "hexgrid":
            # Build clean kwargs
            draw_kwargs = {
                "line_width": json_kwargs.get("line_width_px", 0.5)
                # other hex kwargs like major_every could go here
            }
            drawing.draw_hex_grid(
                ctx,
                draw_x_start,
                draw_x_end,
                draw_y_start,
                draw_y_end,
                region_spacing_px,
                **draw_kwargs,
            )

        elif template_type:
            print(f"Warning: Unknown template type '{template_type}' in region '{name}'. Skipping.")

    # 5. Draw Title Element (if specified)
    # This draws *after* all other regions, so it appears on top.
    if "title_element" in config:
        print("  Drawing title element...")
        cover_config = config["title_element"]

        # Pass the page dimensions AND the content area boundaries
        # so region_rect works correctly.
        draw_title_element(
            ctx,
            width,
            height,
            cover_config,
            content_x_start,
            content_y_start,
            content_width,
            content_height,
        )

    return surface
