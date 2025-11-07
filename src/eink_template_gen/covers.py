"""
Title page pattern generators for decorative covers
"""

from math import pow, sqrt

import cairo

from .cover_drawing import (
    draw_10_print_tiles,
    draw_contour_lines,
    draw_decorative_border,
    draw_diagonal_truchet_tiles,
    draw_hexagonal_truchet_tiles,
    draw_lsystem_pattern,
    draw_noise_field,
    draw_truchet_tiles,
)
from .cover_elements import draw_title_element, draw_title_frame, draw_title_text
from .separator_config import parse_separator_config
from .separators import draw_separator_line
from .utils import calculate_adjusted_margins, calculate_adjusted_margins_x


def create_truchet_title(
    width,
    height,
    dpi,
    spacing_mm,
    margin_mm,
    line_width_px,
    header=None,
    footer=None,
    rotation_seed=None,
    auto_adjust_spacing=True,
    truchet_fill_grey=None,
    truchet_variant="classic",
    decorative_border=None,
    cover_config=None,
):
    """
    Create a Truchet tile pattern title page

    Args:
        ... (existing args) ...
        truchet_variant: 'classic', 'cross', 'triangle', 'wave', 'mixed'
        decorative_border: None, 'simple', 'double', 'ornate', 'geometric'
        cover_config: Dict with title frame/text configuration (optional)

    Returns:
        Cairo surface with Truchet tile pattern
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

    # White background
    ctx.set_source_rgb(1, 1, 1)
    ctx.paint()

    # Calculate base margins
    base_margin = round(margin_mm * mm2px)

    # Calculate adjusted margins for both axes
    content_height = height - (2 * base_margin)
    content_width = width - (2 * base_margin)

    m_top, m_bottom = calculate_adjusted_margins(content_height, spacing_px, base_margin)
    m_left, m_right = calculate_adjusted_margins_x(content_width, spacing_px, base_margin)

    # Parse header separator
    header_style, header_kwargs = parse_separator_config(header)
    if header_style:
        draw_separator_line(
            ctx, m_left, width - m_right, m_top, style=header_style, **header_kwargs
        )

    # Parse footer separator
    footer_style, footer_kwargs = parse_separator_config(footer)
    if footer_style:
        draw_separator_line(
            ctx, m_left, width - m_right, height - m_bottom, style=footer_style, **footer_kwargs
        )

    # Draw Truchet tiles
    draw_truchet_tiles(
        ctx,
        m_left,
        width - m_right,
        m_top,
        height - m_bottom,
        spacing_px,
        line_width_px,
        rotation_seed=rotation_seed,
        fill_grey=truchet_fill_grey,
        variant=truchet_variant,
    )

    # Draw decorative border if specified
    if decorative_border:
        draw_decorative_border(
            ctx,
            m_left,
            width - m_right,
            m_top,
            height - m_bottom,
            border_width=line_width_px * 2,
            style=decorative_border,
        )

    # Draw title frame and text if configured
    if cover_config:
        draw_title_element(ctx, width, height, cover_config)

    return surface


def _draw_title_element(ctx, page_width, page_height, config):
    """
    Draw title frame and text from configuration

    Args:
        ctx: Cairo context
        page_width: Page width in pixels
        page_height: Page height in pixels
        config: Dict with title configuration
    """

    # Get horizontal position (default to center)
    x_center = config.get("x_center", page_width / 2)

    # Get vertical position:
    # 1. Check for explicit 'y_center' coordinate
    y_center = config.get("y_center")
    if y_center is None:
        # 2. If not present, use 'v_align' setting
        v_align = config.get("v_align", "top")  # Default to 'top'

        if v_align == "center":
            y_center = page_height / 2
        elif v_align == "bottom":
            y_center = page_height * (2 / 3)
        else:  # 'top'
            y_center = page_height / 3

    # Get frame dimensions
    frame_width = config.get("frame_width", page_width * 0.6)
    frame_height = config.get("frame_height", page_height * 0.2)

    # Draw frame (always draw unless explicitly disabled)
    if config.get("show_frame", True):
        draw_title_frame(
            ctx,
            x_center,
            y_center,
            frame_width,
            frame_height,
            shape=config.get("frame_shape", "rounded-rectangle"),
            border_style=config.get("border_style", "solid"),
            border_width=config.get("border_width", 2.0),
            border_grey=config.get("border_grey", 0),
            fill_grey=config.get("fill_grey", 15),  # White fill by default
            corner_radius=config.get("corner_radius", 10),
        )

    # Draw text only if provided and non-empty
    text = config.get("text", "").strip()
    if text:
        draw_title_text(
            ctx,
            text,
            x_center,
            y_center,
            font_family=config.get("font_family", "Serif"),
            font_size=config.get("font_size", 48),
            font_weight=config.get("font_weight", "bold"),
            font_slant=config.get("font_slant", "normal"),
            text_grey=config.get("text_grey", 0),
            letter_spacing=config.get("letter_spacing", 0),
        )


def create_diagonal_truchet_title(
    width,
    height,
    dpi,
    spacing_mm,
    margin_mm,
    line_width_px,  # Not used by this, but kept for consistency
    header=None,
    footer=None,
    rotation_seed=None,
    auto_adjust_spacing=True,
    diagonal_fill_grey_1=0,
    diagonal_fill_grey_2=15,
    cover_config=None,
):
    """
    Create a diagonal Truchet tile pattern title page

    Args:
        ... (standard args) ...
        diagonal_fill_grey_1: Greyscale 0-15 for first triangle
        diagonal_fill_grey_2: Greyscale 0-15 for second triangle
        cover_config: Dict with title frame/text configuration (optional)

    Returns:
        Cairo surface with diagonal Truchet tile pattern
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

    # White background
    ctx.set_source_rgb(1, 1, 1)
    ctx.paint()

    # Calculate base margins
    base_margin = round(margin_mm * mm2px)

    # Calculate adjusted margins for both axes
    content_height = height - (2 * base_margin)
    content_width = width - (2 * base_margin)

    m_top, m_bottom = calculate_adjusted_margins(content_height, spacing_px, base_margin)
    m_left, m_right = calculate_adjusted_margins_x(content_width, spacing_px, base_margin)

    # Parse header separator
    header_style, header_kwargs = parse_separator_config(header)
    if header_style:
        draw_separator_line(
            ctx, m_left, width - m_right, m_top, style=header_style, **header_kwargs
        )

    # Parse footer separator
    footer_style, footer_kwargs = parse_separator_config(footer)
    if footer_style:
        draw_separator_line(
            ctx, m_left, width - m_right, height - m_bottom, style=footer_style, **footer_kwargs
        )

    # Draw Diagonal Truchet tiles
    draw_diagonal_truchet_tiles(
        ctx,
        m_left,
        width - m_right,
        m_top,
        height - m_bottom,
        spacing_px,
        rotation_seed=rotation_seed,
        fill_grey_1=diagonal_fill_grey_1,
        fill_grey_2=diagonal_fill_grey_2,
    )

    # Draw title frame and text if configured
    if cover_config:
        draw_title_element(ctx, width, height, cover_config)

    return surface


# --- Hexagonal Truchet Title Generator ---


def create_hexagonal_truchet_title(
    width,
    height,
    dpi,
    spacing_mm,
    margin_mm,
    line_width_px,
    header=None,
    footer=None,
    rotation_seed=None,
    auto_adjust_spacing=True,
    cover_config=None,
):
    """
    Create a hexagonal Truchet tile pattern title page
    'spacing_mm' defines the side length of the hexagon.

    Args:
        ... (standard args) ...
        cover_config: Dict with title frame/text configuration (optional)

    Returns:
        Cairo surface with hexagonal Truchet tile pattern
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

    # White background
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

    # Parse header separator
    header_style, header_kwargs = parse_separator_config(header)
    if header_style:
        draw_separator_line(
            ctx, m_left, width - m_right, m_top, style=header_style, **header_kwargs
        )

    # Parse footer separator
    footer_style, footer_kwargs = parse_separator_config(footer)
    if footer_style:
        draw_separator_line(
            ctx, m_left, width - m_right, height - m_bottom, style=footer_style, **footer_kwargs
        )

    # Draw Hexagonal Truchet tiles
    draw_hexagonal_truchet_tiles(
        ctx,
        m_left,
        width - m_right,
        m_top,
        height - m_bottom,
        spacing_px,
        line_width_px,
        rotation_seed=rotation_seed,
    )

    # Draw title frame and text if configured
    if cover_config:
        draw_title_element(ctx, width, height, cover_config)

    return surface


def create_10_print_title(
    width,
    height,
    dpi,
    spacing_mm,
    margin_mm,
    line_width_px,
    header=None,
    footer=None,
    rotation_seed=None,
    auto_adjust_spacing=True,
    cover_config=None,
):
    """
    Create a "10 PRINT" (diagonal maze) title page

    Args:
        ... (standard args) ...
        cover_config: Dict with title frame/text configuration (optional)

    Returns:
        Cairo surface with "10 PRINT" pattern
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

    # White background
    ctx.set_source_rgb(1, 1, 1)
    ctx.paint()

    # Calculate base margins
    base_margin = round(margin_mm * mm2px)

    # Calculate adjusted margins for both axes
    content_height = height - (2 * base_margin)
    content_width = width - (2 * base_margin)

    m_top, m_bottom = calculate_adjusted_margins(content_height, spacing_px, base_margin)
    m_left, m_right = calculate_adjusted_margins_x(content_width, spacing_px, base_margin)

    # Parse header separator
    header_style, header_kwargs = parse_separator_config(header)
    if header_style:
        draw_separator_line(
            ctx, m_left, width - m_right, m_top, style=header_style, **header_kwargs
        )

    # Parse footer separator
    footer_style, footer_kwargs = parse_separator_config(footer)
    if footer_style:
        draw_separator_line(
            ctx, m_left, width - m_right, height - m_bottom, style=footer_style, **footer_kwargs
        )

    # Draw 10 PRINT tiles
    draw_10_print_tiles(
        ctx,
        m_left,
        width - m_right,
        m_top,
        height - m_bottom,
        spacing_px,
        line_width_px,
        rotation_seed=rotation_seed,
    )

    # Draw title frame and text if configured
    if cover_config:
        draw_title_element(ctx, width, height, cover_config)

    return surface


def create_lsystem_title(
    width,
    height,
    dpi,
    spacing_mm,
    margin_mm,
    line_width_px,
    header=None,
    footer=None,
    auto_adjust_spacing=True,
    cover_config=None,
    decorative_border=None,
    # L-System specific params:
    lsystem_config=None,
    lsystem_iterations=4,
):
    """
    Generic L-System generator.
    Calculates step_length automatically based on iterations and content area.
    """
    mm2px = dpi / 25.4

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    ctx = cairo.Context(surface)

    # White background
    ctx.set_source_rgb(1, 1, 1)
    ctx.paint()

    # Calculate base margins
    base_margin = round(margin_mm * mm2px)

    # L-Systems don't align to a grid, so we just use the base margins
    m_top = base_margin
    m_bottom = base_margin
    m_left = base_margin
    m_right = base_margin

    # Parse header separator
    header_style, header_kwargs = parse_separator_config(header)
    if header_style:
        draw_separator_line(
            ctx, m_left, width - m_right, m_top, style=header_style, **header_kwargs
        )

    # Parse footer separator
    footer_style, footer_kwargs = parse_separator_config(footer)
    if footer_style:
        draw_separator_line(
            ctx, m_left, width - m_right, height - m_bottom, style=footer_style, **footer_kwargs
        )

    # --- L-System Specific Logic ---
    if not lsystem_config:
        print("Error: No L-System config provided.")
        return surface

    # Update config with CLI parameters
    lsystem_config["iterations"] = lsystem_iterations

    # Set content area
    content_width = width - m_left - m_right
    content_height = height - m_top - m_bottom
    min_content_dim = min(content_width, content_height)

    # --- Calculate Step Length ---
    step_length_px = 10  # Default fallback

    # Get the function that estimates the size (in steps) of the bounding box
    estimator_func = lsystem_config.get("bounding_box_estimator")

    if estimator_func:
        # Get the number of "steps" the curve takes to cross the bounding box
        num_steps = estimator_func(lsystem_iterations)
        if num_steps > 0:
            # Calculate step_length to fill 80% of the smallest dimension (was 95%, now smaller for better visibility)
            step_length_px = (min_content_dim * 0.80) / num_steps

    lsystem_config["step_length"] = step_length_px

    # Set a smart start position based on the config
    start_pos_key = lsystem_config.get("start_pos", "center")

    # Calculate padding to center the drawing
    box_steps = estimator_func(lsystem_iterations) if estimator_func else 0
    if box_steps > 0:
        padding_x = (content_width - (step_length_px * box_steps)) / 2
        padding_y = (content_height - (step_length_px * box_steps)) / 2
    else:
        padding_x = content_width * 0.1
        padding_y = content_height * 0.1

    # Handle negative padding (if box is larger than content area)
    padding_x = max(padding_x, content_width * 0.05)
    padding_y = max(padding_y, content_height * 0.05)

    if start_pos_key == "bottom_left":
        x_start = m_left + padding_x
        y_start = height - m_bottom - padding_y
    elif start_pos_key == "top_left":
        x_start = m_left + padding_x
        y_start = m_top + padding_y
    elif start_pos_key == "bottom_center":
        x_start = width / 2
        y_start = height - m_bottom - padding_y
    elif start_pos_key == "dragon_start":
        # Special position for dragon curve - center it better
        x_start = width / 2
        y_start = height / 2
    else:  # "center"
        x_start = width / 2
        y_start = height / 2

    print(
        f"Generating L-System with {lsystem_iterations} iterations and {step_length_px:.2f}px step..."
    )

    # Draw the L-System pattern
    draw_lsystem_pattern(
        ctx, lsystem_config, x_start, y_start, content_width, content_height, line_width_px
    )

    # Draw decorative border if specified
    if decorative_border:
        draw_decorative_border(
            ctx,
            m_left,
            width - m_right,
            m_top,
            height - m_bottom,
            border_width=line_width_px * 2,
            style=decorative_border,
        )

    # Draw title frame and text if configured
    if cover_config:
        draw_title_element(ctx, width, height, cover_config)

    return surface


# --- Specific L-System Definitions ---


def create_hilbert_curve_title(**kwargs):
    """
    Create a Hilbert Curve (space-filling)
    """
    hilbert_config = {
        "axiom": "A",
        "rules": {"A": "+BF-AFA-FB+", "B": "-AF+BFB+FA-"},
        "angle": 90,
        "start_angle": 0,
        "start_pos": "center",
        # A Hilbert curve of n iterations fills a 2^n x 2^n grid
        "bounding_box_estimator": lambda it: pow(2, it) - 1,
    }
    kwargs["lsystem_config"] = hilbert_config
    return create_lsystem_title(**kwargs)


def create_dragon_curve_title(**kwargs):
    """
    Create a Dragon Curve
    """
    dragon_config = {
        "axiom": "FX",
        "rules": {"X": "X+YF+", "Y": "-FX-Y"},
        "angle": 90,
        "start_angle": 0,
        # Use a special start key
        "start_pos": "center",
        # Bounding box is roughly (sqrt(2))^n. 1.414^n is close enough.
        "bounding_box_estimator": lambda it: pow(1.414, it),
    }
    kwargs["lsystem_config"] = dragon_config
    return create_lsystem_title(**kwargs)


def create_koch_snowflake_title(**kwargs):
    """
    Create a Koch Snowflake (classic fractal with 6-fold symmetry)
    """
    koch_config = {
        "axiom": "F++F++F",  # Equilateral triangle
        "rules": {"F": "F-F++F-F"},
        "angle": 60,
        "start_angle": 0,
        "start_pos": "center",
        "bounding_box_estimator": lambda it: pow(3, it),
    }
    kwargs["lsystem_config"] = koch_config
    return create_lsystem_title(**kwargs)


def create_sierpinski_triangle_title(**kwargs):
    """
    Create a Sierpinski Triangle (elegant recursive triangle pattern)
    """
    sierpinski_config = {
        "axiom": "F-G-G",
        "rules": {"F": "F-G+F+G-F", "G": "GG"},
        "angle": 120,
        "start_angle": 0,
        "start_pos": "bottom_left",
        "bounding_box_estimator": lambda it: pow(2, it),
    }
    kwargs["lsystem_config"] = sierpinski_config
    return create_lsystem_title(**kwargs)


def create_plant_fractal_title(**kwargs):
    """
    Create an organic plant-like branching fractal
    """
    plant_config = {
        "axiom": "X",
        "rules": {"X": "F+[[X]-X]-F[-FX]+X", "F": "FF"},
        "angle": 25,
        "start_angle": 90,  # Grow upward
        "start_pos": "bottom_center",
        "bounding_box_estimator": lambda it: pow(2, it) * 1.5,
    }
    kwargs["lsystem_config"] = plant_config
    return create_lsystem_title(**kwargs)


def create_gosper_curve_title(**kwargs):
    """
    Create a Gosper Curve (space-filling hexagonal pattern)
    """
    gosper_config = {
        "axiom": "A",
        "rules": {"A": "A-B--B+A++AA+B-", "B": "+A-BB--B-A++A+B"},
        "angle": 60,
        "start_angle": 0,
        "start_pos": "center",
        "bounding_box_estimator": lambda it: pow(2.65, it),
    }
    kwargs["lsystem_config"] = gosper_config
    return create_lsystem_title(**kwargs)


def create_levy_c_curve_title(**kwargs):
    """
    Create a Lévy C Curve (elegant symmetric fractal)
    """
    levy_config = {
        "axiom": "F",
        "rules": {"F": "+F--F+"},
        "angle": 45,
        "start_angle": 0,
        "start_pos": "center",
        "bounding_box_estimator": lambda it: pow(1.414, it),
    }
    kwargs["lsystem_config"] = levy_config
    return create_lsystem_title(**kwargs)


def create_contour_lines_title(
    width,
    height,
    dpi,
    spacing_mm,
    margin_mm,
    line_width_px,
    header=None,
    footer=None,
    auto_adjust_spacing=True,
    cover_config=None,
    decorative_border=None,
    contour_interval=0.1,
    noise_scale=0.02,
    octaves=4,
    contour_seed=None,
    contour_style="smooth",
):
    """
    Create a contour line (topographic map style) title page using noise.

    Args:
        ... (standard args) ...
        contour_interval: Elevation difference between lines (0.05-0.2 recommended)
        noise_scale: Frequency of noise (0.01-0.05, smaller = larger features)
        octaves: Number of noise octaves (1-6, more = more detail)
        contour_seed: Random seed for reproducibility
        contour_style: 'smooth' (terrain-like), 'turbulent' (marble-like), 'simple' (basic)
        cover_config: Dict with title frame/text configuration (optional)

    Returns:
        Cairo surface with contour line pattern
    """
    mm2px = dpi / 25.4

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    ctx = cairo.Context(surface)

    # White background
    ctx.set_source_rgb(1, 1, 1)
    ctx.paint()

    # Calculate base margins
    base_margin = round(margin_mm * mm2px)

    # Contours don't align to a grid, so we just use the base margins
    m_top = base_margin
    m_bottom = base_margin
    m_left = base_margin
    m_right = base_margin

    # Parse header separator
    header_style, header_kwargs = parse_separator_config(header)
    if header_style:
        draw_separator_line(
            ctx, m_left, width - m_right, m_top, style=header_style, **header_kwargs
        )

    # Parse footer separator
    footer_style, footer_kwargs = parse_separator_config(footer)
    if footer_style:
        draw_separator_line(
            ctx, m_left, width - m_right, height - m_bottom, style=footer_style, **footer_kwargs
        )

    print(f"Generating contour lines with {octaves} octaves, style='{contour_style}'...")

    # Draw contour lines
    draw_contour_lines(
        ctx,
        m_left,
        width - m_right,
        m_top,
        height - m_bottom,
        contour_interval=contour_interval,
        line_width=line_width_px,
        noise_scale=noise_scale,
        octaves=octaves,
        seed=contour_seed,
        style=contour_style,
    )

    if decorative_border:
        draw_decorative_border(
            ctx,
            m_left,
            width - m_right,
            m_top,
            height - m_bottom,
            border_width=line_width_px * 2,
            style=decorative_border,
        )

    # Draw title frame and text if configured
    if cover_config:
        draw_title_element(ctx, width, height, cover_config)

    return surface


def create_noise_field_title(
    width,
    height,
    dpi,
    spacing_mm,
    margin_mm,
    line_width_px,  # Not used but kept for consistency
    header=None,
    footer=None,
    auto_adjust_spacing=True,
    cover_config=None,
    decorative_border=None,
    # Noise field params:
    noise_scale=0.02,
    octaves=4,
    noise_seed=None,
    noise_style="smooth",
    greyscale_levels=16,
):
    """
    Create a noise field title page (greyscale texture).

    Args:
        ... (standard args) ...
        noise_scale: Frequency of noise (0.01-0.05)
        octaves: Number of noise octaves (1-6)
        noise_seed: Random seed
        noise_style: 'smooth', 'turbulent', or 'simple'
        greyscale_levels: Number of grey levels (1-16)
        cover_config: Dict with title frame/text configuration (optional)

    Returns:
        Cairo surface with noise field pattern
    """
    mm2px = dpi / 25.4

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    ctx = cairo.Context(surface)

    # White background
    ctx.set_source_rgb(1, 1, 1)
    ctx.paint()

    # Calculate base margins
    base_margin = round(margin_mm * mm2px)

    m_top = base_margin
    m_bottom = base_margin
    m_left = base_margin
    m_right = base_margin

    # Parse header separator
    header_style, header_kwargs = parse_separator_config(header)
    if header_style:
        draw_separator_line(
            ctx, m_left, width - m_right, m_top, style=header_style, **header_kwargs
        )

    # Parse footer separator
    footer_style, footer_kwargs = parse_separator_config(footer)
    if footer_style:
        draw_separator_line(
            ctx, m_left, width - m_right, height - m_bottom, style=footer_style, **footer_kwargs
        )

    print(f"Generating noise field with {octaves} octaves, style='{noise_style}'...")

    # Draw noise field
    draw_noise_field(
        ctx,
        m_left,
        width - m_right,
        m_top,
        height - m_bottom,
        noise_scale=noise_scale,
        octaves=octaves,
        seed=noise_seed,
        style=noise_style,
        greyscale_levels=greyscale_levels,
    )

    if decorative_border:
        draw_decorative_border(
            ctx,
            m_left,
            width - m_right,
            m_top,
            height - m_bottom,
            border_width=line_width_px * 2,
            style=decorative_border,
        )

    # Draw title frame and text if configured
    if cover_config:
        draw_title_element(ctx, width, height, cover_config)

    return surface


COVER_REGISTRY = {
    "truchet": create_truchet_title,
    "diagonal_truchet": create_diagonal_truchet_title,
    "hexagonal_truchet": create_hexagonal_truchet_title,
    "ten_print": create_10_print_title,
    "hilbert_curve": create_hilbert_curve_title,
    "dragon_curve": create_dragon_curve_title,
    "koch_snowflake": create_koch_snowflake_title,
    "sierpinski_triangle": create_sierpinski_triangle_title,
    "plant_fractal": create_plant_fractal_title,
    "gosper_curve": create_gosper_curve_title,
    "levy_c_curve": create_levy_c_curve_title,
    "contour_lines": create_contour_lines_title,
    "noise_field": create_noise_field_title,
}
