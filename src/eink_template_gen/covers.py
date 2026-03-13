"""
Title page pattern generators for decorative covers
"""

from math import pow

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
from .separators import draw_page_separators
from .utils import (
    PageMargins,
    SpacingResult,
    create_canvas,
)

# --- L-System Definitions ---
# (Unchanged)
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


# --- Data-Driven Registry (Unchanged) ---
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
    "_lsystem": {
        "draw_func": draw_lsystem_pattern,
        "align_unit_h": "none",
        "align_unit_v": "none",
        "specific_args_map": {"line_width_px": "line_width"},
    },
}

for lsystem_name in L_SYSTEM_DEFINITIONS.keys():
    COVER_REGISTRY[lsystem_name] = COVER_REGISTRY["_lsystem"]


# --- Main Factory Function ---


def create_cover_surface(
    cover_type: str,
    margins: PageMargins,
    spacing: SpacingResult,
    page_width: int,
    page_height: int,
    header: str,
    footer: str,
    **kwargs,
) -> cairo.ImageSurface:
    """
    Primary factory for generating all cover pages.
    (Refactored to use PageMargins and SpacingResult)

    Args:
        cover_type (str): The name of the cover (e.g., "truchet")
        margins (PageMargins): Pre-calculated margin object
        spacing (SpacingResult): Pre-calculated spacing object
        page_width (int): Full page width
        page_height (int): Full page height
        header (str): Header config string
        footer (str): Footer config string
        **kwargs: A dict of all other args (cover_config, line_width_px, etc.)
    """
    # 1. Get Config
    is_lsystem = cover_type in L_SYSTEM_DEFINITIONS
    config_key = "_lsystem" if is_lsystem else cover_type

    if config_key not in COVER_REGISTRY:
        raise ValueError(f"Unknown cover type '{cover_type}'")

    config = COVER_REGISTRY[config_key]
    draw_func = config["draw_func"]

    spacing.print_adjustment_message()  # Print if adjustment happened
    spacing = spacing.pixels

    # 2. Setup Canvas (DRY)
    surface, ctx = create_canvas(page_width, page_height)

    # 3. Draw Headers/Footers (DRY)
    draw_page_separators(ctx, margins, page_width, page_height, header, footer)

    # 4. Prepare and Call Drawing Function
    draw_kwargs = {
        "ctx": ctx,
        "x_start": margins.content_x_start,
        "x_end": margins.content_x_start + margins.content_width,
        "y_start": margins.content_y_start,
        "y_end": margins.content_y_start + margins.content_height,
        "spacing": spacing,
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

        min_content_dim = min(margins.content_width, margins.content_height)
        step_length_px = 10  # Default

        estimator_func = lsystem_config.get("bounding_box_estimator")
        if estimator_func:
            num_steps = estimator_func(lsystem_iterations)
            if num_steps > 0:
                step_length_px = (min_content_dim * 0.80) / num_steps

        lsystem_config["step_length"] = step_length_px

        start_pos_key = lsystem_config.get("start_pos", "center")
        padding_x = margins.content_width * 0.1
        padding_y = margins.content_height * 0.1

        if start_pos_key == "bottom_left":
            x_start = margins.content_x_start + padding_x
            y_start = margins.content_y_start + margins.content_height - padding_y
        elif start_pos_key == "top_left":
            x_start = margins.content_x_start + padding_x
            y_start = margins.content_y_start + padding_y
        elif start_pos_key == "bottom_center":
            x_start = margins.content_x_start + (margins.content_width / 2)
            y_start = margins.content_y_start + margins.content_height - padding_y
        else:  # "center"
            x_start = margins.content_x_start + (margins.content_width / 2)
            y_start = margins.content_y_start + (margins.content_height / 2)

        print(
            f"Generating L-System with {lsystem_iterations} iterations and {step_length_px:.2f}px step..."
        )

        # Override draw_kwargs for L-System
        draw_kwargs["lsystem_config"] = lsystem_config
        draw_kwargs["x_start"] = x_start
        draw_kwargs["y_start"] = y_start
        draw_kwargs["width"] = margins.content_width
        draw_kwargs["height"] = margins.content_height

    # Call the specific drawing function
    try:
        draw_func(**draw_kwargs)
    except Exception as e:
        print(f"Error drawing cover style '{cover_type}': {e}")
        raise

    # 5. Draw Decorative Border
    decorative_border = kwargs.get("decorative_border")
    if decorative_border:
        draw_decorative_border(
            ctx,
            margins.content_x_start,
            margins.content_x_start + margins.content_width,
            margins.content_y_start,
            margins.content_y_start + margins.content_height,
            border_width=kwargs.get("line_width_px", 0.5) * 2,
            style=decorative_border,
        )

    # 6. Draw Title Element
    cover_config = kwargs.get("cover_config")
    if cover_config:
        draw_title_element(
            ctx,
            page_width,
            page_height,
            cover_config,
            # Pass the content area rect for JSON-style positioning
            margins.content_x_start,
            margins.content_y_start,
            margins.content_width,
            margins.content_height,
        )

    return surface
