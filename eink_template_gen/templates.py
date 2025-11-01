"""
Template creation functions
"""
import cairo
from math import sin, cos, tan, radians, sqrt
from .drawing import (
    draw_lined_section, 
    draw_dot_grid, 
    draw_grid, 
    draw_manuscript_lines,
    draw_french_ruled,
    draw_dot_grid_with_crosshairs,
    draw_music_staff,
    draw_isometric_grid,
    draw_hex_grid
)
from .separators import draw_separator_line, draw_separator
from .utils import (
    calculate_adjusted_margins, 
    calculate_adjusted_margins_x,
    calculate_major_aligned_margins,
    calculate_major_aligned_margins_x,
    parse_spacing
)

def create_hybrid_template(width, height, dpi, spacing_mm, margin_mm,
                          section_gap_mm, line_width_px, dot_radius_px,
                          header_separator=None, footer_separator=None,
                          split_ratio=0.6,
                          auto_adjust_spacing=True):
    """
    Create a hybrid template with lined section (left) and dot grid (right)
    """
    mm2px = dpi / 25.4

    if auto_adjust_spacing:
        from .utils import snap_spacing_to_clean_pixels
        adjusted_mm, spacing_px, was_adjusted = snap_spacing_to_clean_pixels(spacing_mm, dpi)
        if was_adjusted:
            print(f"Note: Adjusted spacing from {spacing_mm}mm to {adjusted_mm:.3f}mm for pixel-perfect alignment")
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
    
    # Draw header separator (using adjusted margins)
    if header_separator:
        draw_separator_line(ctx, m_left, width - m_right, m_top, style=header_separator)
    
    # Draw footer separator (using adjusted margins)
    if footer_separator:
        draw_separator_line(ctx, m_left, width - m_right, height - m_bottom, style=footer_separator)
    
    # draw lined section (left) with boundary skipping
    draw_lined_section(ctx, m_left, split_x - half_gap,
                      m_top, height - m_bottom,
                      spacing_px, line_width_px,
                      skip_first=header_separator is not None,
                      skip_last=footer_separator is not None)
    
    # draw dot grid section (right) with boundary skipping
    draw_dot_grid(ctx, split_x + half_gap, width - m_right,
                 m_top, height - m_bottom,
                 spacing_px, dot_radius_px,
                 skip_first_row=header_separator is not None,
                 skip_last_row=footer_separator is not None)
    
    # draw vertical separator between sections
    draw_separator(ctx, split_x, m_top, height - m_bottom)
    
    return surface

def create_lined_template(width, height, dpi, spacing_mm, margin_mm,
                         line_width_px,
                         header_separator=None, footer_separator=None,
                         major_every=None, major_width_add_px=1.5,
                         auto_adjust_spacing=True):
    """
    Create a simple lined template
    """
    mm2px = dpi / 25.4
    
    # Auto-adjust spacing if requested
    if auto_adjust_spacing:
        # This function needs to be imported from utils
        from .utils import snap_spacing_to_clean_pixels
        adjusted_mm, spacing_px, was_adjusted = snap_spacing_to_clean_pixels(spacing_mm, dpi)
        if was_adjusted:
            print(f"Note: Adjusted spacing from {spacing_mm}mm to {adjusted_mm:.3f}mm for pixel-perfect alignment")
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
    
    # Lined templates don't have a horizontal grid, so no x-adjustment
    m_left = base_margin
    m_right = base_margin
    
    # Calculate adjusted top/bottom margins
    content_height = height - (2 * base_margin)
    m_top, m_bottom = calculate_adjusted_margins(content_height, spacing_px, base_margin)
    
    # Draw header separator
    if header_separator:
        draw_separator_line(ctx, m_left, width - m_right, m_top, style=header_separator)
    
    # Draw footer separator
    if footer_separator:
        draw_separator_line(ctx, m_left, width - m_right, height - m_bottom, style=footer_separator)
    
    # draw lines with weight variation
    draw_lined_section(ctx, m_left, width - m_right,
                      m_top, height - m_bottom,
                      spacing_px, line_width_px,
                      skip_first=header_separator is not None,
                      skip_last=footer_separator is not None,
                      major_every=major_every,
                      major_width_add_px=major_width_add_px)
    
    return surface

def create_dotgrid_template(width, height, dpi, spacing_mm, margin_mm,
                           dot_radius_px,
                           header_separator=None, footer_separator=None,
                           major_every=None, major_width_add_px=1.5,
                           crosshair_size=4,
                           auto_adjust_spacing=True,
                           force_major_alignment=False):
    """
    Create a dot grid template
    """
    mm2px = dpi / 25.4

    if auto_adjust_spacing:
        from .utils import snap_spacing_to_clean_pixels
        adjusted_mm, spacing_px, was_adjusted = snap_spacing_to_clean_pixels(spacing_mm, dpi)
        if was_adjusted:
            print(f"Note: Adjusted spacing from {spacing_mm}mm to {adjusted_mm:.3f}mm for pixel-perfect alignment")
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
    
    # Calculate adjusted margins for both axes
    content_height = height - (2 * base_margin)
    content_width = width - (2 * base_margin)
    
    if force_major_alignment and major_every:
        from .utils import calculate_major_aligned_margins, calculate_major_aligned_margins_x
        m_top, m_bottom, num_v_units = calculate_major_aligned_margins(
            content_height, spacing_px, base_margin, major_every
        )
        m_left, m_right, num_h_units = calculate_major_aligned_margins_x(
            content_width, spacing_px, base_margin, major_every
        )
        print(f"Note: Force-aligned to {num_h_units}×{num_v_units} major units ({major_every}×{major_every} grid)")
    else:
        m_top, m_bottom = calculate_adjusted_margins(content_height, spacing_px, base_margin)
        m_left, m_right = calculate_adjusted_margins_x(content_width, spacing_px, base_margin)
    
    # Draw header separator
    if header_separator:
        draw_separator_line(ctx, m_left, width - m_right, m_top, style=header_separator)
    
    # Draw footer separator
    if footer_separator:
        draw_separator_line(ctx, m_left, width - m_right, height - m_bottom, style=footer_separator)
    
    # draw dot grid with crosshairs if major_every is specified
    if major_every:
        draw_dot_grid_with_crosshairs(ctx, m_left, width - m_right,
                     m_top, height - m_bottom,
                     spacing_px, dot_radius_px,
                     skip_first_row=header_separator is not None,
                     skip_last_row=footer_separator is not None,
                     major_every=major_every,
                     crosshair_size=crosshair_size)
    else:
        draw_dot_grid(ctx, m_left, width - m_right,
                     m_top, height - m_bottom,
                     spacing_px, dot_radius_px,
                     skip_first_row=header_separator is not None,
                     skip_last_row=footer_separator is not None)
    
    return surface

def create_grid_template(width, height, dpi, spacing_mm, margin_mm,
                        line_width_px,
                        header_separator=None, footer_separator=None,
                        major_every=None, major_width_add_px=1.5,
                        crosshair_size=3, no_crosshairs=False,
                        auto_adjust_spacing=True,
                        force_major_alignment=False):
    """
    Create a full grid template (horizontal and vertical lines)
    """
    mm2px = dpi / 25.4

    if auto_adjust_spacing:
        from .utils import snap_spacing_to_clean_pixels
        adjusted_mm, spacing_px, was_adjusted = snap_spacing_to_clean_pixels(spacing_mm, dpi)
        if was_adjusted:
            print(f"Note: Adjusted spacing from {spacing_mm}mm to {adjusted_mm:.3f}mm for pixel-perfect alignment")
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
    
    # Calculate adjusted margins for both axes
    content_height = height - (2 * base_margin)
    content_width = width - (2 * base_margin)
    
    if force_major_alignment and major_every:
        from .utils import calculate_major_aligned_margins, calculate_major_aligned_margins_x
        m_top, m_bottom, num_v_units = calculate_major_aligned_margins(
            content_height, spacing_px, base_margin, major_every
        )
        m_left, m_right, num_h_units = calculate_major_aligned_margins_x(
            content_width, spacing_px, base_margin, major_every
        )
        print(f"Note: Force-aligned to {num_h_units}×{num_v_units} major units ({major_every}×{major_every} grid)")
    else:
        m_top, m_bottom = calculate_adjusted_margins(content_height, spacing_px, base_margin)
        m_left, m_right = calculate_adjusted_margins_x(content_width, spacing_px, base_margin)

    # Calculate crosshair size
    actual_crosshair_size = 0 if no_crosshairs else crosshair_size
    
    # Draw header separator
    if header_separator:
        draw_separator_line(ctx, m_left, width - m_right, m_top, style=header_separator)
    
    # Draw footer separator
    if footer_separator:
        draw_separator_line(ctx, m_left, width - m_right, height - m_bottom, style=footer_separator)
    
    draw_grid(ctx, m_left, width - m_right,
             m_top, height - m_bottom,
             spacing_px, line_width_px,
             skip_first_row=header_separator is not None,
             skip_last_row=footer_separator is not None,
             major_every=major_every,
             major_width_add_px=major_width_add_px,
             crosshair_size=actual_crosshair_size)
    
    return surface

def create_manuscript_template(width, height, dpi, spacing_mm, margin_mm,
                              line_width_px,
                              header_separator=None, footer_separator=None,
                              midline_style='dashed', ascender_opacity=0.3,
                              auto_adjust_spacing=True):
    """
    Create a manuscript template for handwriting practice (4-line system)
    """
    mm2px = dpi / 25.4

    if auto_adjust_spacing:
        from .utils import snap_spacing_to_clean_pixels
        adjusted_mm, spacing_px, was_adjusted = snap_spacing_to_clean_pixels(spacing_mm, dpi)
        if was_adjusted:
            print(f"Note: Adjusted spacing from {spacing_mm}mm to {adjusted_mm:.3f}mm for pixel-perfect alignment")
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
    
    # No horizontal grid component, so no x-adjustment
    m_left = base_margin
    m_right = base_margin
    
    # Calculate adjusted top/bottom margins
    content_height = height - (2 * base_margin)
    m_top, m_bottom = calculate_adjusted_margins(content_height, spacing_px, base_margin)
    
    # Draw header separator
    if header_separator:
        draw_separator_line(ctx, m_left, width - m_right, m_top, style=header_separator)
    
    # Draw footer separator
    if footer_separator:
        draw_separator_line(ctx, m_left, width - m_right, height - m_bottom, style=footer_separator)
    
    # draw manuscript lines
    draw_manuscript_lines(ctx, m_left, width - m_right,
                         m_top, height - m_bottom,
                         spacing_px, line_width_px,
                         midline_style, ascender_opacity)
    
    return surface

def create_french_ruled_template(width, height, dpi, spacing_mm, margin_mm,
                                line_width_px,
                                header_separator=None, footer_separator=None,
                                margin_line_offset_mm=20, show_margin_line=True,
                                show_vertical_lines=True,
                                auto_adjust_spacing=True):
    """
    Create a French ruled (Seyès) template for handwriting
    """
    mm2px = dpi / 25.4

    if auto_adjust_spacing:
        from .utils import snap_spacing_to_clean_pixels
        adjusted_mm, spacing_px, was_adjusted = snap_spacing_to_clean_pixels(spacing_mm, dpi)
        if was_adjusted:
            print(f"Note: Adjusted spacing from {spacing_mm}mm to {adjusted_mm:.3f}mm for pixel-perfect alignment")
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

    # Calculate adjusted left/right margins
    # Vertical lines are spaced at 4 * spacing_px
    vertical_spacing_px = spacing_px * 4
    content_width = width - (2 * base_margin)
    m_left, m_right = calculate_adjusted_margins_x(content_width, vertical_spacing_px, base_margin)
    
    # Draw header separator
    if header_separator:
        draw_separator_line(ctx, m_left, width - m_right, m_top, style=header_separator)
    
    # Draw footer separator
    if footer_separator:
        draw_separator_line(ctx, m_left, width - m_right, height - m_bottom, style=footer_separator)
    
    # Calculate margin line offset
    margin_line_offset_px = round(margin_line_offset_mm * mm2px) if show_margin_line else None
    
    # draw French ruled lines
    draw_french_ruled(ctx, m_left, width - m_right,
                     m_top, height - m_bottom,
                     spacing_px, line_width_px,
                     margin_line_offset_px=margin_line_offset_px,
                     show_vertical_lines=show_vertical_lines)
    
    return surface

def create_music_staff_template(width, height, dpi, spacing_mm, margin_mm,
                               line_width_px,
                               header_separator=None, footer_separator=None,
                               staff_gap_mm=10,
                               auto_adjust_spacing=True):
    """
    Create a music staff template for musical notation
    """
    mm2px = dpi / 25.4

    if auto_adjust_spacing:
        from .utils import snap_spacing_to_clean_pixels
        adjusted_mm, spacing_px, was_adjusted = snap_spacing_to_clean_pixels(spacing_mm, dpi)
        if was_adjusted:
            print(f"Note: Adjusted spacing from {spacing_mm}mm to {adjusted_mm:.3f}mm for pixel-perfect alignment")
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
    
    # No horizontal grid component
    m_left = base_margin
    m_right = base_margin
    
    # Use the adjusted spacing_px
    line_spacing_px = spacing_px
    staff_gap_px = int(staff_gap_mm * mm2px)
    
    # Height of one complete staff (5 lines = 4 spaces) plus gap
    staff_height_px = line_spacing_px * 4
    staff_unit_px = staff_height_px + staff_gap_px
    
    # Calculate adjusted top/bottom margins to eliminate leftover space
    content_height = height - (2 * base_margin)
    m_top, m_bottom = calculate_adjusted_margins(content_height, staff_unit_px, base_margin)
    
    # Draw header separator
    if header_separator:
        draw_separator_line(ctx, m_left, width - m_right, m_top, style=header_separator)
    
    # Draw footer separator
    if footer_separator:
        draw_separator_line(ctx, m_left, width - m_right, height - m_bottom, style=footer_separator)
    
    # Draw music staves
    # We pass staff_spacing_mm (the original or adjusted mm) for consistency
    draw_music_staff(ctx, m_left, width - m_right,
                    m_top, height - m_bottom,
                    spacing_mm, dpi, line_width_px, staff_gap_mm)
    
    return surface

def create_isometric_template(width, height, dpi, spacing_mm, margin_mm,
                             line_width_px,
                             header_separator=None, footer_separator=None,
                             auto_adjust_spacing=True):
    """
    Create an isometric grid template for technical drawing
    """
    mm2px = dpi / 25.4

    if auto_adjust_spacing:
        from .utils import snap_spacing_to_clean_pixels  # Import if not at top
        adjusted_mm, spacing_px, was_adjusted = snap_spacing_to_clean_pixels(spacing_mm, dpi)
        if was_adjusted:
            print(f"Note: Adjusted spacing from {spacing_mm}mm to {adjusted_mm:.3f}mm for pixel-perfect alignment")
        spacing_mm = adjusted_mm  # Update for filename/reporting
    else:
        spacing_px = spacing_mm * mm2px
    
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    ctx = cairo.Context(surface)
    
    # white background
    ctx.set_source_rgb(1, 1, 1)
    ctx.paint()
    
    # calculate margins
    base_margin = round(margin_mm * mm2px)

    # The user's snapped 'spacing_px' is the PERPENDICULAR spacing (p).
    # This is what draw_isometric_grid expects.
    
    from math import sin, cos, tan, radians
    
    # 1. The perpendicular spacing 'p' is the user's snapped spacing.
    perpendicular_spacing_p = spacing_px

    # 2. Calculate the true VERTICAL repeating unit (the triangle height 'h').
    # h = p * tan(60)
    vertical_unit_h = perpendicular_spacing_p * tan(radians(60))

    # 3. Adjust Top/Bottom margins using this vertical unit.
    content_height = height - (2 * base_margin)
    m_top, m_bottom = calculate_adjusted_margins(content_height, vertical_unit_h, base_margin)

    # 4. Calculate the true HORIZONTAL repeating unit (the side length 's').
    # This is the spacing for the vertical 0-degree lines.
    # p = s * cos(30)  =>  s = p / cos(30)
    horizontal_unit_s = perpendicular_spacing_p / cos(radians(30))
    
    # 5. Adjust Left/Right margins using this horizontal unit.
    content_width = width - (2 * base_margin)
    m_left, m_right = calculate_adjusted_margins_x(content_width, horizontal_unit_s, base_margin)
    
    # Draw header separator
    if header_separator:
        draw_separator_line(ctx, m_left, width - m_right, m_top, style=header_separator)
    
    # Draw footer separator
    if footer_separator:
        draw_separator_line(ctx, m_left, width - m_right, height - m_bottom, style=footer_separator)
    
    # Draw isometric grid
    draw_isometric_grid(ctx, m_left, width - m_right,
                       m_top, height - m_bottom,
                       perpendicular_spacing_p, line_width_px) # Pass the original 'p'
    
    return surface

def create_hex_template(width, height, dpi, spacing_mm, margin_mm,
                         line_width_px,
                         header_separator=None, footer_separator=None,
                         auto_adjust_spacing=True):
    """
    Create a hexagonal grid template
    'spacing_mm' defines the side length of the hexagon
    """
    mm2px = dpi / 25.4

    if auto_adjust_spacing:
        from .utils import snap_spacing_to_clean_pixels
        adjusted_mm, spacing_px, was_adjusted = snap_spacing_to_clean_pixels(spacing_mm, dpi)
        if was_adjusted:
            print(f"Note: Adjusted spacing from {spacing_mm}mm to {adjusted_mm:.3f}mm for pixel-perfect alignment")
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
    
    # 'spacing_px' is the side length (s)
    s = spacing_px
    
    # Calculate horizontal and vertical distances between hex centers
    v_dist = sqrt(3) * s
    h_dist = 1.5 * s

    # Adjust margins based on the repeating grid units
    content_height = height - (2 * base_margin)
    m_top, m_bottom = calculate_adjusted_margins(content_height, v_dist, base_margin)
    
    content_width = width - (2 * base_margin)
    m_left, m_right = calculate_adjusted_margins_x(content_width, h_dist, base_margin)
    
    # Draw header separator
    if header_separator:
        draw_separator_line(ctx, m_left, width - m_right, m_top, style=header_separator)
    
    # Draw footer separator
    if footer_separator:
        draw_separator_line(ctx, m_left, width - m_right, height - m_bottom, style=footer_separator)
    
    # Draw hex grid
    draw_hex_grid(ctx, m_left, width - m_right,
                  m_top, height - m_bottom,
                  spacing_px, line_width_px)
    
    return surface

def create_column_template(width, height, dpi, spacing_mm, margin_mm,
                          num_columns, num_rows, column_gap_mm, row_gap_mm,
                          base_template, template_kwargs,
                          header_separator=None, footer_separator=None,
                          auto_adjust_spacing=True):
    """
    Create a multi-column, multi-row template with any base template type
    """
    mm2px = dpi / 25.4

    # This import is needed for the margin calculations
    from .utils import snap_spacing_to_clean_pixels
    
    if auto_adjust_spacing:
        adjusted_mm, spacing_px, was_adjusted = snap_spacing_to_clean_pixels(spacing_mm, dpi)
        if was_adjusted:
            print(f"Note: Adjusted spacing from {spacing_mm}mm to {adjusted_mm:.3f}mm for pixel-perfect alignment")
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
    
    if base_template == 'music_staff':
        # Use staff unit for page adjustment
        staff_gap_mm_val = template_kwargs.get('staff_gap_mm', 10)
        staff_gap_px = int(staff_gap_mm_val * mm2px)
        staff_height_px = spacing_px * 4
        page_adj_y_spacing = staff_height_px + staff_gap_px
    elif base_template == 'french_ruled':
        page_adj_x_spacing = spacing_px * 4
    elif base_template in ['lined', 'manuscript']:
        page_adj_x_spacing = 1 # No horizontal adjustment
        
    content_height_page = height - (2 * base_margin)
    m_top_page, m_bottom_page = calculate_adjusted_margins(content_height_page, page_adj_y_spacing, base_margin)
    
    content_width_page = width - (2 * base_margin)
    m_left_page, m_right_page = calculate_adjusted_margins_x(content_width_page, page_adj_x_spacing, base_margin)
    
    # Draw header separator (using page margins)
    if header_separator:
        draw_separator_line(ctx, m_left_page, width - m_right_page, m_top_page, style=header_separator)
    
    # Draw footer separator (using page margins)
    if footer_separator:
        draw_separator_line(ctx, m_left_page, width - m_right_page, height - m_bottom_page, style=footer_separator)
    
    # --- Cell Calculation & Drawing ---
    
    # Calculate cell dimensions based on *adjusted* page content area
    available_width = (width - m_left_page - m_right_page) - ((num_columns - 1) * col_gap_px)
    column_width = available_width // num_columns
    
    available_height = (height - m_top_page - m_bottom_page) - ((num_rows - 1) * row_gap_px)
    row_height = available_height // num_rows
    
    # Get the ruling orientation (e.g., vertical lines)
    ruling_orientation = template_kwargs.pop('orientation', 'horizontal')
    
    for r in range(num_rows):
        y_start_cell = m_top_page + (r * (row_height + row_gap_px))
        y_end_cell = y_start_cell + row_height
        
        for c in range(num_columns):
            x_start_cell = m_left_page + (c * (column_width + col_gap_px))
            x_end_cell = x_start_cell + column_width
            
            # --- SOLVE THE 'TODO': Internal Margin Adjustment ---
            # Calculate pixel-perfect margins *inside* this cell
            # to fill the space perfectly.
            
            cell_width = x_end_cell - x_start_cell
            cell_height = y_end_cell - y_start_cell

            # Use the same adjustment spacing as the page
            internal_m_top, internal_m_bottom = calculate_adjusted_margins(cell_height, page_adj_y_spacing, 0)
            internal_m_left, internal_m_right = calculate_adjusted_margins_x(cell_width, page_adj_x_spacing, 0)

            # Define the final drawing boundaries *inside* the cell
            draw_x_start = x_start_cell + internal_m_left
            draw_x_end = x_end_cell - internal_m_right
            draw_y_start = y_start_cell + internal_m_top
            draw_y_end = y_end_cell - internal_m_bottom
            
            # Determine if we need to skip drawing on separator lines
            skip_first = (r == 0) and (header_separator is not None)
            skip_last = (r == num_rows - 1) and (footer_separator is not None)
            
            # --- Draw content in the cell ---
            if base_template == 'lined':
                draw_lined_section(ctx, draw_x_start, draw_x_end, draw_y_start, draw_y_end,
                                 spacing_px, template_kwargs.get('line_width_px', 0.5),
                                 skip_first=skip_first, skip_last=skip_last,
                                 major_every=template_kwargs.get('major_every'),
                                 major_width_add_px=template_kwargs.get('major_width_add_px', 1.5))
            
            elif base_template == 'dotgrid':
                draw_dot_grid(ctx, draw_x_start, draw_x_end, draw_y_start, draw_y_end,
                            spacing_px, template_kwargs.get('dot_radius_px', 1.5),
                            skip_first_row=skip_first, skip_last_row=skip_last)
            
            elif base_template == 'grid':
                draw_grid(ctx, draw_x_start, draw_x_end, draw_y_start, draw_y_end,
                         spacing_px, template_kwargs.get('line_width_px', 0.5),
                         skip_first_row=skip_first, skip_last_row=skip_last,
                         major_every=template_kwargs.get('major_every'),
                         major_width_add_px=template_kwargs.get('major_width_add_px', 1.5),
                         crosshair_size=template_kwargs.get('crosshair_size', 3))
            
            elif base_template == 'manuscript':
                 draw_manuscript_lines(ctx, draw_x_start, draw_x_end, draw_y_start, draw_y_end,
                         spacing_px, template_kwargs.get('line_width_px', 0.5),
                         template_kwargs.get('midline_style', 'dashed'),
                         template_kwargs.get('ascender_opacity', 0.3))
            
            elif base_template == 'french_ruled':
                # Note: French ruled margin line probably won't work well in columns
                draw_french_ruled(ctx, draw_x_start, draw_x_end, draw_y_start, draw_y_end,
                         spacing_px, template_kwargs.get('line_width_px', 0.5),
                         margin_line_offset_px=None, # Disable margin line in columns
                         show_vertical_lines=True)
            
            elif base_template == 'music_staff':
                draw_music_staff(ctx, draw_x_start, draw_x_end, draw_y_start, draw_y_end,
                                spacing_mm, dpi, template_kwargs.get('line_width_px', 0.5),
                                template_kwargs.get('staff_gap_mm', 10))
            
            elif base_template == 'isometric':
                draw_isometric_grid(ctx, draw_x_start, draw_x_end, draw_y_start, draw_y_end,
                                    spacing_px, template_kwargs.get('line_width_px', 0.5))
            
            elif base_template == 'hexgrid':
                draw_hex_grid(ctx, draw_x_start, draw_x_end, draw_y_start, draw_y_end,
                              spacing_px, template_kwargs.get('line_width_px', 0.5))
            
            # --- Draw Column Separator ---
            if c < num_columns - 1:
                sep_x = x_end_cell + (col_gap_px // 2)
                # Draw separator line only in the vertical bounds of the page content
                draw_separator(ctx, sep_x, m_top_page, height - m_bottom_page)
        
        # --- Draw Row Separator ---
        if r < num_rows - 1:
            sep_y = y_end_cell + (row_gap_px // 2)
            ctx.set_line_width(1.0)
            ctx.set_source_rgba(0, 0, 0, 0.3)
            # Draw separator line only in the horizontal bounds of the page content
            ctx.move_to(m_left_page, sep_y + 0.5)
            ctx.line_to(width - m_right_page, sep_y + 0.5)
            ctx.stroke()
    
    return surface

def create_cell_grid_template(width, height, dpi, spacing_mm, margin_mm,
                              cell_definitions,  # <-- NEW
                              column_gap_mm, row_gap_mm,
                              header_separator=None, footer_separator=None,
                              auto_adjust_spacing=True):
    """
    Create a multi-column, multi-row template where each cell can be
    a different template type.
    """
    mm2px = dpi / 25.4
    from .utils import snap_spacing_to_clean_pixels, calculate_adjusted_margins, calculate_adjusted_margins_x
    
    # --- Page-level Margin Adjustment ---
    # This is the trickiest part. How do we align the page?
    # We must "nominate" a template type to govern the page alignment.
    # Let's use the top-left cell as the "master".
    
    master_template_type = cell_definitions[0][0]['type']
    master_kwargs = cell_definitions[0][0]['kwargs']
    
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
    
    if master_template_type == 'music_staff':
        staff_gap_mm_val = master_kwargs.get('staff_gap_mm', 10)
        staff_gap_px = int(staff_gap_mm_val * mm2px)
        staff_height_px = spacing_px * 4
        page_adj_y_spacing = staff_height_px + staff_gap_px
    elif master_template_type == 'french_ruled':
        page_adj_x_spacing = spacing_px * 4
    elif master_template_type in ['lined', 'manuscript']:
        page_adj_x_spacing = 1 # No horizontal adjustment
    
    content_height_page = height - (2 * base_margin)
    m_top_page, m_bottom_page = calculate_adjusted_margins(content_height_page, page_adj_y_spacing, base_margin)
    content_width_page = width - (2 * base_margin)
    m_left_page, m_right_page = calculate_adjusted_margins_x(content_width_page, page_adj_x_spacing, base_margin)
    
    if header_separator:
        draw_separator_line(ctx, m_left_page, width - m_right_page, m_top_page, style=header_separator)
    if footer_separator:
        draw_separator_line(ctx, m_left_page, width - m_right_page, height - m_bottom_page, style=footer_separator)
    
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
            template_type = cell_def['type']
            template_kwargs = cell_def['kwargs']
            
            # Calculate internal margins for *this cell*
            cell_width = x_end_cell - x_start_cell
            cell_height = y_end_cell - y_start_cell
            
            # --- Internal Alignment ---
            # We use the *master* page alignment for all cells
            # This ensures all internal cell content aligns across separators
            internal_m_top, internal_m_bottom = calculate_adjusted_margins(cell_height, page_adj_y_spacing, 0)
            internal_m_left, internal_m_right = calculate_adjusted_margins_x(cell_width, page_adj_x_spacing, 0)

            draw_x_start = x_start_cell + internal_m_left
            draw_x_end = x_end_cell - internal_m_right
            draw_y_start = y_start_cell + internal_m_top
            draw_y_end = y_end_cell - internal_m_bottom
            
            skip_first = (r == 0) and (header_separator is not None)
            skip_last = (r == num_rows - 1) and (footer_separator is not None)
            
            # --- BIG DISPATCH BLOCK ---
            # This calls the correct draw function based on the cell's type
            
            if template_type == 'lined':
                draw_lined_section(ctx, draw_x_start, draw_x_end, draw_y_start, draw_y_end,
                                 spacing_px, template_kwargs.get('line_width_px', 0.5),
                                 skip_first=skip_first, skip_last=skip_last,
                                 major_every=template_kwargs.get('major_every'),
                                 major_width_add_px=template_kwargs.get('major_width_add_px', 1.5))
            
            elif template_type == 'dotgrid':
                draw_dot_grid(ctx, draw_x_start, draw_x_end, draw_y_start, draw_y_end,
                            spacing_px, template_kwargs.get('dot_radius_px', 1.5),
                            skip_first_row=skip_first, skip_last_row=skip_last)
            
            elif template_type == 'grid':
                draw_grid(ctx, draw_x_start, draw_x_end, draw_y_start, draw_y_end,
                         spacing_px, template_kwargs.get('line_width_px', 0.5),
                         skip_first_row=skip_first, skip_last_row=skip_last,
                         major_every=template_kwargs.get('major_every'),
                         major_width_add_px=template_kwargs.get('major_width_add_px', 1.5),
                         crosshair_size=template_kwargs.get('crosshair_size', 4))
            
            elif template_type == 'manuscript':
                 draw_manuscript_lines(ctx, draw_x_start, draw_x_end, draw_y_start, draw_y_end,
                         spacing_px, template_kwargs.get('line_width_px', 0.5),
                         template_kwargs.get('midline_style', 'dashed'),
                         template_kwargs.get('ascender_opacity', 0.3))
            
            elif template_type == 'french_ruled':
                draw_french_ruled(ctx, draw_x_start, draw_x_end, draw_y_start, draw_y_end,
                         spacing_px, template_kwargs.get('line_width_px', 0.5),
                         margin_line_offset_px=None,
                         show_vertical_lines=True)
            
            elif template_type == 'music_staff':
                draw_music_staff(ctx, draw_x_start, draw_x_end, draw_y_start, draw_y_end,
                                spacing_mm, dpi, template_kwargs.get('line_width_px', 0.5),
                                template_kwargs.get('staff_gap_mm', 10))
            
            elif template_type == 'isometric':
                draw_isometric_grid(ctx, draw_x_start, draw_x_end, draw_y_start, draw_y_end,
                                    spacing_px, template_kwargs.get('line_width_px', 0.5))
            
            elif template_type == 'hexgrid':
                draw_hex_grid(ctx, draw_x_start, draw_x_end, draw_y_start, draw_y_end,
                              spacing_px, template_kwargs.get('line_width_px', 0.5))
            
            # --- Draw Separators ---
            if c < num_columns - 1:
                sep_x = x_end_cell + (col_gap_px // 2)
                draw_separator(ctx, sep_x, m_top_page, height - m_bottom_page)
        
        if r < num_rows - 1:
            sep_y = y_end_cell + (row_gap_px // 2)
            ctx.set_line_width(1.0)
            ctx.set_source_rgba(0, 0, 0, 0.3)
            ctx.move_to(m_left_page, sep_y + 0.5)
            ctx.line_to(width - m_right_page, sep_y + 0.5)
            ctx.stroke()
    
    return surface

def create_json_layout_template(config, device_config, margin_mm, auto_adjust=True, force_major_alignment=False):
    """
    Create a complex, ratio-based template from a JSON config object.
    This is the main "layout engine".
    """
    
    # 1. Setup Canvas and Device
    width = device_config['width']
    height = device_config['height']
    dpi = device_config['dpi']
    mm2px = dpi / 25.4
    
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    ctx = cairo.Context(surface)
    ctx.set_source_rgb(1, 1, 1) # White background
    ctx.paint()
    
    # 2. Setup Page Margins and Content Area
    base_margin = round(margin_mm * mm2px)
    
    # Get master spacing for page alignment
    master_spacing_mm = config.get('master_spacing_mm', 6)
    master_spacing_px, _, _, _, _ = parse_spacing(
        str(master_spacing_mm), dpi, auto_adjust=auto_adjust
    )
    
    # Calculate pixel-perfect page margins
    content_height_page = height - (2 * base_margin)
    m_top_page, m_bottom_page = calculate_adjusted_margins(content_height_page, master_spacing_px, base_margin)
    
    content_width_page = width - (2 * base_margin)
    # Use 1 for x-adj if master spacing is only for Y (most common)
    m_left_page, m_right_page = calculate_adjusted_margins_x(content_width_page, 1, base_margin)
    
    # Define the pixel-perfect content area
    content_x_start = m_left_page
    content_y_start = m_top_page
    content_width = width - m_left_page - m_right_page
    content_height = height - m_top_page - m_bottom_page
    
    print(f"Note: Page content area is {content_width}px × {content_height}px")
    
    # 3. Draw Page-Level Separators
    if config.get('header_separator'):
        draw_separator_line(ctx, m_left_page, width - m_right_page, m_top_page, 
                            style=config['header_separator'])
    
    if config.get('footer_separator'):
        draw_separator_line(ctx, m_left_page, width - m_right_page, height - m_bottom_page, 
                            style=config['footer_separator'])
    
    # 4. Draw Layout Regions
    if 'page_layout' not in config or not config['page_layout']:
        raise ValueError("JSON config must contain a 'page_layout' array with at least one region.")
        
    for region in config['page_layout']:
        name = region.get('name', 'Unnamed Region')
        print(f"  Drawing region: '{name}'")
        
        # 4a. Calculate Region Pixel Boundaries
        rect_percents = region.get('region_rect')
        if not rect_percents or len(rect_percents) != 4:
            raise ValueError(f"Region '{name}' has invalid or missing 'region_rect'. "
                             "Must be [x_start_p, y_start_p, width_p, height_p]")
        
        x_p, y_p, w_p, h_p = rect_percents
        
        cell_x_start_abs = content_x_start + (x_p * content_width)
        cell_y_start_abs = content_y_start + (y_p * content_height)
        cell_width_abs = w_p * content_width
        cell_height_abs = h_p * content_height
        cell_x_end_abs = cell_x_start_abs + cell_width_abs
        cell_y_end_abs = cell_y_start_abs + cell_height_abs

        # 4b. Get Region-Specific Spacing
        # Default to master spacing
        region_spacing_mm = region.get('spacing_mm', master_spacing_mm)
        region_spacing_px, _, _, _, _ = parse_spacing(
            str(region_spacing_mm), dpi, auto_adjust=auto_adjust
        )
        
        # 4c. Calculate Internal Pixel-Perfect Margins for this Region
        adj_y_spacing = region_spacing_px
        adj_x_spacing = region_spacing_px
        
        template_type = region.get('template')
        json_kwargs = region.get('kwargs', {})
        
        if template_type == 'french_ruled':
            adj_x_spacing = region_spacing_px * 4
        elif template_type in ['lined', 'manuscript']:
            adj_x_spacing = 1 # No x-adjustment
            
        major_every = json_kwargs.get('major_every')
        
        use_force_align = (force_major_alignment and 
                           major_every and 
                           template_type in ['grid', 'dotgrid'])
        
        if use_force_align:
            print(f"  Note: Applying major-force-alignment to region '{name}'")
            internal_m_top, internal_m_bottom, _ = calculate_major_aligned_margins(
                cell_height_abs, adj_y_spacing, 0, major_every
            )
            internal_m_left, internal_m_right, _ = calculate_major_aligned_margins_x(
                cell_width_abs, adj_x_spacing, 0, major_every
            )
        else:
            internal_m_top, internal_m_bottom = calculate_adjusted_margins(cell_height_abs, adj_y_spacing, 0)
            internal_m_left, internal_m_right = calculate_adjusted_margins_x(cell_width_abs, adj_x_spacing, 0)
        
        # 4d. Define Final Drawing Boundaries
        draw_x_start = cell_x_start_abs + internal_m_left
        draw_x_end = cell_x_end_abs - internal_m_right
        draw_y_start = cell_y_start_abs + internal_m_top
        draw_y_end = cell_y_end_abs - internal_m_bottom
        
        # Dispatch
        if template_type == 'lined':
            # Build clean kwargs
            draw_kwargs = {
                'line_width': json_kwargs.get('line_width_px', 0.5),
                'skip_first': json_kwargs.get('skip_first', False),
                'skip_last': json_kwargs.get('skip_last', False),
                'major_every': json_kwargs.get('major_every'),
                'major_width_add_px': json_kwargs.get('major_width_add_px', 1.5)
            }
            draw_lined_section(ctx, draw_x_start, draw_x_end, draw_y_start, draw_y_end,
                             region_spacing_px, **draw_kwargs)
        
        elif template_type == 'dotgrid':
            # Build clean kwargs
            draw_kwargs = {
                'dot_radius': json_kwargs.get('dot_radius_px', 1.5),
                'skip_first_row': json_kwargs.get('skip_first_row', False),
                'skip_last_row': json_kwargs.get('skip_last_row', False)
            }
            draw_dot_grid(ctx, draw_x_start, draw_x_end, draw_y_start, draw_y_end,
                        region_spacing_px, **draw_kwargs)
        
        elif template_type == 'grid':
            # Build clean kwargs
            draw_kwargs = {
                'line_width': json_kwargs.get('line_width_px', 0.5),
                'skip_first_row': json_kwargs.get('skip_first_row', False),
                'skip_last_row': json_kwargs.get('skip_last_row', False),
                'major_every': json_kwargs.get('major_every'),
                'major_width_add_px': json_kwargs.get('major_width_add_px', 1.5),
                'crosshair_size': json_kwargs.get('crosshair_size', 4)
            }
            draw_grid(ctx, draw_x_start, draw_x_end, draw_y_start, draw_y_end,
                     region_spacing_px, **draw_kwargs)
        
        elif template_type == 'manuscript':
             # Build clean kwargs
            draw_kwargs = {
                'line_width': json_kwargs.get('line_width_px', 0.5),
                'midline_style': json_kwargs.get('midline_style', 'dashed'),
                'ascender_opacity': json_kwargs.get('ascender_opacity', 0.3)
            }
            draw_manuscript_lines(ctx, draw_x_start, draw_x_end, draw_y_start, draw_y_end,
                     region_spacing_px, **draw_kwargs)
        
        elif template_type == 'french_ruled':
            # Build clean kwargs
            draw_kwargs = {
                'line_width': json_kwargs.get('line_width_px', 0.5),
                'margin_line_offset_px': json_kwargs.get('margin_line_offset_px'), # None by default
                'show_vertical_lines': json_kwargs.get('show_vertical_lines', True)
            }
            draw_french_ruled(ctx, draw_x_start, draw_x_end, draw_y_start, draw_y_end,
                     region_spacing_px, **draw_kwargs)
        
        elif template_type == 'music_staff':
            # Build clean kwargs
            draw_kwargs = {
                'line_width': json_kwargs.get('line_width_px', 0.5),
                'staff_gap_mm': json_kwargs.get('staff_gap_mm', 10),
                'staff_spacing_mm': region_spacing_mm,
                'dpi': dpi
            }
            draw_music_staff(ctx, draw_x_start, draw_x_end, draw_y_start, draw_y_end,
                             **draw_kwargs)
        
        elif template_type == 'isometric':
            # Build clean kwargs
            draw_kwargs = {
                'line_width': json_kwargs.get('line_width_px', 0.5),
                'major_every': json_kwargs.get('major_every'),
                'major_width_add_px': json_kwargs.get('major_width_add_px', 1.5)
            }
            draw_isometric_grid(ctx, draw_x_start, draw_x_end, draw_y_start, draw_y_end,
                                region_spacing_px, **draw_kwargs)
        
        elif template_type == 'hexgrid':
            # Build clean kwargs
            draw_kwargs = {
                'line_width': json_kwargs.get('line_width_px', 0.5)
                # other hex kwargs like major_every could go here
            }
            draw_hex_grid(ctx, draw_x_start, draw_x_end, draw_y_start, draw_y_end,
                          region_spacing_px, **draw_kwargs)
        
        elif template_type:
            print(f"Warning: Unknown template type '{template_type}' in region '{name}'. Skipping.")
            
        # --- END OF FIX ---

    return surface

# Template registry for easy lookup
TEMPLATE_REGISTRY = {
    'lined': create_lined_template,
    'dotgrid': create_dotgrid_template,
    'grid': create_grid_template,
    'hybrid_lined_dotgrid': create_hybrid_template,
    'manuscript': create_manuscript_template,
    'french_ruled': create_french_ruled_template,
    'music_staff': create_music_staff_template,
    'isometric': create_isometric_template,
    'hexgrid': create_hex_template,
}
