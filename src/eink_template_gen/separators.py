"""
Separator line styles for headers and footers

This module uses a registry pattern for extensibility. To add a new style:
1.  Create a new internal function, e.g., _draw_my_style(ctx, x_start, x_end, y, ...).
    It *must* accept ctx, x_start, x_end, and y.
2.  Add it to the STYLE_REGISTRY dictionary at the bottom of the file.
3.  Add its name to the SEPARATOR_STYLES list.
"""

import inspect
from math import pi, radians, sin

import cairo

from .devices import snap_to_eink_greyscale

# --- Internal Helper Functions for Each Style ---


def _draw_bold(ctx, x_start, x_end, y, line_width=4.0):
    ctx.set_line_width(line_width)
    ctx.move_to(x_start, y + 0.5)
    ctx.line_to(x_end, y + 0.5)
    ctx.stroke()


def _draw_double(ctx, x_start, x_end, y, line_width=4.0, gap=4.0):
    half_width = line_width / 2.0
    half_gap = gap / 2.0

    ctx.set_line_width(half_width)
    ctx.move_to(x_start, y - half_gap + 0.5)
    ctx.line_to(x_end, y - half_gap + 0.5)
    ctx.stroke()

    ctx.move_to(x_start, y + half_gap + 0.5)
    ctx.line_to(x_end, y + half_gap + 0.5)
    ctx.stroke()


def _draw_wavy(ctx, x_start, x_end, y, line_width=4.0, amplitude=10.0, wavelength=80.0):
    ctx.set_line_width(line_width)
    ctx.move_to(x_start, y)

    # This pixel-by-pixel approach is smooth and robust
    for x in range(int(x_start), int(x_end) + 1):
        wave_y = y + amplitude * sin(2 * pi * (x - x_start) / wavelength)
        ctx.line_to(x, wave_y)

    # Ensure line reaches the exact end
    wave_y = y + amplitude * sin(2 * pi * (x_end - x_start) / wavelength)
    ctx.line_to(x_end, wave_y)
    ctx.stroke()


def _draw_dashed(ctx, x_start, x_end, y, line_width=4.0, dash_pattern=[5, 3]):
    ctx.set_line_width(line_width)
    ctx.set_dash(dash_pattern)
    ctx.move_to(x_start, y + 0.5)
    ctx.line_to(x_end, y + 0.5)
    ctx.stroke()


def _draw_thick_thin(ctx, x_start, x_end, y, thick_width=4.0, thin_width=0.5, gap=4.0):
    half_gap = gap / 2.0

    ctx.set_line_width(thick_width)
    ctx.move_to(x_start, y - half_gap + 0.5)
    ctx.line_to(x_end, y - half_gap + 0.5)
    ctx.stroke()

    ctx.set_line_width(thin_width)
    ctx.move_to(x_start, y + half_gap + 0.5)
    ctx.line_to(x_end, y + half_gap + 0.5)
    ctx.stroke()


def _draw_zig_zag(ctx, x_start, x_end, y, line_width=4.0, height=10.0, segment_length=10.0):
    ctx.set_line_width(line_width)

    x = x_start
    current_y = y - (height / 2)
    ctx.move_to(x, current_y)

    direction = 1  # 1 for up, -1 for down
    while x < x_end:
        x = min(x + segment_length, x_end)
        current_y = y + (height / 2) * direction
        ctx.line_to(x, current_y)
        direction *= -1
    ctx.stroke()


def _draw_scalloped(ctx, x_start, x_end, y, line_width=4.0, radius=10.0, scallop_direction="down"):
    ctx.set_line_width(line_width)

    x = x_start
    ctx.move_to(x, y)

    # Determine arc angles based on direction
    if scallop_direction == "down":
        angle1, angle2 = 0, pi
    else:  # 'up'
        angle1, angle2 = pi, 0

    while x + (2 * radius) <= x_end:
        # arc(xc, yc, radius, angle1, angle2)
        ctx.arc(x + radius, y, radius, angle1, angle2)
        x += 2 * radius

    # Draw a final connecting line if there's space left
    if x < x_end:
        ctx.line_to(x_end, y)
    ctx.stroke()


def _draw_castellated(ctx, x_start, x_end, y, line_width=4.0, height=10.0, segment_length=20.0):
    ctx.set_line_width(line_width)

    half_height = height / 2.0
    x = x_start
    current_y = y - half_height  # Start low
    ctx.move_to(x, current_y)

    while x < x_end:
        # Move horizontally
        x = min(x + segment_length, x_end)
        ctx.line_to(x, current_y)

        if x < x_end:
            # Move vertically
            current_y = y + half_height if current_y < y else y - half_height
            ctx.line_to(x, current_y)
    ctx.stroke()


def _draw_dotted(ctx, x_start, x_end, y, line_width=4.0, dot_size=None, gap=None):
    # Default dot_size to line_width, gap to 1.5x dot_size
    if dot_size is None:
        dot_size = line_width
    if gap is None:
        gap = dot_size * 1.5

    ctx.set_line_width(dot_size)
    # Dash pattern: 0 pixels of line, (dot_size + gap) pixels of space
    ctx.set_dash([0, dot_size + gap])
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)  # This makes the 0-length dash a round dot

    ctx.move_to(x_start, y + 0.5)
    ctx.line_to(x_end, y + 0.5)
    ctx.stroke()


def _draw_dash_dot(ctx, x_start, x_end, y, line_width=4.0, dash_dot_pattern=[10, 3, 2, 3]):
    ctx.set_line_width(line_width)
    ctx.set_dash(dash_dot_pattern)  # Dash, space, dot, space
    ctx.move_to(x_start, y + 0.5)
    ctx.line_to(x_end, y + 0.5)
    ctx.stroke()


def _draw_barber_stripe(
    ctx, x_start, x_end, y, grey=0, line_height=6.0, stripe_width=6.0, gap_width=6.0, angle=45
):
    """
    Draw barber stripe separator

    Args:
        grey: Greyscale value for stripes (0.0-1.0 or 0-15, default: 0 = black)
        Other args same as before
    """
    angle_rad = radians(angle)
    pat_size = stripe_width + gap_width

    pattern_surface = ctx.get_target().create_similar(
        cairo.CONTENT_COLOR_ALPHA, int(pat_size), int(pat_size)
    )
    pat_ctx = cairo.Context(pattern_surface)

    # Fill pattern with transparent background (the "gap")
    pat_ctx.set_source_rgba(0, 0, 0, 0)
    pat_ctx.paint()

    # Set the stripe color (greyscale snapped)
    grey_value = snap_to_eink_greyscale(grey)
    pat_ctx.set_source_rgb(grey_value, grey_value, grey_value)
    pat_ctx.set_line_width(stripe_width)

    # Rotate the pattern context to draw the angled line
    pat_ctx.translate(pat_size / 2, pat_size / 2)
    pat_ctx.rotate(angle_rad)
    pat_ctx.translate(-pat_size / 2, -pat_size / 2)

    # Draw a line through the middle of the pattern tile
    pat_ctx.move_to(pat_size / 2, -pat_size)
    pat_ctx.line_to(pat_size / 2, pat_size * 2)
    pat_ctx.stroke()

    # Create a cairo pattern from this surface
    pattern = cairo.SurfacePattern(pattern_surface)
    pattern.set_extend(cairo.EXTEND_REPEAT)

    # Fill the separator rectangle with this new pattern
    ctx.set_source(pattern)
    ctx.rectangle(x_start, y - line_height / 2, x_end - x_start, line_height)
    ctx.fill()


def _draw_stitch(
    ctx, x_start, x_end, y, line_width=2.0, stitch_length=8.0, stitch_height=4.0, gap=5.0
):
    ctx.set_line_width(line_width)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)

    x = x_start
    half_h = stitch_height / 2.0

    while x + stitch_length < x_end:
        ctx.move_to(x, y - half_h)
        ctx.line_to(x + stitch_length, y + half_h)
        ctx.stroke()
        x += stitch_length + gap


# --- Main Dispatcher Function ---


def draw_separator_line(ctx, x_start, x_end, y, style="bold", **kwargs):
    """
    Draw decorative separator line

    Args:
        ctx: Cairo context
        x_start: Left boundary (pixels)
        x_end: Right boundary (pixels)
        y: Y position for separator (pixels)
        style: Name of the style to draw.
        **kwargs: Style-specific parameters. See internal functions
            grey/gray: Greyscale value (0.0-1.0 or 0-15 integer)
    """
    if style is None:
        return

    # Save context state to prevent styles from "leaking"
    ctx.save()

    # Handle greyscale color with e-ink snapping
    grey_value = kwargs.get("grey", kwargs.get("gray", 0.0))
    grey_value = snap_to_eink_greyscale(grey_value)

    ctx.set_source_rgb(grey_value, grey_value, grey_value)

    # 2. Find the drawing function
    draw_func = STYLE_REGISTRY.get(style)

    if not draw_func:
        print(f"Warning: Unknown separator style '{style}'. Using 'bold'.")
        draw_func = _draw_bold

    # 3. Inspect the function's signature
    sig = inspect.signature(draw_func)
    valid_params = sig.parameters.keys()

    # 4. Build the final kwargs dict
    # Start with base parameters all functions receive
    final_kwargs = {"ctx": ctx, "x_start": x_start, "x_end": x_end, "y": y}

    # 5. Add all other kwargs from the CLI *only if* the function accepts them
    for key, value in kwargs.items():
        if key not in ["grey", "gray"] and key in valid_params:
            final_kwargs[key] = value

    # 6. Call the function
    try:
        draw_func(**final_kwargs)
    except Exception as e:
        print(f"Error drawing separator style '{style}': {e}")

    # Restore context to its original state
    ctx.restore()


def draw_separator(ctx, x, y_start, y_end, line_width=1.0, grey=5):
    """
    Draw vertical separator line (for dividing columns/sections)

    Args:
        ctx: Cairo context
        x: X position for separator (pixels)
        y_start: Top boundary (pixels)
        y_end: Bottom boundary (pixels)
        line_width: Width of line (pixels)
        grey: Greyscale value (0.0-1.0 or 0-15 integer, default: 5 = #505050)
    """
    ctx.save()
    ctx.set_line_width(line_width)

    # Snap to e-ink greyscale
    grey_value = snap_to_eink_greyscale(grey)
    ctx.set_source_rgb(grey_value, grey_value, grey_value)

    ctx.move_to(x + 0.5, y_start)
    ctx.line_to(x + 0.5, y_end)
    ctx.stroke()
    ctx.restore()


# --- Style Registry and Public List ---

STYLE_REGISTRY = {
    "bold": _draw_bold,
    "double": _draw_double,
    "wavy": _draw_wavy,
    "dashed": _draw_dashed,
    "thick_thin": _draw_thick_thin,
    "zig-zag": _draw_zig_zag,
    "scalloped": _draw_scalloped,
    "castellated": _draw_castellated,
    "dotted": _draw_dotted,
    "dash-dot": _draw_dash_dot,
    "barber-stripe": _draw_barber_stripe,
    "stitch": _draw_stitch,
}

# Available separator styles for reference
SEPARATOR_STYLES = sorted([style for style in STYLE_REGISTRY.keys()]) + [None]
