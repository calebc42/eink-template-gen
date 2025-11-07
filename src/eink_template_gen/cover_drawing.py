"""
Drawing functions for title page patterns
"""

import random
from math import pi, sqrt

import cairo

from .devices import snap_to_eink_greyscale
from .lsystem import generate_lsystem_string
from .noise import fractal_noise_2d, simple_noise_2d, turbulence_2d

# In cover_drawing.py, update draw_truchet_tiles function:


def draw_truchet_tiles(
    ctx,
    x_start,
    x_end,
    y_start,
    y_end,
    tile_size_px,
    line_width,
    rotation_seed=None,
    fill_grey=None,
    variant="classic",
):
    """
    Draw Truchet tile pattern with quarter-circle arcs

    Args:
        ctx: Cairo context
        x_start: Left boundary (pixels)
        x_end: Right boundary (pixels)
        y_start: Top boundary (pixels)
        y_end: Bottom boundary (pixels)
        tile_size_px: Size of each tile (pixels)
        line_width: Width of arcs (pixels)
        rotation_seed: Integer seed for reproducible patterns (None = random)
        fill_grey: Greyscale 0-15 to fill tiles (None = outline)
        variant: 'classic' (arcs), 'cross' (L-shapes), 'triangle' (diagonals), 'wave' (sine), 'mixed'
    """
    import random

    # Set random seed if provided for reproducible patterns
    if rotation_seed is not None:
        random.seed(rotation_seed)

    # Set defaults (will be overridden in _draw_truchet_tile if filling)
    ctx.set_source_rgb(0, 0, 0)
    ctx.set_line_width(line_width)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)

    # Calculate number of tiles
    num_cols = int((x_end - x_start) / tile_size_px)
    num_rows = int((y_end - y_start) / tile_size_px)

    # Draw each tile
    for row in range(num_rows):
        for col in range(num_cols):
            x = x_start + (col * tile_size_px)
            y = y_start + (row * tile_size_px)

            # Randomly choose rotation (0, 90, 180, or 270 degrees)
            rotation = random.choice([0, 1, 2, 3])

            # Choose tile type based on variant
            if variant == "cross":
                _draw_truchet_cross_tile(ctx, x, y, tile_size_px, rotation, fill_grey, line_width)
            elif variant == "triangle":
                _draw_truchet_triangle_tile(
                    ctx, x, y, tile_size_px, rotation, fill_grey, line_width
                )
            elif variant == "wave":
                _draw_truchet_wave_tile(ctx, x, y, tile_size_px, rotation, fill_grey, line_width)
            elif variant == "mixed":
                # Randomly choose between different styles
                tile_type = random.choice(["classic", "cross", "triangle"])
                if tile_type == "cross":
                    _draw_truchet_cross_tile(
                        ctx, x, y, tile_size_px, rotation, fill_grey, line_width
                    )
                elif tile_type == "triangle":
                    _draw_truchet_triangle_tile(
                        ctx, x, y, tile_size_px, rotation, fill_grey, line_width
                    )
                else:  # classic
                    _draw_truchet_tile(ctx, x, y, tile_size_px, rotation, fill_grey, line_width)
            else:  # 'classic'
                _draw_truchet_tile(ctx, x, y, tile_size_px, rotation, fill_grey, line_width)


def _draw_truchet_tile(ctx, x, y, size, rotation, fill_grey, line_width):
    """
    Draw a single Truchet tile with quarter-circle arcs,
    either as outlines or filled regions.

    Args:
        ctx: Cairo context
        x: Top-left x coordinate
        y: Top-left y coordinate
        size: Tile size
        rotation: 0-3 (representing 0°, 90°, 180°, 270°)
        fill_grey: Greyscale 0-15 to fill, or None for outline
        line_width: Width for outline strokes
    """
    # Save context state
    ctx.save()

    # Move to tile center and rotate
    center_x = x + size / 2
    center_y = y + size / 2
    ctx.translate(center_x, center_y)
    ctx.rotate(rotation * pi / 2)
    ctx.translate(-center_x, -center_y)

    if fill_grey is not None:
        # --- FILL LOGIC ---
        fill_color = snap_to_eink_greyscale(fill_grey)
        ctx.set_source_rgb(fill_color, fill_color, fill_color)

        # Draw Path 1 (Top-Right Region)
        ctx.move_to(x, y)  # Top-left
        # Arc from (x,y) to (x+size, y+size)
        ctx.arc(x, y + size, size, -pi / 2, 0)
        ctx.line_to(x + size, y)  # Top-right
        ctx.close_path()
        ctx.fill()

        # Draw Path 2 (Bottom-Left Region)
        # We must move to the arc's start point: (x+size, y+size)
        ctx.move_to(x + size, y + size)
        # Arc from (x+size, y+size) to (x,y)
        ctx.arc(x + size, y, size, pi / 2, pi)
        ctx.line_to(x, y + size)  # Bottom-left
        ctx.close_path()  # Close back to (x+size, y+size)
        ctx.fill()
    else:
        # --- OUTLINE LOGIC ---
        ctx.set_source_rgb(0, 0, 0)
        ctx.set_line_width(line_width)

        # Top-left to bottom-right arc
        ctx.arc(x, y + size, size, -pi / 2, 0)
        ctx.stroke()

        # Bottom-right to top-left arc
        ctx.arc(x + size, y, size, pi / 2, pi)
        ctx.stroke()

    # Restore context state
    ctx.restore()


def _draw_truchet_cross_tile(ctx, x, y, size, rotation, fill_grey, line_width):
    """
    Draw a single Truchet tile with L-shaped cross pattern.

    Args:
        ctx: Cairo context
        x, y, size: Tile boundaries
        rotation: 0-3 (representing 0°, 90°, 180°, 270°)
        fill_grey: Greyscale 0-15 to fill, or None for outline
        line_width: Width for outline strokes
    """
    ctx.save()

    center_x = x + size / 2
    center_y = y + size / 2
    ctx.translate(center_x, center_y)
    ctx.rotate(rotation * pi / 2)
    ctx.translate(-center_x, -center_y)

    if fill_grey is not None:
        fill_color = snap_to_eink_greyscale(fill_grey)
        ctx.set_source_rgb(fill_color, fill_color, fill_color)
    else:
        ctx.set_source_rgb(0, 0, 0)
        ctx.set_line_width(line_width)

    # Draw L-shape
    ctx.move_to(x, center_y)
    ctx.line_to(center_x, center_y)
    ctx.line_to(center_x, y + size)

    if fill_grey is not None:
        ctx.line_to(x, y + size)
        ctx.close_path()
        ctx.fill()
    else:
        ctx.stroke()

    ctx.restore()


def _draw_truchet_triangle_tile(ctx, x, y, size, rotation, fill_grey, line_width):
    """
    Draw a single Truchet tile with diagonal triangle pattern.
    """
    ctx.save()

    center_x = x + size / 2
    center_y = y + size / 2
    ctx.translate(center_x, center_y)
    ctx.rotate(rotation * pi / 2)
    ctx.translate(-center_x, -center_y)

    if fill_grey is not None:
        fill_color = snap_to_eink_greyscale(fill_grey)
        ctx.set_source_rgb(fill_color, fill_color, fill_grey)

        # Fill triangle from corner
        ctx.move_to(x, y)
        ctx.line_to(x + size, y)
        ctx.line_to(x, y + size)
        ctx.close_path()
        ctx.fill()
    else:
        ctx.set_source_rgb(0, 0, 0)
        ctx.set_line_width(line_width)

        # Draw diagonal
        ctx.move_to(x, y)
        ctx.line_to(x + size, y + size)
        ctx.stroke()

    ctx.restore()


def _draw_truchet_wave_tile(ctx, x, y, size, rotation, fill_grey, line_width):
    """
    Draw a single Truchet tile with sine wave pattern.
    """
    from math import sin

    ctx.save()

    center_x = x + size / 2
    center_y = y + size / 2
    ctx.translate(center_x, center_y)
    ctx.rotate(rotation * pi / 2)
    ctx.translate(-center_x, -center_y)

    ctx.set_source_rgb(0, 0, 0)
    ctx.set_line_width(line_width)

    # Draw sine wave across tile
    steps = 10
    ctx.move_to(x, center_y)
    for i in range(steps + 1):
        t = i / steps
        wave_x = x + t * size
        wave_y = center_y + (size * 0.25) * sin(t * pi * 2)
        ctx.line_to(wave_x, wave_y)

    ctx.stroke()
    ctx.restore()


def draw_diagonal_truchet_tiles(
    ctx,
    x_start,
    x_end,
    y_start,
    y_end,
    tile_size_px,
    rotation_seed=None,
    fill_grey_1=0,
    fill_grey_2=15,
):
    """
    Draw diagonal Truchet tile pattern (squares split by a diagonal).

    Args:
        ctx: Cairo context
        x_start...y_end: Boundaries
        tile_size_px: Size of each tile
        rotation_seed: Integer seed for reproducible patterns
        fill_grey_1: Fill for the first triangle (0-15)
        fill_grey_2: Fill for the second triangle (0-15)
    """
    if rotation_seed is not None:
        random.seed(rotation_seed)

    # Calculate number of tiles
    num_cols = int((x_end - x_start) / tile_size_px) + 1
    num_rows = int((y_end - y_start) / tile_size_px) + 1

    # Snap colors
    color_1 = snap_to_eink_greyscale(fill_grey_1)
    color_2 = snap_to_eink_greyscale(fill_grey_2)

    # Draw each tile
    for row in range(num_rows):
        for col in range(num_cols):
            x = x_start + (col * tile_size_px)
            y = y_start + (row * tile_size_px)

            # Randomly choose rotation (0 or 90 degrees)
            rotation = random.choice([0, 1])

            _draw_diagonal_tile(ctx, x, y, tile_size_px, rotation, color_1, color_2)


def _draw_diagonal_tile(ctx, x, y, size, rotation, color_1_val, color_2_val):
    """
    Draw a single diagonal-split tile.

    Args:
        ctx: Cairo context
        x, y, size: Tile boundaries
        rotation: 0 or 1
        color_1_val, color_2_val: Greyscale values (0.0-1.0) for the two fills
    """
    ctx.save()

    # Path for triangle 1
    ctx.move_to(x, y)
    ctx.line_to(x + size, y)
    if rotation == 0:
        ctx.line_to(x, y + size)
    else:
        ctx.line_to(x + size, y + size)
    ctx.close_path()

    ctx.set_source_rgb(color_1_val, color_1_val, color_1_val)
    ctx.fill()

    # Path for triangle 2
    ctx.move_to(x, y + size)
    ctx.line_to(x + size, y + size)
    if rotation == 0:
        ctx.line_to(x + size, y)
    else:
        ctx.line_to(x, y)
    ctx.close_path()

    ctx.set_source_rgb(color_2_val, color_2_val, color_2_val)
    ctx.fill()

    ctx.restore()


# --- Hexagonal Truchet ---


def draw_hexagonal_truchet_tiles(
    ctx, x_start, x_end, y_start, y_end, tile_size_px, line_width, rotation_seed=None
):
    """
    Draw a Truchet pattern on a hexagonal grid.
    'tile_size_px' is the side length 's' of the hexagon.

    Args:
        ctx: Cairo context
        x_start...y_end: Boundaries
        tile_size_px: Side length 's' of the hexagon
        line_width: Width of the connecting lines
        rotation_seed: Integer seed
    """
    if rotation_seed is not None:
        random.seed(rotation_seed)

    ctx.save()
    ctx.set_source_rgb(0, 0, 0)
    ctx.set_line_width(line_width)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)

    width = x_end - x_start
    height = y_end - y_start

    # 'tile_size_px' is the side length (s)
    s = tile_size_px

    # Calculate horizontal and vertical distances between hex centers
    v_dist = sqrt(3) * s
    h_dist = 1.5 * s

    # Calculate number of rows and columns needed to fill the space
    num_rows = int(height / v_dist) + 2
    num_cols = int(width / h_dist) + 2

    # Set clipping region
    ctx.rectangle(x_start, y_start, width, height)
    ctx.clip()

    # Draw columns of hexagons
    for col in range(num_cols):
        x_c = x_start + (col * h_dist)

        for row in range(num_rows):
            # Calculate base y_center for the row
            y_c = y_start + (row * v_dist)

            # Stagger every other column
            if col % 2:
                y_c += v_dist / 2

            # Randomly choose rotation (0 or 1)
            rotation = random.choice([0, 1])
            _draw_hexagonal_tile(ctx, x_c, y_c, s, rotation)

    ctx.restore()


def _draw_hexagonal_tile(ctx, x_c, y_c, s, rotation):
    """
    Draw a single hexagonal tile with 3 spokes connecting
    alternating side midpoints.

    Args:
        ctx: Cairo context
        x_c, y_c: Center of the hexagon
        s: Side length
        rotation: 0 or 1 (alternating patterns)
    """
    ctx.save()
    ctx.translate(x_c, y_c)

    hex_height_half = (sqrt(3) * s) / 2
    side_mid_x = s * 0.75
    side_mid_y_half = hex_height_half / 2

    if rotation == 0:
        # Variant 1: Top, Bottom-Right, Bottom-Left
        # Spoke 1 (Top)
        ctx.move_to(0, 0)
        ctx.line_to(0, -hex_height_half)
        ctx.stroke()

        # Spoke 2 (Bottom-Right)
        ctx.move_to(0, 0)
        ctx.line_to(side_mid_x, side_mid_y_half)
        ctx.stroke()

        # Spoke 3 (Bottom-Left)
        ctx.move_to(0, 0)
        ctx.line_to(-side_mid_x, side_mid_y_half)
        ctx.stroke()
    else:
        # Variant 2: Bottom, Top-Right, Top-Left
        # Spoke 1 (Bottom)
        ctx.move_to(0, 0)
        ctx.line_to(0, hex_height_half)
        ctx.stroke()

        # Spoke 2 (Top-Right)
        ctx.move_to(0, 0)
        ctx.line_to(side_mid_x, -side_mid_y_half)
        ctx.stroke()

        # Spoke 3 (Top-Left)
        ctx.move_to(0, 0)
        ctx.line_to(-side_mid_x, -side_mid_y_half)
        ctx.stroke()

    ctx.restore()


def draw_10_print_tiles(
    ctx, x_start, x_end, y_start, y_end, tile_size_px, line_width, rotation_seed=None
):
    """
    Draw "10 PRINT" pattern (random forward/back slashes).

    Args:
        ctx: Cairo context
        x_start...y_end: Boundaries
        tile_size_px: Size of each tile
        line_width: Width of the slashes
        rotation_seed: Integer seed for reproducible patterns
    """
    if rotation_seed is not None:
        random.seed(rotation_seed)

    ctx.save()
    ctx.set_source_rgb(0, 0, 0)
    ctx.set_line_width(line_width)

    # Calculate number of tiles
    num_cols = int((x_end - x_start) / tile_size_px) + 1
    num_rows = int((y_end - y_start) / tile_size_px) + 1

    # Draw each tile
    for row in range(num_rows):
        for col in range(num_cols):
            x = x_start + (col * tile_size_px)
            y = y_start + (row * tile_size_px)

            # Randomly choose slash direction (0 or 1)
            direction = random.choice([0, 1])

            _draw_10_print_tile(ctx, x, y, tile_size_px, direction)

    ctx.restore()


def _draw_10_print_tile(ctx, x, y, size, direction):
    """
    Draw a single forward or back slash in a tile.

    Args:
        ctx: Cairo context
        x, y, size: Tile boundaries
        direction: 0 for backslash (\\), 1 for forward slash (/)
    """
    if direction == 0:
        # Backslash (\)
        ctx.move_to(x, y)
        ctx.line_to(x + size, y + size)
    else:
        # Forward slash (/)
        ctx.move_to(x, y + size)
        ctx.line_to(x + size, y)

    ctx.stroke()


def draw_lsystem_pattern(ctx, lsystem_config, x_start, y_start, width, height, line_width):
    """
    High-level "turtle" that draws a generated L-System string.

    Args:
        ctx: Cairo context
        lsystem_config (dict): Contains all rules for the L-System
            {
                "axiom": str,
                "rules": dict,
                "iterations": int,
                "angle": int (degrees),
                "step_length": int (pixels),
                "start_angle": int (degrees)
            }
        x_start, y_start: Starting coordinates for the turtle
        width, height: Bounding box of the content area
        line_width: Width of the lines to draw
    """

    # 1. Generate the command string
    command_string = generate_lsystem_string(
        lsystem_config["axiom"], lsystem_config["rules"], lsystem_config["iterations"]
    )

    # 2. Setup the turtle
    ctx.save()
    ctx.set_source_rgb(0, 0, 0)
    ctx.set_line_width(line_width)
    ctx.set_line_cap(cairo.LINE_CAP_SQUARE)

    # Move to the starting position and set initial angle
    ctx.move_to(x_start, y_start)
    ctx.save()  # Save this initial state

    # Set the starting angle
    # We must translate to origin (0,0) to rotate the *world*,
    # then translate back.
    ctx.translate(x_start, y_start)
    ctx.rotate(lsystem_config.get("start_angle", 0) * pi / 180)
    ctx.translate(-x_start, -y_start)

    step_length = lsystem_config["step_length"]
    angle_rad = lsystem_config["angle"] * pi / 180

    # 3. Read the command string and draw
    for char in command_string:
        if char == "F" or char == "G":
            # "Move forward and draw"
            # Get current point
            x, y = ctx.get_current_point()
            # We must use ctx.rel_line_to to draw relative to
            # our *current rotated angle*.
            ctx.rel_line_to(step_length, 0)

        elif char == "f":
            # "Move forward without drawing"
            x, y = ctx.get_current_point()
            ctx.rel_move_to(step_length, 0)

        elif char == "+":
            # "Turn left" (positive rotation)
            x, y = ctx.get_current_point()
            ctx.translate(x, y)
            ctx.rotate(angle_rad)
            ctx.translate(-x, -y)

        elif char == "-":
            # "Turn right" (negative rotation)
            x, y = ctx.get_current_point()
            ctx.translate(x, y)
            ctx.rotate(-angle_rad)
            ctx.translate(-x, -y)

        elif char == "[":
            # "Push state"
            ctx.save()

        elif char == "]":
            # "Pop state"
            ctx.restore()

    # Apply the drawing
    ctx.stroke()
    ctx.restore()


def _smooth_heightmap(heightmap, passes=1):
    """Apply simple 3x3 Gaussian smoothing to heightmap"""
    for _ in range(passes):
        smoothed = []
        for y in range(len(heightmap)):
            row = []
            for x in range(len(heightmap[0])):
                # 3x3 kernel with center weight
                total = 0
                weight = 0
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < len(heightmap) and 0 <= nx < len(heightmap[0]):
                            kernel_weight = 1 if (dx == 0 and dy == 0) else 0.5
                            total += heightmap[ny][nx] * kernel_weight
                            weight += kernel_weight
                row.append(total / weight)
            smoothed.append(row)
        heightmap = smoothed
    return heightmap


def draw_contour_lines(
    ctx,
    x_start,
    x_end,
    y_start,
    y_end,
    contour_interval=0.1,
    line_width=1.0,
    noise_scale=0.02,
    octaves=4,
    seed=None,
    style="smooth",
):
    """
    Draw contour lines based on noise heightmap (like topographic maps).

    Args:
        ctx: Cairo context
        x_start, x_end, y_start, y_end: Boundaries
        contour_interval: Elevation difference between lines (0.0-1.0)
        line_width: Width of contour lines
        noise_scale: Frequency of noise (smaller = larger features)
        octaves: Number of noise octaves (more = more detail)
        seed: Random seed for reproducibility
        style: 'smooth' (fractal noise), 'turbulent' (marble-like), 'simple' (basic)
    """
    import random

    if seed is not None:
        actual_seed = seed
    else:
        actual_seed = random.randint(0, 1000000)

    ctx.save()
    ctx.set_source_rgb(0, 0, 0)
    ctx.set_line_width(line_width)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)

    width = x_end - x_start
    height = y_end - y_start

    # Choose noise function
    def noise_func_turbulent(x, y):
        return turbulence_2d(x, y, octaves, actual_seed)

    def noise_func_simple(x, y):
        return simple_noise_2d(x, y, actual_seed)

    def noise_func_smooth(x, y):
        return fractal_noise_2d(x, y, octaves, 0.5, 2.0, actual_seed)

    if style == "turbulent":
        noise_func = noise_func_turbulent
    elif style == "simple":
        noise_func = noise_func_simple
    else:  # 'smooth'
        noise_func = noise_func_smooth

    # Generate heightmap (sample-based approach)
    # Using a coarser grid for performance, then interpolating
    sample_step = 2  # Sample every N pixels
    samples_x = int(width / sample_step) + 2
    samples_y = int(height / sample_step) + 2

    # Build heightmap
    heightmap = []
    for sy in range(samples_y):
        row = []
        for sx in range(samples_x):
            # Convert pixel coordinates to noise space
            px = x_start + (sx * sample_step)
            py = y_start + (sy * sample_step)
            noise_x = px * noise_scale
            noise_y = py * noise_scale

            height = noise_func(noise_x, noise_y)
            row.append(height)
        heightmap.append(row)

    heightmap = _smooth_heightmap(heightmap, passes=2)

    # Draw contours using marching squares approach
    # For each contour level
    num_contours = int(1.0 / contour_interval)

    for level_idx in range(num_contours):
        threshold = level_idx * contour_interval

        # Check each cell in the grid
        for sy in range(samples_y - 1):
            for sx in range(samples_x - 1):
                # Get the four corners of this cell
                tl = heightmap[sy][sx]  # top-left
                tr = heightmap[sy][sx + 1]  # top-right
                bl = heightmap[sy + 1][sx]  # bottom-left
                br = heightmap[sy + 1][sx + 1]  # bottom-right

                # Convert to pixel coordinates
                px = x_start + (sx * sample_step)
                py = y_start + (sy * sample_step)

                # Draw line segments where contour crosses edges
                _draw_contour_cell(ctx, px, py, sample_step, sample_step, tl, tr, bl, br, threshold)

    ctx.restore()


def _draw_contour_cell(ctx, x, y, width, height, tl, tr, bl, br, threshold):
    """
    Draw contour line segments in a single cell using marching squares.

    Args:
        ctx: Cairo context
        x, y: Top-left corner of cell
        width, height: Cell dimensions
        tl, tr, bl, br: Height values at corners (top-left, top-right, bottom-left, bottom-right)
        threshold: Contour level threshold
    """
    # Determine which corners are above/below threshold
    # Build a 4-bit case index
    case = 0
    if tl >= threshold:
        case |= 8
    if tr >= threshold:
        case |= 4
    if br >= threshold:
        case |= 2
    if bl >= threshold:
        case |= 1

    # Linear interpolation to find exact crossing points
    def lerp_edge(v1, v2, t, p1, p2):
        """Interpolate position where threshold crosses between v1 and v2"""
        if abs(v2 - v1) < 0.0001:
            return 0.5  # Avoid division by zero
        return (t - v1) / (v2 - v1)

    # Edge midpoints (we'll adjust these with interpolation)
    top_t = lerp_edge(tl, tr, threshold, 0, 1)
    right_t = lerp_edge(tr, br, threshold, 0, 1)
    bottom_t = lerp_edge(bl, br, threshold, 0, 1)
    left_t = lerp_edge(tl, bl, threshold, 0, 1)

    # Calculate actual crossing points
    top = (x + width * top_t, y)
    right = (x + width, y + height * right_t)
    bottom = (x + width * bottom_t, y + height)
    left = (x, y + height * left_t)

    # Draw line segments based on marching squares case
    # There are 16 cases (2^4), but many are symmetric
    lines = []

    if case == 1 or case == 14:
        lines = [(left, bottom)]
    elif case == 2 or case == 13:
        lines = [(bottom, right)]
    elif case == 3 or case == 12:
        lines = [(left, right)]
    elif case == 4 or case == 11:
        lines = [(top, right)]
    elif case == 5:
        lines = [(left, top), (bottom, right)]
    elif case == 6 or case == 9:
        lines = [(top, bottom)]
    elif case == 7 or case == 8:
        lines = [(left, top)]
    elif case == 10:
        lines = [(top, left), (right, bottom)]
    # case 0 and 15: no lines (all above or all below)

    # Draw the line segments
    for (x1, y1), (x2, y2) in lines:
        ctx.move_to(x1, y1)
        ctx.line_to(x2, y2)
        ctx.stroke()


def draw_noise_field(
    ctx,
    x_start,
    x_end,
    y_start,
    y_end,
    noise_scale=0.02,
    octaves=4,
    seed=None,
    style="smooth",
    greyscale_levels=16,
):
    """
    Draw a noise field as a greyscale pattern (for testing/backgrounds).

    Args:
        ctx: Cairo context
        x_start, x_end, y_start, y_end: Boundaries
        noise_scale: Frequency of noise
        octaves: Number of noise octaves
        seed: Random seed
        style: 'smooth', 'turbulent', or 'simple'
        greyscale_levels: Number of grey levels (1-16 for e-ink)
    """
    import random

    from .devices import snap_to_eink_greyscale

    if seed is not None:
        actual_seed = seed
    else:
        actual_seed = random.randint(0, 1000000)

    # Choose noise function
    def noise_func_turbulent(x, y):
        return turbulence_2d(x, y, octaves, actual_seed)

    def noise_func_simple(x, y):
        return simple_noise_2d(x, y, actual_seed)

    def noise_func_smooth(x, y):
        return fractal_noise_2d(x, y, octaves, 0.5, 2.0, actual_seed)

    if style == "turbulent":
        noise_func = noise_func_turbulent
    elif style == "simple":
        noise_func = noise_func_simple
    else:  # 'smooth'
        noise_func = noise_func_smooth

    ctx.save()

    # Render pixel by pixel (or with a step for performance)
    step = 2  # Render every N pixels

    for py in range(int(y_start), int(y_end), step):
        for px in range(int(x_start), int(x_end), step):
            noise_x = px * noise_scale
            noise_y = py * noise_scale

            noise_val = noise_func(noise_x, noise_y)

            # Convert to e-ink greyscale
            grey_level = int(noise_val * (greyscale_levels - 1))
            grey = snap_to_eink_greyscale(grey_level)

            ctx.set_source_rgb(grey, grey, grey)
            ctx.rectangle(px, py, step, step)
            ctx.fill()

    ctx.restore()


# In cover_drawing.py, add at the end:


def draw_decorative_border(ctx, x_start, x_end, y_start, y_end, border_width=2, style="simple"):
    """
    Draw decorative borders around the pattern area.

    Args:
        ctx: Cairo context
        x_start, x_end, y_start, y_end: Border boundaries
        border_width: Width of border lines
        style: 'simple', 'double', 'ornate', 'geometric'
    """
    ctx.save()
    ctx.set_source_rgb(0, 0, 0)

    if style == "double":
        # Inner border
        ctx.set_line_width(border_width * 0.6)
        ctx.rectangle(x_start + 5, y_start + 5, x_end - x_start - 10, y_end - y_start - 10)
        ctx.stroke()

        # Outer border
        ctx.set_line_width(border_width)
        ctx.rectangle(x_start, y_start, x_end - x_start, y_end - y_start)
        ctx.stroke()

    elif style == "ornate":
        # Main border
        ctx.set_line_width(border_width)
        ctx.rectangle(x_start, y_start, x_end - x_start, y_end - y_start)
        ctx.stroke()

        # Corner ornaments
        corner_size = 15
        _draw_border_corner_ornament(ctx, x_start, y_start, corner_size, "top-left")
        _draw_border_corner_ornament(ctx, x_end, y_start, corner_size, "top-right")
        _draw_border_corner_ornament(ctx, x_start, y_end, corner_size, "bottom-left")
        _draw_border_corner_ornament(ctx, x_end, y_end, corner_size, "bottom-right")

    elif style == "geometric":
        # Border with small geometric accents
        ctx.set_line_width(border_width)
        ctx.rectangle(x_start, y_start, x_end - x_start, y_end - y_start)
        ctx.stroke()

        # Add small squares at intervals
        spacing = 50
        square_size = 3
        for x in range(int(x_start) + spacing, int(x_end), spacing):
            # Top edge
            ctx.rectangle(x - square_size / 2, y_start - square_size / 2, square_size, square_size)
            ctx.fill()
            # Bottom edge
            ctx.rectangle(x - square_size / 2, y_end - square_size / 2, square_size, square_size)
            ctx.fill()

        for y in range(int(y_start) + spacing, int(y_end), spacing):
            # Left edge
            ctx.rectangle(x_start - square_size / 2, y - square_size / 2, square_size, square_size)
            ctx.fill()
            # Right edge
            ctx.rectangle(x_end - square_size / 2, y - square_size / 2, square_size, square_size)
            ctx.fill()

    else:  # 'simple'
        ctx.set_line_width(border_width)
        ctx.rectangle(x_start, y_start, x_end - x_start, y_end - y_start)
        ctx.stroke()

    ctx.restore()


def _draw_border_corner_ornament(ctx, x, y, size, position):
    """Draw decorative corner flourish for borders"""
    ctx.save()
    ctx.set_line_width(1.0)

    if position == "top-left":
        # Small curve in corner
        ctx.arc(x + size, y + size, size, pi, 3 * pi / 2)
        ctx.stroke()
        # Inner detail
        ctx.arc(x + size / 2, y + size / 2, size / 2, pi, 3 * pi / 2)
        ctx.stroke()

    elif position == "top-right":
        ctx.arc(x - size, y + size, size, 3 * pi / 2, 2 * pi)
        ctx.stroke()
        ctx.arc(x - size / 2, y + size / 2, size / 2, 3 * pi / 2, 2 * pi)
        ctx.stroke()

    elif position == "bottom-left":
        ctx.arc(x + size, y - size, size, pi / 2, pi)
        ctx.stroke()
        ctx.arc(x + size / 2, y - size / 2, size / 2, pi / 2, pi)
        ctx.stroke()

    elif position == "bottom-right":
        ctx.arc(x - size, y - size, size, 0, pi / 2)
        ctx.stroke()
        ctx.arc(x - size / 2, y - size / 2, size / 2, 0, pi / 2)
        ctx.stroke()

    ctx.restore()
