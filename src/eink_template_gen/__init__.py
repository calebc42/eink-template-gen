# eink_template_gen/__init__.py
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
    handle_cover_generation,
    handle_json_generation,
    handle_list_devices,
    handle_list_templates,
    handle_multi_template_generation,
    handle_set_default_device,
    handle_set_default_margin,
    handle_show_spacing_info,
    handle_single_template_generation,
)

# --- Config Functions (from .config) ---
from .config import get_default_device, get_default_margin, set_default_device, set_default_margin

# --- Device Functions (from .devices) ---
from .devices import DEVICES, get_device, list_devices

# --- Template Functions (from .templates) ---
from .templates import (
    TEMPLATE_REGISTRY,
    create_cell_grid_template,
    create_column_template,
    create_hybrid_template,
    create_json_layout_template,
    create_template_surface,
)

# Define what `from template_gen import *` imports
__all__ = [
    # Actions
    "handle_json_generation",
    "handle_cover_generation",
    "handle_single_template_generation",
    "handle_multi_template_generation",
    # Config/Device
    "get_default_device",
    "set_default_device",
    "get_default_margin",
    "set_default_margin",
    "get_device",
    "list_devices",
    "DEVICES",
    # Templates
    "TEMPLATE_REGISTRY",
    "create_template_surface",
    "create_hybrid_template",
    "create_column_template",
    "create_cell_grid_template",
    "create_json_layout_template",
]
