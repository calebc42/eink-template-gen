"""
Reusable decorative elements for title pages
"""

from math import pi

import cairo

from .devices import snap_to_eink_greyscale


def draw_title_element(
    ctx,
    page_width,
    page_height,
    config,
    content_x_start=0,
    content_y_start=0,
    content_width=None,
    content_height=None,
):
    """
    Draw title frame and text from configuration, with multiple
    positioning modes.

    Args:
        ctx: Cairo context
        page_width, page_height: Full page dimensions
        config: Dict with title configuration
        content_x_start, content_y_start: Top-left corner of the
                                          content area (for JSON layout)
        content_width, content_height: Dimensions of the
                                       content area (for JSON layout)
    """
    # Use content area if provided, else fall back to full page
    if content_width is None:
        content_width = page_width
    if content_height is None:
        content_height = page_height

    if "region_rect" in config:
        # --- 1. JSON Ratio/Cell Mode ---
        # Position is defined by the region_rect
        x_p, y_p, w_p, h_p = config["region_rect"]

        frame_width = w_p * content_width
        frame_height = h_p * content_height

        # Calculate center based on region's top-left corner and its *own* dimensions
        x_center = content_x_start + (x_p * content_width) + (frame_width / 2)
        y_center = content_y_start + (y_p * content_height) + (frame_height / 2)

    else:
        # --- 2. CLI Alignment/Pixel Mode ---

        # Get frame dimensions (default relative to page)
        frame_width = config.get("frame_width", page_width * 0.6)
        frame_height = config.get("frame_height", page_height * 0.2)

        # --- Horizontal Alignment ---
        # Priority: 1. explicit pixels, 2. h_align, 3. default
        x_center = config.get("x_center")
        if x_center is None:
            h_align = config.get("h_align", "center")
            if h_align == "left":
                x_center = page_width / 3
            elif h_align == "right":
                x_center = page_width * (2 / 3)
            else:  # 'center'
                x_center = page_width / 2

        # --- Vertical Alignment ---
        # Priority: 1. explicit pixels, 2. v_align, 3. default
        y_center = config.get("y_center")
        if y_center is None:
            v_align = config.get("v_align", "top")
            if v_align == "center":
                y_center = page_height / 2
            elif v_align == "bottom":
                y_center = page_height * (2 / 3)
            else:  # 'top'
                y_center = page_height / 3

    # --- Draw Frame and Text (Same as before) ---

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
            fill_grey=config.get("fill_grey", 15),
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


def draw_title_frame(
    ctx,
    x_center,
    y_center,
    width,
    height,
    shape="rectangle",
    border_style="solid",
    border_width=2.0,
    border_grey=0,
    fill_grey=None,
    corner_radius=10,
):
    """
    Draw a decorative frame for title text

    Args:
        ctx: Cairo context
        x_center: Center X coordinate
        y_center: Center Y coordinate
        width: Frame width in pixels
        height: Frame height in pixels
        shape: 'rectangle', 'rounded-rectangle', 'ellipse', 'circle'
        border_style: 'solid', 'dashed', 'dotted', 'double', 'ornate'
        border_width: Width of border in pixels
        border_grey: Border greyscale (0-15 or 0.0-1.0)
        fill_grey: Fill greyscale (None = transparent, 0-15 or 0.0-1.0)
        corner_radius: Corner radius for rounded rectangles (pixels)
    """
    ctx.save()

    # Calculate top-left corner
    x = x_center - width / 2
    y = y_center - height / 2

    # Draw fill if specified
    if fill_grey is not None:
        fill_color = snap_to_eink_greyscale(fill_grey)
        ctx.set_source_rgb(fill_color, fill_color, fill_color)
        _draw_shape_path(ctx, x, y, width, height, shape, corner_radius)
        ctx.fill()

    # Draw border
    border_color = snap_to_eink_greyscale(border_grey)
    ctx.set_source_rgb(border_color, border_color, border_color)

    if border_style == "solid":
        _draw_solid_border(ctx, x, y, width, height, shape, border_width, corner_radius)
    elif border_style == "dashed":
        _draw_dashed_border(ctx, x, y, width, height, shape, border_width, corner_radius)
    elif border_style == "dotted":
        _draw_dotted_border(ctx, x, y, width, height, shape, border_width, corner_radius)
    elif border_style == "double":
        _draw_double_border(ctx, x, y, width, height, shape, border_width, corner_radius)
    elif border_style == "ornate":
        _draw_ornate_border(ctx, x, y, width, height, shape, border_width, corner_radius)
    else:
        # Fallback to solid
        _draw_solid_border(ctx, x, y, width, height, shape, border_width, corner_radius)

    ctx.restore()


def draw_title_text(
    ctx,
    text,
    x_center,
    y_center,
    font_family="Serif",
    font_size=48,
    font_weight="bold",
    font_slant="normal",
    text_grey=0,
    letter_spacing=0,
):
    """
    Draw title text with customizable styling

    Args:
        ctx: Cairo context
        text: Text to draw
        x_center: Center X coordinate for text
        y_center: Center Y coordinate for text
        font_family: 'Serif', 'Sans', 'Monospace', or any system font
        font_size: Font size in points
        font_weight: 'normal' or 'bold'
        font_slant: 'normal', 'italic', 'oblique'
        text_grey: Text greyscale (0-15 or 0.0-1.0)
        letter_spacing: Additional spacing between letters (pixels)
    """
    ctx.save()

    # Set font
    slant_map = {
        "normal": cairo.FONT_SLANT_NORMAL,
        "italic": cairo.FONT_SLANT_ITALIC,
        "oblique": cairo.FONT_SLANT_OBLIQUE,
    }

    weight_map = {"normal": cairo.FONT_WEIGHT_NORMAL, "bold": cairo.FONT_WEIGHT_BOLD}

    ctx.select_font_face(
        font_family,
        slant_map.get(font_slant, cairo.FONT_SLANT_NORMAL),
        weight_map.get(font_weight, cairo.FONT_WEIGHT_NORMAL),
    )
    ctx.set_font_size(font_size)

    # Set color
    text_color = snap_to_eink_greyscale(text_grey)
    ctx.set_source_rgb(text_color, text_color, text_color)

    # Handle letter spacing
    if letter_spacing > 0:
        # Draw each character individually with spacing
        x_offset = 0
        for char in text:
            extents = ctx.text_extents(char)
            x_offset += extents.width + letter_spacing

        # Calculate starting position to center the text
        total_width = x_offset - letter_spacing  # Remove last spacing
        x_pos = x_center - total_width / 2

        for char in text:
            extents = ctx.text_extents(char)
            ctx.move_to(x_pos, y_center + extents.height / 2)
            ctx.show_text(char)
            x_pos += extents.width + letter_spacing
    else:
        # Normal text rendering
        extents = ctx.text_extents(text)
        x_pos = x_center - extents.width / 2
        y_pos = y_center + extents.height / 2

        ctx.move_to(x_pos, y_pos)
        ctx.show_text(text)

    ctx.restore()


# --- Helper Functions for Shape Drawing ---


def _draw_shape_path(ctx, x, y, width, height, shape, corner_radius):
    """Create a path for the given shape (doesn't stroke/fill)"""
    if shape == "rectangle":
        ctx.rectangle(x, y, width, height)

    elif shape == "rounded-rectangle":
        _rounded_rectangle_path(ctx, x, y, width, height, corner_radius)

    elif shape == "ellipse":
        ctx.save()
        ctx.translate(x + width / 2, y + height / 2)
        ctx.scale(width / 2, height / 2)
        ctx.arc(0, 0, 1, 0, 2 * pi)
        ctx.restore()

    elif shape == "circle":
        radius = min(width, height) / 2
        ctx.arc(x + width / 2, y + height / 2, radius, 0, 2 * pi)


def _rounded_rectangle_path(ctx, x, y, width, height, radius):
    """Create a rounded rectangle path"""
    # Clamp radius to half the smallest dimension
    radius = min(radius, width / 2, height / 2)

    # Top-right corner
    ctx.arc(x + width - radius, y + radius, radius, -pi / 2, 0)
    # Bottom-right corner
    ctx.arc(x + width - radius, y + height - radius, radius, 0, pi / 2)
    # Bottom-left corner
    ctx.arc(x + radius, y + height - radius, radius, pi / 2, pi)
    # Top-left corner
    ctx.arc(x + radius, y + radius, radius, pi, 3 * pi / 2)
    ctx.close_path()


def _draw_solid_border(ctx, x, y, width, height, shape, border_width, corner_radius):
    """Draw a solid border"""
    ctx.set_line_width(border_width)
    _draw_shape_path(ctx, x, y, width, height, shape, corner_radius)
    ctx.stroke()


def _draw_dashed_border(ctx, x, y, width, height, shape, border_width, corner_radius):
    """Draw a dashed border"""
    ctx.set_line_width(border_width)
    ctx.set_dash([10, 5])
    _draw_shape_path(ctx, x, y, width, height, shape, corner_radius)
    ctx.stroke()


def _draw_dotted_border(ctx, x, y, width, height, shape, border_width, corner_radius):
    """Draw a dotted border"""
    ctx.set_line_width(border_width)
    ctx.set_dash([2, 4])
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    _draw_shape_path(ctx, x, y, width, height, shape, corner_radius)
    ctx.stroke()


def _draw_double_border(ctx, x, y, width, height, shape, border_width, corner_radius):
    """Draw a double border"""
    gap = border_width * 2

    # Outer border
    ctx.set_line_width(border_width)
    _draw_shape_path(ctx, x, y, width, height, shape, corner_radius)
    ctx.stroke()

    # Inner border
    inner_x = x + gap
    inner_y = y + gap
    inner_width = width - 2 * gap
    inner_height = height - 2 * gap

    if inner_width > 0 and inner_height > 0:
        _draw_shape_path(ctx, inner_x, inner_y, inner_width, inner_height, shape, corner_radius)
        ctx.stroke()


def _draw_ornate_border(ctx, x, y, width, height, shape, border_width, corner_radius):
    """Draw an ornate border with decorative corners"""
    # Draw main border
    ctx.set_line_width(border_width)
    _draw_shape_path(ctx, x, y, width, height, shape, corner_radius)
    ctx.stroke()

    # Add corner decorations (small flourishes)
    if shape in ["rectangle", "rounded-rectangle"]:
        flourish_size = min(width, height) * 0.05
        _draw_corner_flourish(ctx, x, y, flourish_size, border_width, "top-left")
        _draw_corner_flourish(ctx, x + width, y, flourish_size, border_width, "top-right")
        _draw_corner_flourish(ctx, x, y + height, flourish_size, border_width, "bottom-left")
        _draw_corner_flourish(
            ctx, x + width, y + height, flourish_size, border_width, "bottom-right"
        )


def _draw_corner_flourish(ctx, x, y, size, line_width, position):
    """Draw a small decorative flourish at a corner"""
    ctx.set_line_width(line_width * 0.75)

    if position == "top-left":
        ctx.move_to(x, y + size)
        ctx.curve_to(x, y, x, y, x + size, y)
    elif position == "top-right":
        ctx.move_to(x - size, y)
        ctx.curve_to(x, y, x, y, x, y + size)
    elif position == "bottom-left":
        ctx.move_to(x, y - size)
        ctx.curve_to(x, y, x, y, x + size, y)
    elif position == "bottom-right":
        ctx.move_to(x - size, y)
        ctx.curve_to(x, y, x, y, x, y - size)

    ctx.stroke()
