"""
Utility functions for template generation
"""

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

def generate_filename(template_type, spacing_val, **kwargs):
    """
    Generate descriptive filename based on template params
    Structure: [orientation_]type_spacing_[width/radius_][columns_][rows_][ratio_][h-sep_][f-sep_].png
    
    Args:
        template_type: Type of template (e.g., 'lined', 'grid')
        spacing_val: Spacing value (float for mm, int for px)
        **kwargs: Optional parameters:
            - spacing_mode: 'mm' or 'px' (default: 'mm')
            - line_width_px: (float)
            - dot_radius_px: (float)
            - header_separator: (str)
            - footer_separator: (str)
            - orientation: 'horizontal' or 'vertical'
            - columns: Number of columns (int)
            - rows: Number of rows (int)  <-- NEW
            - split_ratio: Ratio string (e.g., '60-40')
    
    Returns:
        Filename string with .png extension
    """
    parts = []
    
    # Orientation only if columns > 1
    columns = kwargs.get('columns', 1)
    if 'orientation' in kwargs and columns > 1:
        parts.append(kwargs['orientation'])
    
    # Template type
    parts.append(template_type)
    
    # Spacing (handles mm/px)
    spacing_mode = kwargs.get('spacing_mode', 'mm')
    if spacing_mode == 'px':
        spacing_str = f"{int(spacing_val)}px"
    else:  # 'mm'
        spacing_str = str(int(spacing_val)) if spacing_val == int(spacing_val) else str(spacing_val).replace('.', '_')
        spacing_str += "mm"
    parts.append(spacing_str)
    
    # Line Width / Dot Radius
    if 'line_width_px' in kwargs:
        lw = kwargs['line_width_px']
        lw_str = str(lw).replace('.', '_')
        parts.append(f"{lw_str}px")
    elif 'dot_radius_px' in kwargs:
        dr = kwargs['dot_radius_px']
        dr_str = str(dr).replace('.', '_')
        parts.append(f"{dr_str}rad") # Use 'rad' to distinguish from 'px'

    # Columns (if present and > 1)
    if columns > 1:
        parts.append(f"{columns}col")
    
    # --- START FIX ---
    # Rows (if present and > 1)
    rows = kwargs.get('rows', 1)
    if rows > 1:
        parts.append(f"{rows}rows")
    # --- END FIX ---
    
    # Split ratio (if present)
    if 'split_ratio' in kwargs:
        parts.append(kwargs['split_ratio'])
    
    # Header Separator
    header_sep = kwargs.get('header_separator')
    if header_sep:
        parts.append(f"h-{header_sep}")
            
    # Footer Separator
    footer_sep = kwargs.get('footer_separator')
    if footer_sep:
        parts.append(f"f-{footer_sep}")
    
    return "_".join(parts) + ".png"

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
    if spacing_str.endswith('px'):
        # PX mode - exact pixels
        mode = 'px'
        spacing_px = float(spacing_str[:-2])
        original_mm = spacing_px / mm2px
        adjusted_mm = original_mm
        was_adjusted = False
        
    elif spacing_str.endswith('mm'):
        # MM mode - millimeters
        mode = 'mm'
        original_mm = float(spacing_str[:-2])
        
        if auto_adjust:
            adjusted_mm, spacing_px, was_adjusted = snap_spacing_to_clean_pixels(original_mm, dpi)
        else:
            spacing_px = original_mm * mm2px
            adjusted_mm = original_mm
            was_adjusted = False
    
    else:
        # No unit - assume mm
        mode = 'mm'
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
    if mode == 'px':
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
    print('=' * 80)
    
    if mode == 'px':
        print(f"Input: {int(spacing_px)}px")
        print(f"Equivalent: {original_mm:.4f}mm")
        print(f"\n✓ PIXEL-PERFECT (exact pixels specified)")
        print(f"  No adjustment needed")
    else:
        print(f"Input: {original_mm}mm")
        print(f"Exact pixels: {original_mm * dpi / 25.4:.4f}px")
        
        if was_adjusted:
            print(f"\n⚙️  AUTO-ADJUSTMENT AVAILABLE")
            print(f"  Original: {original_mm}mm = {original_mm * dpi / 25.4:.4f}px")
            print(f"  Adjusted: {adjusted_mm:.4f}mm = {int(spacing_px)}px (pixel-perfect)")
            print(f"  Difference: {abs(adjusted_mm - original_mm):.4f}mm ({abs(adjusted_mm - original_mm) / original_mm * 100:.2f}%)")
            
            # Calculate error accumulation
            error_per_line = (original_mm * dpi / 25.4) - int(original_mm * dpi / 25.4)
            if error_per_line > 0.5:
                error_per_line -= 1
            error_40_lines = abs(error_per_line * 40)
            
            print(f"\n  Without adjustment:")
            print(f"    Error per line: {abs(error_per_line):.4f}px")
            print(f"    Accumulated over 40 lines: {error_40_lines:.2f}px")
        else:
            print(f"\n✓ ALREADY PIXEL-PERFECT")
            print(f"  Spacing is exactly {int(spacing_px)} pixels")
            print(f"  No adjustment needed")
    
    print('=' * 80)

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
    
    return (base_margin + start_addition, 
            base_margin + end_addition, 
            num_complete_units)

def calculate_major_aligned_margins_x(content_width, spacing_px, base_margin, major_every):
    """
    Calculate left/right margins that force grid to end on major lines
    (Same logic as calculate_major_aligned_margins but for horizontal axis)
    """
    return calculate_major_aligned_margins(content_width, spacing_px, base_margin, major_every)
