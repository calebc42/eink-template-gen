# template_gen/config.py

import json
import os
from pathlib import Path

import platformdirs

# Define the app name for platformdirs
APP_NAME = "eink-template-gen"


def get_config_file():
    """Get the cross-platform, user-specific config file path."""

    # Get the recommended config directory for this OS
    # e.g., ~/.config/eink-template-gen
    config_dir = Path(platformdirs.user_config_dir(APP_NAME))

    # Ensure the directory exists
    os.makedirs(config_dir, exist_ok=True)

    # Return the full path to the config.json file
    return config_dir / "config.json"


def _load_config():
    """Load the config file and return its contents as a dict."""
    config_file = get_config_file()
    if config_file.exists():
        try:
            with open(config_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            # Return empty dict if file is corrupt or unreadable
            return {}
    return {}


def _save_config(config_dict):
    """Save the given dict to the config file."""
    config_file = get_config_file()
    try:
        with open(config_file, "w") as f:
            json.dump(config_dict, f, indent=2)
        return True
    except IOError as e:
        print(f"Error writing to config file: {e}")
        return False


def get_config_value(key, default=None):
    """Get a specific value from the config file."""
    config = _load_config()
    return config.get(key, default)


def set_config_value(key, value):
    """Set a specific value in the config file."""
    config = _load_config()
    config[key] = value
    return _save_config(config)


# --- Specific Accessors ---


def get_default_device():
    """Get the default device from local config file, or None if not set"""
    return get_config_value("default_device", default=None)


def set_default_device(device_id):
    """Set the default device in the local config file"""
    return set_config_value("default_device", device_id)


def get_default_margin():
    """Get the default margin from local config file, or 0.0 if not set"""
    return get_config_value("default_margin", default=0.0)


def set_default_margin(margin_mm):
    """Set the default margin in the local config file"""
    try:
        # Ensure margin is stored as a float
        margin_float = float(margin_mm)
        return set_config_value("default_margin", margin_float)
    except ValueError:
        print("Error: Margin must be a number.")
        return False
