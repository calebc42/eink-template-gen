# template_gen/__init__.py
"""
Supernote Template Generator
Generate custom, pixel-perfect templates for e-ink devices
"""

# Import the version from your pyproject.toml
# This requires installing `importlib-metadata`
from importlib.metadata import version
try:
    __version__ = version("eink-template-gen")
except Exception:
    __version__ = "0.0.0-unknown"


# --- Core Functions (from .actions) ---
# These are the main entry points
from .actions import (
    handle_cli_generation,
    handle_json_generation,
    handle_list_devices,
    handle_list_templates,
    handle_set_default_device,
    handle_set_default_margin,
    handle_show_spacing_info
)

# --- Config Functions (from .config) ---
from .config import get_default_device, set_default_device, get_default_margin, set_default_margin

# --- Device Functions (from .devices) ---
from .devices import DEVICES, get_device, list_devices

# --- Template Functions (from .templates) ---
from .templates import (
    TEMPLATE_REGISTRY,
    create_lined_template,
    create_dotgrid_template,
    create_grid_template,
    create_manuscript_template,
    create_french_ruled_template,
    create_music_staff_template,
    create_isometric_template,
    create_hex_template,
    create_hybrid_template,
    create_column_template,
    create_cell_grid_template,
    create_json_layout_template
)

# --- Drawing Primitives (from .drawing) ---
# (Usually you don't export these, but you could)
from .drawing import (
    draw_lined_section,
    draw_dot_grid,
    draw_grid
    # ... and so on
)


# Define what `from template_gen import *` imports
__all__ = [
    # Actions
    'handle_cli_generation',
    'handle_json_generation',
    
    # Config/Device
    'get_default_device',
    'set_default_device',
    'get_default_margin',
    'set_default_margin'
    'get_device',
    'list_devices',
    'DEVICES',
    
    # Templates
    'TEMPLATE_REGISTRY',
    'create_lined_template',
    'create_dotgrid_template',
    'create_grid_template',
    'create_manuscript_template',
    'create_french_ruled_template',
    'create_music_staff_template',
    'create_isometric_template',
    'create_hex_template',
    'create_hybrid_template',
    'create_column_template',
    'create_cell_grid_template',
    'create_json_layout_template'
]
