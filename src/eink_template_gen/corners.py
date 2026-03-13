"""
Corner ornament system for decorative page corners

This module uses a registry pattern for extensibility. To add a new style:
1. Create a new internal function, e.g., _draw_my_corner(ctx, x, y, ...).
2. Add it to the CORNER_REGISTRY dictionary at the bottom.
"""

from math import pi

from .devices import snap_to_eink_greyscale

# --- Internal Helper Functions for Each Corner Style ---


def _draw_circuit_corner(ctx, x, y, size=20.0, line_width=1.5, corner="top-left"):
    """
    Draw circuit board style corner with traces and pads

    Args:
        x, y: Corner position
        size: Size of the corner ornament
        line_width: Width of circuit traces
        corner: Which corner ("top-left", "top-right", "bottom-left", "bottom-right")
    """
    # Determine direction multipliers based on corner
    if corner == "top-left":
        h_dir, v_dir = 1, 1  # traces go right and down
    elif corner == "top-right":
        h_dir, v_dir = -1, 1  # traces go left and down
    elif corner == "bottom-left":
        h_dir, v_dir = 1, -1  # traces go right and up
    else:  # "bottom-right"
        h_dir, v_dir = -1, -1  # traces go left and up

    ctx.set_line_width(line_width)

    # Main L-bracket frame
    ctx.move_to(x, y + (v_dir * size))
    ctx.line_to(x, y)
    ctx.line_to(x + (h_dir * size), y)
    ctx.set_line_width(line_width * 1.5)
    ctx.stroke()

    # Corner pad (connection point)
    ctx.arc(x, y, size * 0.15, 0, 2 * pi)
    ctx.fill()
    ctx.arc(x, y, size * 0.25, 0, 2 * pi)
    ctx.set_line_width(line_width * 0.8)
    ctx.stroke()

    # Horizontal traces with pads
    for i in range(2):
        trace_y = y + (v_dir * (size * 0.35 + i * size * 0.3))
        trace_len = size * 0.7

        ctx.set_line_width(line_width)
        ctx.move_to(x + (h_dir * size * 0.3), trace_y + 0.5)
        ctx.line_to(x + (h_dir * trace_len), trace_y + 0.5)
        ctx.stroke()

        # End pad
        pad_x = x + (h_dir * trace_len)
        ctx.rectangle(pad_x - 2, trace_y - 2, 4, 4)
        ctx.stroke()
        ctx.arc(pad_x, trace_y, 1, 0, 2 * pi)
        ctx.fill()

    # Vertical traces with pads
    for i in range(2):
        trace_x = x + (h_dir * (size * 0.35 + i * size * 0.3))
        trace_len = size * 0.7

        ctx.set_line_width(line_width)
        ctx.move_to(trace_x + 0.5, y + (v_dir * size * 0.3))
        ctx.line_to(trace_x + 0.5, y + (v_dir * trace_len))
        ctx.stroke()

        # End pad
        pad_y = y + (v_dir * trace_len)
        ctx.rectangle(trace_x - 2, pad_y - 2, 4, 4)
        ctx.stroke()
        ctx.arc(trace_x, pad_y, 1, 0, 2 * pi)
        ctx.fill()


def _draw_bracket(
    ctx, x, y, size=20.0, line_width=2.0, corner="top-left", notch=True, double=False
):
    """
    Draw simple bracket corner marker

    Args:
        x, y: Corner position
        size: Size of the bracket
        line_width: Width of lines
        corner: Which corner
        notch: Whether to add notches at the ends
        double: Whether to draw double lines
    """
    if corner == "top-left":
        h_dir, v_dir = 1, 1
    elif corner == "top-right":
        h_dir, v_dir = -1, 1
    elif corner == "bottom-left":
        h_dir, v_dir = 1, -1
    else:  # "bottom-right"
        h_dir, v_dir = -1, -1

    ctx.set_line_width(line_width)

    # Main bracket
    ctx.move_to(x + (h_dir * size), y)
    ctx.line_to(x, y)
    ctx.line_to(x, y + (v_dir * size))
    ctx.stroke()

    # Double line version
    if double:
        offset = line_width * 2
        ctx.move_to(x + (h_dir * size), y + (v_dir * offset))
        ctx.line_to(x + (h_dir * offset), y + (v_dir * offset))
        ctx.line_to(x + (h_dir * offset), y + (v_dir * size))
        ctx.stroke()

    # Notches at ends
    if notch:
        notch_size = size * 0.2

        # Horizontal notch
        ctx.move_to(x + (h_dir * size), y - (v_dir * notch_size))
        ctx.line_to(x + (h_dir * size), y + (v_dir * notch_size))
        ctx.stroke()

        # Vertical notch
        ctx.move_to(x - (h_dir * notch_size), y + (v_dir * size))
        ctx.line_to(x + (h_dir * notch_size), y + (v_dir * size))
        ctx.stroke()


def _draw_crosshair(ctx, x, y, size=15.0, line_width=1.5, corner="top-left", center_circle=True):
    """
    Draw registration mark / crosshair style corner

    Args:
        x, y: Corner position
        size: Size of the crosshair
        line_width: Width of lines
        corner: Which corner
        center_circle: Whether to draw center circle
    """
    ctx.set_line_width(line_width)

    # Crosshair lines
    ctx.move_to(x - size, y + 0.5)
    ctx.line_to(x + size, y + 0.5)
    ctx.stroke()

    ctx.move_to(x + 0.5, y - size)
    ctx.line_to(x + 0.5, y + size)
    ctx.stroke()

    # Center circle
    if center_circle:
        ctx.arc(x, y, size * 0.3, 0, 2 * pi)
        ctx.stroke()
        ctx.arc(x, y, size * 0.15, 0, 2 * pi)
        ctx.fill()

    # Corner indicators (small ticks)
    tick_size = size * 0.3
    tick_offset = size * 0.7

    if corner == "top-left":
        h_dir, v_dir = 1, 1
    elif corner == "top-right":
        h_dir, v_dir = -1, 1
    elif corner == "bottom-left":
        h_dir, v_dir = 1, -1
    else:  # "bottom-right"
        h_dir, v_dir = -1, -1

    # Direction ticks
    ctx.move_to(x + (h_dir * tick_offset), y)
    ctx.line_to(x + (h_dir * (tick_offset + tick_size)), y)
    ctx.stroke()

    ctx.move_to(x, y + (v_dir * tick_offset))
    ctx.line_to(x, y + (v_dir * (tick_offset + tick_size)))
    ctx.stroke()


def _draw_geometric_frame(ctx, x, y, size=20.0, line_width=1.5, corner="top-left", num_frames=3):
    """
    Draw nested geometric frames in corner

    Args:
        x, y: Corner position
        size: Size of outer frame
        line_width: Width of lines
        corner: Which corner
        num_frames: Number of nested frames (1-5)
    """
    if corner == "top-left":
        h_dir, v_dir = 1, 1
    elif corner == "top-right":
        h_dir, v_dir = -1, 1
    elif corner == "bottom-left":
        h_dir, v_dir = 1, -1
    else:  # "bottom-right"
        h_dir, v_dir = -1, -1

    ctx.set_line_width(line_width)

    # Draw nested rectangles
    for i in range(num_frames):
        inset = i * (size / (num_frames + 1))
        frame_size = size - inset

        x_corner = x + (h_dir * inset)
        y_corner = y + (v_dir * inset)

        # L-shaped frame
        ctx.move_to(x_corner + (h_dir * frame_size), y_corner)
        ctx.line_to(x_corner, y_corner)
        ctx.line_to(x_corner, y_corner + (v_dir * frame_size))
        ctx.stroke()


def _draw_tech_marker(
    ctx, x, y, size=18.0, line_width=1.5, corner="top-left", marker_style="arrows"
):
    """
    Draw technical marker with directional indicators

    Args:
        x, y: Corner position
        size: Size of the marker
        line_width: Width of lines
        corner: Which corner
        marker_style: "arrows", "compass", or "grid"
    """
    if corner == "top-left":
        h_dir, v_dir = 1, 1
    elif corner == "top-right":
        h_dir, v_dir = -1, 1
    elif corner == "bottom-left":
        h_dir, v_dir = 1, -1
    else:  # "bottom-right"
        h_dir, v_dir = -1, -1

    ctx.set_line_width(line_width)

    if marker_style == "arrows":
        # Cardinal direction arrows
        arrow_size = size * 0.4

        # Horizontal arrow
        ctx.move_to(x, y)
        ctx.line_to(x + (h_dir * size), y)
        ctx.stroke()

        ctx.move_to(x + (h_dir * (size - arrow_size)), y - arrow_size / 2)
        ctx.line_to(x + (h_dir * size), y)
        ctx.line_to(x + (h_dir * (size - arrow_size)), y + arrow_size / 2)
        ctx.stroke()

        # Vertical arrow
        ctx.move_to(x, y)
        ctx.line_to(x, y + (v_dir * size))
        ctx.stroke()

        ctx.move_to(x - arrow_size / 2, y + (v_dir * (size - arrow_size)))
        ctx.line_to(x, y + (v_dir * size))
        ctx.line_to(x + arrow_size / 2, y + (v_dir * (size - arrow_size)))
        ctx.stroke()

    elif marker_style == "compass":
        # Compass rose style
        ctx.arc(x, y, size * 0.3, 0, 2 * pi)
        ctx.stroke()

        # Four cardinal points
        for angle in [0, 90, 180, 270]:
            rad = (angle * pi) / 180
            import math

            x_end = x + size * 0.5 * math.cos(rad)
            y_end = y + size * 0.5 * math.sin(rad)

            ctx.move_to(x, y)
            ctx.line_to(x_end, y_end)
            ctx.stroke()

    elif marker_style == "grid":
        # Small grid pattern
        grid_spacing = size / 4
        for i in range(5):
            offset = i * grid_spacing

            # Horizontal lines
            ctx.move_to(x, y + (v_dir * offset))
            ctx.line_to(x + (h_dir * size), y + (v_dir * offset))
            ctx.stroke()

            # Vertical lines
            ctx.move_to(x + (h_dir * offset), y)
            ctx.line_to(x + (h_dir * offset), y + (v_dir * size))
            ctx.stroke()


def _draw_diagonal_stripes(
    ctx, x, y, size=20.0, line_width=1.5, corner="top-left", num_stripes=4, stripe_gap=4.0
):
    """
    Draw diagonal stripe pattern in corner

    Args:
        x, y: Corner position
        size: Size of the corner area
        line_width: Width of stripe lines
        corner: Which corner
        num_stripes: Number of diagonal stripes
        stripe_gap: Gap between stripes
    """
    if corner == "top-left":
        h_dir, v_dir = 1, 1
    elif corner == "top-right":
        h_dir, v_dir = -1, 1
    elif corner == "bottom-left":
        h_dir, v_dir = 1, -1
    else:  # "bottom-right"
        h_dir, v_dir = -1, -1

    ctx.set_line_width(line_width)

    # Draw diagonal stripes
    for i in range(num_stripes):
        offset = i * stripe_gap

        # Diagonal line from horizontal edge
        x_start = x + (h_dir * offset)
        y_start = y
        x_end = x
        y_end = y + (v_dir * offset)

        ctx.move_to(x_start, y_start)
        ctx.line_to(x_end, y_end)
        ctx.stroke()

        # Additional stripes along the edges
        if i > 0:
            # From vertical edge
            x_start2 = x
            y_start2 = y + (v_dir * (offset + stripe_gap))
            x_end2 = x + (h_dir * (offset + stripe_gap))
            y_end2 = y

            if offset + stripe_gap <= size:
                ctx.move_to(x_start2, y_start2)
                ctx.line_to(x_end2, y_end2)
                ctx.stroke()


def _draw_corner_node(
    ctx, x, y, size=12.0, line_width=1.5, corner="top-left", node_style="circuit"
):
    """
    Draw a connection node style corner marker

    Args:
        x, y: Corner position
        size: Size of the node area
        line_width: Width of lines
        corner: Which corner
        node_style: "circuit", "mechanical", or "organic"
    """
    if corner == "top-left":
        h_dir, v_dir = 1, 1
    elif corner == "top-right":
        h_dir, v_dir = -1, 1
    elif corner == "bottom-left":
        h_dir, v_dir = 1, -1
    else:  # "bottom-right"
        h_dir, v_dir = -1, -1

    ctx.set_line_width(line_width)

    if node_style == "circuit":
        # Central node
        ctx.arc(x, y, size * 0.25, 0, 2 * pi)
        ctx.fill()
        ctx.arc(x, y, size * 0.4, 0, 2 * pi)
        ctx.stroke()

        # Connection traces
        ctx.move_to(x, y)
        ctx.line_to(x + (h_dir * size), y)
        ctx.stroke()

        ctx.move_to(x, y)
        ctx.line_to(x, y + (v_dir * size))
        ctx.stroke()

        # Small nodes at ends
        ctx.arc(x + (h_dir * size), y, size * 0.15, 0, 2 * pi)
        ctx.fill()

        ctx.arc(x, y + (v_dir * size), size * 0.15, 0, 2 * pi)
        ctx.fill()

    elif node_style == "mechanical":
        # Mounting hole style
        ctx.arc(x, y, size * 0.3, 0, 2 * pi)
        ctx.stroke()
        ctx.arc(x, y, size * 0.15, 0, 2 * pi)
        ctx.fill()

        # Corner brackets
        bracket_size = size * 0.6
        ctx.move_to(x + (h_dir * bracket_size), y)
        ctx.line_to(x, y)
        ctx.line_to(x, y + (v_dir * bracket_size))
        ctx.stroke()


def _draw_pixel_art_corner(
    ctx, x, y, size=16.0, line_width=1.0, corner="top-left", pattern="blocks"
):
    """
    Draw pixelated/blocky corner ornament

    Args:
        x, y: Corner position
        size: Size (should be multiple of pixel_size for clean look)
        line_width: Width of pixel outlines
        corner: Which corner
        pattern: "blocks", "steps", or "checker"
    """
    if corner == "top-left":
        h_dir, v_dir = 1, 1
    elif corner == "top-right":
        h_dir, v_dir = -1, 1
    elif corner == "bottom-left":
        h_dir, v_dir = 1, -1
    else:  # "bottom-right"
        h_dir, v_dir = -1, -1

    ctx.set_line_width(line_width)
    pixel_size = size / 4  # 4x4 grid

    if pattern == "blocks":
        # Random-ish blocky pattern
        blocks = [
            (0, 0),
            (1, 0),
            (2, 0),
            (0, 1),
            (1, 1),
            (0, 2),
            (1, 2),
            (2, 2),
            (0, 3),
            (1, 3),
            (2, 3),
            (3, 3),
        ]

        for bx, by in blocks:
            px = x + (h_dir * bx * pixel_size)
            py = y + (v_dir * by * pixel_size)

            ctx.rectangle(px, py, h_dir * pixel_size, v_dir * pixel_size)
            ctx.fill()

    elif pattern == "steps":
        # Staircase pattern
        for i in range(4):
            for j in range(4 - i):
                px = x + (h_dir * j * pixel_size)
                py = y + (v_dir * i * pixel_size)

                ctx.rectangle(px, py, h_dir * pixel_size, v_dir * pixel_size)
                ctx.fill()

    elif pattern == "checker":
        # Checkerboard pattern
        for i in range(4):
            for j in range(4):
                if (i + j) % 2 == 0:
                    px = x + (h_dir * j * pixel_size)
                    py = y + (v_dir * i * pixel_size)

                    ctx.rectangle(px, py, h_dir * pixel_size, v_dir * pixel_size)
                    ctx.fill()


# --- Main Drawing Function ---


def draw_corner_ornament(ctx, x, y, style="bracket", corner="top-left", size=20.0, **kwargs):
    """
    Draw decorative corner ornament

    Args:
        ctx: Cairo context
        x, y: Corner position (actual corner point of the page margin)
        style: Name of the style to draw
        corner: Which corner ("top-left", "top-right", "bottom-left", "bottom-right")
        size: Size of the ornament in pixels
        **kwargs: Style-specific parameters
    """
    if style is None:
        return

    # Save context state
    ctx.save()

    # Handle greyscale color
    grey_value = kwargs.get("grey", kwargs.get("gray", 0.0))
    grey_value = snap_to_eink_greyscale(grey_value)
    ctx.set_source_rgb(grey_value, grey_value, grey_value)

    # Get the drawing function
    draw_func = CORNER_REGISTRY.get(style)

    if not draw_func:
        print(f"Warning: Unknown corner style '{style}'. Using 'bracket'.")
        draw_func = _draw_bracket

    # Build kwargs for the function
    import inspect

    sig = inspect.signature(draw_func)
    valid_params = sig.parameters.keys()

    final_kwargs = {"ctx": ctx, "x": x, "y": y, "corner": corner, "size": size}

    # Add all other kwargs only if the function accepts them
    for key, value in kwargs.items():
        if key not in ["grey", "gray"] and key in valid_params:
            final_kwargs[key] = value

    # Call the function
    try:
        draw_func(**final_kwargs)
    except Exception as e:
        print(f"Error drawing corner style '{style}': {e}")

    # Restore context
    ctx.restore()


def draw_page_corners(
    ctx,
    margins,
    page_width,
    page_height,
    corner_style=None,
    corner_size=20.0,
    margin_inset_ratio=0.618,
    **kwargs,
) -> bool:
    """
    Draw corner ornaments positioned in the margins with slight overlap into content

    Args:
        ctx: Cairo context
        margins: PageMargins object
        page_width: Page width in pixels
        page_height: Page height in pixels
        corner_style: Style name or dict mapping corner names to styles
        corner_size: Size of corner ornaments
        margin_inset_ratio: Ratio of ornament that extends into content (default: 0.618 - golden ratio)
        **kwargs: Style parameters

    Returns:
        bool: True if corners were drawn
    """
    if corner_style is None:
        return False

    # Handle different corner style specifications
    if isinstance(corner_style, str):
        # Same style for all corners
        styles = {
            "top-left": corner_style,
            "top-right": corner_style,
            "bottom-left": corner_style,
            "bottom-right": corner_style,
        }
    elif isinstance(corner_style, dict):
        # Different styles per corner
        styles = corner_style
    else:
        return False

    # Calculate the offset based on golden ratio
    # The ornament extends INTO the content by (corner_size * margin_inset_ratio)
    # So we need to offset the "origin" point by that amount AWAY from content
    inset_amount = corner_size * margin_inset_ratio

    # Corner positions (offset into the margins)
    corners = {
        "top-left": (
            margins.left - (corner_size - inset_amount),  # Move left into margin
            margins.top - (corner_size - inset_amount),  # Move up into margin
        ),
        "top-right": (
            page_width - margins.right + (corner_size - inset_amount),  # Move right into margin
            margins.top - (corner_size - inset_amount),  # Move up into margin
        ),
        "bottom-left": (
            margins.left - (corner_size - inset_amount),  # Move left into margin
            page_height - margins.bottom + (corner_size - inset_amount),  # Move down into margin
        ),
        "bottom-right": (
            page_width - margins.right + (corner_size - inset_amount),  # Move right into margin
            page_height - margins.bottom + (corner_size - inset_amount),  # Move down into margin
        ),
    }

    # Draw each corner
    for corner_name, (x, y) in corners.items():
        style = styles.get(corner_name)
        if style:
            draw_corner_ornament(ctx, x, y, style, corner_name, corner_size, **kwargs)

    return True


# --- Style Registry ---


CORNER_REGISTRY = {
    "circuit-corner": _draw_circuit_corner,
    "bracket": _draw_bracket,
    "crosshair": _draw_crosshair,
    "geometric-frame": _draw_geometric_frame,
    "tech-marker": _draw_tech_marker,
    "diagonal-stripes": _draw_diagonal_stripes,
    "corner-node": _draw_corner_node,
    "pixel-art": _draw_pixel_art_corner,
}

# Available corner styles for reference
CORNER_STYLES = sorted([style for style in CORNER_REGISTRY.keys()]) + [None]
