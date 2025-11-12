"""
Glyph library for decorative elements

This module provides a collection of small, reusable geometric primitives
and technical symbols that can be used for decorative purposes.

All glyphs follow a consistent contract:
- Accept (ctx, x, y, size) as base parameters
- Draw centered at (x, y)
- Stay within a size × size bounding box
- Return actual drawn bounds (width, height)
"""

import inspect
from math import pi, cos, sin, sqrt, radians
from typing import Tuple, List, Optional

import cairo

from .devices import snap_to_eink_greyscale


# --- Basic Shapes ---


def _draw_circle(ctx, x, y, size=10, line_width=1.0, filled=False, grey=0):
    """
    Draw a circle
    
    Args:
        ctx: Cairo context
        x, y: Center point
        size: Bounding box size
        line_width: Line width for outline
        filled: Whether to fill the circle
        grey: Greyscale value (0-15 or 0.0-1.0)
    
    Returns:
        tuple: (width, height) of drawn element
    """
    radius = size / 2
    
    if filled:
        ctx.arc(x, y, radius, 0, 2 * pi)
        ctx.fill()
    else:
        ctx.arc(x, y, radius, 0, 2 * pi)
        ctx.set_line_width(line_width)
        ctx.stroke()
    
    return (size, size)


def _draw_square(ctx, x, y, size=10, line_width=1.0, filled=False, grey=0):
    """Draw a square centered at (x, y)"""
    half = size / 2
    
    if filled:
        ctx.rectangle(x - half, y - half, size, size)
        ctx.fill()
    else:
        ctx.rectangle(x - half, y - half, size, size)
        ctx.set_line_width(line_width)
        ctx.stroke()
    
    return (size, size)


def _draw_diamond(ctx, x, y, size=10, line_width=1.0, filled=False, grey=0):
    """Draw a diamond (rotated square) centered at (x, y)"""
    half = size / 2
    
    ctx.move_to(x, y - half)  # Top
    ctx.line_to(x + half, y)  # Right
    ctx.line_to(x, y + half)  # Bottom
    ctx.line_to(x - half, y)  # Left
    ctx.close_path()
    
    if filled:
        ctx.fill()
    else:
        ctx.set_line_width(line_width)
        ctx.stroke()
    
    return (size, size)


def _draw_triangle(ctx, x, y, size=10, line_width=1.0, filled=False, grey=0):
    """Draw an equilateral triangle pointing up, centered at (x, y)"""
    # Equilateral triangle geometry
    height = size * (sqrt(3) / 2)
    half_base = size / 2
    
    # Center vertically
    y_offset = height / 3
    
    ctx.move_to(x, y - (height - y_offset))  # Top
    ctx.line_to(x + half_base, y + y_offset)  # Bottom right
    ctx.line_to(x - half_base, y + y_offset)  # Bottom left
    ctx.close_path()
    
    if filled:
        ctx.fill()
    else:
        ctx.set_line_width(line_width)
        ctx.stroke()
    
    return (size, size)


# --- Arrows (8 Directions) ---


def _draw_arrow_right(ctx, x, y, size=10, line_width=1.0, filled=False, grey=0):
    """Draw a right-pointing arrow"""
    length = size * 0.8
    arrow_width = size * 0.4
    
    # Shaft
    ctx.move_to(x - length/2, y)
    ctx.line_to(x + length/2 - arrow_width*0.6, y)
    
    # Arrowhead
    ctx.line_to(x + length/2 - arrow_width*0.6, y - arrow_width/2)
    ctx.line_to(x + length/2, y)
    ctx.line_to(x + length/2 - arrow_width*0.6, y + arrow_width/2)
    ctx.line_to(x + length/2 - arrow_width*0.6, y)
    
    ctx.set_line_width(line_width)
    ctx.stroke()
    
    return (size, size)


def _draw_arrow_left(ctx, x, y, size=10, line_width=1.0, filled=False, grey=0):
    """Draw a left-pointing arrow"""
    length = size * 0.8
    arrow_width = size * 0.4
    
    # Shaft
    ctx.move_to(x + length/2, y)
    ctx.line_to(x - length/2 + arrow_width*0.6, y)
    
    # Arrowhead
    ctx.line_to(x - length/2 + arrow_width*0.6, y - arrow_width/2)
    ctx.line_to(x - length/2, y)
    ctx.line_to(x - length/2 + arrow_width*0.6, y + arrow_width/2)
    ctx.line_to(x - length/2 + arrow_width*0.6, y)
    
    ctx.set_line_width(line_width)
    ctx.stroke()
    
    return (size, size)


def _draw_arrow_up(ctx, x, y, size=10, line_width=1.0, filled=False, grey=0):
    """Draw an up-pointing arrow"""
    length = size * 0.8
    arrow_width = size * 0.4
    
    # Shaft
    ctx.move_to(x, y + length/2)
    ctx.line_to(x, y - length/2 + arrow_width*0.6)
    
    # Arrowhead
    ctx.line_to(x - arrow_width/2, y - length/2 + arrow_width*0.6)
    ctx.line_to(x, y - length/2)
    ctx.line_to(x + arrow_width/2, y - length/2 + arrow_width*0.6)
    ctx.line_to(x, y - length/2 + arrow_width*0.6)
    
    ctx.set_line_width(line_width)
    ctx.stroke()
    
    return (size, size)


def _draw_arrow_down(ctx, x, y, size=10, line_width=1.0, filled=False, grey=0):
    """Draw a down-pointing arrow"""
    length = size * 0.8
    arrow_width = size * 0.4
    
    # Shaft
    ctx.move_to(x, y - length/2)
    ctx.line_to(x, y + length/2 - arrow_width*0.6)
    
    # Arrowhead
    ctx.line_to(x - arrow_width/2, y + length/2 - arrow_width*0.6)
    ctx.line_to(x, y + length/2)
    ctx.line_to(x + arrow_width/2, y + length/2 - arrow_width*0.6)
    ctx.line_to(x, y + length/2 - arrow_width*0.6)
    
    ctx.set_line_width(line_width)
    ctx.stroke()
    
    return (size, size)


def _draw_arrow_diagonal_ne(ctx, x, y, size=10, line_width=1.0, filled=False, grey=0):
    """Draw a northeast-pointing arrow"""
    length = size * 0.7
    arrow_width = size * 0.35
    
    # Calculate diagonal offsets
    dx = length / sqrt(2)
    dy = length / sqrt(2)
    
    # Shaft
    ctx.move_to(x - dx/2, y + dy/2)
    ctx.line_to(x + dx/2 - arrow_width*0.4, y - dy/2 + arrow_width*0.4)
    
    # Arrowhead
    ctx.line_to(x + dx/2 - arrow_width*0.6, y - dy/2 + arrow_width*0.6 - arrow_width/2)
    ctx.line_to(x + dx/2, y - dy/2)
    ctx.line_to(x + dx/2 - arrow_width*0.6 + arrow_width/2, y - dy/2 + arrow_width*0.6)
    
    ctx.set_line_width(line_width)
    ctx.stroke()
    
    return (size, size)


def _draw_arrow_diagonal_nw(ctx, x, y, size=10, line_width=1.0, filled=False, grey=0):
    """Draw a northwest-pointing arrow"""
    length = size * 0.7
    arrow_width = size * 0.35
    
    dx = length / sqrt(2)
    dy = length / sqrt(2)
    
    # Shaft
    ctx.move_to(x + dx/2, y + dy/2)
    ctx.line_to(x - dx/2 + arrow_width*0.4, y - dy/2 + arrow_width*0.4)
    
    # Arrowhead
    ctx.line_to(x - dx/2 + arrow_width*0.6, y - dy/2 + arrow_width*0.6 - arrow_width/2)
    ctx.line_to(x - dx/2, y - dy/2)
    ctx.line_to(x - dx/2 + arrow_width*0.6 - arrow_width/2, y - dy/2 + arrow_width*0.6)
    
    ctx.set_line_width(line_width)
    ctx.stroke()
    
    return (size, size)


def _draw_arrow_diagonal_se(ctx, x, y, size=10, line_width=1.0, filled=False, grey=0):
    """Draw a southeast-pointing arrow"""
    length = size * 0.7
    arrow_width = size * 0.35
    
    dx = length / sqrt(2)
    dy = length / sqrt(2)
    
    # Shaft
    ctx.move_to(x - dx/2, y - dy/2)
    ctx.line_to(x + dx/2 - arrow_width*0.4, y + dy/2 - arrow_width*0.4)
    
    # Arrowhead
    ctx.line_to(x + dx/2 - arrow_width*0.6, y + dy/2 - arrow_width*0.6 + arrow_width/2)
    ctx.line_to(x + dx/2, y + dy/2)
    ctx.line_to(x + dx/2 - arrow_width*0.6 + arrow_width/2, y + dy/2 - arrow_width*0.6)
    
    ctx.set_line_width(line_width)
    ctx.stroke()
    
    return (size, size)


def _draw_arrow_diagonal_sw(ctx, x, y, size=10, line_width=1.0, filled=False, grey=0):
    """Draw a southwest-pointing arrow"""
    length = size * 0.7
    arrow_width = size * 0.35
    
    dx = length / sqrt(2)
    dy = length / sqrt(2)
    
    # Shaft
    ctx.move_to(x + dx/2, y - dy/2)
    ctx.line_to(x - dx/2 + arrow_width*0.4, y + dy/2 - arrow_width*0.4)
    
    # Arrowhead
    ctx.line_to(x - dx/2 + arrow_width*0.6, y + dy/2 - arrow_width*0.6 + arrow_width/2)
    ctx.line_to(x - dx/2, y + dy/2)
    ctx.line_to(x - dx/2 + arrow_width*0.6 - arrow_width/2, y + dy/2 - arrow_width*0.6)
    
    ctx.set_line_width(line_width)
    ctx.stroke()
    
    return (size, size)


# --- Nodes (Connection Points) ---


def _draw_node_filled(ctx, x, y, size=10, line_width=1.0, filled=True, grey=0):
    """Draw a filled circle node"""
    radius = size / 2
    ctx.arc(x, y, radius, 0, 2 * pi)
    ctx.fill()
    
    return (size, size)


def _draw_node_ring(ctx, x, y, size=10, line_width=1.0, filled=False, grey=0):
    """Draw a hollow ring node"""
    radius = size / 2
    ctx.arc(x, y, radius, 0, 2 * pi)
    ctx.set_line_width(line_width * 1.2)
    ctx.stroke()
    
    return (size, size)


def _draw_node_double(ctx, x, y, size=10, line_width=1.0, filled=False, grey=0):
    """Draw a double-ring node"""
    radius_outer = size / 2
    radius_inner = size / 4
    
    # Inner filled circle
    ctx.arc(x, y, radius_inner, 0, 2 * pi)
    ctx.fill()
    
    # Outer ring
    ctx.arc(x, y, radius_outer, 0, 2 * pi)
    ctx.set_line_width(line_width)
    ctx.stroke()
    
    return (size, size)


def _draw_node_cross(ctx, x, y, size=10, line_width=1.0, filled=False, grey=0):
    """Draw a crosshair node"""
    extent = size / 2
    
    ctx.set_line_width(line_width * 1.2)
    
    # Horizontal line
    ctx.move_to(x - extent, y)
    ctx.line_to(x + extent, y)
    ctx.stroke()
    
    # Vertical line
    ctx.move_to(x, y - extent)
    ctx.line_to(x, y + extent)
    ctx.stroke()
    
    # Center dot
    ctx.arc(x, y, size * 0.15, 0, 2 * pi)
    ctx.fill()
    
    return (size, size)


# --- Technical Symbols ---


def _draw_plus(ctx, x, y, size=10, line_width=1.0, filled=False, grey=0):
    """Draw a plus sign (+)"""
    extent = size / 2
    
    ctx.set_line_width(line_width * 1.5)
    
    # Horizontal
    ctx.move_to(x - extent, y)
    ctx.line_to(x + extent, y)
    ctx.stroke()
    
    # Vertical
    ctx.move_to(x, y - extent)
    ctx.line_to(x, y + extent)
    ctx.stroke()
    
    return (size, size)


def _draw_cross(ctx, x, y, size=10, line_width=1.0, filled=False, grey=0):
    """Draw a cross/X symbol (×)"""
    extent = size / 2
    
    ctx.set_line_width(line_width * 1.5)
    
    # Diagonal from top-left to bottom-right
    ctx.move_to(x - extent, y - extent)
    ctx.line_to(x + extent, y + extent)
    ctx.stroke()
    
    # Diagonal from top-right to bottom-left
    ctx.move_to(x + extent, y - extent)
    ctx.line_to(x - extent, y + extent)
    ctx.stroke()
    
    return (size, size)


def _draw_asterisk(ctx, x, y, size=10, line_width=1.0, filled=False, grey=0):
    """Draw an asterisk (*) - 8 rays"""
    extent = size / 2
    
    ctx.set_line_width(line_width)
    
    # 8 directions
    angles = [0, 45, 90, 135, 180, 225, 270, 315]
    
    for angle in angles:
        rad = radians(angle)
        x_end = x + extent * cos(rad)
        y_end = y + extent * sin(rad)
        
        ctx.move_to(x, y)
        ctx.line_to(x_end, y_end)
        ctx.stroke()
    
    return (size, size)


def _draw_crosshair(ctx, x, y, size=10, line_width=1.0, filled=False, grey=0):
    """Draw a registration mark / crosshair"""
    outer_extent = size / 2
    inner_gap = size / 5
    
    ctx.set_line_width(line_width)
    
    # Horizontal lines (left and right of center)
    ctx.move_to(x - outer_extent, y)
    ctx.line_to(x - inner_gap, y)
    ctx.stroke()
    
    ctx.move_to(x + inner_gap, y)
    ctx.line_to(x + outer_extent, y)
    ctx.stroke()
    
    # Vertical lines (top and bottom of center)
    ctx.move_to(x, y - outer_extent)
    ctx.line_to(x, y - inner_gap)
    ctx.stroke()
    
    ctx.move_to(x, y + inner_gap)
    ctx.line_to(x, y + outer_extent)
    ctx.stroke()
    
    # Center circle
    ctx.arc(x, y, size * 0.15, 0, 2 * pi)
    ctx.stroke()
    
    return (size, size)


def _draw_bracket_l(ctx, x, y, size=10, line_width=1.0, filled=False, grey=0):
    """Draw an L-bracket corner marker"""
    extent = size / 2
    
    ctx.set_line_width(line_width * 1.5)
    
    ctx.move_to(x + extent, y - extent)
    ctx.line_to(x - extent, y - extent)
    ctx.line_to(x - extent, y + extent)
    
    ctx.stroke()
    
    return (size, size)


# --- Circuit Symbols (Simplified) ---


def _draw_resistor(ctx, x, y, size=10, line_width=1.0, filled=False, grey=0):
    """Draw a simplified resistor symbol"""
    width = size * 0.8
    height = size * 0.4
    
    ctx.set_line_width(line_width)
    
    # Rectangle body
    ctx.rectangle(x - width/2, y - height/2, width, height)
    ctx.stroke()
    
    # Internal lines (simplified zigzag pattern)
    third = width / 3
    ctx.move_to(x - width/2 + third, y - height/2)
    ctx.line_to(x - width/2 + third, y + height/2)
    ctx.stroke()
    
    ctx.move_to(x - width/2 + 2*third, y - height/2)
    ctx.line_to(x - width/2 + 2*third, y + height/2)
    ctx.stroke()
    
    return (size, size)


def _draw_capacitor(ctx, x, y, size=10, line_width=1.0, filled=False, grey=0):
    """Draw a simplified capacitor symbol"""
    height = size * 0.7
    gap = size * 0.15
    
    ctx.set_line_width(line_width * 1.5)
    
    # Two parallel lines
    ctx.move_to(x - gap/2, y - height/2)
    ctx.line_to(x - gap/2, y + height/2)
    ctx.stroke()
    
    ctx.move_to(x + gap/2, y - height/2)
    ctx.line_to(x + gap/2, y + height/2)
    ctx.stroke()
    
    return (size, size)


def _draw_diode(ctx, x, y, size=10, line_width=1.0, filled=False, grey=0):
    """Draw a simplified diode symbol"""
    triangle_size = size * 0.5
    line_width_symbol = line_width * 1.2
    
    ctx.set_line_width(line_width_symbol)
    
    # Triangle (anode side)
    ctx.move_to(x - triangle_size/2, y - triangle_size/2)
    ctx.line_to(x, y)
    ctx.line_to(x - triangle_size/2, y + triangle_size/2)
    ctx.close_path()
    ctx.stroke()
    
    # Cathode bar
    ctx.move_to(x, y - triangle_size/2)
    ctx.line_to(x, y + triangle_size/2)
    ctx.stroke()
    
    return (size, size)


def _draw_ic_chip(ctx, x, y, size=10, line_width=1.0, filled=False, grey=0):
    """Draw a simplified IC chip symbol"""
    body_size = size * 0.7
    pin_length = size * 0.15
    
    ctx.set_line_width(line_width)
    
    # Chip body
    ctx.rectangle(x - body_size/2, y - body_size/2, body_size, body_size)
    ctx.stroke()
    
    # Pins (4 on each side)
    num_pins = 2
    spacing = body_size / (num_pins + 1)
    
    for i in range(1, num_pins + 1):
        offset = -body_size/2 + i * spacing
        
        # Left pins
        ctx.move_to(x - body_size/2, y + offset)
        ctx.line_to(x - body_size/2 - pin_length, y + offset)
        ctx.stroke()
        
        # Right pins
        ctx.move_to(x + body_size/2, y + offset)
        ctx.line_to(x + body_size/2 + pin_length, y + offset)
        ctx.stroke()
        
        # Top pins
        ctx.move_to(x + offset, y - body_size/2)
        ctx.line_to(x + offset, y - body_size/2 - pin_length)
        ctx.stroke()
        
        # Bottom pins
        ctx.move_to(x + offset, y + body_size/2)
        ctx.line_to(x + offset, y + body_size/2 + pin_length)
        ctx.stroke()
    
    return (size, size)


# --- Decorative Symbols ---


def _draw_star(ctx, x, y, size=10, line_width=1.0, filled=False, grey=0):
    """Draw a 5-pointed star"""
    outer_radius = size / 2
    inner_radius = size / 5
    
    points = []
    for i in range(10):
        angle = (i * 36 - 90) * pi / 180  # Start at top
        radius = outer_radius if i % 2 == 0 else inner_radius
        px = x + radius * cos(angle)
        py = y + radius * sin(angle)
        points.append((px, py))
    
    # Draw star
    ctx.move_to(points[0][0], points[0][1])
    for px, py in points[1:]:
        ctx.line_to(px, py)
    ctx.close_path()
    
    if filled:
        ctx.fill()
    else:
        ctx.set_line_width(line_width)
        ctx.stroke()
    
    return (size, size)


def _draw_gear(ctx, x, y, size=10, line_width=1.0, filled=False, grey=0):
    """Draw a simplified gear/cog symbol"""
    outer_radius = size / 2
    inner_radius = size / 3
    tooth_height = size * 0.15
    num_teeth = 8
    
    ctx.set_line_width(line_width)
    
    # Draw gear teeth
    for i in range(num_teeth):
        angle1 = (i * 360 / num_teeth - 90) * pi / 180
        angle2 = ((i + 0.3) * 360 / num_teeth - 90) * pi / 180
        angle3 = ((i + 0.7) * 360 / num_teeth - 90) * pi / 180
        angle4 = ((i + 1) * 360 / num_teeth - 90) * pi / 180
        
        # Outer arc of tooth
        x1 = x + outer_radius * cos(angle1)
        y1 = y + outer_radius * sin(angle1)
        x2 = x + (outer_radius + tooth_height) * cos(angle2)
        y2 = y + (outer_radius + tooth_height) * sin(angle2)
        x3 = x + (outer_radius + tooth_height) * cos(angle3)
        y3 = y + (outer_radius + tooth_height) * sin(angle3)
        x4 = x + outer_radius * cos(angle4)
        y4 = y + outer_radius * sin(angle4)
        
        if i == 0:
            ctx.move_to(x1, y1)
        else:
            ctx.line_to(x1, y1)
        
        ctx.line_to(x2, y2)
        ctx.line_to(x3, y3)
        ctx.line_to(x4, y4)
    
    ctx.close_path()
    ctx.stroke()
    
    # Center hole
    ctx.arc(x, y, inner_radius, 0, 2 * pi)
    ctx.stroke()
    
    return (size, size)


def _draw_dot(ctx, x, y, size=10, line_width=1.0, filled=True, grey=0):
    """Draw a small filled dot"""
    radius = size / 4  # Smaller than other circles
    ctx.arc(x, y, radius, 0, 2 * pi)
    ctx.fill()
    
    return (size, size)


def _draw_pixel_block(ctx, x, y, size=10, line_width=1.0, filled=True, grey=0):
    """Draw a small pixel-art style block"""
    block_size = size / 2
    half = block_size / 2
    
    ctx.rectangle(x - half, y - half, block_size, block_size)
    ctx.fill()
    
    return (size, size)


# --- Main Drawing Function ---


def draw_glyph(ctx, x, y, glyph_name, size=10, **kwargs):
    """
    Draw a glyph at the specified position
    
    Args:
        ctx: Cairo context
        x, y: Center position for the glyph
        glyph_name: Name of the glyph to draw
        size: Size of the glyph (bounding box)
        **kwargs: Glyph-specific parameters (line_width, filled, grey, etc.)
    
    Returns:
        tuple: (width, height) of drawn glyph
    """
    # Save context state
    ctx.save()
    
    # Handle greyscale color
    grey_value = kwargs.get("grey", kwargs.get("gray", 0.0))
    grey_value = snap_to_eink_greyscale(grey_value)
    ctx.set_source_rgb(grey_value, grey_value, grey_value)
    
    # Get the drawing function
    draw_func = GLYPH_REGISTRY.get(glyph_name)
    
    if not draw_func:
        print(f"Warning: Unknown glyph '{glyph_name}'. Using 'circle'.")
        draw_func = _draw_circle
    
    # Build kwargs for the function
    sig = inspect.signature(draw_func)
    valid_params = sig.parameters.keys()
    
    final_kwargs = {"ctx": ctx, "x": x, "y": y, "size": size}
    
    # Add all other kwargs only if the function accepts them
    for key, value in kwargs.items():
        if key not in ["grey", "gray"] and key in valid_params:
            final_kwargs[key] = value
    
    # Call the function
    try:
        result = draw_func(**final_kwargs)
        ctx.restore()
        return result
    except Exception as e:
        print(f"Error drawing glyph '{glyph_name}': {e}")
        ctx.restore()
        return (size, size)


# --- Glyph Registry ---


GLYPH_REGISTRY = {
    # Basic shapes
    "circle": _draw_circle,
    "square": _draw_square,
    "diamond": _draw_diamond,
    "triangle": _draw_triangle,
    
    # Arrows - Cardinal
    "arrow-right": _draw_arrow_right,
    "arrow-left": _draw_arrow_left,
    "arrow-up": _draw_arrow_up,
    "arrow-down": _draw_arrow_down,
    
    # Arrows - Diagonal
    "arrow-ne": _draw_arrow_diagonal_ne,
    "arrow-nw": _draw_arrow_diagonal_nw,
    "arrow-se": _draw_arrow_diagonal_se,
    "arrow-sw": _draw_arrow_diagonal_sw,
    
    # Nodes
    "node-filled": _draw_node_filled,
    "node-ring": _draw_node_ring,
    "node-double": _draw_node_double,
    "node-cross": _draw_node_cross,
    
    # Technical symbols
    "plus": _draw_plus,
    "cross": _draw_cross,
    "asterisk": _draw_asterisk,
    "crosshair": _draw_crosshair,
    "bracket": _draw_bracket_l,
    
    # Circuit symbols
    "resistor": _draw_resistor,
    "capacitor": _draw_capacitor,
    "diode": _draw_diode,
    "ic-chip": _draw_ic_chip,
    
    # Decorative
    "star": _draw_star,
    "gear": _draw_gear,
    "dot": _draw_dot,
    "pixel-block": _draw_pixel_block,
}


# --- Category Mapping ---


GLYPH_CATEGORIES = {
    "basic_shapes": ["circle", "square", "diamond", "triangle"],
    "arrows": [
        "arrow-right", "arrow-left", "arrow-up", "arrow-down",
        "arrow-ne", "arrow-nw", "arrow-se", "arrow-sw"
    ],
    "nodes": ["node-filled", "node-ring", "node-double", "node-cross"],
    "technical": ["plus", "cross", "asterisk", "crosshair", "bracket"],
    "circuit": ["resistor", "capacitor", "diode", "ic-chip"],
    "decorative": ["star", "gear", "dot", "pixel-block"],
}


# --- Glyph Metadata ---


GLYPH_METADATA = {
    # Basic shapes
    "circle": {
        "category": "basic_shapes",
        "default_size": 8,
        "description": "Simple circle",
        "filled_variant": True,
        "symmetry": "radial",
        "visual_weight": "light",
    },
    "square": {
        "category": "basic_shapes",
        "default_size": 8,
        "description": "Simple square",
        "filled_variant": True,
        "symmetry": "radial",
        "visual_weight": "medium",
    },
    "diamond": {
        "category": "basic_shapes",
        "default_size": 8,
        "description": "Diamond (rotated square)",
        "filled_variant": True,
        "symmetry": "radial",
        "visual_weight": "light",
    },
    "triangle": {
        "category": "basic_shapes",
        "default_size": 8,
        "description": "Equilateral triangle",
        "filled_variant": True,
        "symmetry": "vertical",
        "visual_weight": "medium",
    },
    
    # Arrows - Cardinal
    "arrow-right": {
        "category": "arrows",
        "default_size": 10,
        "description": "Right-pointing arrow",
        "filled_variant": False,
        "symmetry": "horizontal",
        "visual_weight": "medium",
    },
    "arrow-left": {
        "category": "arrows",
        "default_size": 10,
        "description": "Left-pointing arrow",
        "filled_variant": False,
        "symmetry": "horizontal",
        "visual_weight": "medium",
    },
    "arrow-up": {
        "category": "arrows",
        "default_size": 10,
        "description": "Up-pointing arrow",
        "filled_variant": False,
        "symmetry": "vertical",
        "visual_weight": "medium",
    },
    "arrow-down": {
        "category": "arrows",
        "default_size": 10,
        "description": "Down-pointing arrow",
        "filled_variant": False,
        "symmetry": "vertical",
        "visual_weight": "medium",
    },
    
    # Arrows - Diagonal
    "arrow-ne": {
        "category": "arrows",
        "default_size": 10,
        "description": "Northeast-pointing arrow",
        "filled_variant": False,
        "symmetry": "diagonal",
        "visual_weight": "medium",
    },
    "arrow-nw": {
        "category": "arrows",
        "default_size": 10,
        "description": "Northwest-pointing arrow",
        "filled_variant": False,
        "symmetry": "diagonal",
        "visual_weight": "medium",
    },
    "arrow-se": {
        "category": "arrows",
        "default_size": 10,
        "description": "Southeast-pointing arrow",
        "filled_variant": False,
        "symmetry": "diagonal",
        "visual_weight": "medium",
    },
    "arrow-sw": {
        "category": "arrows",
        "default_size": 10,
        "description": "Southwest-pointing arrow",
        "filled_variant": False,
        "symmetry": "diagonal",
        "visual_weight": "medium",
    },
    
    # Nodes
    "node-filled": {
        "category": "nodes",
        "default_size": 6,
        "description": "Filled circle node",
        "filled_variant": False,
        "symmetry": "radial",
        "visual_weight": "heavy",
    },
    "node-ring": {
        "category": "nodes",
        "default_size": 6,
        "description": "Hollow ring node",
        "filled_variant": False,
        "symmetry": "radial",
        "visual_weight": "light",
    },
    "node-double": {
        "category": "nodes",
        "default_size": 8,
        "description": "Double-ring node",
        "filled_variant": False,
        "symmetry": "radial",
        "visual_weight": "medium",
    },
    "node-cross": {
        "category": "nodes",
        "default_size": 8,
        "description": "Crosshair node",
        "filled_variant": False,
        "symmetry": "radial",
        "visual_weight": "medium",
    },
    
    # Technical symbols
    "plus": {
        "category": "technical",
        "default_size": 8,
        "description": "Plus sign (+)",
        "filled_variant": False,
        "symmetry": "radial",
        "visual_weight": "medium",
    },
    "cross": {
        "category": "technical",
        "default_size": 8,
        "description": "Cross/X symbol (×)",
        "filled_variant": False,
        "symmetry": "radial",
        "visual_weight": "medium",
    },
    "asterisk": {
        "category": "technical",
        "default_size": 8,
        "description": "8-ray asterisk (*)",
        "filled_variant": False,
        "symmetry": "radial",
        "visual_weight": "light",
    },
    "crosshair": {
        "category": "technical",
        "default_size": 10,
        "description": "Registration mark / crosshair",
        "filled_variant": False,
        "symmetry": "radial",
        "visual_weight": "light",
    },
    "bracket": {
        "category": "technical",
        "default_size": 8,
        "description": "L-bracket corner marker",
        "filled_variant": False,
        "symmetry": "none",
        "visual_weight": "medium",
    },
    
    # Circuit symbols
    "resistor": {
        "category": "circuit",
        "default_size": 12,
        "description": "Resistor symbol",
        "filled_variant": False,
        "symmetry": "horizontal",
        "visual_weight": "medium",
    },
    "capacitor": {
        "category": "circuit",
        "default_size": 10,
        "description": "Capacitor symbol",
        "filled_variant": False,
        "symmetry": "vertical",
        "visual_weight": "light",
    },
    "diode": {
        "category": "circuit",
        "default_size": 10,
        "description": "Diode symbol",
        "filled_variant": False,
        "symmetry": "horizontal",
        "visual_weight": "medium",
    },
    "ic-chip": {
        "category": "circuit",
        "default_size": 14,
        "description": "IC chip symbol",
        "filled_variant": False,
        "symmetry": "radial",
        "visual_weight": "heavy",
    },
    
    # Decorative
    "star": {
        "category": "decorative",
        "default_size": 10,
        "description": "5-pointed star",
        "filled_variant": True,
        "symmetry": "radial",
        "visual_weight": "medium",
    },
    "gear": {
        "category": "decorative",
        "default_size": 12,
        "description": "Gear/cog symbol",
        "filled_variant": False,
        "symmetry": "radial",
        "visual_weight": "heavy",
    },
    "dot": {
        "category": "decorative",
        "default_size": 6,
        "description": "Small dot",
        "filled_variant": False,
        "symmetry": "radial",
        "visual_weight": "light",
    },
    "pixel-block": {
        "category": "decorative",
        "default_size": 6,
        "description": "Pixel-art style block",
        "filled_variant": False,
        "symmetry": "radial",
        "visual_weight": "heavy",
    },
}


# --- Helper Functions ---


def get_glyph_by_category(category: str) -> List[str]:
    """
    Return all glyph names in a category
    
    Args:
        category: Category name
    
    Returns:
        List of glyph names
    """
    return GLYPH_CATEGORIES.get(category, [])


def get_all_categories() -> List[str]:
    """Return list of all category names"""
    return list(GLYPH_CATEGORIES.keys())


def get_random_glyph(category: Optional[str] = None, exclude: Optional[List[str]] = None, 
                     seed: Optional[int] = None) -> str:
    """
    Get a random glyph name, optionally filtered by category
    
    Args:
        category: Optional category to filter by
        exclude: Optional list of glyph names to exclude
        seed: Optional random seed for reproducibility
    
    Returns:
        Random glyph name
    """
    import random
    
    if seed is not None:
        random.seed(seed)
    
    if category:
        glyph_list = get_glyph_by_category(category)
    else:
        glyph_list = list(GLYPH_REGISTRY.keys())
    
    if exclude:
        glyph_list = [g for g in glyph_list if g not in exclude]
    
    if not glyph_list:
        return "circle"  # Fallback
    
    return random.choice(glyph_list)


def get_glyph_visual_weight(glyph_name: str) -> str:
    """
    Return visual weight (light/medium/heavy)
    
    Args:
        glyph_name: Name of the glyph
    
    Returns:
        Visual weight string ("light", "medium", or "heavy")
    """
    metadata = GLYPH_METADATA.get(glyph_name, {})
    return metadata.get("visual_weight", "medium")


def get_glyph_default_size(glyph_name: str) -> int:
    """
    Return the default size for a glyph
    
    Args:
        glyph_name: Name of the glyph
    
    Returns:
        Default size in pixels
    """
    metadata = GLYPH_METADATA.get(glyph_name, {})
    return metadata.get("default_size", 10)


def list_glyphs(category: Optional[str] = None) -> List[str]:
    """
    List available glyphs, optionally filtered by category
    
    Args:
        category: Optional category to filter by
    
    Returns:
        List of glyph names
    """
    if category:
        return get_glyph_by_category(category)
    else:
        return sorted(list(GLYPH_REGISTRY.keys()))


def get_glyph_info(glyph_name: str) -> dict:
    """
    Get metadata for a specific glyph
    
    Args:
        glyph_name: Name of the glyph
    
    Returns:
        Metadata dictionary
    """
    return GLYPH_METADATA.get(glyph_name, {
        "category": "unknown",
        "default_size": 10,
        "description": "Unknown glyph",
        "filled_variant": False,
        "symmetry": "none",
        "visual_weight": "medium",
    })


# --- Glyph Collection System ---


GLYPH_COLLECTIONS = {
    "technical": [
        "circle", "square", "cross", "plus", "crosshair",
        "node-ring", "node-double", "bracket"
    ],
    "circuit": [
        "node-filled", "node-ring", "node-double",
        "resistor", "capacitor", "diode", "ic-chip",
        "arrow-right", "arrow-left"
    ],
    "geometric": [
        "circle", "square", "diamond", "triangle",
        "star", "cross", "plus"
    ],
    "arrows": [
        "arrow-right", "arrow-left", "arrow-up", "arrow-down",
        "arrow-ne", "arrow-nw", "arrow-se", "arrow-sw"
    ],
    "nodes": [
        "node-filled", "node-ring", "node-double", "node-cross",
        "dot", "crosshair"
    ],
    "decorative": [
        "star", "asterisk", "gear", "diamond", "triangle"
    ],
    "minimal": [
        "dot", "circle", "square", "plus", "cross"
    ],
    "all": list(GLYPH_REGISTRY.keys()),
}


# Add to glyphs.py
def get_collection(collection_name: str) -> List[str]:
    """
    Get a predefined collection of glyphs (alias for get_palette for compatibility)
    
    Args:
        collection_name: Name of the collection
    
    Returns:
        List of glyph names
    """
    return GLYPH_COLLECTIONS.get(collection_name, GLYPH_COLLECTIONS.get("minimal", []))


def list_collections() -> List[str]:
    """Return list of all available collection names"""
    return list(GLYPH_COLLECTIONS.keys())


# --- Available glyphs list for CLI ---


AVAILABLE_GLYPHS = sorted(list(GLYPH_REGISTRY.keys()))
