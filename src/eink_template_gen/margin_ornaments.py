"""
Margin ornament system for decorative margin elements

This module provides algorithms for placing glyphs in page margins
to add visual interest without interfering with the content area.
"""

import random
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass

import cairo

from .glyphs import draw_glyph, get_glyph_by_category, get_collection, get_glyph_visual_weight
from .utils import PageMargins


# --- Data Structures ---


@dataclass
class PlacedGlyph:
    """Represents a glyph placed at a specific position"""
    glyph_name: str
    x: float
    y: float
    size: float
    rotation: float = 0.0
    
    def get_bounds(self) -> Tuple[float, float, float, float]:
        """Return bounding box (x1, y1, x2, y2)"""
        half = self.size / 2
        return (
            self.x - half,
            self.y - half,
            self.x + half,
            self.y + half
        )
    
    def overlaps(self, other: 'PlacedGlyph', min_spacing: float = 0) -> bool:
        """Check if this glyph overlaps with another"""
        x1_min, y1_min, x1_max, y1_max = self.get_bounds()
        x2_min, y2_min, x2_max, y2_max = other.get_bounds()
        
        # Expand bounds by min_spacing
        x1_min -= min_spacing
        y1_min -= min_spacing
        x1_max += min_spacing
        y1_max += min_spacing
        
        # Check for overlap
        return not (x1_max < x2_min or x1_min > x2_max or y1_max < y2_min or y1_min > y2_max)


@dataclass
class MarginBounds:
    """Defines the four margin regions"""
    top: Tuple[float, float, float, float]     # (x1, y1, x2, y2)
    bottom: Tuple[float, float, float, float]
    left: Tuple[float, float, float, float]
    right: Tuple[float, float, float, float]
    
    @classmethod
    def from_page_margins(cls, margins: PageMargins, page_width: int, page_height: int):
        """Create margin bounds from PageMargins object"""
        return cls(
            top=(0, 0, page_width, margins.top),
            bottom=(0, page_height - margins.bottom, page_width, page_height),
            left=(0, margins.top, margins.left, page_height - margins.bottom),
            right=(page_width - margins.right, margins.top, page_width, page_height - margins.bottom)
        )
    
    def get_all_bounds(self) -> List[Tuple[float, float, float, float]]:
        """Return all four margin regions as a list"""
        return [self.top, self.bottom, self.left, self.right]
    
    def get_area(self, region: str) -> float:
        """Calculate area of a specific margin region"""
        bounds = getattr(self, region)
        x1, y1, x2, y2 = bounds
        return (x2 - x1) * (y2 - y1)
    
    def get_total_area(self) -> float:
        """Calculate total area of all margins"""
        return sum(self.get_area(r) for r in ['top', 'bottom', 'left', 'right'])


# --- Scatter Algorithm ---


def scatter_glyphs(
    margin_bounds: MarginBounds,
    glyph_list: List[str],
    density: float = 0.3,
    size_range: Tuple[float, float] = (6, 12),
    min_spacing: float = 10.0,
    seed: Optional[int] = None,
    exclude_corners: bool = True,
    corner_exclusion_size: float = 30.0,
    visual_balance: bool = True,
    max_attempts: int = 1000,
) -> List[PlacedGlyph]:
    """
    Scatter glyphs randomly in margin areas
    
    Args:
        margin_bounds: Margin regions to place glyphs in
        glyph_list: List of glyph names to choose from
        density: Density factor (0.0-1.0, where 1.0 = very dense)
        size_range: (min_size, max_size) for random glyph sizing
        min_spacing: Minimum spacing between glyphs (pixels)
        seed: Random seed for reproducibility
        exclude_corners: Don't place glyphs near corners
        corner_exclusion_size: Size of corner exclusion zones
        visual_balance: Try to balance visual weight across quadrants
        max_attempts: Maximum placement attempts per glyph
    
    Returns:
        List of PlacedGlyph objects
    """
    if seed is not None:
        random.seed(seed)
    
    placed_glyphs = []
    
    # Calculate how many glyphs to place based on density
    total_area = margin_bounds.get_total_area()
    avg_glyph_size = sum(size_range) / 2
    glyph_area = avg_glyph_size * avg_glyph_size
    
    # Estimate number of glyphs (with spacing)
    effective_area_per_glyph = glyph_area + (min_spacing * min_spacing)
    max_glyphs = int(total_area / effective_area_per_glyph)
    num_glyphs = max(1, int(max_glyphs * density))
    
    # Track visual weight per quadrant for balancing
    quadrant_weights = {"tl": 0, "tr": 0, "bl": 0, "br": 0}
    
    # Try to place glyphs
    attempts = 0
    while len(placed_glyphs) < num_glyphs and attempts < max_attempts:
        attempts += 1
        
        # Pick a random margin region
        region_name = random.choice(['top', 'bottom', 'left', 'right'])
        bounds = getattr(margin_bounds, region_name)
        x1, y1, x2, y2 = bounds
        
        # Random position within this region
        x = random.uniform(x1, x2)
        y = random.uniform(y1, y2)
        
        # Check corner exclusion
        if exclude_corners:
            # Get page corners (approximate from bounds)
            page_width = max(margin_bounds.right[2], margin_bounds.top[2])
            page_height = max(margin_bounds.bottom[3], margin_bounds.left[3])
            
            corners = [
                (0, 0),  # top-left
                (page_width, 0),  # top-right
                (0, page_height),  # bottom-left
                (page_width, page_height),  # bottom-right
            ]
            
            too_close_to_corner = False
            for cx, cy in corners:
                dist = ((x - cx)**2 + (y - cy)**2)**0.5
                if dist < corner_exclusion_size:
                    too_close_to_corner = True
                    break
            
            if too_close_to_corner:
                continue
        
        # Pick glyph
        if visual_balance:
            # Choose glyph based on current quadrant balance
            quadrant = _get_quadrant(x, y, margin_bounds)
            
            # If this quadrant is heavy, prefer light glyphs
            if quadrant_weights[quadrant] > sum(quadrant_weights.values()) / 4:
                # Prefer light glyphs
                light_glyphs = [g for g in glyph_list if get_glyph_visual_weight(g) == "light"]
                glyph_name = random.choice(light_glyphs) if light_glyphs else random.choice(glyph_list)
            else:
                glyph_name = random.choice(glyph_list)
        else:
            glyph_name = random.choice(glyph_list)
        
        # Random size
        size = random.uniform(size_range[0], size_range[1])
        
        # Create placement
        new_glyph = PlacedGlyph(glyph_name, x, y, size)
        
        # Check for overlaps
        overlaps = False
        for existing in placed_glyphs:
            if new_glyph.overlaps(existing, min_spacing):
                overlaps = True
                break
        
        if not overlaps:
            placed_glyphs.append(new_glyph)
            
            # Update visual weight tracking
            if visual_balance:
                weight = get_glyph_visual_weight(glyph_name)
                weight_value = {"light": 1, "medium": 2, "heavy": 3}.get(weight, 2)
                quadrant = _get_quadrant(x, y, margin_bounds)
                quadrant_weights[quadrant] += weight_value
    
    return placed_glyphs


def _get_quadrant(x: float, y: float, margin_bounds: MarginBounds) -> str:
    """Determine which quadrant a point is in (tl, tr, bl, br)"""
    # Approximate page center from margin bounds
    page_width = max(margin_bounds.right[2], margin_bounds.top[2])
    page_height = max(margin_bounds.bottom[3], margin_bounds.left[3])
    
    cx = page_width / 2
    cy = page_height / 2
    
    if x < cx and y < cy:
        return "tl"
    elif x >= cx and y < cy:
        return "tr"
    elif x < cx and y >= cy:
        return "bl"
    else:
        return "br"


# --- Grid Placement Algorithm ---


def grid_placement(
    margin_bounds: MarginBounds,
    glyph_list: List[str],
    spacing: float = 50.0,
    pattern: str = "regular",
    size: float = 8.0,
    offset_x: float = 0.0,
    offset_y: float = 0.0,
) -> List[PlacedGlyph]:
    """
    Place glyphs in a regular grid pattern in margins
    
    Args:
        margin_bounds: Margin regions to place glyphs in
        glyph_list: List of glyph names to choose from
        spacing: Distance between grid points
        pattern: "regular", "checkerboard", or "alternating"
        size: Size of glyphs
        offset_x: Horizontal offset for grid start
        offset_y: Vertical offset for grid start
    
    Returns:
        List of PlacedGlyph objects
    """
    placed_glyphs = []
    glyph_index = 0
    
    for region_name in ['top', 'bottom', 'left', 'right']:
        bounds = getattr(margin_bounds, region_name)
        x1, y1, x2, y2 = bounds
        
        # Generate grid points in this region
        x = x1 + offset_x
        while x < x2:
            y = y1 + offset_y
            while y < y2:
                # Check pattern rules
                should_place = True
                
                if pattern == "checkerboard":
                    # Skip every other position in checkerboard pattern
                    grid_x = int((x - x1) / spacing)
                    grid_y = int((y - y1) / spacing)
                    if (grid_x + grid_y) % 2 == 1:
                        should_place = False
                
                if should_place:
                    # Pick glyph (cycle through list)
                    glyph_name = glyph_list[glyph_index % len(glyph_list)]
                    
                    if pattern == "alternating":
                        glyph_index += 1
                    
                    placed_glyphs.append(PlacedGlyph(glyph_name, x, y, size))
                
                y += spacing
            x += spacing
    
    return placed_glyphs


# --- Clustered Placement Algorithm ---


def clustered_placement(
    margin_bounds: MarginBounds,
    glyph_list: List[str],
    num_clusters: int = 4,
    glyphs_per_cluster: int = 5,
    cluster_radius: float = 30.0,
    size_range: Tuple[float, float] = (6, 12),
    seed: Optional[int] = None,
) -> List[PlacedGlyph]:
    """
    Place glyphs in clusters/groups
    
    Args:
        margin_bounds: Margin regions to place glyphs in
        glyph_list: List of glyph names to choose from
        num_clusters: Number of cluster centers
        glyphs_per_cluster: Glyphs to place around each center
        cluster_radius: Radius of each cluster
        size_range: (min_size, max_size) for random glyph sizing
        seed: Random seed for reproducibility
    
    Returns:
        List of PlacedGlyph objects
    """
    if seed is not None:
        random.seed(seed)
    
    placed_glyphs = []
    
    # Pick random cluster centers
    all_bounds = margin_bounds.get_all_bounds()
    
    for _ in range(num_clusters):
        # Pick random margin region and position for cluster center
        bounds = random.choice(all_bounds)
        x1, y1, x2, y2 = bounds
        
        center_x = random.uniform(x1, x2)
        center_y = random.uniform(y1, y2)
        
        # Place glyphs around this center
        for _ in range(glyphs_per_cluster):
            # Random offset from center
            angle = random.uniform(0, 2 * 3.14159)
            distance = random.uniform(0, cluster_radius)
            
            x = center_x + distance * random.uniform(-1, 1)
            y = center_y + distance * random.uniform(-1, 1)
            
            # Ensure it's still within the margin bounds
            if x < x1 or x > x2 or y < y1 or y > y2:
                continue
            
            glyph_name = random.choice(glyph_list)
            size = random.uniform(size_range[0], size_range[1])
            
            placed_glyphs.append(PlacedGlyph(glyph_name, x, y, size))
    
    return placed_glyphs


# --- Edge Placement Algorithm ---


def edge_aligned_placement(
    margin_bounds: MarginBounds,
    glyph_list: List[str],
    spacing: float = 80.0,
    size: float = 8.0,
    edge_offset: float = 10.0,
    edges: List[str] = None,
) -> List[PlacedGlyph]:
    """
    Place glyphs along the edges of margins at regular intervals
    
    Args:
        margin_bounds: Margin regions to place glyphs in
        glyph_list: List of glyph names to choose from
        spacing: Distance between glyphs along edge
        size: Size of glyphs
        edge_offset: Distance from edge
        edges: Which edges to place on (["top", "bottom", "left", "right"])
    
    Returns:
        List of PlacedGlyph objects
    """
    if edges is None:
        edges = ["top", "bottom", "left", "right"]
    
    placed_glyphs = []
    glyph_index = 0
    
    for edge in edges:
        if edge == "top":
            bounds = margin_bounds.top
            x1, y1, x2, y2 = bounds
            # Place along bottom edge of top margin
            y = y2 - edge_offset
            x = x1 + spacing / 2
            while x < x2:
                glyph_name = glyph_list[glyph_index % len(glyph_list)]
                placed_glyphs.append(PlacedGlyph(glyph_name, x, y, size))
                glyph_index += 1
                x += spacing
        
        elif edge == "bottom":
            bounds = margin_bounds.bottom
            x1, y1, x2, y2 = bounds
            # Place along top edge of bottom margin
            y = y1 + edge_offset
            x = x1 + spacing / 2
            while x < x2:
                glyph_name = glyph_list[glyph_index % len(glyph_list)]
                placed_glyphs.append(PlacedGlyph(glyph_name, x, y, size))
                glyph_index += 1
                x += spacing
        
        elif edge == "left":
            bounds = margin_bounds.left
            x1, y1, x2, y2 = bounds
            # Place along right edge of left margin
            x = x2 - edge_offset
            y = y1 + spacing / 2
            while y < y2:
                glyph_name = glyph_list[glyph_index % len(glyph_list)]
                placed_glyphs.append(PlacedGlyph(glyph_name, x, y, size))
                glyph_index += 1
                y += spacing
        
        elif edge == "right":
            bounds = margin_bounds.right
            x1, y1, x2, y2 = bounds
            # Place along left edge of right margin
            x = x1 + edge_offset
            y = y1 + spacing / 2
            while y < y2:
                glyph_name = glyph_list[glyph_index % len(glyph_list)]
                placed_glyphs.append(PlacedGlyph(glyph_name, x, y, size))
                glyph_index += 1
                y += spacing
    
    return placed_glyphs


# --- Main Drawing Function ---


def draw_margin_ornaments(
    ctx: cairo.Context,
    placed_glyphs: List[PlacedGlyph],
    line_width: float = 1.0,
    grey: int = 0,
) -> None:
    """
    Draw all placed glyphs
    
    Args:
        ctx: Cairo context
        placed_glyphs: List of PlacedGlyph objects
        line_width: Line width for glyphs
        grey: Greyscale value (0-15 or 0.0-1.0)
    """
    for glyph in placed_glyphs:
        draw_glyph(
            ctx,
            glyph.x,
            glyph.y,
            glyph.glyph_name,
            size=glyph.size,
            line_width=line_width,
            grey=grey,
        )


# --- Convenience Functions ---


def apply_margin_ornaments(
    ctx: cairo.Context,
    margins: PageMargins,
    page_width: int,
    page_height: int,
    style: str = "scattered",
    glyph_spec: str = "technical",
    **kwargs
) -> bool:
    """
    High-level function to apply margin ornaments
    
    Args:
        ctx: Cairo context
        margins: PageMargins object
        page_width: Page width in pixels
        page_height: Page height in pixels
        style: Placement style ("scattered", "grid", "clustered", "edge-aligned")
        glyph_spec: Category name, collection name, or comma-separated glyph list
        **kwargs: Style-specific parameters
    
    Returns:
        bool: True if ornaments were drawn
    """
    # Parse glyph specification
    if "," in glyph_spec:
        # Explicit list of glyphs
        glyph_list = [g.strip() for g in glyph_spec.split(",")]
    else:
        # Try as category first, then collection
        from .glyphs import get_glyph_by_category, get_collection
        
        glyph_list = get_glyph_by_category(glyph_spec)
        if not glyph_list:
            glyph_list = get_collection(glyph_spec)
        
        if not glyph_list:
            print(f"Warning: Unknown glyph specification '{glyph_spec}'. Using 'technical' category.")
            glyph_list = get_glyph_by_category("technical")
    
    # Create margin bounds
    margin_bounds = MarginBounds.from_page_margins(margins, page_width, page_height)
    
    # Separate drawing kwargs from placement kwargs
    drawing_kwargs = {
        'line_width': kwargs.pop('line_width', 1.0),
        'grey': kwargs.pop('grey', 0)
    }
    
    # All remaining kwargs go to placement algorithm
    placement_kwargs = kwargs
    
    # Choose placement algorithm
    if style == "scattered":
        placed_glyphs = scatter_glyphs(margin_bounds, glyph_list, **placement_kwargs)
    elif style == "grid":
        placed_glyphs = grid_placement(margin_bounds, glyph_list, **placement_kwargs)
    elif style == "clustered":
        placed_glyphs = clustered_placement(margin_bounds, glyph_list, **placement_kwargs)
    elif style == "edge-aligned":
        placed_glyphs = edge_aligned_placement(margin_bounds, glyph_list, **placement_kwargs)
    else:
        print(f"Warning: Unknown margin ornament style '{style}'. Using 'scattered'.")
        placed_glyphs = scatter_glyphs(margin_bounds, glyph_list, **placement_kwargs)
    
    # Draw them
    draw_margin_ornaments(ctx, placed_glyphs, **drawing_kwargs)
    
    return len(placed_glyphs) > 0
