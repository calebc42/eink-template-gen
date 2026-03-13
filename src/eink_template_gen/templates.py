"""
Template creation functions and the new Template Factory
"""

from dataclasses import dataclass
from math import cos, radians, sqrt, tan
from typing import Tuple

import cairo

from . import drawing
from .cover_elements import draw_title_element
from .devices import snap_to_eink_greyscale
from .separators import draw_page_separators, draw_separator
from .utils import (
    PageMargins,
    calculate_page_margins,
    calculate_spacing,
    create_canvas,
    parse_spacing,
)

# --- Dispatcher Helper for Dotgrid ---


def _draw_dotgrid_dispatcher(
    ctx,
    x_start,
    x_end,
    y_start,
    y_end,
    spacing_px,
    dot_radius,
    skip_first_row=False,
    skip_last_row=False,
    major_every=None,
    crosshair_size=4,
    **kwargs,
):
    """
    Dispatches to the correct dotgrid draw function based on whether
    major_every is specified.
    """
    if major_every:
        drawing.draw_dot_grid_with_crosshairs(
            ctx,
            x_start,
            x_end,
            y_start,
            y_end,
            spacing_px,
            dot_radius,
            skip_first_row=skip_first_row,
            skip_last_row=skip_last_row,
            major_every=major_every,
            crosshair_size=crosshair_size,
        )
    else:
        drawing.draw_dot_grid(
            ctx,
            x_start,
            x_end,
            y_start,
            y_end,
            spacing_px,
            dot_radius,
            skip_first_row=skip_first_row,
            skip_last_row=skip_last_row,
        )


# --- Data-Driven Template Registry (ENHANCED) ---

TEMPLATE_REGISTRY = {
    "lined": {
        "draw_func": drawing.draw_lined_section,
        "horizontal_align_unit": "none",
        "vertical_align_unit": "default",
        "skip_param_name": "skip",  # Uses skip_first, skip_last
        "decorations": ["line_numbers"],
        "specific_args_map": {
            "line_width_px": "line_width",
            "major_every": "major_every",
            "major_width_add_px": "major_width_add_px",
        },
    },
    "dotgrid": {
        "draw_func": _draw_dotgrid_dispatcher,
        "horizontal_align_unit": "default",
        "vertical_align_unit": "default",
        "skip_param_name": "skip_row",  # Uses skip_first_row, skip_last_row
        "decorations": [],  # No labels for dotgrid
        "specific_args_map": {
            "dot_radius_px": "dot_radius",
            "major_every": "major_every",
            "crosshair_size": "crosshair_size",
        },
    },
    "grid": {
        "draw_func": drawing.draw_grid,
        "horizontal_align_unit": "default",
        "vertical_align_unit": "default",
        "skip_param_name": "skip_row",
        "decorations": ["cell_labels", "axis_labels"],
        "specific_args_map": {
            "line_width_px": "line_width",
            "major_every": "major_every",
            "major_width_add_px": "major_width_add_px",
            "crosshair_size": "crosshair_size",
        },
    },
    "manuscript": {
        "draw_func": drawing.draw_manuscript_lines,
        "horizontal_align_unit": "none",
        "vertical_align_unit": "default",
        "skip_param_name": "skip",
        "decorations": [],
        "specific_args_map": {
            "line_width_px": "line_width",
            "midline_style": "midline_style",
            "ascender_opacity": "ascender_opacity",
        },
    },
    "french_ruled": {
        "draw_func": drawing.draw_french_ruled,
        "horizontal_align_unit": "french_ruled",
        "vertical_align_unit": "default",
        "skip_param_name": "skip",
        "decorations": [],
        "specific_args_map": {
            "line_width_px": "line_width",
            "margin_line_offset_px": "margin_line_offset_px",
            "show_vertical_lines": "show_vertical_lines",
        },
    },
    "music_staff": {
        "draw_func": drawing.draw_music_staff,
        "horizontal_align_unit": "none",
        "vertical_align_unit": "music_staff",
        "skip_param_name": None,  # Doesn't support skipping
        "decorations": [],
        "specific_args_map": {
            "line_width_px": "line_width",
            "staff_gap_mm": "staff_gap_mm",
        },
    },
    "isometric": {
        "draw_func": drawing.draw_isometric_grid,
        "horizontal_align_unit": "isometric",
        "vertical_align_unit": "isometric",
        "skip_param_name": None,
        "decorations": [],
        "specific_args_map": {
            "line_width_px": "line_width",
            "major_every": "major_every",
            "major_width_add_px": "major_width_add_px",
        },
    },
    "hexgrid": {
        "draw_func": drawing.draw_hex_grid,
        "horizontal_align_unit": "hexgrid",
        "vertical_align_unit": "hexgrid",
        "skip_param_name": None,
        "decorations": [],
        "specific_args_map": {
            "line_width_px": "line_width",
            "major_every": "major_every",
            "major_width_add_px": "major_width_add_px",
        },
    },
    "hybrid_lined_dotgrid": {
        "draw_func": "hybrid_special_case",  # Handled separately
    },
}

# --- NEW AlignmentUnits CLASS ---


@dataclass
class AlignmentUnits:
    """Alignment unit configuration for margin calculations"""

    vertical: float
    horizontal: float

    @classmethod
    def from_template_config(
        cls, template_type: str, spacing_px: float, dpi: int, template_kwargs: dict = None
    ) -> "AlignmentUnits":
        """
        Calculate alignment units based on template type.

        This consolidates the alignment logic that was scattered across
        multiple files.
        """
        template_kwargs = template_kwargs or {}
        mm2px = dpi / 25.4

        # Get config from registry
        config = TEMPLATE_REGISTRY.get(template_type, {})
        v_setting = config.get("vertical_align_unit", "default")
        h_setting = config.get("horizontal_align_unit", "default")

        # Calculate vertical alignment
        v_align = spacing_px  # default
        if v_setting == "none":
            v_align = 1
        elif v_setting == "music_staff":
            staff_gap_mm = template_kwargs.get("staff_gap_mm", 10)
            staff_gap_px = round(staff_gap_mm * mm2px)
            v_align = (spacing_px * 4) + staff_gap_px
        elif v_setting == "isometric":
            v_align = spacing_px * tan(radians(60))
        elif v_setting == "hexgrid":
            v_align = sqrt(3) * spacing_px

        # Calculate horizontal alignment
        h_align = spacing_px  # default
        if h_setting == "none":
            h_align = 1
        elif h_setting == "french_ruled":
            h_align = spacing_px * 4
        elif h_setting == "isometric":
            h_align = spacing_px / cos(radians(30))
        elif h_setting == "hexgrid":
            h_align = 1.5 * spacing_px

        return cls(vertical=v_align, horizontal=h_align)


# --- NEW TEMPLATE RENDERER CLASS ---


class TemplateRenderer:
    """Unified template rendering with shared logic"""

    def __init__(self, ctx: cairo.Context, dpi: int):
        self.ctx = ctx
        self.dpi = dpi

    def render(
        self,
        template_type: str,
        bounds: Tuple[int, int, int, int],  # x_start, x_end, y_start, y_end
        spacing_px: float,
        spacing_mm: float,
        template_kwargs: dict,
        skip_first: bool = False,
        skip_last: bool = False,
    ):
        """
        Render any template type within given bounds.

        This consolidates the drawing logic from _draw_cell_template
        and create_template_surface.
        """
        x_start, x_end, y_start, y_end = bounds

        # Get template config
        config = TEMPLATE_REGISTRY.get(template_type)
        if not config:
            if template_type == "blank" or not template_type:
                return  # Do nothing for "blank" templates
            raise ValueError(f"Unknown template type: {template_type}")

        # Build draw kwargs
        draw_kwargs = self._build_draw_kwargs(
            config,
            x_start,
            x_end,
            y_start,
            y_end,
            spacing_px,
            spacing_mm,
            template_kwargs,
            skip_first,
            skip_last,
        )

        # Call drawing function
        draw_func = config["draw_func"]
        try:
            draw_func(**draw_kwargs)
        except TypeError as e:
            print("\n--- ERROR ---")
            print(f"Argument mismatch calling draw function for '{template_type}'.")
            print(f"Error: {e}")
            print(f"Attempted to call: {draw_func.__name__}")
            print(f"With arguments: {list(draw_kwargs.keys())}")
            raise

        # Draw decorations (line numbers, labels, etc.)
        self._render_decorations(
            template_type, x_start, x_end, y_start, y_end, spacing_px, template_kwargs
        )

    def _build_draw_kwargs(
        self,
        config,
        x_start,
        x_end,
        y_start,
        y_end,
        spacing_px,
        spacing_mm,
        template_kwargs,
        skip_first,
        skip_last,
    ):
        """Build kwargs for drawing function"""
        kwargs = {
            "ctx": self.ctx,
            "x_start": x_start,
            "x_end": x_end,
            "y_start": y_start,
            "y_end": y_end,
            "spacing_px": spacing_px,
        }

        # Add skip logic based on template type
        skip_param_name = config.get("skip_param_name")
        if skip_param_name == "skip":
            kwargs["skip_first"] = skip_first
            kwargs["skip_last"] = skip_last
        elif skip_param_name == "skip_row":
            kwargs["skip_first_row"] = skip_first
            kwargs["skip_last_row"] = skip_last

        # Map template-specific args
        arg_map = config.get("specific_args_map", {})
        for cli_arg, func_arg in arg_map.items():
            if cli_arg in template_kwargs:
                kwargs[func_arg] = template_kwargs[cli_arg]

        # Special cases
        if template_kwargs.get("no_crosshairs"):
            kwargs["crosshair_size"] = 0

        if config.get("draw_func") == drawing.draw_music_staff:  # Check if it's music_staff
            kwargs["staff_spacing_mm"] = spacing_mm
            kwargs["dpi"] = self.dpi
            kwargs.pop("spacing_px", None)

        return kwargs

    def _render_decorations(
        self, template_type, x_start, x_end, y_start, y_end, spacing_px, template_kwargs
    ):
        """Render line numbers, labels, etc."""
        config = TEMPLATE_REGISTRY.get(template_type, {})
        decorations = config.get("decorations", [])

        if "line_numbers" in decorations and "line_number_config" in template_kwargs:
            drawing.draw_line_numbering(
                self.ctx, y_start, y_end, spacing_px, template_kwargs["line_number_config"]
            )

        if "cell_labels" in decorations and "cell_label_config" in template_kwargs:
            drawing.draw_cell_labeling(
                self.ctx,
                x_start,
                x_end,
                y_start,
                y_end,
                spacing_px,
                template_kwargs["cell_label_config"],
            )

        if "axis_labels" in decorations and "axis_label_config" in template_kwargs:
            drawing.draw_axis_labeling(
                self.ctx,
                x_start,
                x_end,
                y_start,
                y_end,
                spacing_px,
                template_kwargs["axis_label_config"],
            )


# --- GRID LAYOUT CLASS ---


@dataclass
class GridCell:
    """A single cell in a grid layout"""

    row: int
    col: int
    x_start: int
    x_end: int
    y_start: int
    y_end: int

    @property
    def width(self) -> int:
        return self.x_end - self.x_start

    @property
    def height(self) -> int:
        return self.y_end - self.y_start

    @property
    def bounds(self) -> Tuple[int, int, int, int]:
        return self.x_start, self.x_end, self.y_start, self.y_end


class GridLayout:
    """Calculate and manage grid cell positions"""

    def __init__(
        self,
        margins: PageMargins,
        num_rows: int,
        num_columns: int,
        col_gap_px: int,
        row_gap_px: int,
    ):
        self.margins = margins
        self.num_rows = num_rows
        self.num_columns = num_columns
        self.col_gap_px = col_gap_px
        self.row_gap_px = row_gap_px

        # Calculate cell dimensions
        available_width = margins.content_width - ((num_columns - 1) * col_gap_px)
        self.cell_width = available_width // num_columns

        available_height = margins.content_height - ((num_rows - 1) * row_gap_px)
        self.cell_height = available_height // num_rows

    def get_cell(self, row: int, col: int) -> GridCell:
        """Get cell bounds for specific row/column"""
        x_start = self.margins.left + (col * (self.cell_width + self.col_gap_px))
        x_end = x_start + self.cell_width

        y_start = self.margins.top + (row * (self.cell_height + self.row_gap_px))
        y_end = y_start + self.cell_height

        return GridCell(row, col, x_start, x_end, y_start, y_end)

    def iter_cells(self):
        """Iterate over all cells in row-major order"""
        for r in range(self.num_rows):
            for c in range(self.num_columns):
                yield self.get_cell(r, c)

    def draw_separators(self, ctx: cairo.Context, page_width: int, page_height: int):
        """Draw all grid separators"""
        # Vertical separators
        for c in range(self.num_columns - 1):
            cell = self.get_cell(0, c)
            sep_x = cell.x_end + (self.col_gap_px // 2)
            draw_separator(ctx, sep_x, self.margins.top, page_height - self.margins.bottom, grey=5)

        # Horizontal separators
        for r in range(self.num_rows - 1):
            cell = self.get_cell(r, 0)
            sep_y = cell.y_end + (self.row_gap_px // 2)
            ctx.set_line_width(1.0)
            grey_val = snap_to_eink_greyscale(5)
            ctx.set_source_rgb(grey_val, grey_val, grey_val)
            ctx.move_to(self.margins.left, sep_y + 0.5)
            ctx.line_to(page_width - self.margins.right, sep_y + 0.5)
            ctx.stroke()


# --- GENERATION FUNCTIONS ---


def create_template_surface(
    template_type: str,
    device_config: dict,
    spacing_str: str,
    margin_mm: float,
    auto_adjust_spacing: bool,
    force_major_alignment: bool,
    header: str,
    footer: str,
    template_kwargs: dict,
) -> cairo.ImageSurface:
    """
    Primary factory for generating single-page templates.
    """
    # 1. Setup
    width = device_config["width"]
    height = device_config["height"]
    dpi = device_config["dpi"]

    # --- Legacy: Hybrid Template (Must handle first) ---
    if template_type == "hybrid_lined_dotgrid":
        try:
            spacing_mm_val = float(str(spacing_str).lower().replace("mm", "").replace("px", ""))
        except ValueError:
            spacing_mm_val = 6.0  # Fallback

        return create_hybrid_template(
            width=width,
            height=height,
            dpi=dpi,
            spacing_mm=spacing_mm_val,
            margin_mm=margin_mm,
            section_gap_mm=template_kwargs.get("section_gap_mm", spacing_mm_val),
            line_width_px=template_kwargs.get("line_width_px", 0.5),
            dot_radius_px=template_kwargs.get("dot_radius_px", 1.5),
            header=header,
            footer=footer,
            split_ratio=template_kwargs.get("split_ratio", 0.6),
            auto_adjust_spacing=auto_adjust_spacing,
            force_major_alignment=force_major_alignment,
        )

    # 2. Calculate spacing
    # We use parse_spacing here, not calculate_spacing, to maintain compatibility
    # with the 'px' mode string.
    spacing_px, original_mm, adjusted_mm, was_adjusted, mode = parse_spacing(
        spacing_str, dpi, auto_adjust=auto_adjust_spacing
    )
    if mode == "mm" and was_adjusted:
        print(
            f"Note: Adjusted spacing from {original_mm}mm to {adjusted_mm:.3f}mm ({int(spacing_px)}px) for pixel-perfect alignment"
        )
    elif mode == "px":
        print(f"Using exact pixel spacing: {int(spacing_px)}px (≈{original_mm:.2f}mm)")

    # 3. Create canvas
    surface, ctx = create_canvas(width, height)

    # 4. Calculate alignment units
    alignment = AlignmentUnits.from_template_config(template_type, spacing_px, dpi, template_kwargs)

    # 5. Calculate margins
    margins = calculate_page_margins(
        width,
        height,
        dpi,
        margin_mm,
        alignment.vertical,
        alignment.horizontal,
        template_kwargs.get("major_every"),
        force_major_alignment and template_kwargs.get("major_every"),
    )

    # 6. Draw separators
    has_header, has_footer = draw_page_separators(ctx, margins, width, height, header, footer)

    # 7. Render template
    renderer = TemplateRenderer(ctx, dpi)
    renderer.render(
        template_type,
        margins.bounds,
        spacing_px,
        adjusted_mm,  # Pass adjusted_mm for music_staff
        template_kwargs,
        skip_first=has_header,
        skip_last=has_footer,
    )

    # Draw corner ornaments if specified
    corner_style = template_kwargs.get("corner_style")
    if corner_style:
        from .corners import draw_page_corners

        ctx_corners = cairo.Context(surface)

        corner_kwargs = {"grey": template_kwargs.get("corner_grey", 0)}

        draw_page_corners(
            ctx_corners,
            margins,
            width,
            height,
            corner_style,
            template_kwargs.get("corner_size", 20.0),
            **corner_kwargs,
        )

    return surface


# --- COMPLEX LAYOUT ---


def create_hybrid_template(
    width,
    height,
    dpi,
    spacing_mm,
    margin_mm,
    section_gap_mm,
    line_width_px,
    dot_radius_px,
    header=None,
    footer=None,
    split_ratio=0.6,
    auto_adjust_spacing=True,
    force_major_alignment=None,  # Note: force_major_alignment not implemented for hybrid
):
    """
    Create a hybrid template with lined section (left) and dot grid (right)
    (Refactored to use new helpers)
    """
    # 1. Setup
    mm2px = dpi / 25.4
    spacing = calculate_spacing(spacing_mm, dpi, auto_adjust_spacing)
    spacing.print_adjustment_message()
    spacing_px = spacing.pixels

    # 2. Canvas
    surface, ctx = create_canvas(width, height)

    # 3. Alignment & Margins (Hybrid uses "default" for both sides)
    alignment = AlignmentUnits(vertical=spacing_px, horizontal=spacing_px)
    margins = calculate_page_margins(
        width, height, dpi, margin_mm, alignment.vertical, alignment.horizontal
    )

    # 4. Separators
    has_header, has_footer = draw_page_separators(ctx, margins, width, height, header, footer)

    # 5. Calculate Split
    split_x_abs = margins.content_x_start + (margins.content_width * split_ratio)
    gap_px = round(section_gap_mm * mm2px)
    half_gap = gap_px // 2

    # 6. Render
    renderer = TemplateRenderer(ctx, dpi)

    # Left Side (Lined)
    renderer.render(
        "lined",
        bounds=(margins.left, split_x_abs - half_gap, margins.top, height - margins.bottom),
        spacing_px=spacing_px,
        spacing_mm=spacing.mm,
        template_kwargs={"line_width_px": line_width_px},
        skip_first=has_header,
        skip_last=has_footer,
    )

    # Right Side (Dotgrid)
    renderer.render(
        "dotgrid",
        bounds=(
            split_x_abs + half_gap,
            width - margins.right,
            margins.top,
            height - margins.bottom,
        ),
        spacing_px=spacing_px,
        spacing_mm=spacing.mm,
        template_kwargs={"dot_radius_px": dot_radius_px},
        skip_first=has_header,
        skip_last=has_footer,
    )

    # 7. Draw vertical separator
    draw_separator(ctx, split_x_abs, margins.top, height - margins.bottom, grey=5)

    return surface


def create_column_template(
    width,
    height,
    dpi,
    spacing_mm,
    margin_mm,
    num_columns,
    num_rows,
    column_gap_mm,
    row_gap_mm,
    base_template,
    template_kwargs,
    header=None,
    footer=None,
    auto_adjust_spacing=True,
    force_major_alignment=None,
):
    """
    Create a multi-column, multi-row template with any base template type
    (Refactored to use new helpers)
    """
    # 1. Setup
    spacing = calculate_spacing(spacing_mm, dpi, auto_adjust_spacing)
    spacing.print_adjustment_message()
    spacing_px = spacing.pixels

    col_gap_px = round(column_gap_mm * (dpi / 25.4))
    row_gap_px = round(row_gap_mm * (dpi / 25.4))

    # 2. Canvas
    surface, ctx = create_canvas(width, height)

    # 3. Alignment & Margins (Based on the single base_template type)
    alignment = AlignmentUnits.from_template_config(base_template, spacing_px, dpi, template_kwargs)
    margins = calculate_page_margins(
        width,
        height,
        dpi,
        margin_mm,
        alignment.vertical,
        alignment.horizontal,
        template_kwargs.get("major_every"),
        force_major_alignment and template_kwargs.get("major_every"),
    )

    # 4. Separators
    has_header, has_footer = draw_page_separators(ctx, margins, width, height, header, footer)

    # 5. Grid Layout
    grid = GridLayout(margins, num_rows, num_columns, col_gap_px, row_gap_px)
    renderer = TemplateRenderer(ctx, dpi)

    # 6. Render all cells
    for cell in grid.iter_cells():
        # Adjust internal margins for perfect alignment
        internal_margins = calculate_page_margins(
            cell.width, cell.height, dpi, 0, alignment.vertical, alignment.horizontal
        )

        cell_bounds = (
            cell.x_start + internal_margins.left,
            cell.x_end - internal_margins.right,
            cell.y_start + internal_margins.top,
            cell.y_end - internal_margins.bottom,
        )

        renderer.render(
            base_template,
            cell_bounds,
            spacing_px,
            spacing.mm,
            template_kwargs,
            skip_first=(cell.row == 0) and has_header,
            skip_last=(cell.row == num_rows - 1) and has_footer,
        )

    # 7. Draw grid separators
    grid.draw_separators(ctx, width, height)
    return surface


def create_cell_grid_template(
    width,
    height,
    dpi,
    spacing_mm,
    margin_mm,
    cell_definitions,
    column_gap_mm,
    row_gap_mm,
    header=None,
    footer=None,
    auto_adjust_spacing=True,
    force_major_alignment=None,
):
    """
    Create a multi-column, multi-row template where each cell can be
    a different template type. (Refactored)
    """
    # 1. Setup
    spacing = calculate_spacing(spacing_mm, dpi, auto_adjust_spacing)
    spacing.print_adjustment_message()
    spacing_px = spacing.pixels

    col_gap_px = round(column_gap_mm * (dpi / 25.4))
    row_gap_px = round(row_gap_mm * (dpi / 25.4))

    num_rows = len(cell_definitions)
    num_columns = len(cell_definitions[0]) if num_rows > 0 else 0

    # 2. Canvas
    surface, ctx = create_canvas(width, height)

    # 3. Alignment & Margins (Based on top-left cell)
    master_template_type = cell_definitions[0][0]["type"]
    master_kwargs = cell_definitions[0][0]["kwargs"]
    alignment = AlignmentUnits.from_template_config(
        master_template_type, spacing_px, dpi, master_kwargs
    )
    margins = calculate_page_margins(
        width,
        height,
        dpi,
        margin_mm,
        alignment.vertical,
        alignment.horizontal,
        master_kwargs.get("major_every"),
        force_major_alignment and master_kwargs.get("major_every"),
    )

    # 4. Separators
    has_header, has_footer = draw_page_separators(ctx, margins, width, height, header, footer)

    # 5. Grid Layout
    grid = GridLayout(margins, num_rows, num_columns, col_gap_px, row_gap_px)
    renderer = TemplateRenderer(ctx, dpi)

    # 6. Render all cells
    for cell in grid.iter_cells():
        cell_def = cell_definitions[cell.row][cell.col]
        template_type = cell_def["type"]
        template_kwargs = cell_def["kwargs"]

        # Calculate internal alignment for this specific cell
        cell_alignment = AlignmentUnits.from_template_config(
            template_type, spacing_px, dpi, template_kwargs
        )
        internal_margins = calculate_page_margins(
            cell.width, cell.height, dpi, 0, cell_alignment.vertical, cell_alignment.horizontal
        )

        cell_bounds = (
            cell.x_start + internal_margins.left,
            cell.x_end - internal_margins.right,
            cell.y_start + internal_margins.top,
            cell.y_end - internal_margins.bottom,
        )

        renderer.render(
            template_type,
            cell_bounds,
            spacing_px,
            spacing.mm,
            template_kwargs,
            skip_first=(cell.row == 0) and has_header,
            skip_last=(cell.row == num_rows - 1) and has_footer,
        )

    # 7. Draw grid separators
    grid.draw_separators(ctx, width, height)
    return surface


def create_json_layout_template(
    config, device_config, margin_mm, auto_adjust=True, force_major_alignment=False
):
    """
    Create a complex, ratio-based template from a JSON config object.
    (Refactored)
    """
    # 1. Setup
    width = device_config["width"]
    height = device_config["height"]
    dpi = device_config["dpi"]

    master_spacing_mm = config.get("master_spacing_mm", 6)

    # 2. Canvas
    surface, ctx = create_canvas(width, height)
    renderer = TemplateRenderer(ctx, dpi)

    # 3. Page Margins (JSON layouts typically use simple 'none' alignment for the page)
    page_alignment = AlignmentUnits(vertical=1, horizontal=1)
    page_margins = calculate_page_margins(
        width, height, dpi, margin_mm, page_alignment.vertical, page_alignment.horizontal
    )
    print(
        f"Note: Page content area is {page_margins.content_width}px × {page_margins.content_height}px"
    )

    # 4. Page Separators
    has_header, has_footer = draw_page_separators(
        ctx, page_margins, width, height, config.get("header"), config.get("footer")
    )

    # 5. Draw Layout Regions
    if "page_layout" not in config or not config["page_layout"]:
        raise ValueError("JSON config must contain a 'page_layout' array.")

    for region in config["page_layout"]:
        name = region.get("name", "Unnamed Region")
        print(f"  Drawing region: '{name}'")

        # 5a. Calculate Region Pixel Boundaries
        rect_percents = region.get("region_rect")
        if not rect_percents or len(rect_percents) != 4:
            raise ValueError(f"Region '{name}' missing 'region_rect'.")

        x_p, y_p, w_p, h_p = rect_percents
        cell_x_start = page_margins.content_x_start + (x_p * page_margins.content_width)
        cell_y_start = page_margins.content_y_start + (y_p * page_margins.content_height)
        cell_width = w_p * page_margins.content_width
        cell_height = h_p * page_margins.content_height

        # 5b. Get Region-Specific Spacing
        region_spacing_mm = region.get("spacing_mm", master_spacing_mm)
        region_spacing = calculate_spacing(region_spacing_mm, dpi, auto_adjust)

        template_type = region.get("template")
        json_kwargs = region.get("kwargs", {})

        # 5c. Calculate Internal Alignment & Margins
        cell_alignment = AlignmentUnits.from_template_config(
            template_type, region_spacing.pixels, dpi, json_kwargs
        )
        major_every = json_kwargs.get("major_every")

        internal_margins = calculate_page_margins(
            cell_width,
            cell_height,
            dpi,
            0,  # 0 base margin
            cell_alignment.vertical,
            cell_alignment.horizontal,
            major_every,
            force_major_alignment and major_every,
        )

        # 5d. Define Final Drawing Boundaries
        cell_bounds = (
            cell_x_start + internal_margins.left,
            cell_x_start + cell_width - internal_margins.right,
            cell_y_start + internal_margins.top,
            cell_y_start + cell_height - internal_margins.bottom,
        )

        # 5e. Render
        renderer.render(
            template_type,
            cell_bounds,
            region_spacing.pixels,
            region_spacing.mm,
            json_kwargs,
            # Note: JSON layout doesn't currently use page-level header/footer skip logic
        )

        # 5f. Render JSON-defined decorations (different from standard kwargs)
        # (This duplicates logic from renderer, but JSON is a special case)
        if region.get("line_numbers"):
            cfg = region.get(
                "line_number_config",
                {"side": "left", "interval": 5, "margin_px": 40, "font_size": 18, "grey": 8},
            )
            drawing.draw_line_numbering(
                ctx, cell_bounds[2], cell_bounds[3], region_spacing.pixels, cfg
            )
        if region.get("cell_label_config"):
            drawing.draw_cell_labeling(
                ctx,
                cell_bounds[0],
                cell_bounds[1],
                cell_bounds[2],
                cell_bounds[3],
                region_spacing.pixels,
                region["cell_label_config"],
            )
        if region.get("axis_label_config"):
            drawing.draw_axis_labeling(
                ctx,
                cell_bounds[0],
                cell_bounds[1],
                cell_bounds[2],
                cell_bounds[3],
                region_spacing.pixels,
                region["axis_label_config"],
            )

    # 6. Draw Title Element
    if "title_element" in config:
        print("  Drawing title element...")
        draw_title_element(
            ctx,
            width,
            height,
            config["title_element"],
            page_margins.content_x_start,
            page_margins.content_y_start,
            page_margins.content_width,
            page_margins.content_height,
        )

    return surface
