"""
Utility functions for template generation
"""

import os
from dataclasses import dataclass
from typing import Tuple

import cairo

# --- Canvas Helper ---


def create_canvas(
    width: int, height: int, background_color=(1, 1, 1)
) -> Tuple[cairo.ImageSurface, cairo.Context]:
    """
    Create a Cairo surface and context with background.

    Returns:
        Tuple of (surface, context)
    """
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    ctx = cairo.Context(surface)
    ctx.set_source_rgb(*background_color)
    ctx.paint()
    return surface, ctx


# --- Spacing Calculation ---


@dataclass
class SpacingResult:
    """Result of spacing calculation"""

    pixels: float
    mm: float
    was_adjusted: bool
    original_mm: float

    def print_adjustment_message(self):
        """Print adjustment message if needed"""
        if self.was_adjusted:
            print(
                f"Note: Adjusted spacing from {self.original_mm}mm to "
                f"{self.mm:.3f}mm ({int(self.pixels)}px) for pixel-perfect alignment"
            )


def calculate_spacing(spacing_mm: float, dpi: int, auto_adjust: bool = True) -> SpacingResult:
    """
    Calculate spacing with optional auto-adjustment.

    Consolidates the spacing calculation logic that was duplicated
    in every generation function.
    """
    mm2px = dpi / 25.4

    if auto_adjust:
        adjusted_mm, spacing_px, was_adjusted = snap_spacing_to_clean_pixels(spacing_mm, dpi)
        return SpacingResult(
            pixels=spacing_px, mm=adjusted_mm, was_adjusted=was_adjusted, original_mm=spacing_mm
        )
    else:
        spacing_px = spacing_mm * mm2px
        return SpacingResult(
            pixels=spacing_px, mm=spacing_mm, was_adjusted=False, original_mm=spacing_mm
        )


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


# --- Margin & Alignment Calculation ---


@dataclass
class PageMargins:
    """Calculated page margins"""

    top: int
    bottom: int
    left: int
    right: int
    content_x_start: int
    content_y_start: int
    content_width: int
    content_height: int

    @property
    def horizontal_bounds(self) -> Tuple[int, int]:
        """Returns (x_start, x_end)"""
        return self.content_x_start, self.content_x_start + self.content_width

    @property
    def vertical_bounds(self) -> Tuple[int, int]:
        """Returns (y_start, y_end)"""
        return self.content_y_start, self.content_y_start + self.content_height

    @property
    def bounds(self) -> Tuple[int, int, int, int]:
        """Returns (x_start, x_end, y_start, y_end)"""
        return (
            self.content_x_start,
            self.content_x_start + self.content_width,
            self.content_y_start,
            self.content_y_start + self.content_height,
        )


def calculate_page_margins(
    width: int,
    height: int,
    dpi: int,
    margin_mm: float,
    v_align_unit_px: float,
    h_align_unit_px: float,
    major_every: int = None,
    force_major_alignment: bool = False,
) -> PageMargins:
    """
    Calculate all page margins in one place.

    This consolidates the margin calculation logic that was duplicated
    across templates.py, actions.py, and covers.py.
    """
    mm2px = dpi / 25.4
    base_margin = round(margin_mm * mm2px)

    content_height = height - (2 * base_margin)
    content_width = width - (2 * base_margin)

    # Vertical margins
    if force_major_alignment and major_every:
        m_top, m_bottom, _ = calculate_major_aligned_margins(
            content_height, v_align_unit_px, base_margin, major_every
        )
    else:
        m_top, m_bottom = calculate_adjusted_margins(content_height, v_align_unit_px, base_margin)

    # Horizontal margins
    if force_major_alignment and major_every:
        m_left, m_right, _ = calculate_major_aligned_margins_x(
            content_width, h_align_unit_px, base_margin, major_every
        )
    else:
        m_left, m_right = calculate_adjusted_margins_x(content_width, h_align_unit_px, base_margin)

    return PageMargins(
        top=m_top,
        bottom=m_bottom,
        left=m_left,
        right=m_right,
        content_x_start=m_left,
        content_y_start=m_top,
        content_width=width - m_left - m_right,
        content_height=height - m_top - m_bottom,
    )


def calculate_adjusted_margins(content_height, spacing_px, base_margin):
    """
    Calculate adjusted top/bottom margins to eliminate leftover space
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
    """
    return calculate_adjusted_margins(content_width, spacing_px, base_margin)


def calculate_major_aligned_margins(content_dimension, spacing_px, base_margin, major_every):
    """
    Calculate margins that force grid to end on major lines
    """
    if not major_every or major_every <= 0:
        m_start, m_end = calculate_adjusted_margins(content_dimension, spacing_px, base_margin)
        return m_start, m_end, 0

    major_unit_px = major_every * spacing_px
    num_complete_units = int(content_dimension / major_unit_px)
    needed_space = num_complete_units * major_unit_px
    leftover_space = content_dimension - needed_space

    if leftover_space >= major_unit_px:
        num_complete_units += 1
        needed_space += major_unit_px
        leftover_space -= major_unit_px

    start_addition = int(leftover_space / 2)
    end_addition = int(leftover_space - start_addition)

    return (base_margin + start_addition, base_margin + end_addition, num_complete_units)


def calculate_major_aligned_margins_x(content_width, spacing_px, base_margin, major_every):
    """
    Calculate left/right margins that force grid to end on major lines
    """
    return calculate_major_aligned_margins(content_width, spacing_px, base_margin, major_every)


def get_clean_spacing_options(dpi, min_mm=4, max_mm=12, step_mm=0.5):
    """
    Generates a list of pixel-perfect spacing options for the wizard.
    """
    options = []
    current_mm = min_mm
    while current_mm <= max_mm:
        # Find the nearest pixel-perfect spacing for this mm value
        adjusted_mm, spacing_px, was_adjusted = snap_spacing_to_clean_pixels(
            current_mm, dpi, tolerance_mm=step_mm
        )

        # Format for display: (e.g., 6.01, 71)
        option_tuple = (round(adjusted_mm, 2), int(spacing_px))

        if option_tuple not in options:
            options.append(option_tuple)

        current_mm += step_mm
    return options


# --- Old Spacing & Filename Functions (Still needed by actions.py) ---


def mm_to_px(mm, dpi):
    """
    Convert millimeters to pixels
    """
    return (dpi / 25.4) * mm


def px_to_mm(px, dpi):
    """
    Convert pixels to millimeters
    """
    return (px * 25.4) / dpi


def parse_spacing(spacing_str, dpi, auto_adjust=True):
    """
    Parse spacing string and return pixel value
    """
    spacing_str = str(spacing_str).lower().strip()
    mm2px = dpi / 25.4

    if spacing_str.endswith("px"):
        mode = "px"
        spacing_px = float(spacing_str[:-2])
        original_mm = spacing_px / mm2px
        adjusted_mm = original_mm
        was_adjusted = False

    elif spacing_str.endswith("mm"):
        mode = "mm"
        original_mm = float(spacing_str[:-2])

        if auto_adjust:
            adjusted_mm, spacing_px, was_adjusted = snap_spacing_to_clean_pixels(original_mm, dpi)
        else:
            spacing_px = original_mm * mm2px
            adjusted_mm = original_mm
            was_adjusted = False

    else:
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


def calculate_spacing_from_line_count(content_dimension, num_lines, enforce_exact=True):
    """
    Calculate spacing needed to fit exactly N lines in a given space
    """
    if num_lines <= 0:
        raise ValueError("Number of lines must be greater than 0")

    spacing_px = content_dimension / num_lines
    is_fractional = abs(spacing_px - round(spacing_px)) > 0.001

    if not enforce_exact and is_fractional:
        spacing_px = round(spacing_px)
        is_fractional = False

    return spacing_px, is_fractional


def calculate_spacing_from_line_count_with_margins(
    page_dimension, num_lines, margin_px, enforce_exact=True
):
    """
    Calculate spacing needed to fit exactly N lines with specified margins
    """
    content_dimension = page_dimension - (2 * margin_px)

    if content_dimension <= 0:
        raise ValueError(
            f"Margins ({margin_px}px each) are too large for page dimension ({page_dimension}px)"
        )

    spacing_px, is_fractional = calculate_spacing_from_line_count(
        content_dimension, num_lines, enforce_exact
    )

    return spacing_px, is_fractional, content_dimension


def parse_line_count_spec(spec_str):
    """
    Parse line count specification string
    """
    spec_str = spec_str.strip().lower().replace(" lines", "").replace("lines", "")

    if "x" in spec_str:
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
                f"Invalid grid line count format: '{spec_str}'. Both H and V must be integers."
            )
    else:
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
    """
    if v_lines is None:
        if is_fractional:
            return f"{h_lines} lines at {h_spacing_px:.3f}px spacing (fractional - may accumulate error)"
        else:
            return f"{h_lines} lines at {int(h_spacing_px)}px spacing"
    else:
        h_frac = abs(h_spacing_px - round(h_spacing_px)) > 0.001
        v_frac = abs(v_spacing_px - round(v_spacing_px)) > 0.001

        if h_frac or v_frac:
            return f"{h_lines}×{v_lines} grid at {h_spacing_px:.3f}px × {v_spacing_px:.3f}px spacing (fractional)"
        else:
            return (
                f"{h_lines}×{v_lines} grid at {int(h_spacing_px)}px × {int(v_spacing_px)}px spacing"
            )


def generate_filename(template_type, **kwargs):
    """
    Generate a descriptive, relative filename based on template params.
    """
    parts = []

    # --- 1. Primary Descriptor (Spacing or Line Count) ---
    if kwargs.get("lines"):
        lines_str = str(kwargs["lines"])
        parts.append(lines_str)
        if kwargs.get("enforce_margins"):
            parts.append("exact")
    else:
        spacing_str_val = kwargs.get("spacing", "6")
        spacing_mode = kwargs.get("spacing_mode", "mm")

        if spacing_mode == "px":
            try:
                spacing_str_val = str(int(float(spacing_str_val)))
            except ValueError:
                spacing_str_val = str(spacing_str_val).replace("px", "")
            spacing_str = f"{spacing_str_val}px"
        else:  # 'mm'
            spacing_str_val = str(spacing_str_val).replace("mm", "").replace(".", "_")
            spacing_str = f"{spacing_str_val}mm"
        parts.append(spacing_str)

    # --- 2. Core Style (Widths, Gaps) ---
    if "line_width_px" in kwargs:
        lw = kwargs["line_width_px"]
        lw_str = str(lw).replace(".", "_")
        parts.append(f"w{lw_str}px")

    if "dot_radius_px" in kwargs:
        dr = kwargs["dot_radius_px"]
        dr_str = str(dr).replace(".", "_")
        parts.append(f"dr{dr_str}px")

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
        parts.append(f"{rows}r_by_{columns}c")

    if "section_gap_cols" in kwargs or "section_gap_rows" in kwargs:
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
    if kwargs.get("major_every"):
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
    if kwargs.get("line_numbers_interval"):  # Changed from line_numbers
        parts.append("lnums")
    if kwargs.get("cell_labels"):
        parts.append("cell_labels")
    if kwargs.get("axis_labels"):
        parts.append("axis_labels")

    # --- 6. Other Style Variants ---
    if kwargs.get("midline_style") == "dotted":
        parts.append("dotted_mid")

    # --- 7. Separators ---
    header = kwargs.get("header")
    if header:
        parts.append(f"h-{header}")

    footer = kwargs.get("footer")
    if footer:
        parts.append(f"f-{footer}")

    # --- 8. Assemble Path ---
    if template_type == "title":
        cover_type = kwargs.get("title", "unknown_cover")
        base_dir = os.path.join(template_type, cover_type)

        if kwargs.get("truchet_seed"):
            parts.append(f"seed{kwargs['truchet_seed']}")
        if kwargs.get("noise_seed"):
            parts.append(f"seed{kwargs['noise_seed']}")
        if kwargs.get("title_text"):
            parts.append("titled")

    else:
        base_dir = template_type

    clean_parts = [part for part in parts if part is not None]
    filename = "_".join(clean_parts) + ".png"
    relative_path = os.path.join(base_dir, filename)

    return relative_path
