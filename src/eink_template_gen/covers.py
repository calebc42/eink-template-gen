"""
Title page pattern generators for decorative covers
"""

from math import cos, pow, radians, sqrt, tan

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
from .cover_elements import draw_title_element
from .separator_config import parse_separator_config
from .separators import draw_separator_line
from .utils import (
    calculate_adjusted_margins,
    calculate_adjusted_margins_x,
    snap_spacing_to_clean_pixels,
)

# --- L-System Definitions ---
# Moved from individual functions into a data-driven dict
L_SYSTEM_DEFINITIONS = {
    "hilbert_curve": {
        "axiom": "A",
        "rules": {"A": "+BF-AFA-FB+", "B": "-AF+BFB+FA-"},
        "angle": 90,
        "start_angle": 0,
        "start_pos": "center",
        "bounding_box_estimator": lambda it: pow(2, it) - 1,
    },
    "dragon_curve": {
        "axiom": "FX",
        "rules": {"X": "X+YF+", "Y": "-FX-Y"},
        "angle": 90,
        "start_angle": 0,
        "start_pos": "center",
        "bounding_box_estimator": lambda it: pow(1.414, it),
    },
    "koch_snowflake": {
        "axiom": "F++F++F",
        "rules": {"F": "F-F++F-F"},
        "angle": 60,
        "start_angle": 0,
        "start_pos": "center",
        "bounding_box_estimator": lambda it: pow(3, it),
    },
    "sierpinski_triangle": {
        "axiom": "F-G-G",
        "rules": {"F": "F-G+F+G-F", "G": "GG"},
        "angle": 120,
        "start_angle": 0,
        "start_pos": "bottom_left",
        "bounding_box_estimator": lambda it: pow(2, it),
    },
    "plant_fractal": {
        "axiom": "X",
        "rules": {"X": "F+[[X]-X]-F[-FX]+X", "F": "FF"},
        "angle": 25,
        "start_angle": 90,
        "start_pos": "bottom_center",
        "bounding_box_estimator": lambda it: pow(2, it) * 1.5,
    },
    "gosper_curve": {
        "axiom": "A",
        "rules": {"A": "A-B--B+A++AA+B-", "B": "+A-BB--B-A++A+B"},
        "angle": 60,
        "start_angle": 0,
        "start_pos": "center",
        "bounding_box_estimator": lambda it: pow(2.65, it),
    },
    "levy_c_curve": {
        "axiom": "F",
        "rules": {"F": "+F--F+"},
        "angle": 45,
        "start_angle": 0,
        "start_pos": "center",
        "bounding_box_estimator": lambda it: pow(1.414, it),
    },
}


# --- New Data-Driven Registry ---
COVER_REGISTRY = {
    "truchet": {
        "draw_func": draw_truchet_tiles,
        "align_unit_h": "default",
        "align_unit_v": "default",
        "specific_args_map": {
            "line_width_px": "line_width",
            "truchet_seed": "rotation_seed",
            "truchet_fill_grey": "fill_grey",
            "truchet_variant": "variant",
        },
    },
    "diagonal_truchet": {
        "draw_func": draw_diagonal_truchet_tiles,
        "align_unit_h": "default",
        "align_unit_v": "default",
        "specific_args_map": {
            "truchet_seed": "rotation_seed",
            "diag_fill_grey1": "fill_grey_1",
            "diag_fill_grey2": "fill_grey_2",
        },
    },
    "hexagonal_truchet": {
        "draw_func": draw_hexagonal_truchet_tiles,
        "align_unit_h": "hexagonal",
        "align_unit_v": "hexagonal",
        "specific_args_map": {
            "line_width_px": "line_width",
            "truchet_seed": "rotation_seed",
        },
    },
    "ten_print": {
        "draw_func": draw_10_print_tiles,
        "align_unit_h": "default",
        "align_unit_v": "default",
        "specific_args_map": {
            "line_width_px": "line_width",
            "truchet_seed": "rotation_seed",
        },
    },
    "contour_lines": {
        "draw_func": draw_contour_lines,
        "align_unit_h": "none",
        "align_unit_v": "none",
        "specific_args_map": {
            "line_width_px": "line_width",
            "contour_interval": "contour_interval",
            "noise_scale": "noise_scale",
            "octaves": "octaves",
            "noise_seed": "seed",
            "noise_style": "style",
        },
    },
    "noise_field": {
        "draw_func": draw_noise_field,
        "align_unit_h": "none",
        "align_unit_v": "none",
        "specific_args_map": {
            "noise_scale": "noise_scale",
            "octaves": "octaves",
            "noise_seed": "seed",
            "noise_style": "style",
            "greyscale_levels": "greyscale_levels",
        },
    },
    # Internal pseudo-type for all L-Systems
    "_lsystem": {
        "draw_func": draw_lsystem_pattern,
        "align_unit_h": "none",
        "align_unit_v": "none",
        "specific_args_map": {"line_width_px": "line_width"},
    },
}

# Add L-systems to the registry dynamically
for lsystem_name in L_SYSTEM_DEFINITIONS.keys():
    COVER_REGISTRY[lsystem_name] = COVER_REGISTRY["_lsystem"]


# --- New Main Factory Function ---


def create_cover_surface(cover_type, **kwargs):
    """
    Primary factory for generating all cover pages.
    This replaces all the individual `create_..._title` functions.

    Args:
        cover_type (str): The name of the cover (e.g., "truchet", "hilbert_curve")
        **kwargs: A dict of all args from handle_cover_generation, including:
            - width, height, dpi
            - spacing_mm, margin_mm, line_width_px
            - header, footer, auto_adjust_spacing
            - cover_config (dict)
            - decorative_border
            - all other pattern-specific args (truchet_seed, noise_scale, etc.)
    """
    # 1. Unpack basic args
    width = kwargs["width"]
    height = kwargs["height"]
    dpi = kwargs["dpi"]
    spacing_mm = kwargs["spacing_mm"]
    margin_mm = kwargs["margin_mm"]
    auto_adjust_spacing = kwargs.get("auto_adjust_spacing", True)
    mm2px = dpi / 25.4

    # 2. Get Config
    is_lsystem = cover_type in L_SYSTEM_DEFINITIONS
    config_key = "_lsystem" if is_lsystem else cover_type

    if config_key not in COVER_REGISTRY:
        raise ValueError(f"Unknown cover type '{cover_type}'")

    config = COVER_REGISTRY[config_key]
    draw_func = config["draw_func"]

    # 3. Setup Canvas
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
    ctx.set_source_rgb(1, 1, 1)
    ctx.paint()

    # 4. Calculate Margins
    base_margin = round(margin_mm * mm2px)
    content_height = height - (2 * base_margin)
    content_width = width - (2 * base_margin)

    # Get alignment units based on cover type
    v_align_setting = config.get("vertical_align_unit", "none")
    h_align_setting = config.get("horizontal_align_unit", "none")

    v_align_unit_px = spacing_px
    if v_align_setting == "none":
        v_align_unit_px = 1
    elif v_align_setting == "hexagonal":
        v_align_unit_px = sqrt(3) * spacing_px
    elif v_align_setting == "isometric":
        v_align_unit_px = spacing_px * tan(radians(60))

    h_align_unit_px = spacing_px
    if h_align_setting == "none":
        h_align_unit_px = 1
    elif h_align_setting == "hexagonal":
        h_align_unit_px = 1.5 * spacing_px
    elif h_align_setting == "isometric":
        h_align_unit_px = spacing_px / cos(radians(30))

    # L-Systems and noise patterns use "none", so they just get the base margin
    m_top, m_bottom = calculate_adjusted_margins(content_height, v_align_unit_px, base_margin)
    m_left, m_right = calculate_adjusted_margins_x(content_width, h_align_unit_px, base_margin)

    # 5. Draw Headers/Footers
    header = kwargs.get("header")
    header_style, header_kwargs = parse_separator_config(header)
    if header_style:
        draw_separator_line(
            ctx, m_left, width - m_right, m_top, style=header_style, **header_kwargs
        )

    footer = kwargs.get("footer")
    footer_style, footer_kwargs = parse_separator_config(footer)
    if footer_style:
        draw_separator_line(
            ctx, m_left, width - m_right, height - m_bottom, style=footer_style, **footer_kwargs
        )

    # 6. Prepare and Call Drawing Function
    draw_kwargs = {
        "ctx": ctx,
        "x_start": m_left,
        "x_end": width - m_right,
        "y_start": m_top,
        "y_end": height - m_bottom,
        "spacing_px": spacing_px,
    }

    # Map CLI args to function's kwargs
    arg_map = config.get("specific_args_map", {})
    for cli_arg, func_arg in arg_map.items():
        if cli_arg in kwargs:
            draw_kwargs[func_arg] = kwargs[cli_arg]

    # Handle L-System special case
    if is_lsystem:
        lsystem_config = L_SYSTEM_DEFINITIONS[cover_type].copy()
        lsystem_iterations = kwargs.get("lsystem_iterations", 4)
        lsystem_config["iterations"] = lsystem_iterations

        min_content_dim = min(content_width, content_height)
        step_length_px = 10  # Default

        estimator_func = lsystem_config.get("bounding_box_estimator")
        if estimator_func:
            num_steps = estimator_func(lsystem_iterations)
            if num_steps > 0:
                step_length_px = (min_content_dim * 0.80) / num_steps

        lsystem_config["step_length"] = step_length_px

        start_pos_key = lsystem_config.get("start_pos", "center")
        padding_x = content_width * 0.1
        padding_y = content_height * 0.1

        if start_pos_key == "bottom_left":
            x_start = m_left + padding_x
            y_start = height - m_bottom - padding_y
        elif start_pos_key == "top_left":
            x_start = m_left + padding_x
            y_start = m_top + padding_y
        elif start_pos_key == "bottom_center":
            x_start = width / 2
            y_start = height - m_bottom - padding_y
        else:  # "center"
            x_start = width / 2
            y_start = height / 2

        print(
            f"Generating L-System with {lsystem_iterations} iterations and {step_length_px:.2f}px step..."
        )

        # Override draw_kwargs for L-System
        draw_kwargs["lsystem_config"] = lsystem_config
        draw_kwargs["x_start"] = x_start
        draw_kwargs["y_start"] = y_start
        draw_kwargs["width"] = content_width
        draw_kwargs["height"] = content_height

    # Call the specific drawing function
    try:
        draw_func(**draw_kwargs)
    except Exception as e:
        print(f"Error drawing cover style '{cover_type}': {e}")
        # Raise to stop execution
        raise

    # 7. Draw Decorative Border
    decorative_border = kwargs.get("decorative_border")
    if decorative_border:
        draw_decorative_border(
            ctx,
            m_left,
            width - m_right,
            m_top,
            height - m_bottom,
            border_width=kwargs.get("line_width_px", 0.5) * 2,
            style=decorative_border,
        )

    # 8. Draw Title Element
    cover_config = kwargs.get("cover_config")
    if cover_config:
        draw_title_element(ctx, width, height, cover_config)

    return surface
