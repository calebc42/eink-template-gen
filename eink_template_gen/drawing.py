"""
Core drawing functions for template elements
"""
from math import pi, sin, cos, tan, radians, sqrt

def draw_lined_section(ctx, x_start, x_end, y_start, y_end, spacing_px, line_width, 
                      skip_first=False, skip_last=False, major_every=None, major_width_add_px=1.5):
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

def draw_dot_grid(ctx, x_start, x_end, y_start, y_end, spacing_px, dot_radius, skip_first_row=False, skip_last_row=False):
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

def draw_grid(ctx, x_start, x_end, y_start, y_end, spacing_px, line_width,
              skip_first_row=False, skip_last_row=False, 
              major_every=None, major_width_add_px=1.5, crosshair_size=4):
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
        major_row_indices = [i for i in range(first_row_idx, last_row_idx + 1) if i % major_every == 0]
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

def draw_manuscript_lines(ctx, x_start, x_end, y_start, y_end, spacing_px, 
                         line_width, midline_style='dashed', ascender_grey=14):
    """
    Draw manuscript lines for handwriting practice (4-line system)
    
    Args:
        ascender_grey: Greyscale for ascender line (default: 14 = #e0e0e0, very light)
    """
    # Snap the ascender grey to e-ink palette
    grey_value = snap_to_eink_greyscale(ascender_grey)
    
    gap = spacing_px // 3
    
    y = y_start
    while y + spacing_px <= y_end:
        ctx.set_source_rgb(grey_value, grey_value, grey_value)
        ctx.set_line_width(line_width)
        ctx.move_to(x_start, y + 0.5)
        ctx.line_to(x_end, y + 0.5)
        ctx.stroke()
        
        # Midline (dashed)
        ctx.set_source_rgb(0, 0, 0)
        if midline_style == 'dashed':
            ctx.set_dash([5, 3])
        elif midline_style == 'dotted':
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
        
        # Descender line (solid)
        ctx.set_line_width(line_width)
        ctx.move_to(x_start, y + spacing_px + 0.5)
        ctx.line_to(x_end, y + spacing_px + 0.5)
        ctx.stroke()
        
        y += spacing_px

def draw_dot_grid_with_crosshairs(ctx, x_start, x_end, y_start, y_end, spacing_px, dot_radius,
                                 skip_first_row=False, skip_last_row=False,
                                 major_every=None, crosshair_size=4):
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

def draw_french_ruled(ctx, x_start, x_end, y_start, y_end, spacing_px, 
                     line_width, margin_line_offset_px=None, 
                     margin_line_color=(1, 0, 0), margin_line_opacity=0.3,
                     show_vertical_lines=True):
    """
    Draw French ruled (Seyès) lines for handwriting
    """
    # Draw horizontal lines using the existing major/minor system
    # Every 4th line (0, 4, 8, 12...) is thick
    draw_lined_section(ctx, x_start, x_end, y_start, y_end, 
                      spacing_px, line_width,
                      skip_first=False, skip_last=False,
                      major_every=4, major_width_add_px=2.0)
    
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
            ctx.set_source_rgba(*margin_line_color, margin_line_opacity)
            ctx.set_line_width(line_width * 1.5)
            ctx.move_to(margin_x + 0.5, y_start)
            ctx.line_to(margin_x + 0.5, y_end)
            ctx.stroke()

def draw_columns(ctx, width, height, dpi, num_columns, column_gap_mm, 
                margin_mm, spacing_mm, template_type, template_kwargs,
                orientation='vertical'):
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
    
    if orientation == 'vertical':
        # Side-by-side columns (vertical dividers)
        available_width = width - (2 * base_margin) - ((num_columns - 1) * gap_px)
        column_width = available_width // num_columns
        
        for i in range(num_columns):
            x_start = base_margin + (i * (column_width + gap_px))
            x_end = x_start + column_width
            y_start = base_margin
            y_end = height - base_margin
            
            columns.append({
                'x_start': x_start,
                'x_end': x_end,
                'y_start': y_start,
                'y_end': y_end
            })
            
            # Draw vertical separator after each column except the last
            if i < num_columns - 1:
                sep_x = x_end + (gap_px // 2)
                draw_separator(ctx, sep_x, y_start, y_end)
    
    else:  # horizontal
        # Stacked columns (horizontal dividers)
        available_height = height - (2 * base_margin) - ((num_columns - 1) * gap_px)
        column_height = available_height // num_columns
        
        for i in range(num_columns):
            x_start = base_margin
            x_end = width - base_margin
            y_start = base_margin + (i * (column_height + gap_px))
            y_end = y_start + column_height
            
            columns.append({
                'x_start': x_start,
                'x_end': x_end,
                'y_start': y_start,
                'y_end': y_end
            })
            
            # Draw horizontal separator after each column except the last
            if i < num_columns - 1:
                sep_y = y_end + (gap_px // 2)
                ctx.set_line_width(1.0)
                ctx.set_source_rgba(0, 0, 0, 0.3)
                ctx.move_to(x_start, sep_y + 0.5)
                ctx.line_to(x_end, sep_y + 0.5)
                ctx.stroke()
    
    return columns

def draw_music_staff(ctx, x_start, x_end, y_start, y_end, staff_spacing_mm, dpi,
                    line_width, staff_gap_mm=10):
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

# def draw_isometric_grid(ctx, x_start, x_end, y_start, y_end, spacing_px, line_width,
#                        major_every=None, major_width_add_px=1.5, crosshair_size=0):
#     """
#     Draw isometric grid (60° triangular pattern) using rotations.
    
#     This method draws three sets of parallel lines, rotated at 0, 60,
#     and 120 degrees.
    
#     Args:
#         ctx: Cairo context
#         x_start: Left boundary (pixels)
#         x_end: Right boundary (pixels)
#         y_start: Top boundary (pixels)
#         y_end: Bottom boundary (pixels)
#         spacing_px: Perpendicular spacing between parallel lines (pixels)
#         line_width: Width of grid lines (pixels)
#         major_every: Make every Nth line thicker
#         major_width_add_px: Multiplier for major line thickness
#         crosshair_size: Size of cross-hair extensions (0 = disabled)
#     """
#     ctx.save()  # --- Save the original context state (Outer) ---
#     ctx.set_source_rgb(0, 0, 0)
    
#     width = x_end - x_start
#     height = y_end - y_start
    
#     # Center point for rotation
#     cx = x_start + width / 2
#     cy = y_start + height / 2
    
#     # We need to draw lines on a "virtual" canvas that is large
#     # enough to cover the real canvas when rotated.
#     # The diagonal of the drawing area is a safe bet.
#     diag = sqrt(width**2 + height**2)
    
#     # Calculate how many lines we need to draw to cover the diagonal
#     num_lines = int(diag / spacing_px) + 2
#     if num_lines % 2 == 0:
#         num_lines += 1  # Ensure odd number for symmetry around center

#     # --- Helper to draw a simple parallel grid ---
#     # This grid is centered at (0,0) relative to the current transform
#     def draw_parallel_lines(spacing):
#         for i in range(-num_lines // 2, num_lines // 2 + 1):
#             offset = i * spacing
            
#             # Determine line weight
#             if major_every and (abs(i) % major_every == 0):
#                 ctx.set_line_width(line_width * major_width_mult)
#             else:
#                 ctx.set_line_width(line_width)
            
#             # Draw a line 'diag' long, centered at the offset
#             # We use 1.2 * diag just to be extra safe
#             ctx.move_to(offset, -diag * 0.6)
#             ctx.line_to(offset, diag * 0.6)
#             ctx.stroke()
    
#     # Set clipping region so lines don't go outside margins
#     # This clip path is set ONCE and will be reset by the final ctx.restore()
#     ctx.rectangle(x_start, y_start, width, height)
#     ctx.clip()

#     # --- Draw 3 sets of rotated lines ---
    
#     # Set 1: 0 degrees (vertical)
#     ctx.save()  # Save the clipped state
#     ctx.translate(cx, cy) # Move to center
#     # Align grid to the center (no offset needed for centered grid)
#     draw_parallel_lines(spacing_px)
#     ctx.restore() # Restore to clipped state
    
#     # Set 2: 60 degrees
#     ctx.save()  # Save the clipped state
#     ctx.translate(cx, cy) # Move to center
#     ctx.rotate(radians(60))
#     draw_parallel_lines(spacing_px)
#     ctx.restore() # Restore to clipped state

#     # Set 3: 120 degrees
#     ctx.save()  # Save the clipped state
#     ctx.translate(cx, cy) # Move to center
#     ctx.rotate(radians(120))
#     draw_parallel_lines(spacing_px)
#     ctx.restore() # Restore to clipped state

#     # Reset clipping path and restore main context
#     ctx.restore()  # --- Restore the original context state (Outer) ---
    
#     # Cross-hair drawing for this method is very complex
#     # and would require finding all 3-line intersections.
#     pass

def draw_isometric_grid(ctx, x_start, x_end, y_start, y_end, spacing_px, line_width,
                       major_every=None, major_width_add_px=1.5, crosshair_size=0):
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
    ctx.translate(cx, cy) # Move to center
    # Align grid to the center (no offset needed for centered grid)
    draw_parallel_lines(spacing_px)
    ctx.restore() # Restore to clipped state
    
    # Set 2: 60 degrees
    ctx.save()  # Save the clipped state
    ctx.translate(cx, cy) # Move to center
    ctx.rotate(radians(60))
    draw_parallel_lines(spacing_px)
    ctx.restore() # Restore to clipped state

    # Set 3: 120 degrees
    ctx.save()  # Save the clipped state
    ctx.translate(cx, cy) # Move to center
    ctx.rotate(radians(120))
    draw_parallel_lines(spacing_px)
    ctx.restore() # Restore to clipped state

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
    
    ctx.move_to(x_center + size_s, y_center) # Right
    ctx.line_to(x_center + size_s / 2, y_center - hex_height / 2) # Top-right
    ctx.line_to(x_center - size_s / 2, y_center - hex_height / 2) # Top-left
    ctx.line_to(x_center - size_s, y_center) # Left
    ctx.line_to(x_center - size_s / 2, y_center + hex_height / 2) # Bottom-left
    ctx.line_to(x_center + size_s / 2, y_center + hex_height / 2) # Bottom-right
    ctx.close_path()
    ctx.stroke()

def draw_hex_grid(ctx, x_start, x_end, y_start, y_end, spacing_px, line_width,
                  major_every=None, major_width_add_px=1.5, crosshair_size=0):
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
