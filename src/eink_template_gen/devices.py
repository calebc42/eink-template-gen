"""
Device specifications for supported e-ink devices
"""

import json
import sys

# Use the correct import logic based on Python version
if sys.version_info >= (3, 9):
    from importlib.resources import as_file, files
else:
    # Python 3.8 uses the 'importlib_resources' backport
    from importlib_resources import as_file, files


# --- Greyscale Palette ---

# E-ink native greyscale palette (16 levels)
EINK_GREYSCALE_PALETTE = [
    0.0,  # 0:  #000000 (black)
    16 / 255,  # 1:  #101010
    32 / 255,  # 2:  #202020
    48 / 255,  # 3:  #303030
    64 / 255,  # 4:  #404040
    80 / 255,  # 5:  #505050
    96 / 255,  # 6:  #606060
    112 / 255,  # 7:  #707070
    128 / 255,  # 8:  #808080 (medium grey)
    144 / 255,  # 9:  #909090
    160 / 255,  # 10: #a0a0a0
    176 / 255,  # 11: #b0b0b0
    192 / 255,  # 12: #c0c0c0
    208 / 255,  # 13: #d0d0d0
    224 / 255,  # 14: #e0e0e0
    1.0,  # 15: #ffffff (white)
]


def snap_to_eink_greyscale(grey_value):
    """
    Snap a grey value to the nearest e-ink native greyscale level

    Args:
        grey_value: Float 0.0-1.0 or int 0-15

    Returns:
        Float snapped to nearest e-ink greyscale level (0.0-1.0)
    """
    # Handle 0-15 integer scale
    if grey_value > 1.0:
        grey_value = int(grey_value)
        if 0 <= grey_value <= 15:
            return EINK_GREYSCALE_PALETTE[grey_value]
        else:
            # Clamp and convert
            grey_value = max(0, min(15, grey_value)) / 15.0

    # Clamp to valid range
    grey_value = max(0.0, min(1.0, grey_value))

    # Snap to nearest palette value
    closest_idx = min(
        range(len(EINK_GREYSCALE_PALETTE)),
        key=lambda i: abs(EINK_GREYSCALE_PALETTE[i] - grey_value),
    )

    return EINK_GREYSCALE_PALETTE[closest_idx]


def print_greyscale_palette():
    """Print the e-ink greyscale palette for reference"""
    print("\nE-ink Greyscale Palette (16 levels):")
    print("=" * 50)
    for i, value in enumerate(EINK_GREYSCALE_PALETTE):
        hex_value = int(value * 255)
        hex_str = f"#{hex_value:02x}{hex_value:02x}{hex_value:02x}"
        print(f"  {i:2d}: {value:.4f} → {hex_str}")
    print("=" * 50)


# --- Device Loading ---


def _load_devices():
    """
    Loads device definitions from the devices.json file.
    """
    try:
        # Get a reference to the devices.json file within the package
        # 'files' returns a Traversable object
        json_path_ref = files("eink_template_gen").joinpath("devices.json")

        # 'as_file' provides a context manager to get a real file path
        with as_file(json_path_ref) as json_file_path:
            with open(json_file_path, "r") as f:
                devices_list = json.load(f)

        # Convert the list of devices into a dictionary keyed by 'id'
        devices_dict = {device.pop("id"): device for device in devices_list}
        return devices_dict

    except Exception as e:
        print(f"Error loading devices.json: {e}")
        print("Falling back to empty device list.")
        return {}


# Load devices on module import
DEVICES = _load_devices()

# --- Device Functions ---


def get_device(device_name):
    """
    Get device configuration by name

    Args:
        device_name: Device identifier (e.g., 'manta', 'a5x')

    Returns:
        Device configuration dict

    Raises:
        ValueError: If device not found
    """
    if not DEVICES:
        raise ValueError("Device list is empty. Check devices.json.")

    if device_name not in DEVICES:
        available = ", ".join(DEVICES.keys())
        raise ValueError(f"Unknown device '{device_name}'. Available: {available}")

    return DEVICES[device_name]


def add_device(device_id, width, height, dpi, name, diagonal_inches=None, default_margin_mm=None):
    """
    Add a new device configuration *at runtime*.
    Note: This does not modify the devices.json file.

    Args:
        device_id: Unique identifier for the device (e.g., 'manta', 'a5x')
        width: Screen width in pixels
        height: Screen height in pixels
        dpi: Screen DPI
        name: Human-readable device name
        diagonal_inches: Screen diagonal size in inches (optional)
        default_margin_mm: Default margin for this device in mm (optional)

    Raises:
        ValueError: If device_id already exists
    """
    if device_id in DEVICES:
        raise ValueError(f"Device '{device_id}' already exists. Use a different ID.")

    DEVICES[device_id] = {
        "width": width,
        "height": height,
        "dpi": dpi,
        "name": name,
    }

    if diagonal_inches is not None:
        DEVICES[device_id]["diagonal_inches"] = diagonal_inches

    if default_margin_mm is not None:
        DEVICES[device_id]["default_margin_mm"] = default_margin_mm


def list_devices():
    """
    List all available devices

    Returns:
        List of device IDs
    """
    return list(DEVICES.keys())
