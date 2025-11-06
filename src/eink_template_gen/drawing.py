"""
Core drawing functions for template elements
"""

from math import pi, radians, sqrt

import cairo

from .devices import snap_to_eink_greyscale


def draw_lined_section(
    ctx,
    x_start,
    x_end,
    y_start,
    y_end,
    spacing_px,
    line_width,
    skip_first=False,
    skip_last=False,
    major_every=None,
    major_width_add_px=1.5,
):
    """
    Draw horizontal ruled lines in a bounded area with optional weight variation

    Args:
        ctx: Cairo context
        x_start: Left boundary (pixels)
        x_end: Right boundary (pixels)
        y_start: Top boundary (pixels)
        y_end: Bottom boundary (pixels)
        spacing_px: Spacing between lines (pixels)
        line_width: Width of lines (pixels)
        skip_first: If True, skip the line at y_start
        skip_last: If True, skip the line at y_end
        major_every: Draw every Nth line thicker (None = all lines same weight)
        major_width_add_px: Added width for major lines (default: 1.5)
    """
    ctx.set_source_rgb(0, 0, 0)

    # Calculate how many lines would fit in the space
    total_height = y_end - y_start
    num_lines = int(total_height // spacing_px) + 1

    # Adjust start and end based on skipping
    first_line_idx = 1 if skip_first else 0
    last_line_idx = num_lines - 2 if skip_last else num_lines - 1

    # Draw lines
    for i in range(first_line_idx, last_line_idx + 1):
        y = y_start + (i * spacing_px)

        # Determine line weight
        if major_every and (i % major_every == 0):
            ctx.set_line_width(line_width + major_width_add_px)
        else:
            ctx.set_line_width(line_width)

        ctx.move_to(x_start, y + 0.5)
        ctx.line_to(x_end, y + 0.5)
        ctx.stroke()


def draw_dot_grid(
    ctx,
    x_start,
    x_end,
    y_start,
    y_end,
    spacing_px,
    dot_radius,
    skip_first_row=False,
    skip_last_row=False,
):
    """
    Draw dot grid in a bounded area
    """
    ctx.set_source_rgb(0, 0, 0)

    # Calculate how many rows would fit
    total_height = y_end - y_start
    num_rows = int(total_height // spacing_px) + 1

    # Calculate how many columns would fit
    total_width = x_end - x_start
    num_cols = int(total_width // spacing_px) + 1

    # Adjust start and end based on skipping
    first_row_idx = 1 if skip_first_row else 0
    last_row_idx = num_rows - 2 if skip_last_row else num_rows - 1

    # Draw dots
    for row_idx in range(first_row_idx, last_row_idx + 1):
        y = y_start + (row_idx * spacing_px)
        for col_idx in range(num_cols):
            x = x_start + (col_idx * spacing_px)
            ctx.arc(x, y, dot_radius, 0, 2 * pi)
            ctx.fill()


def draw_grid(
    ctx,
    x_start,
    x_end,
    y_start,
    y_end,
    spacing_px,
    line_width,
    skip_first_row=False,
    skip_last_row=False,
    major_every=None,
    major_width_add_px=1.5,
    crosshair_size=4,
):
    """
    Draw full grid (horizontal and vertical lines) in a bounded area with optional weight variation and cross-hairs

    Args:
        ctx: Cairo context
        x_start: Left boundary (pixels)
        x_end: Right boundary (pixels)
        y_start: Top boundary (pixels)
        y_end: Bottom boundary (pixels)
        spacing_px: Spacing between grid lines (pixels)
        line_width: Width of lines (pixels)
        skip_first_row: If True, skip horizontal line at y_start
        skip_last_row: If True, skip horizontal line at y_end
        major_every: Draw every Nth line thicker (None = all lines same weight)
        major_width_add_px: Added width for major lines (default: 1.5)
        crosshair_size: Size of cross-hair extensions in pixels (default: 4)
    """
    ctx.set_source_rgb(0, 0, 0)

    # Calculate how many horizontal lines would fit
    total_height = y_end - y_start
    num_horizontal_lines = int(total_height // spacing_px) + 1

    # Calculate how many vertical lines would fit
    total_width = x_end - x_start
    num_vertical_lines = int(total_width // spacing_px) + 1

    # First pass: draw all lines normally
    first_row_idx = 1 if skip_first_row else 0
    last_row_idx = num_horizontal_lines - 2 if skip_last_row else num_horizontal_lines - 1

    for i in range(first_row_idx, last_row_idx + 1):
        y = y_start + (i * spacing_px)

        # Determine line weight
        if major_every and (i % major_every == 0):
            ctx.set_line_width(line_width + major_width_add_px)
        else:
            ctx.set_line_width(line_width)

        ctx.move_to(x_start, y + 0.5)
        ctx.line_to(x_end, y + 0.5)
        ctx.stroke()

    # Draw vertical lines
    for i in range(num_vertical_lines):
        x = x_start + (i * spacing_px)

        # Determine line weight
        if major_every and (i % major_every == 0):
            ctx.set_line_width(line_width + major_width_add_px)
        else:
            ctx.set_line_width(line_width)

        ctx.move_to(x + 0.5, y_start)
        ctx.line_to(x + 0.5, y_end)
        ctx.stroke()

    # Second pass: draw cross-hairs at major intersections
    if major_every and crosshair_size > 0:
        ctx.set_line_width(line_width + major_width_add_px)

        # Find major line indices
        major_row_indices = [
            i for i in range(first_row_idx, last_row_idx + 1) if i % major_every == 0
        ]
        major_col_indices = [i for i in range(num_vertical_lines) if i % major_every == 0]

        # Draw cross-hairs at each major intersection
        for row_idx in major_row_indices:
            y = y_start + (row_idx * spacing_px)
            for col_idx in major_col_indices:
                x = x_start + (col_idx * spacing_px)

                # Draw a full horizontal line segment
                ctx.move_to(x - crosshair_size + 0.5, y + 0.5)
                ctx.line_to(x + crosshair_size + 0.5, y + 0.5)
                ctx.stroke()

                # Draw a full vertical line segment
                ctx.move_to(x + 0.5, y - crosshair_size + 0.5)
                ctx.line_to(x + 0.5, y + crosshair_size + 0.5)
                ctx.stroke()


def draw_manuscript_lines(
    ctx,
    x_start,
    x_end,
    y_start,
    y_end,
    spacing_px,
    line_width,
    midline_style="dashed",
    ascender_opacity=0.3,
    skip_first=False,
    skip_last=False,
):
    """
    Draw manuscript lines for handwriting practice (4-line system)

    Args:
        ctx: Cairo context
        x_start: Left boundary (pixels)
        x_end: Right boundary (pixels)
        y_start: Top boundary (pixels)
        y_end: Bottom boundary (pixels)
        spacing_px: Spacing between baseline groups (pixels)
        line_width: Width of lines (pixels)
        midline_style: 'dashed' or 'dotted' for the midline
        ascender_opacity: Opacity for the ascender line (0.0-1.0 or 0-15)
        skip_first: If True, skip the first ascender line
        skip_last: If True, skip the last descender line
    """
    # Snap the ascender opacity to e-ink greyscale
    ascender_grey = snap_to_eink_greyscale(ascender_opacity)

    gap = spacing_px // 3

    y = y_start
    line_index = 0

    while y + spacing_px <= y_end:
        # Determine if this is the first or last line group
        is_first = line_index == 0
        is_last = y + spacing_px * 2 > y_end

        # Ascender line (light) - skip if first and skip_first is True
        if not (is_first and skip_first):
            ctx.set_source_rgb(ascender_grey, ascender_grey, ascender_grey)
            ctx.set_line_width(line_width)
            ctx.move_to(x_start, y + 0.5)
            ctx.line_to(x_end, y + 0.5)
            ctx.stroke()

        # Midline (dashed)
        ctx.set_source_rgb(0, 0, 0)
        if midline_style == "dashed":
            ctx.set_dash([5, 3])
        elif midline_style == "dotted":
            ctx.set_dash([2, 3])
        ctx.set_line_width(line_width)
        ctx.move_to(x_start, y + gap + 0.5)
        ctx.line_to(x_end, y + gap + 0.5)
        ctx.stroke()
        ctx.set_dash([])  # reset

        # Baseline (solid, slightly thicker)
        ctx.set_source_rgb(0, 0, 0)
        ctx.set_line_width(line_width * 1.5)
        ctx.move_to(x_start, y + (2 * gap) + 0.5)
        ctx.line_to(x_end, y + (2 * gap) + 0.5)
        ctx.stroke()

        # Descender line (solid) - skip if last and skip_last is True
        if not (is_last and skip_last):
            ctx.set_line_width(line_width)
            ctx.move_to(x_start, y + spacing_px + 0.5)
            ctx.line_to(x_end, y + spacing_px + 0.5)
            ctx.stroke()

        y += spacing_px
        line_index += 1


def draw_dot_grid_with_crosshairs(
    ctx,
    x_start,
    x_end,
    y_start,
    y_end,
    spacing_px,
    dot_radius,
    skip_first_row=False,
    skip_last_row=False,
    major_every=None,
    crosshair_size=4,
):
    """
    Draw dot grid with cross-hairs at major intersections
    """
    ctx.set_source_rgb(0, 0, 0)

    # Calculate how many rows and columns would fit
    total_height = y_end - y_start
    num_rows = int(total_height // spacing_px) + 1

    total_width = x_end - x_start
    num_cols = int(total_width // spacing_px) + 1

    # Adjust start and end based on skipping
    actual_y_start = y_start + spacing_px if skip_first_row else y_start

    if skip_last_row:
        actual_y_end = y_end - ((y_end - y_start) % spacing_px)
    else:
        actual_y_end = y_end

    # Draw dots
    row_idx = 0
    y = actual_y_start
    while y <= actual_y_end:
        col_idx = 0
        x = x_start
        while x <= x_end:
            ctx.arc(x, y, dot_radius, 0, 2 * pi)
            ctx.fill()
            x += spacing_px
            col_idx += 1
        y += spacing_px
        row_idx += 1

    # Draw cross-hairs at major intersections if requested
    if major_every and crosshair_size > 0:
        # Find major row and column indices
        major_row_indices = [i for i in range(num_rows) if i % major_every == 0]
        major_col_indices = [i for i in range(num_cols) if i % major_every == 0]

        # Draw cross-hairs at each major intersection
        for row_idx in major_row_indices:
            y = y_start + (row_idx * spacing_px)
            for col_idx in major_col_indices:
                x = x_start + (col_idx * spacing_px)

                # Draw cross-hair (4 small extensions from center)
                # Right extension
                ctx.move_to(x + dot_radius, y)
                ctx.line_to(x + crosshair_size, y)
                ctx.stroke()

                # Left extension
                ctx.move_to(x - crosshair_size, y)
                ctx.line_to(x - dot_radius, y)
                ctx.stroke()

                # Up extension
                ctx.move_to(x, y - crosshair_size)
                ctx.line_to(x, y - dot_radius)
                ctx.stroke()

                # Down extension
                ctx.move_to(x, y + dot_radius)
                ctx.line_to(x, y + crosshair_size)
                ctx.stroke()


def draw_french_ruled(
    ctx,
    x_start,
    x_end,
    y_start,
    y_end,
    spacing_px,
    line_width,
    margin_line_offset_px=None,
    margin_line_color=(1, 0, 0),
    margin_line_opacity=0.3,
    show_vertical_lines=True,
    skip_first=False,
    skip_last=False,
):
    """
    Draw French ruled (Seyès) lines for handwriting
    """
    # Draw horizontal lines using the existing major/minor system
    # Every 4th line (0, 4, 8, 12...) is thick
    draw_lined_section(
        ctx,
        x_start,
        x_end,
        y_start,
        y_end,
        spacing_px,
        line_width,
        skip_first=False,
        skip_last=False,
        major_every=4,
        major_width_add_px=2.0,
    )

    # Draw vertical lines if requested (every 4 * spacing)
    if show_vertical_lines:
        vertical_spacing_px = spacing_px * 4
        x = x_start
        ctx.set_source_rgb(0, 0, 0)
        ctx.set_line_width(line_width)
        while x <= x_end:
            ctx.move_to(x + 0.5, y_start)
            ctx.line_to(x + 0.5, y_end)
            ctx.stroke()
            x += vertical_spacing_px

    # Draw left margin line if specified
    if margin_line_offset_px:
        # Note: margin_line_offset_px is distance from *page* left, not m_left
        # Let's assume it's from m_left for now, as passed by template
        margin_x = x_start + margin_line_offset_px
        if margin_x < x_end:
            # Use greyscale snap for margin line
            grey_val = snap_to_eink_greyscale(margin_line_opacity)
            ctx.set_source_rgb(grey_val, grey_val, grey_val)  # Assuming red is not desired
            ctx.set_line_width(line_width * 1.5)
            ctx.move_to(margin_x + 0.5, y_start)
            ctx.line_to(margin_x + 0.5, y_end)
            ctx.stroke()


def draw_columns(
    ctx,
    width,
    height,
    dpi,
    num_columns,
    column_gap_mm,
    margin_mm,
    spacing_mm,
    template_type,
    template_kwargs,
    orientation="vertical",
):
    """
    Draw a multi-column layout with any template type
    (This is a simplified version, not fully margin-aware)
    """
    mm2px = dpi / 25.4
    base_margin = round(margin_mm * mm2px)
    gap_px = round(column_gap_mm * mm2px)

    # This function is complex and would need its own
    # margin calculations per-column.
    # For now, we just use the bounds given.

    columns = []

    if orientation == "vertical":
        # Side-by-side columns (vertical dividers)
        available_width = width - (2 * base_margin) - ((num_columns - 1) * gap_px)
        column_width = available_width // num_columns

        for i in range(num_columns):
            x_start = base_margin + (i * (column_width + gap_px))
            x_end = x_start + column_width
            y_start = base_margin
            y_end = height - base_margin

            columns.append({"x_start": x_start, "x_end": x_end, "y_start": y_start, "y_end": y_end})

            # Draw vertical separator after each column except the last
            if i < num_columns - 1:
                sep_x = x_end + (gap_px // 2)
                draw_separator(ctx, sep_x, y_start, y_end, grey=5)  # MODIFIED

    else:  # horizontal
        # Stacked columns (horizontal dividers)
        available_height = height - (2 * base_margin) - ((num_columns - 1) * gap_px)
        column_height = available_height // num_columns

        for i in range(num_columns):
            x_start = base_margin
            x_end = width - base_margin
            y_start = base_margin + (i * (column_height + gap_px))
            y_end = y_start + column_height

            columns.append({"x_start": x_start, "x_end": x_end, "y_start": y_start, "y_end": y_end})

            # Draw horizontal separator after each column except the last
            if i < num_columns - 1:
                sep_y = y_end + (gap_px // 2)
                ctx.set_line_width(1.0)
                # --- Use greyscale snap ---
                grey_val = snap_to_eink_greyscale(5)
                ctx.set_source_rgb(grey_val, grey_val, grey_val)
                ctx.move_to(x_start, sep_y + 0.5)
                ctx.line_to(x_end, sep_y + 0.5)
                ctx.stroke()

    return columns


def draw_music_staff(
    ctx, x_start, x_end, y_start, y_end, staff_spacing_mm, dpi, line_width, staff_gap_mm=10
):
    """
    Draw music staff lines (5-line staves for musical notation)
    """
    mm2px = dpi / 25.4
    line_spacing_px = int(staff_spacing_mm * mm2px)
    staff_gap_px = int(staff_gap_mm * mm2px)

    # Height of one complete staff (5 lines = 4 spaces between them)
    staff_height_px = line_spacing_px * 4

    # Total height needed for one staff plus gap
    staff_unit_px = staff_height_px + staff_gap_px

    ctx.set_source_rgb(0, 0, 0)
    ctx.set_line_width(line_width)

    y = y_start
    while y + staff_height_px <= y_end:
        # Draw 5 lines for this staff
        for line_num in range(5):
            line_y = y + (line_num * line_spacing_px)
            ctx.move_to(x_start, line_y + 0.5)
            ctx.line_to(x_end, line_y + 0.5)
            ctx.stroke()

        # Move to next staff position
        y += staff_unit_px


def draw_isometric_grid(
    ctx,
    x_start,
    x_end,
    y_start,
    y_end,
    spacing_px,
    line_width,
    major_every=None,
    major_width_add_px=1.5,
    crosshair_size=0,
):
    """
    Draw isometric grid (60° triangular pattern) using rotations.

    This method draws three sets of parallel lines, rotated at 0, 60,
    and 120 degrees.

    Args:
        ctx: Cairo context
        x_start: Left boundary (pixels)
        x_end: Right boundary (pixels)
        y_start: Top boundary (pixels)
        y_end: Bottom boundary (pixels)
        spacing_px: Perpendicular spacing between parallel lines (pixels)
        line_width: Width of grid lines (pixels)
        major_every: Make every Nth line thicker
        major_width_add_px: Multiplier for major line thickness
        crosshair_size: Size of cross-hair extensions (0 = disabled)
    """
    ctx.save()  # --- Save the original context state (Outer) ---
    ctx.set_source_rgb(0, 0, 0)

    width = x_end - x_start
    height = y_end - y_start

    # Center point for rotation
    cx = x_start + width / 2
    cy = y_start + height / 2

    # We need to draw lines on a "virtual" canvas that is large
    # enough to cover the real canvas when rotated.
    # The diagonal of the drawing area is a safe bet.
    diag = sqrt(width**2 + height**2)

    # Calculate how many lines we need to draw to cover the diagonal
    num_lines = int(diag / spacing_px) + 2
    if num_lines % 2 == 0:
        num_lines += 1  # Ensure odd number for symmetry around center

    # --- Helper to draw a simple parallel grid ---
    # This grid is centered at (0,0) relative to the current transform
    def draw_parallel_lines(spacing):
        for i in range(-num_lines // 2, num_lines // 2 + 1):
            offset = i * spacing

            # Determine line weight
            if major_every and (abs(i) % major_every == 0):
                ctx.set_line_width(line_width + major_width_add_px)
            else:
                ctx.set_line_width(line_width)

            # Draw a line 'diag' long, centered at the offset
            # We use 1.2 * diag just to be extra safe
            ctx.move_to(offset, -diag * 0.6)
            ctx.line_to(offset, diag * 0.6)
            ctx.stroke()

    # Set clipping region so lines don't go outside margins
    # This clip path is set ONCE and will be reset by the final ctx.restore()
    ctx.rectangle(x_start, y_start, width, height)
    ctx.clip()

    # --- Draw 3 sets of rotated lines ---

    # Set 1: 0 degrees (vertical)
    ctx.save()  # Save the clipped state
    ctx.translate(cx, cy)  # Move to center
    # Align grid to the center (no offset needed for centered grid)
    draw_parallel_lines(spacing_px)
    ctx.restore()  # Restore to clipped state

    # Set 2: 60 degrees
    ctx.save()  # Save the clipped state
    ctx.translate(cx, cy)  # Move to center
    ctx.rotate(radians(60))
    draw_parallel_lines(spacing_px)
    ctx.restore()  # Restore to clipped state

    # Set 3: 120 degrees
    ctx.save()  # Save the clipped state
    ctx.translate(cx, cy)  # Move to center
    ctx.rotate(radians(120))
    draw_parallel_lines(spacing_px)
    ctx.restore()  # Restore to clipped state

    # Reset clipping path and restore main context
    ctx.restore()  # --- Restore the original context state (Outer) ---

    # Cross-hair drawing for this method is very complex
    # and would require finding all 3-line intersections.
    pass


def _draw_isometric_crosshair(ctx, x, y, size):
    """Draw a small cross-hair at an isometric intersection"""
    # This function is retained but not called by the new grid logic
    ctx.move_to(x - size, y)
    ctx.line_to(x + size, y)
    ctx.stroke()

    ctx.move_to(x, y - size)
    ctx.line_to(x, y + size)
    ctx.stroke()


def _draw_hexagon(ctx, x_center, y_center, size_s):
    """
    Helper function to draw a single flat-top hexagon

    Args:
        ctx: Cairo context
        x_center: Center X coordinate
        y_center: Center Y coordinate
        size_s: Side length
    """
    hex_height = sqrt(3) * size_s

    ctx.move_to(x_center + size_s, y_center)  # Right
    ctx.line_to(x_center + size_s / 2, y_center - hex_height / 2)  # Top-right
    ctx.line_to(x_center - size_s / 2, y_center - hex_height / 2)  # Top-left
    ctx.line_to(x_center - size_s, y_center)  # Left
    ctx.line_to(x_center - size_s / 2, y_center + hex_height / 2)  # Bottom-left
    ctx.line_to(x_center + size_s / 2, y_center + hex_height / 2)  # Bottom-right
    ctx.close_path()
    ctx.stroke()


def draw_hex_grid(
    ctx,
    x_start,
    x_end,
    y_start,
    y_end,
    spacing_px,
    line_width,
    major_every=None,
    major_width_add_px=1.5,
    crosshair_size=0,
):
    """
    Draw a flat-top hexagonal grid

    Args:
        ctx: Cairo context
        x_start: Left boundary (pixels)
        x_end: Right boundary (pixels)
        y_start: Top boundary (pixels)
        y_end: Bottom boundary (pixels)
        spacing_px: Side length 's' of the hexagon
        line_width: Width of grid lines (pixels)
    """
    ctx.save()
    ctx.set_source_rgb(0, 0, 0)
    ctx.set_line_width(line_width)

    width = x_end - x_start
    height = y_end - y_start

    # 'spacing_px' is the side length (s)
    s = spacing_px

    # Calculate horizontal and vertical distances between hex centers
    v_dist = sqrt(3) * s
    h_dist = 1.5 * s

    # Calculate number of rows and columns needed to fill the space
    # Add 2 to draw partially outside the bounds to ensure full coverage
    num_rows = int(height / v_dist) + 2
    num_cols = int(width / h_dist) + 2

    # Set clipping region
    ctx.rectangle(x_start, y_start, width, height)
    ctx.clip()

    # Draw columns of hexagons
    for col in range(num_cols):
        x_c = x_start + (col * h_dist)

        for row in range(num_rows):
            # Calculate base y_center for the row
            y_c = y_start + (row * v_dist)

            # Stagger every other column
            if col % 2:
                y_c += v_dist / 2

            _draw_hexagon(ctx, x_c, y_c, s)

    ctx.restore()


# Draw Line Numbering
def draw_line_numbering(ctx, y_start, y_end, spacing_px, config):
    """
    Draws line numbers in the margin.

    Args:
        ctx: Cairo context
        y_start: Top boundary (pixels) of the lined area
        y_end: Bottom boundary (pixels) of the lined area
        spacing_px: Spacing between lines (pixels)
        config: Dictionary with numbering settings:
            {
                "side": "left" | "right",
                "interval": int,
                "margin_px": int,
                "font_size": int,
                "grey": int (0-15) | float (0.0-1.0)
            }
    """
    try:
        # --- 1. Setup Font and Color ---
        ctx.save()
        font_size = config.get("font_size", 18)
        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(font_size)

        # Set color
        grey_level = config.get("grey", 8)  # Default to 8 (#808080)
        grey_rgb = snap_to_eink_greyscale(grey_level)
        ctx.set_source_rgb(grey_rgb, grey_rgb, grey_rgb)

        # --- 2. Get Config ---
        interval = config.get("interval", 1)
        side = config.get("side", "left")
        margin_px = config.get("margin_px", 40)  # Horizontal pixel distance from *page edge*

        # --- 3. Calculate Line *Spaces* ---
        total_height = y_end - y_start
        # We are numbering the spaces *between* lines.
        num_spaces = int(total_height // spacing_px)

        # --- 4. Draw Numbers ---
        for i in range(num_spaces):  # Loop from 0 to num_spaces - 1
            line_count = i + 1  # 1-based indexing

            if line_count % interval == 0:
                # y is the y of the line *above* the space
                y = y_start + (i * spacing_px)
                line_num_str = str(line_count)

                # Get text size to center it
                extents = ctx.text_extents(line_num_str)
                text_width = extents.width
                text_height = extents.height

                # Center text in the *space below* the line
                text_y = (y + (spacing_px / 2)) + (text_height / 2)

                if side == "left":
                    # Center the number in the margin
                    text_x = margin_px - (text_width / 2)
                else:  # "right" side
                    # Get page width from context
                    page_width = ctx.get_target().get_width()
                    # Center number in the right margin
                    text_x = page_width - margin_px - (text_width / 2)

                ctx.move_to(text_x, text_y)
                ctx.show_text(line_num_str)

    except Exception as e:
        print(f"Error drawing line numbering: {e}")
    finally:
        ctx.restore()


def draw_cell_labeling(ctx, x_start, x_end, y_start, y_end, spacing_px, config):
    """
    Draws 'A, B, C' and '1, 2, 3' style labels in the page margins.

    Args:
        ctx: Cairo context
        x_start, x_end: Left/Right boundaries (pixels) of the grid area
        y_start, y_end: Top/Bottom boundaries (pixels) of the grid area
        spacing_px: Spacing between grid lines (pixels)
        config: Dictionary with labeling settings:
            {
                "x_axis_padding_px": int (padding from top/bottom grid edge),
                "x_axis_side": "top" | "bottom",
                "y_axis_padding_px": int (padding from left/right grid edge),
                "y_axis_side": "left" | "right",
                "font_size": int,
                "grey": int (0-15) | float (0.0-1.0)
            }
    """
    try:
        # --- 1. Setup Font and Color ---
        ctx.save()
        font_size = config.get("font_size", 16)
        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(font_size)

        grey_level = config.get("grey", 10)  # Default to 10 (#a0a0a0)
        grey_rgb = snap_to_eink_greyscale(grey_level)
        ctx.set_source_rgb(grey_rgb, grey_rgb, grey_rgb)

        # --- 2. Get Config ---
        y_axis_padding_px = config.get("y_axis_padding_px", 10)
        x_axis_padding_px = config.get("x_axis_padding_px", 10)
        y_axis_side = config.get("y_axis_side", "left")
        x_axis_side = config.get("x_axis_side", "bottom")  # Default to bottom

        # --- 3. Draw X-Axis Labels (A, B, C...) ---
        num_x_lines = int((x_end - x_start) // spacing_px) + 1
        for i in range(num_x_lines - 1):  # Loop stops one line sooner
            x_pos = x_start + (i * spacing_px)

            # Convert index to alphabet (A, B, ... Z, AA, AB, ...)
            label_str = ""
            n = i
            while n >= 0:
                label_str = chr(ord("A") + n % 26) + label_str
                n = n // 26 - 1
                if n < -1:
                    break  # Handle 0-case

            extents = ctx.text_extents(label_str)

            # Center text in the *space to the right* of the line
            text_x = (x_pos + (spacing_px / 2)) - (extents.width / 2)

            if x_axis_side == "top":
                text_y = y_start - x_axis_padding_px  # Baseline is above grid
            else:  # "bottom"
                text_y = y_end + x_axis_padding_px + font_size  # Baseline is below grid

            ctx.move_to(text_x, text_y)
            ctx.show_text(label_str)

        # --- 4. Draw Y-Axis Labels (1, 2, 3...) ---
        num_y_lines = int((y_end - y_start) // spacing_px) + 1
        for i in range(num_y_lines - 1):  # Loop stops one line sooner
            y_pos = y_start + (i * spacing_px)
            label_str = str(i + 1)  # 1-based index

            extents = ctx.text_extents(label_str)

            # Align text to grid
            if y_axis_side == "right":
                # Left-aligned: x_pos is the start of the text
                text_x = x_end + y_axis_padding_px
            else:  # "left"
                # Right-aligned: x_pos is the start of the text, so we subtract its width
                text_x = x_start - y_axis_padding_px - extents.width

            # Center text in the *space below* the line
            text_y = (y_pos + (spacing_px / 2)) + (extents.height / 2)

            ctx.move_to(text_x, text_y)
            ctx.show_text(label_str)

    except Exception as e:
        print(f"Error drawing cell labeling: {e}")
    finally:
        ctx.restore()


def draw_axis_labeling(ctx, x_start, x_end, y_start, y_end, spacing_px, config):
    """
    Draws '0, 5, 10' style plot numbering in the margins.

    Args:
        ctx: Cairo context
        x_start, x_end: Left/Right boundaries (pixels) of the grid area
        y_start, y_end: Top/Bottom boundaries (pixels) of the grid area
        spacing_px: Spacing between grid lines (pixels)
        config: Dictionary with labeling settings:
            {
                "origin": "topLeft" | "bottomLeft",
                "interval": int,
                "x_axis_padding_px": int (padding from top/bottom grid edge),
                "x_axis_side": "top" | "bottom",
                "y_axis_padding_px": int (padding from left/right grid edge),
                "y_axis_side": "left" | "right",
                "font_size": int,
                "grey": int (0-15) | float (0.0-1.0)
            }
    """
    try:
        # --- 1. Setup Font and Color ---
        ctx.save()
        font_size = config.get("font_size", 16)
        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(font_size)

        grey_level = config.get("grey", 10)  # Default to 10 (#a0a0a0)
        grey_rgb = snap_to_eink_greyscale(grey_level)
        ctx.set_source_rgb(grey_rgb, grey_rgb, grey_rgb)

        # --- 2. Get Config ---
        origin = config.get("origin", "topLeft")
        interval = config.get("interval", 1)
        if interval == 0:
            interval = 1  # Prevent divide-by-zero

        y_axis_padding_px = config.get("y_axis_padding_px", 10)
        x_axis_padding_px = config.get("x_axis_padding_px", 10)
        y_axis_side = config.get("y_axis_side", "left")
        x_axis_side = config.get("x_axis_side", "bottom")  # Default to bottom

        # --- 3. Calculate Grid Size ---
        num_x_lines = int((x_end - x_start) // spacing_px) + 1
        num_y_lines = int((y_end - y_start) // spacing_px) + 1

        # --- 4. Draw X-Axis Labels (Top/Bottom Margin) ---
        for i in range(num_x_lines):
            label = i  # X label is 'i' for both topLeft and bottomLeft

            if label % interval == 0:
                x_pos = x_start + (i * spacing_px)
                label_str = str(label)

                extents = ctx.text_extents(label_str)
                text_x = x_pos - (extents.width / 2)  # Center on the grid line

                if x_axis_side == "top":
                    text_y = y_start - x_axis_padding_px  # Baseline is above grid
                else:  # "bottom"
                    text_y = y_end + x_axis_padding_px + font_size  # Baseline is below grid

                ctx.move_to(text_x, text_y)
                ctx.show_text(label_str)

        # --- 5. Draw Y-Axis Labels (Left/Right Margin) ---
        for i in range(num_y_lines):
            # Determine the label based on origin
            if origin == "bottomLeft":
                label = (num_y_lines - 1) - i
            else:  # "topLeft" (default)
                label = i

            # Check if the LABEL is a multiple of interval
            if label % interval == 0:
                y_pos = y_start + (i * spacing_px)
                label_str = str(label)

                extents = ctx.text_extents(label_str)

                # Align text to grid
                if y_axis_side == "right":
                    # Left-aligned: x_pos is the start of the text
                    text_x = x_end + y_axis_padding_px
                else:  # "left"
                    # Right-aligned: x_pos is the start of the text, so we subtract its width
                    text_x = x_start - y_axis_padding_px - extents.width

                text_y = y_pos + (extents.height / 2)  # Center on grid line

                ctx.move_to(text_x, text_y)
                ctx.show_text(label_str)

    except Exception as e:
        print(f"Error drawing axis labeling: {e}")
    finally:
        ctx.restore()


# Add a fallback for the draw_separator function if it's not imported
# (though it should be from .separators)
try:
    from .separators import draw_separator
except ImportError:

    def draw_separator(ctx, x, y_start, y_end, line_width=1.0, opacity=0.3):
        """Fallback vertical separator line"""
        ctx.save()
        ctx.set_line_width(line_width)
        ctx.set_source_rgba(0, 0, 0, opacity)
        ctx.move_to(x + 0.5, y_start)
        ctx.line_to(x + 0.5, y_end)
        ctx.stroke()
        ctx.restore()
