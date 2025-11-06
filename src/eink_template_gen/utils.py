"""
Utility functions for template generation
"""

import os


def calculate_adjusted_margins(content_height, spacing_px, base_margin):
    """
    Calculate adjusted top/bottom margins to eliminate leftover space

    Args:
        content_height: Total height available for content
        spacing_px: Spacing between lines in pixels
        base_margin: Original margin size

    Returns:
        Tuple of (top_margin, bottom_margin)
    """
    # Calculate how many complete lines fit
    num_lines = int(content_height / spacing_px)

    # Calculate total space used by lines
    total_line_space = num_lines * spacing_px

    # Calculate remaining space
    remaining_space = content_height - total_line_space

    # Split remaining space and add to margins
    top_addition = int(remaining_space // 2)
    bottom_addition = int(remaining_space - top_addition)  # handles odd pixels

    return base_margin + top_addition, base_margin + bottom_addition


def calculate_adjusted_margins_x(content_width, spacing_px, base_margin):
    """
    Calculate adjusted left/right margins to eliminate leftover space

    Args:
        content_width: Total width available for content
        spacing_px: Spacing between vertical lines in pixels
        base_margin: Original margin size

    Returns:
        Tuple of (left_margin, right_margin)
    """
    # Calculate how many complete lines fit
    num_lines = int(content_width / spacing_px)

    # Calculate total space used by lines
    total_line_space = num_lines * spacing_px

    # Calculate remaining space
    remaining_space = content_width - total_line_space

    # Split remaining space and add to margins
    left_addition = int(remaining_space // 2)
    right_addition = int(remaining_space - left_addition)  # handles odd pixels

    return base_margin + left_addition, base_margin + right_addition


def generate_filename(template_type, **kwargs):
    """
    Generate a descriptive, relative filename based on template params.

    Args:
        template_type: The base command/type (e.g., 'lined', 'grid', 'title')
        **kwargs: All other parameters from argparse (ideally vars(args)).
                Should include 'spacing' (or 'lines') and 'spacing_mode'.

    Returns:
        Relative path string (e.g., "lined/7mm_w0_5px_lnums.png")
    """
    parts = []

    # --- 1. Primary Descriptor (Spacing or Line Count) ---
    if kwargs.get("lines"):
        # Line count mode (e.g., --lines 40x30)
        lines_str = str(kwargs["lines"])  # This will be "40x30"
        parts.append(lines_str)
        if kwargs.get("enforce_exact_spacing"):
            parts.append("exact")
    else:
        # Spacing mode (e.g., --spacing 7)
        spacing_str_val = kwargs.get("spacing", "6")
        # 'spacing_mode' should be passed in kwargs by the caller
        # (after calling parse_spacing)
        spacing_mode = kwargs.get("spacing_mode", "mm")

        if spacing_mode == "px":
            # --- Clean up pixel values ---
            try:
                # Handle "71.0px" from --lines mode
                spacing_str_val = str(int(float(spacing_str_val)))
            except ValueError:
                # Handle "71px"
                spacing_str_val = str(spacing_str_val).replace("px", "")
            spacing_str = f"{spacing_str_val}px"
        else:  # 'mm'
            # --- Use original mm string ---
            spacing_str_val = str(spacing_str_val).replace("mm", "").replace(".", "_")
            spacing_str = f"{spacing_str_val}mm"
        parts.append(spacing_str)

    # --- 2. Core Style (Widths, Gaps) ---
    if "line_width_px" in kwargs:
        lw = kwargs["line_width_px"]
        lw_str = str(lw).replace(".", "_")
        parts.append(f"w{lw_str}px")  # 'w' for width

    if "dot_radius_px" in kwargs:
        dr = kwargs["dot_radius_px"]
        dr_str = str(dr).replace(".", "_")
        parts.append(f"dr{dr_str}px")  # 'dr' for dot radius

    if "staff_gap_mm" in kwargs:
        sg = kwargs["staff_gap_mm"]
        sg_str = str(sg).replace(".", "_")
        parts.append(f"gap{sg_str}mm")

    if "section_gap_mm" in kwargs:
        sg = kwargs["section_gap_mm"]
        sg_str = str(sg).replace(".", "_")
        parts.append(f"sgap{sg_str}mm")

    # --- 3. Grid/Multi Layout ---
    columns = kwargs.get("columns", 1)
    rows = kwargs.get("rows", 1)

    if rows > 1 or columns > 1:
        parts.append(f"{rows}r_by_{columns}c")  # e.g., "2r_by_3c"

    if "section_gap_cols" in kwargs or "section_gap_rows" in kwargs:
        # Mirrors the logic in your multi parser
        spacing_val = kwargs.get("spacing", "6")
        scg = kwargs.get("section_gap_cols", spacing_val)
        srg = kwargs.get("section_gap_rows", spacing_val)

        scg_str = str(scg).replace(".", "_")
        srg_str = str(srg).replace(".", "_")

        if scg is not None:
            parts.append(f"cgap{scg_str}mm")
        if srg is not None:
            parts.append(f"rgap{srg_str}mm")

    if kwargs.get("orientation") == "vertical":
        parts.append("vertical")

    if "split_ratio" in kwargs:
        try:
            ratio_float = float(kwargs["split_ratio"])
            ratio_p1 = int(ratio_float * 100)
            ratio_p2 = 100 - ratio_p1
            parts.append(f"{ratio_p1}-{ratio_p2}split")
        except (ValueError, TypeError):
            parts.append(f"ratio{kwargs['split_ratio']}")

    # --- 4. Major Lines / Grids ---
    if kwargs.get("major_every"):  # Check for non-zero, non-None
        parts.append(f"maj{kwargs['major_every']}")
        if "major_width_add_px" in kwargs:
            mw = kwargs["major_width_add_px"]
            mw_str = str(mw).replace(".", "_")
            parts.append(f"maj_w_add{mw_str}px")

    if kwargs.get("crosshair_size") and kwargs.get("major_every"):
        cs = kwargs["crosshair_size"]
        parts.append(f"cross{cs}px")

    if kwargs.get("no_crosshairs"):
        parts.append("no_cross")

    # --- 5. Labels & Numbers ---
    if kwargs.get("line_numbers"):
        parts.append("lnums")
    if kwargs.get("cell_labels"):
        parts.append("cell_labels")
    if kwargs.get("axis_labels"):
        parts.append("axis_labels")

    # --- 6. Other Style Variants ---
    if kwargs.get("midline_style") == "dotted":  # Only if not default 'dashed'
        parts.append("dotted_mid")

    # --- 7. Separators ---
    header_sep = kwargs.get("header_separator")  # from --header-sep
    if header_sep:
        parts.append(f"h-{header_sep}")

    footer_sep = kwargs.get("footer_separator")  # from --footer-sep
    if footer_sep:
        parts.append(f"f-{footer_sep}")

    # --- 8. Assemble Path ---

    # Handle 'title' command, which has a sub-type
    if template_type == "title":
        # The actual cover type is in kwargs['title'] (e.g., 'truchet')
        cover_type = kwargs.get("title", "unknown_cover")
        base_dir = os.path.join(template_type, cover_type)  # e.g., "title/truchet"

        # Add title-specific details
        if kwargs.get("truchet_seed"):
            parts.append(f"seed{kwargs['truchet_seed']}")
        if kwargs.get("noise_seed"):
            parts.append(f"seed{kwargs['noise_seed']}")
        if kwargs.get("title_text"):
            parts.append("titled")  # Don't include the text, just that it has it

    else:
        base_dir = template_type  # e.g., "lined"

    # Filter out empty parts (e.g., if a kwarg was None)
    clean_parts = [part for part in parts if part is not None]

    filename = "_".join(clean_parts) + ".png"

    # Use os.path.join to create the relative path
    relative_path = os.path.join(base_dir, filename)

    return relative_path


def mm_to_px(mm, dpi):
    """
    Convert millimeters to pixels

    Args:
        mm: Measurement in millimeters
        dpi: Device DPI

    Returns:
        Pixels (float)
    """
    return (dpi / 25.4) * mm


def px_to_mm(px, dpi):
    """
    Convert pixels to millimeters

    Args:
        px: Measurement in pixels
        dpi: Device DPI

    Returns:
        Millimeters (float)
    """
    return (px * 25.4) / dpi


# In utils.py


def snap_spacing_to_clean_pixels(spacing_mm, dpi, tolerance_mm=0.5):
    """
    Adjust spacing to nearest value that produces integer pixels

    Args:
        spacing_mm: Desired spacing in millimeters
        dpi: Device DPI
        tolerance_mm: Maximum adjustment allowed (default: 0.5mm)

    Returns:
        Tuple of (adjusted_spacing_mm, spacing_px, was_adjusted)
    """
    mm2px = dpi / 25.4
    ideal_px = spacing_mm * mm2px

    # Try rounding to nearest integer
    rounded_px = round(ideal_px)
    adjusted_mm = rounded_px / mm2px

    # Check if adjustment is within tolerance
    adjustment = abs(adjusted_mm - spacing_mm)

    if adjustment <= tolerance_mm:
        return adjusted_mm, float(rounded_px), adjustment > 0.001
    else:
        # Keep original if adjustment would be too large
        return spacing_mm, ideal_px, False


def get_clean_spacing_options(dpi, min_mm=2, max_mm=15, step_mm=0.5):
    """
    Generate list of spacing values that produce clean integer pixels

    Args:
        dpi: Device DPI
        min_mm: Minimum spacing in mm
        max_mm: Maximum spacing in mm
        step_mm: Step size for checking

    Returns:
        List of (spacing_mm, spacing_px) tuples that are pixel-perfect
    """
    mm2px = dpi / 25.4
    clean_options = []

    current = min_mm
    while current <= max_mm:
        px = current * mm2px
        # Check if it's close to an integer (within 0.1%)
        if abs(px - round(px)) < 0.001:
            clean_options.append((round(current, 3), round(px)))
        current += step_mm

    return clean_options


def parse_spacing(spacing_str, dpi, auto_adjust=True):
    """
    Parse spacing string and return pixel value

    Supports two modes:
    - MM mode: "6mm" or "6" → Auto-adjusts to nearest pixel-perfect value
    - PX mode: "71px" → Uses exact pixel value

    Args:
        spacing_str: Spacing string like "6mm", "71px", "6.5mm", or "6"
        dpi: Device DPI
        auto_adjust: Whether to auto-adjust mm values for pixel perfection

    Returns:
        Tuple of (spacing_px, original_mm, adjusted_mm, was_adjusted, mode)

    Examples:
        parse_spacing("6mm", 300, True) → (71.0, 6.0, 6.011, True, 'mm')
        parse_spacing("71px", 300, True) → (71.0, 6.011, 6.011, False, 'px')
        parse_spacing("6", 300, True) → (71.0, 6.0, 6.011, True, 'mm')
    """
    spacing_str = str(spacing_str).lower().strip()
    mm2px = dpi / 25.4

    # Determine mode based on suffix
    if spacing_str.endswith("px"):
        # PX mode - exact pixels
        mode = "px"
        spacing_px = float(spacing_str[:-2])
        original_mm = spacing_px / mm2px
        adjusted_mm = original_mm
        was_adjusted = False

    elif spacing_str.endswith("mm"):
        # MM mode - millimeters
        mode = "mm"
        original_mm = float(spacing_str[:-2])

        if auto_adjust:
            adjusted_mm, spacing_px, was_adjusted = snap_spacing_to_clean_pixels(original_mm, dpi)
        else:
            spacing_px = original_mm * mm2px
            adjusted_mm = original_mm
            was_adjusted = False

    else:
        # No unit - assume mm
        mode = "mm"
        original_mm = float(spacing_str)

        if auto_adjust:
            adjusted_mm, spacing_px, was_adjusted = snap_spacing_to_clean_pixels(original_mm, dpi)
        else:
            spacing_px = original_mm * mm2px
            adjusted_mm = original_mm
            was_adjusted = False

    return (spacing_px, original_mm, adjusted_mm, was_adjusted, mode)


def format_spacing_summary(spacing_px, original_mm, adjusted_mm, was_adjusted, mode):
    """
    Format spacing information for CLI summary display

    Args:
        spacing_px: Spacing in pixels
        original_mm: Original mm value (user input)
        adjusted_mm: Adjusted mm value (may equal original)
        was_adjusted: Whether adjustment occurred
        mode: 'mm' or 'px'

    Returns:
        Human-readable string describing the spacing
    """
    if mode == "px":
        return f"{int(spacing_px)}px (≈{original_mm:.2f}mm)"
    elif was_adjusted:
        return f"{adjusted_mm:.3f}mm ({int(spacing_px)}px, adjusted from {original_mm}mm)"
    else:
        return f"{original_mm}mm (≈{spacing_px:.1f}px)"


def print_spacing_info(spacing_str, dpi, device_name):
    """
    Print detailed spacing information for analysis

    Args:
        spacing_str: Spacing string to analyze
        dpi: Device DPI
        device_name: Device name for display
    """
    spacing_px, original_mm, adjusted_mm, was_adjusted, mode = parse_spacing(
        spacing_str, dpi, auto_adjust=True
    )

    print(f"\n{'=' * 80}")
    print(f"SPACING ANALYSIS for {device_name} ({dpi} DPI)")
    print("=" * 80)

    if mode == "px":
        print(f"Input: {int(spacing_px)}px")
        print(f"Equivalent: {original_mm:.4f}mm")
        print("\n✓ PIXEL-PERFECT (exact pixels specified)")
        print("  No adjustment needed")
    else:
        print(f"Input: {original_mm}mm")
        print(f"Exact pixels: {original_mm * dpi / 25.4:.4f}px")

        if was_adjusted:
            print("\n⚙️  AUTO-ADJUSTMENT AVAILABLE")
            print(f"  Original: {original_mm}mm = {original_mm * dpi / 25.4:.4f}px")
            print(f"  Adjusted: {adjusted_mm:.4f}mm = {int(spacing_px)}px (pixel-perfect)")
            print(
                f"  Difference: {abs(adjusted_mm - original_mm):.4f}mm ({abs(adjusted_mm - original_mm) / original_mm * 100:.2f}%)"
            )

            # Calculate error accumulation
            error_per_line = (original_mm * dpi / 25.4) - int(original_mm * dpi / 25.4)
            if error_per_line > 0.5:
                error_per_line -= 1
            error_40_lines = abs(error_per_line * 40)

            print("\n  Without adjustment:")
            print(f"    Error per line: {abs(error_per_line):.4f}px")
            print(f"    Accumulated over 40 lines: {error_40_lines:.2f}px")
        else:
            print("\n✓ ALREADY PIXEL-PERFECT")
            print(f"  Spacing is exactly {int(spacing_px)} pixels")
            print("  No adjustment needed")

    print("=" * 80)


def calculate_major_aligned_margins(content_dimension, spacing_px, base_margin, major_every):
    """
    Calculate margins that force grid to end on major lines

    Args:
        content_dimension: Available space (width or height) in pixels
        spacing_px: Spacing between grid lines in pixels
        base_margin: Original margin size in pixels
        major_every: Make every Nth line a major line

    Returns:
        Tuple of (start_margin, end_margin, num_complete_major_units)
    """
    if not major_every or major_every <= 0:
        # Fall back to normal behavior if major_every not specified
        return calculate_adjusted_margins(content_dimension, spacing_px, base_margin)

    # Size of one complete major unit in pixels
    major_unit_px = major_every * spacing_px

    # How many complete major units fit?
    num_complete_units = int(content_dimension / major_unit_px)

    # Calculate space needed for these complete units
    needed_space = num_complete_units * major_unit_px

    # How much space is left over?
    leftover_space = content_dimension - needed_space

    # Can we fit one more complete major unit?
    if leftover_space >= major_unit_px:
        # Yes! Expand to fit it
        num_complete_units += 1
        needed_space += major_unit_px
        leftover_space -= major_unit_px

    # Now center the grid by splitting leftover space
    start_addition = int(leftover_space / 2)
    end_addition = int(leftover_space - start_addition)

    return (base_margin + start_addition, base_margin + end_addition, num_complete_units)


def calculate_major_aligned_margins_x(content_width, spacing_px, base_margin, major_every):
    """
    Calculate left/right margins that force grid to end on major lines
    (Same logic as calculate_major_aligned_margins but for horizontal axis)
    """
    return calculate_major_aligned_margins(content_width, spacing_px, base_margin, major_every)


def calculate_spacing_from_line_count(content_dimension, num_lines, enforce_exact=True):
    """
    Calculate spacing needed to fit exactly N lines in a given space

    Args:
        content_dimension: Available space (width or height) in pixels
        num_lines: Desired number of lines
        enforce_exact: If True, calculate exact spacing. If False, round to nearest pixel.

    Returns:
        Tuple of (spacing_px, is_fractional)
        - spacing_px: Calculated spacing in pixels
        - is_fractional: True if spacing is not a whole number

    Examples:
        calculate_spacing_from_line_count(2000, 40, enforce_exact=True)
        → (50.0, False)  # 40 lines at 50px spacing = 2000px

        calculate_spacing_from_line_count(2000, 41, enforce_exact=True)
        → (48.78..., True)  # Fractional spacing required
    """
    if num_lines <= 0:
        raise ValueError("Number of lines must be greater than 0")

    # Calculate the required spacing
    spacing_px = content_dimension / num_lines

    # Check if it's fractional
    is_fractional = abs(spacing_px - round(spacing_px)) > 0.001

    if not enforce_exact and is_fractional:
        # Round to nearest pixel if not enforcing exact
        spacing_px = round(spacing_px)
        is_fractional = False

    return spacing_px, is_fractional


def calculate_spacing_from_line_count_with_margins(
    page_dimension, num_lines, margin_px, enforce_exact=True
):
    """
    Calculate spacing needed to fit exactly N lines with specified margins

    Args:
        page_dimension: Total page space (width or height) in pixels
        num_lines: Desired number of lines
        margin_px: Margin size in pixels (applied to both sides)
        enforce_exact: If True, calculate exact spacing. If False, round to nearest pixel.

    Returns:
        Tuple of (spacing_px, is_fractional, content_dimension)
        - spacing_px: Calculated spacing in pixels
        - is_fractional: True if spacing is not a whole number
        - content_dimension: Available content space after margins

    Examples:
        calculate_spacing_from_line_count_with_margins(2560, 40, 118, enforce_exact=True)
        → (61.1, True, 2324)  # 40 lines in 2324px (2560 - 2*118) = 58.1px spacing
    """
    # Calculate content dimension after removing margins
    content_dimension = page_dimension - (2 * margin_px)

    if content_dimension <= 0:
        raise ValueError(
            f"Margins ({margin_px}px each) are too large for page dimension ({page_dimension}px)"
        )

    # Calculate spacing for the content area
    spacing_px, is_fractional = calculate_spacing_from_line_count(
        content_dimension, num_lines, enforce_exact
    )

    return spacing_px, is_fractional, content_dimension


def parse_line_count_spec(spec_str):
    """
    Parse line count specification string

    Supports formats:
    - "40" or "40 lines" → 40 lines
    - "40x30" → 40 horizontal lines, 30 vertical lines (for grids)

    Args:
        spec_str: Line count specification string

    Returns:
        Tuple of (h_lines, v_lines) where v_lines may be None for 1D templates

    Examples:
        parse_line_count_spec("40") → (40, None)
        parse_line_count_spec("40 lines") → (40, None)
        parse_line_count_spec("40x30") → (40, 30)
    """
    spec_str = spec_str.strip().lower().replace(" lines", "").replace("lines", "")

    if "x" in spec_str:
        # Grid specification: "40x30"
        parts = spec_str.split("x")
        if len(parts) != 2:
            raise ValueError(
                f"Invalid grid line count format: '{spec_str}'. Use 'HxV' (e.g., '40x30')"
            )
        try:
            h_lines = int(parts[0].strip())
            v_lines = int(parts[1].strip())
            return h_lines, v_lines
        except ValueError:
            raise ValueError(
                f"Invalid grid line count format: '{spec_str}'. Both values must be integers."
            )
    else:
        # Single dimension: "40"
        try:
            lines = int(spec_str)
            return lines, None
        except ValueError:
            raise ValueError(
                f"Invalid line count format: '{spec_str}'. Use an integer (e.g., '40') or 'HxV' (e.g., '40x30')"
            )


def format_line_count_summary(
    h_lines, v_lines, h_spacing_px, v_spacing_px=None, is_fractional=False
):
    """
    Format line count information for CLI summary display

    Args:
        h_lines: Number of horizontal lines
        v_lines: Number of vertical lines (None for 1D templates)
        h_spacing_px: Calculated horizontal spacing
        v_spacing_px: Calculated vertical spacing (for grids)
        is_fractional: Whether spacing is fractional

    Returns:
        Human-readable string describing the line count and spacing
    """
    if v_lines is None:
        # 1D template (lined, dotgrid rows, etc.)
        if is_fractional:
            return f"{h_lines} lines at {h_spacing_px:.3f}px spacing (fractional - may accumulate error)"
        else:
            return f"{h_lines} lines at {int(h_spacing_px)}px spacing"
    else:
        # 2D template (grid, dotgrid)
        h_frac = abs(h_spacing_px - round(h_spacing_px)) > 0.001
        v_frac = abs(v_spacing_px - round(v_spacing_px)) > 0.001

        if h_frac or v_frac:
            return f"{h_lines}×{v_lines} grid at {h_spacing_px:.3f}px × {v_spacing_px:.3f}px spacing (fractional)"
        else:
            return (
                f"{h_lines}×{v_lines} grid at {int(h_spacing_px)}px × {int(v_spacing_px)}px spacing"
            )
