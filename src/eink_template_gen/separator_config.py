"""
Separator configuration parser and preset manager
"""

from .separators import STYLE_REGISTRY


def parse_separator_config(config):
    """
    Parse separator configuration from various input formats

    Args:
        config: Can be:
            - String: "bold" (style name)
            - String: "bold-thick" (preset name)
            - String: "wavy(amplitude=15,wavelength=120)" (style with params)
            - Dict: {"style": "wavy", "amplitude": 15, ...} (JSON format)
            - None: No separator

    Returns:
        Tuple of (style_name, kwargs_dict) or (None, {})

    Examples:
        parse_separator_config("bold")
        → ("bold", {})

        parse_separator_config("bold-thick")
        → ("bold", {"line_width": 8.0})

        parse_separator_config("wavy(amplitude=15,wavelength=120)")
        → ("wavy", {"amplitude": 15.0, "wavelength": 120.0})

        parse_separator_config({"style": "wavy", "amplitude": 15})
        → ("wavy", {"amplitude": 15})
    """
    if config is None:
        return None, {}

    # Case 1: Dictionary (JSON format)
    if isinstance(config, dict):
        style = config.get("style")
        if not style:
            print("Warning: Separator config missing 'style' key. Ignoring.")
            return None, {}

        # Extract all other keys as kwargs
        kwargs = {k: v for k, v in config.items() if k != "style"}
        return style, kwargs

    # Case 2: String
    if isinstance(config, str):
        config = config.strip()

        # Check if it has parameters: "style(param=value,param=value)"
        if "(" in config and config.endswith(")"):
            return _parse_string_with_params(config)

        # Check if it's a preset: "bold-thick"
        if config in SEPARATOR_PRESETS:
            preset = SEPARATOR_PRESETS[config]
            return preset["style"], preset.get("params", {})

        # Plain style name: "bold"
        if config in STYLE_REGISTRY:
            return config, {}

        print(f"Warning: Unknown separator config '{config}'. Ignoring.")
        return None, {}

    print(f"Warning: Invalid separator config type: {type(config)}. Ignoring.")
    return None, {}


def _parse_string_with_params(config_str):
    """
    Parse "style(param=value,param=value)" format

    Args:
        config_str: String like "wavy(amplitude=15,wavelength=120)"

    Returns:
        Tuple of (style_name, kwargs_dict)
    """
    try:
        # Split on first '('
        style, params_str = config_str.split("(", 1)
        style = style.strip()

        # Remove trailing ')'
        params_str = params_str.rstrip(")")

        # Parse parameters
        kwargs = {}
        if params_str:
            for param in params_str.split(","):
                param = param.strip()
                if "=" not in param:
                    print(f"Warning: Invalid parameter format '{param}'. Skipping.")
                    continue

                key, value = param.split("=", 1)
                key = key.strip()
                value = value.strip()

                # Try to convert to appropriate type
                kwargs[key] = _parse_param_value(value)

        return style, kwargs

    except Exception as e:
        print(f"Warning: Failed to parse separator config '{config_str}': {e}")
        return None, {}


def _parse_param_value(value_str):
    """
    Convert string parameter value to appropriate Python type

    Args:
        value_str: String like "15" or "15.5" or "true" or "dashed"

    Returns:
        Converted value (int, float, bool, or str)
    """
    value_str = value_str.strip()

    # Boolean
    if value_str.lower() in ["true", "false"]:
        return value_str.lower() == "true"

    # Try integer
    try:
        if "." not in value_str:
            return int(value_str)
    except ValueError:
        pass

    # Try float
    try:
        return float(value_str)
    except ValueError:
        pass

    # String (remove quotes if present)
    if (value_str.startswith('"') and value_str.endswith('"')) or (
        value_str.startswith("'") and value_str.endswith("'")
    ):
        return value_str[1:-1]

    return value_str


# Preset definitions (we'll populate this next)
SEPARATOR_PRESETS = {
    # Format: "preset-name": {"style": "style-name", "params": {...}}
}
