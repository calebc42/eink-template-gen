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
from typing import Tuple

import cairo

from .devices import snap_to_eink_greyscale
from .utils import PageMargins

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


def draw_page_separators(
    ctx: cairo.Context,
    margins: PageMargins,
    page_width: int,
    page_height: int,
    header: str = None,
    footer: str = None,
) -> Tuple[bool, bool]:
    """
    Draw header and footer separators if configured.

    Returns:
        Tuple of (has_header, has_footer) for skip logic
    """
    from .separator_config import parse_separator_config

    has_header = False
    has_footer = False

    if header:
        header_style, header_kwargs = parse_separator_config(header)
        if header_style:
            draw_separator_line(
                ctx,
                margins.left,
                page_width - margins.right,
                margins.top,
                style=header_style,
                **header_kwargs,
            )
            has_header = True

    if footer:
        footer_style, footer_kwargs = parse_separator_config(footer)
        if footer_style:
            draw_separator_line(
                ctx,
                margins.left,
                page_width - margins.right,
                page_height - margins.bottom,
                style=footer_style,
                **footer_kwargs,
            )
            has_footer = True

    return has_header, has_footer


def _draw_circuit_trace(
    ctx,
    x_start,
    x_end,
    y,
    line_width=1.5,
    node_spacing=80.0,
    node_radius=2.5,
    num_layers=3,
    layer_gap=4.0,
    segment_style="staggered",
):
    """
    Draw circuit trace with multiple layers and overlapping segments

    Args:
        line_width: Width of the trace lines
        node_spacing: Distance between nodes in pixels
        node_radius: Radius of connection nodes
        num_layers: Number of parallel trace layers (1-5)
        layer_gap: Vertical gap between layers
        segment_style: "staggered" (breaks overlap), "continuous", or "mixed"
    """
    # Calculate layer positions
    total_height = (num_layers - 1) * layer_gap
    y_start = y - total_height / 2

    total_length = x_end - x_start
    num_nodes = max(3, int(total_length / node_spacing))
    actual_spacing = total_length / (num_nodes - 1)

    ctx.set_line_width(line_width)

    # Draw each layer
    for layer_idx in range(num_layers):
        y_layer = y_start + (layer_idx * layer_gap)

        # Determine segment pattern for this layer
        if segment_style == "staggered":
            # Offset start position for each layer to create overlap effect
            offset = (layer_idx * actual_spacing / num_layers) % actual_spacing
        elif segment_style == "mixed":
            offset = (layer_idx * actual_spacing / 2) % actual_spacing if layer_idx % 2 else 0
        else:  # "continuous"
            offset = 0

        # Draw segments between nodes
        for i in range(num_nodes - 1):
            x_node1 = x_start + (i * actual_spacing)
            x_node2 = x_start + ((i + 1) * actual_spacing)

            # For staggered, some segments are shorter to create breaks
            if segment_style in ["staggered", "mixed"] and (i + layer_idx) % 2 == 0:
                # Draw from node to midpoint
                x_seg_start = x_node1
                x_seg_end = (x_node1 + x_node2) / 2
            else:
                # Draw full segment
                x_seg_start = x_node1
                x_seg_end = x_node2

            # Apply offset
            x_seg_start += offset
            x_seg_end += offset

            # Clip to bounds
            if x_seg_start < x_start:
                x_seg_start = x_start
            if x_seg_end > x_end:
                x_seg_end = x_end

            if x_seg_start < x_seg_end:
                ctx.move_to(x_seg_start, y_layer + 0.5)
                ctx.line_to(x_seg_end, y_layer + 0.5)
                ctx.stroke()

    # Draw connection nodes on top (so they overlap the segments)
    for i in range(num_nodes):
        x_node = x_start + (i * actual_spacing)

        # Draw node at random layer (creates interconnected look)
        # Use modulo for deterministic "randomness"
        layer_idx = (i * 3) % num_layers  # Simple pseudo-random layer selection
        y_node = y_start + (layer_idx * layer_gap)

        # Outer ring
        ctx.arc(x_node, y_node, node_radius, 0, 2 * pi)
        ctx.set_line_width(line_width * 0.8)
        ctx.stroke()

        # Filled inner node
        ctx.arc(x_node, y_node, node_radius * 0.4, 0, 2 * pi)
        ctx.fill()

        # Occasionally draw a vertical connection between layers
        if i % 3 == 1 and num_layers > 1:
            # Pick two different layers to connect
            layer1 = (i * 2) % num_layers
            layer2 = (i * 5) % num_layers
            if layer1 != layer2:
                y1 = y_start + (min(layer1, layer2) * layer_gap)
                y2 = y_start + (max(layer1, layer2) * layer_gap)

                ctx.set_line_width(line_width * 0.6)
                ctx.move_to(x_node + 0.5, y1)
                ctx.line_to(x_node + 0.5, y2)
                ctx.stroke()


def _draw_data_flow(
    ctx,
    x_start,
    x_end,
    y,
    line_width=1.5,
    arrow_spacing=100.0,
    arrow_size=6.0,
    node_radius=2.0,
    flow_direction="right",
):
    """
    Draw data flow line with directional arrows and connection nodes

    Args:
        line_width: Width of the main line
        arrow_spacing: Distance between flow arrows
        arrow_size: Size of directional arrows
        node_radius: Radius of connection nodes
        flow_direction: "right", "left", or "bidirectional"
    """
    # Round all coordinates to avoid sub-pixel rendering
    x_start = round(x_start)
    x_end = round(x_end)
    y = round(y)

    # Draw the main line
    ctx.set_line_width(line_width)
    ctx.move_to(x_start, y + 0.5)
    ctx.line_to(x_end, y + 0.5)
    ctx.stroke()

    # Calculate positions
    total_length = x_end - x_start
    num_arrows = max(2, int(total_length / arrow_spacing))
    actual_spacing = total_length / num_arrows

    ctx.set_line_width(line_width * 1.2)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)

    for i in range(num_arrows):
        x = round(x_start + (i * actual_spacing) + actual_spacing / 2)

        if x < x_start or x > x_end:
            continue

        if flow_direction in ["right", "bidirectional"]:
            # Right-pointing arrow - using integer math
            arrow_len = round(arrow_size * 0.8)
            arrow_half_width = round(arrow_size * 0.5)

            ctx.move_to(x - arrow_len, y - arrow_half_width + 0.5)
            ctx.line_to(x + 0.5, y + 0.5)
            ctx.line_to(x - arrow_len, y + arrow_half_width + 0.5)
            ctx.stroke()

        if flow_direction in ["left", "bidirectional"]:
            # Left-pointing arrow
            offset = round(arrow_size * 1.8) if flow_direction == "bidirectional" else 0
            arrow_len = round(arrow_size * 0.8)
            arrow_half_width = round(arrow_size * 0.5)

            ctx.move_to(x + arrow_len - offset + 0.5, y - arrow_half_width + 0.5)
            ctx.line_to(x - offset + 0.5, y + 0.5)
            ctx.line_to(x + arrow_len - offset + 0.5, y + arrow_half_width + 0.5)
            ctx.stroke()

        # Small node between arrows
        if i < num_arrows - 1:
            node_x = round(x + actual_spacing / 2)
            if node_x <= x_end:
                ctx.arc(node_x, y, node_radius, 0, 2 * pi)
                ctx.fill()


def _draw_technical(
    ctx,
    x_start,
    x_end,
    y,
    line_width=1.5,
    num_lines=3,
    line_gap=4.0,
    crosshatch_spacing=60.0,
    crosshatch_height=6.0,
):
    """
    Draw technical separator with multiple parallel lines and crosshatching

    Args:
        line_width: Width of each line
        num_lines: Number of parallel lines (1-5)
        line_gap: Gap between parallel lines
        crosshatch_spacing: Distance between crosshatch marks (0 = none)
        crosshatch_height: Height of crosshatch marks
    """
    ctx.set_line_width(line_width)

    # Calculate total height and start position
    total_height = (num_lines - 1) * line_gap
    y_start = y - total_height / 2

    # Draw parallel lines
    for i in range(num_lines):
        y_line = y_start + (i * line_gap)
        ctx.move_to(x_start, y_line + 0.5)
        ctx.line_to(x_end, y_line + 0.5)
        ctx.stroke()

    # Draw crosshatch marks if requested
    if crosshatch_spacing > 0:
        total_length = x_end - x_start
        num_marks = max(2, int(total_length / crosshatch_spacing))
        actual_spacing = total_length / num_marks

        for i in range(num_marks + 1):
            x_mark = x_start + (i * actual_spacing)
            if x_mark <= x_end:
                # Vertical crosshatch mark
                ctx.move_to(x_mark + 0.5, y_start - crosshatch_height / 2)
                ctx.line_to(x_mark + 0.5, y_start + total_height + crosshatch_height / 2)
                ctx.stroke()


def _draw_schematic(
    ctx,
    x_start,
    x_end,
    y,
    line_width=1.5,
    component_spacing=100.0,
    component_style="resistor",
    component_size=10.0,
):
    """
    Draw schematic-style separator with component symbols

    Args:
        line_width: Width of connection lines
        component_spacing: Distance between components
        component_style: "resistor", "capacitor", "node", or "mixed"
        component_size: Size of component symbols
    """
    ctx.set_line_width(line_width)

    # Calculate component positions
    total_length = x_end - x_start
    num_components = max(2, int(total_length / component_spacing))
    actual_spacing = total_length / (num_components - 1) if num_components > 1 else total_length

    prev_x = x_start

    for i in range(num_components):
        x = x_start + (i * actual_spacing)

        # Draw line to this position
        ctx.move_to(prev_x, y + 0.5)
        ctx.line_to(x - component_size / 2, y + 0.5)
        ctx.stroke()

        # Determine which component to draw
        if component_style == "mixed":
            styles = ["resistor", "capacitor", "node"]
            current_style = styles[i % len(styles)]
        else:
            current_style = component_style

        # Draw the component
        if current_style == "resistor":
            # Resistor symbol (zigzag)
            h = component_size / 2
            w = component_size
            ctx.move_to(x - w / 2, y)
            ctx.line_to(x - w / 3, y - h / 2)
            ctx.line_to(x - w / 6, y + h / 2)
            ctx.line_to(x + w / 6, y - h / 2)
            ctx.line_to(x + w / 3, y + h / 2)
            ctx.line_to(x + w / 2, y)
            ctx.stroke()

        elif current_style == "capacitor":
            # Capacitor symbol (two parallel lines)
            ctx.set_line_width(line_width * 1.5)
            ctx.move_to(x - 1.5, y - component_size / 2)
            ctx.line_to(x - 1.5, y + component_size / 2)
            ctx.stroke()
            ctx.move_to(x + 1.5, y - component_size / 2)
            ctx.line_to(x + 1.5, y + component_size / 2)
            ctx.stroke()
            ctx.set_line_width(line_width)

        elif current_style == "node":
            # Connection node
            ctx.arc(x, y, component_size / 4, 0, 2 * pi)
            ctx.fill()
            ctx.arc(x, y, component_size / 3, 0, 2 * pi)
            ctx.stroke()

        prev_x = x + component_size / 2

    # Final line segment
    ctx.move_to(prev_x, y + 0.5)
    ctx.line_to(x_end, y + 0.5)
    ctx.stroke()


def _draw_connection_nodes(
    ctx,
    x_start,
    x_end,
    y,
    line_width=1.5,
    node_spacing=60.0,
    node_radius=3.0,
    node_style="ring",
    connection_lines=True,
):
    """
    Draw a line of connection nodes

    Args:
        line_width: Width of connecting line
        node_spacing: Distance between nodes
        node_radius: Radius of nodes
        node_style: "ring", "filled", "double", or "cross"
        connection_lines: Whether to draw connecting lines between nodes
    """
    # Draw connecting line if requested
    if connection_lines:
        ctx.set_line_width(line_width)
        ctx.move_to(x_start, y + 0.5)
        ctx.line_to(x_end, y + 0.5)
        ctx.stroke()

    # Calculate node positions
    total_length = x_end - x_start
    num_nodes = max(2, int(total_length / node_spacing))
    actual_spacing = total_length / (num_nodes - 1) if num_nodes > 1 else 0

    for i in range(num_nodes):
        x = x_start + (i * actual_spacing)

        if node_style == "ring":
            ctx.arc(x, y, node_radius, 0, 2 * pi)
            ctx.set_line_width(line_width * 1.2)
            ctx.stroke()

        elif node_style == "filled":
            ctx.arc(x, y, node_radius, 0, 2 * pi)
            ctx.fill()

        elif node_style == "double":
            ctx.arc(x, y, node_radius * 0.5, 0, 2 * pi)
            ctx.fill()
            ctx.arc(x, y, node_radius, 0, 2 * pi)
            ctx.set_line_width(line_width)
            ctx.stroke()

        elif node_style == "cross":
            size = node_radius * 1.2
            ctx.set_line_width(line_width * 1.2)
            ctx.move_to(x - size, y)
            ctx.line_to(x + size, y)
            ctx.stroke()
            ctx.move_to(x, y - size)
            ctx.line_to(x, y + size)
            ctx.stroke()
            ctx.arc(x, y, node_radius * 0.3, 0, 2 * pi)
            ctx.fill()


def _draw_digital_signal(
    ctx, x_start, x_end, y, line_width=1.5, pulse_width=40.0, pulse_height=6.0, duty_cycle=0.5
):
    """
    Draw a digital signal waveform (square wave)

    Args:
        line_width: Width of the signal line
        pulse_width: Width of each pulse cycle
        pulse_height: Height of the signal
        duty_cycle: Ratio of high to low (0.0-1.0)
    """
    ctx.set_line_width(line_width)
    ctx.set_line_cap(cairo.LINE_CAP_SQUARE)

    x = x_start
    state = True

    ctx.move_to(x, y - pulse_height if state else y + pulse_height)

    while x < x_end:
        current_y = y - pulse_height if state else y + pulse_height
        pulse_length = pulse_width * (duty_cycle if state else (1 - duty_cycle))
        next_x = min(x + pulse_length, x_end)

        # Horizontal segment
        ctx.line_to(next_x, current_y)

        # Vertical transition
        if next_x < x_end:
            state = not state
            next_y = y - pulse_height if state else y + pulse_height
            ctx.line_to(next_x, next_y)

        x = next_x

    ctx.stroke()


def _draw_pcb_trace(
    ctx, x_start, x_end, y, line_width=4.0, pad_spacing=100.0, pad_size=6.0, via_holes=True
):
    """
    Draw PCB trace with solder pads

    Args:
        line_width: Width of the PCB trace
        pad_spacing: Distance between solder pads
        pad_size: Size of solder pads
        via_holes: Whether to draw via holes in pads
    """
    # Draw the main trace
    ctx.set_line_width(line_width)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.move_to(x_start, y + 0.5)
    ctx.line_to(x_end, y + 0.5)
    ctx.stroke()

    # Calculate pad positions
    total_length = x_end - x_start
    num_pads = max(2, int(total_length / pad_spacing))
    actual_spacing = total_length / (num_pads - 1) if num_pads > 1 else 0

    for i in range(num_pads):
        x = x_start + (i * actual_spacing)

        # Square pad
        ctx.rectangle(x - pad_size / 2, y - pad_size / 2, pad_size, pad_size)
        ctx.set_line_width(1.0)
        ctx.stroke()

        if via_holes:
            # Via hole
            ctx.arc(x, y, pad_size * 0.25, 0, 2 * pi)
            ctx.fill()


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

# Update STYLE_REGISTRY
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
    # New technical/circuit styles
    "circuit-trace": _draw_circuit_trace,
    "data-flow": _draw_data_flow,
    "technical": _draw_technical,
    "schematic": _draw_schematic,
    "connection-nodes": _draw_connection_nodes,
    "digital-signal": _draw_digital_signal,
    "pcb-trace": _draw_pcb_trace,
}

# Available separator styles for reference
SEPARATOR_STYLES = sorted([style for style in STYLE_REGISTRY.keys()]) + [None]
