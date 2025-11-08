import argparse
import json
import os
from datetime import datetime
from typing import Any, Dict, Optional

from .actions import (
    handle_cover_generation,
    handle_json_generation,
    handle_multi_template_generation,
    handle_single_template_generation,
)
from .config import get_default_device, get_default_margin
from .devices import get_device, list_devices
from .templates import TEMPLATE_REGISTRY
from .utils import (
    calculate_spacing_from_line_count_with_margins,
    get_clean_spacing_options,
    parse_line_count_spec,
    parse_spacing,
)


class TemplateWizard:
    """Interactive wizard for template creation"""

    def __init__(self):
        self.config = {}
        self.history = []  # For "back" functionality

    def run(self) -> Optional[Dict[str, Any]]:
        """
        Run the interactive wizard.
        Returns config dict or None if cancelled.
        """
        print("\n" + "=" * 70)
        print("TEMPLATE WIZARD")
        print("=" * 70)
        print("\nThis wizard will guide you through creating a custom template.")
        print("Press Ctrl+C at any time to cancel.\n")

        try:
            # Step 1: Device selection
            self._select_device()

            # Step 2: Template type selection
            self._select_template_type()

            # Step 3: Spacing configuration
            self._configure_spacing()

            # Step 4: Margins
            self._configure_margins()

            # Step 5: Template-specific options
            self._configure_template_options()

            # Step 6: Advanced features
            self._configure_advanced_features()

            # Step 7: Review and confirm
            return self._review_and_confirm()

        except KeyboardInterrupt:
            print("\n\n❌ Wizard cancelled.")
            return None
        except EOFError:
            print("\n\n❌ Wizard cancelled.")
            return None

    def _select_device(self):
        """Step 1: Device selection"""
        print("=" * 70)
        print("STEP 1: Device Selection")
        print("=" * 70)

        devices = list_devices()
        default_device = get_default_device()

        print("\nAvailable devices:")
        for i, device_id in enumerate(devices, 1):
            config = get_device(device_id)
            marker = " (default)" if device_id == default_device else ""
            print(f"  {i}. {config['name']}{marker}")
            print(f"     {config['width']}×{config['height']}px @ {config['dpi']}dpi")

        while True:
            if default_device:
                prompt = f"\nSelect device [1-{len(devices)}] (Enter for default): "
            else:
                prompt = f"\nSelect device [1-{len(devices)}]: "

            choice = input(prompt).strip()

            if not choice and default_device:
                self.config["device"] = default_device
                device_config = get_device(default_device)
                print(f"✓ Using {device_config['name']}")
                break

            try:
                idx = int(choice) - 1
                if 0 <= idx < len(devices):
                    self.config["device"] = devices[idx]
                    device_config = get_device(devices[idx])
                    print(f"✓ Selected {device_config['name']}")
                    break
                else:
                    print(f"⚠️  Please enter a number between 1 and {len(devices)}")
            except ValueError:
                print(f"⚠️  Please enter a number between 1 and {len(devices)}")

    def _select_template_type(self):
        """Step 2: Template type selection"""
        print("\n" + "=" * 70)
        print("STEP 2: Template Type")
        print("=" * 70)

        # Group templates by category
        categories = {
            "Basic Writing": ["lined", "dotgrid", "grid"],
            "Specialized": ["manuscript", "french-ruled", "music-staff"],
            "Alternative Grids": ["isometric", "hexgrid"],
            "Multi-Section": ["multi", "hybrid-lined-dotgrid"],
            "Decorative": ["title"],
            "Complex": ["layout"],
        }

        print("\nTemplate categories:")
        all_templates = []
        idx = 1
        for category, templates in categories.items():
            print(f"\n  {category}:")
            for template in templates:
                print(f"    {idx}. {template}")
                all_templates.append(template)
                idx += 1

        while True:
            choice = input(f"\nSelect template type [1-{len(all_templates)}]: ").strip()

            try:
                idx = int(choice) - 1
                if 0 <= idx < len(all_templates):
                    self.config["template"] = all_templates[idx]
                    print(f"✓ Selected {all_templates[idx]}")

                    # Show description
                    self._show_template_description(all_templates[idx])
                    break
                else:
                    print(f"⚠️  Please enter a number between 1 and {len(all_templates)}")
            except ValueError:
                print(f"⚠️  Please enter a number between 1 and {len(all_templates)}")

    def _show_template_description(self, template_type: str):
        """Show helpful description of template type"""
        descriptions = {
            "lined": "Horizontal ruled lines for writing",
            "dotgrid": "Evenly spaced dots in a grid pattern",
            "grid": "Full graph paper with horizontal and vertical lines",
            "manuscript": "4-line handwriting practice (ascender, midline, baseline, descender)",
            "french-ruled": "Seyès ruled paper (French style with major/minor lines)",
            "music-staff": "5-line musical staves for music notation",
            "isometric": "60° isometric grid for 3D sketching",
            "hexgrid": "Hexagonal grid pattern",
            "multi": "Multiple sections in a grid layout",
            "hybrid-lined-dotgrid": "Split page with lined and dotgrid sections",
            "title": "Decorative title page with patterns",
            "layout": "Complex custom layout from JSON file",
        }

        desc = descriptions.get(template_type, "No description available")
        print(f"   → {desc}")

    def _configure_spacing(self):
        """Step 3: Spacing configuration"""
        print("\n" + "=" * 70)
        print("STEP 3: Spacing Configuration")
        print("=" * 70)

        print("\nYou can specify spacing in two ways:")
        print("  1. Distance between lines (e.g., '6mm' or '71px')")
        print("  2. Number of lines to fit (e.g., '40' or '40x30' for grids)")

        print("\nRecommended spacings:")
        print("  • Writing: 6-8mm")
        print("  • Bullet journal: 5mm")
        print("  • Graph paper: 4-5mm")
        print("  • Large handwriting: 10-12mm")

        while True:
            choice = input(
                "\nSpacing mode:\n  1. Distance (mm/px)\n  2. Line count\n\nSelect [1-2]: "
            ).strip()

            if choice == "1":
                self._configure_spacing_distance()
                break
            elif choice == "2":
                self._configure_spacing_linecount()
                break
            else:
                print("⚠️  Please enter 1 or 2")

    def _configure_spacing_distance(self):
        """Configure spacing by distance"""
        device_config = get_device(self.config["device"])
        dpi = device_config["dpi"]

        print("\nEnter spacing (e.g., '6mm', '7.5mm', or '71px')")

        # Show some good options
        print("\nPixel-perfect options for this device:")
        clean_options = get_clean_spacing_options(dpi, min_mm=4, max_mm=12, step_mm=0.5)
        for mm, px in clean_options[:8]:  # Show first 8
            print(f"  • {mm}mm ({px}px)")

        while True:
            spacing = input("\nSpacing: ").strip()

            if not spacing:
                print("⚠️  Please enter a spacing value")
                continue

            try:
                # Validate by parsing
                spacing_px, original_mm, adjusted_mm, was_adjusted, mode = parse_spacing(
                    spacing, dpi, auto_adjust=True
                )

                self.config["spacing"] = spacing
                print(f"✓ Spacing: {spacing}")

                if was_adjusted:
                    print(
                        f"  Note: Will be adjusted to {adjusted_mm:.3f}mm ({int(spacing_px)}px) for pixel-perfect alignment"
                    )

                break
            except Exception as e:
                print(f"⚠️  Invalid spacing: {e}")

    def _configure_spacing_linecount(self):
        """Configure spacing by line count"""
        template_type = self.config["template"]

        if template_type in ["grid", "dotgrid"]:
            print("\nFor grids, enter 'HxV' (e.g., '40x30')")
            print("  H = horizontal lines (rows)")
            print("  V = vertical lines (columns)")
        else:
            print("\nEnter number of lines (e.g., '40')")

        while True:
            lines = input("\nLine count: ").strip()

            if not lines:
                print("⚠️  Please enter a line count")
                continue

            try:
                # Validate by parsing
                h_lines, v_lines = parse_line_count_spec(lines)

                self.config["lines"] = lines
                print(f"✓ Will fit {lines} lines")

                # Calculate what spacing this means
                device_config = get_device(self.config["device"])
                margin_mm = self.config.get("margin_mm", 0)  # Default to 0 for line count mode
                mm2px = device_config["dpi"] / 25.4
                margin_px = round(margin_mm * mm2px)

                spacing_px, _, _ = calculate_spacing_from_line_count_with_margins(
                    device_config["height"], h_lines, margin_px
                )

                spacing_mm = spacing_px / mm2px
                print(f"  → Spacing will be {spacing_px:.1f}px ({spacing_mm:.2f}mm)")

                break
            except ValueError as e:
                print(f"⚠️  {e}")

    def _configure_margins(self):
        """Step 4: Margin configuration"""
        print("\n" + "=" * 70)
        print("STEP 4: Margins")
        print("=" * 70)

        device_config = get_device(self.config["device"])
        default_margin = device_config.get("default_margin_mm", get_default_margin())

        print(f"\nDefault margin for this device: {default_margin}mm")
        print("Margins provide whitespace around the edges.")

        print("\nNote: In line-count mode, margins default to 0mm")
        print("      Use custom margin to add space around fitted content")

        while True:
            choice = input(f"\nMargin in mm [Enter for {default_margin}mm]: ").strip()

            if not choice:
                if "lines" in self.config:
                    # Line count mode defaults to 0
                    self.config["margin_mm"] = 0
                    print("✓ Using 0mm margins (line count mode)")
                else:
                    self.config["margin_mm"] = default_margin
                    print(f"✓ Using {default_margin}mm margins")
                break

            try:
                margin = float(choice)
                if margin < 0:
                    print("⚠️  Margin cannot be negative")
                    continue
                if margin > 50:
                    print("⚠️  That's a very large margin. Are you sure? (max 50mm)")
                    continue

                self.config["margin_mm"] = margin
                print(f"✓ Margins: {margin}mm")
                break
            except ValueError:
                print("⚠️  Please enter a valid number")

    def _configure_template_options(self):
        """Step 5: Template-specific options"""
        template_type = self.config["template"]

        print("\n" + "=" * 70)
        print("STEP 5: Template Options")
        print("=" * 70)

        # Different options based on template type
        if template_type in ["lined", "grid"]:
            self._configure_major_lines()

        if template_type == "lined":
            self._configure_line_numbers()

        if template_type == "grid":
            self._configure_grid_labels()

        if template_type == "dotgrid":
            self._configure_dot_size()

        # ... etc for other template types

    def _configure_major_lines(self):
        """Configure major line emphasis"""
        print("\nMajor lines are thicker lines that help with counting.")

        choice = input("Add major lines? [y/N]: ").strip().lower()

        if choice == "y":
            while True:
                interval = input("Make every Nth line major [5]: ").strip()
                if not interval:
                    self.config["major_every"] = 5
                    print("✓ Major lines every 5")
                    break
                try:
                    interval = int(interval)
                    if interval < 2:
                        print("⚠️  Interval must be at least 2")
                        continue
                    self.config["major_every"] = interval
                    print(f"✓ Major lines every {interval}")
                    break
                except ValueError:
                    print("⚠️  Please enter a valid number")

    def _configure_line_numbers(self):
        """Configure line numbering"""
        print("\nLine numbers appear in the margin.")

        choice = input("Add line numbers? [y/N]: ").strip().lower()

        if choice == "y":
            interval = input("Number every Nth line [5]: ").strip()
            interval = int(interval) if interval else 5

            side = input("Side [left/right] [left]: ").strip().lower()
            side = side if side in ["left", "right"] else "left"

            self.config["line_numbers"] = True
            self.config["line_numbers_interval"] = interval
            self.config["line_numbers_side"] = side
            print(f"✓ Line numbers every {interval} on {side} side")

    def _configure_grid_labels(self):
        """Configure grid cell/axis labels"""
        print("\nGrids can have two types of labels:")
        print("  1. Cell labels (A, B, C... / 1, 2, 3...)")
        print("  2. Axis labels (0, 5, 10... like graph paper)")

        choice = input(
            "\nLabel style:\n  1. Cell labels\n  2. Axis labels\n  3. None\n\nSelect [1-3] [3]: "
        ).strip()

        if choice == "1":
            self.config["cell_labels"] = True
            print("✓ Cell labels enabled")
        elif choice == "2":
            self.config["axis_labels"] = True
            interval = input("Label every Nth line [5]: ").strip()
            self.config["axis_labels_interval"] = int(interval) if interval else 5
            print(f"✓ Axis labels every {self.config['axis_labels_interval']}")

    def _configure_dot_size(self):
        """Configure dot radius"""
        print("\nDot size affects visibility on the page.")
        print("Recommended: 1.0-2.0px")

        choice = input("Dot radius in pixels [1.5]: ").strip()

        if choice:
            try:
                radius = float(choice)
                if radius < 0.5 or radius > 5:
                    print("⚠️  Using default (1.5px). Valid range: 0.5-5.0px")
                    self.config["dot_radius_px"] = 1.5
                else:
                    self.config["dot_radius_px"] = radius
                    print(f"✓ Dot radius: {radius}px")
            except ValueError:
                print("⚠️  Using default (1.5px)")
                self.config["dot_radius_px"] = 1.5
        else:
            self.config["dot_radius_px"] = 1.5

    def _configure_advanced_features(self):
        """Step 6: Advanced features"""
        print("\n" + "=" * 70)
        print("STEP 6: Advanced Features (Optional)")
        print("=" * 70)

        # Headers/Footers
        choice = input("\nAdd header separator? [y/N]: ").strip().lower()
        if choice == "y":
            self._select_separator("header")

        choice = input("Add footer separator? [y/N]: ").strip().lower()
        if choice == "y":
            self._select_separator("footer")

    def _select_separator(self, position: str):
        """Select separator style"""
        styles = ["bold", "double", "wavy", "dashed", "dotted"]

        print(f"\n{position.capitalize()} separator styles:")
        for i, style in enumerate(styles, 1):
            print(f"  {i}. {style}")

        choice = input(f"Select style [1-{len(styles)}]: ").strip()

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(styles):
                self.config[position] = styles[idx]
                print(f"✓ {position.capitalize()} separator: {styles[idx]}")
        except ValueError:
            print(f"⚠️  Invalid choice, skipping {position} separator")

    def _review_and_confirm(self) -> Optional[Dict[str, Any]]:
        """Step 7: Review and confirm"""
        print("\n" + "=" * 70)
        print("STEP 7: Review & Confirm")
        print("=" * 70)

        # Build preview
        print("\nYour template configuration:")
        print("-" * 70)

        device_config = get_device(self.config["device"])
        print(f"\n📱 Device: {device_config['name']}")
        print(
            f"   {device_config['width']}×{device_config['height']}px @ {device_config['dpi']}dpi"
        )

        print(f"\n📝 Template: {self.config['template']}")

        if "lines" in self.config:
            print(f"\n📏 Lines: {self.config['lines']} (spacing calculated automatically)")
        else:
            print(f"\n📏 Spacing: {self.config['spacing']}")

        print(f"\n📐 Margins: {self.config['margin_mm']}mm")

        # Show options
        options = []
        if self.config.get("major_every"):
            options.append(f"Major lines every {self.config['major_every']}")
        if self.config.get("line_numbers"):
            options.append(f"Line numbers (every {self.config['line_numbers_interval']})")
        if self.config.get("cell_labels"):
            options.append("Cell labels")
        if self.config.get("axis_labels"):
            options.append(f"Axis labels (every {self.config['axis_labels_interval']})")
        if self.config.get("dot_radius_px"):
            options.append(f"Dot radius: {self.config['dot_radius_px']}px")
        if self.config.get("header"):
            options.append(f"Header: {self.config['header']}")
        if self.config.get("footer"):
            options.append(f"Footer: {self.config['footer']}")

        if options:
            print("\n✨ Features:")
            for opt in options:
                print(f"   • {opt}")

        print("\n" + "-" * 70)

        # Options
        print("\nWhat would you like to do?")
        print("  1. Generate template now")
        print("  2. Preview full details (dry-run)")
        print("  3. Save as JSON config")
        print("  4. Start over")
        print("  5. Cancel")

        while True:
            choice = input("\nSelect [1-5]: ").strip()

            if choice == "1":
                return self.config
            elif choice == "2":
                self._show_full_preview()
                # Return to menu
                continue
            elif choice == "3":
                saved = self._save_as_json()
                if saved:
                    # Ask if they want to generate now too
                    generate = input("\nGenerate template now? [y/N]: ").strip().lower()
                    if generate == "y":
                        return self.config
                    else:
                        return None
                # Return to menu if save failed
                continue
            elif choice == "4":
                print("\n🔄 Starting over...\n")
                self.config = {}
                return self.run()  # Recursive restart
            elif choice == "5":
                return None
            else:
                print("⚠️  Please enter 1-5")

    def _save_as_json(self) -> bool:
        """Generate and save JSON configuration"""
        print("\n" + "=" * 70)
        print("SAVE AS JSON")
        print("=" * 70)

        # Build JSON config
        json_config = self._build_json_config()

        # Pretty print the JSON
        print("\nGenerated JSON configuration:")
        print("-" * 70)
        print(json.dumps(json_config, indent=2))
        print("-" * 70)

        # Offer to save
        save = input("\nSave this configuration? [Y/n]: ").strip().lower()
        if save == "n":
            return False

        # Get filename
        default_name = self._suggest_filename()
        filename = input(f"\nFilename [{default_name}]: ").strip()
        if not filename:
            filename = default_name

        # Ensure .json extension
        if not filename.endswith(".json"):
            filename += ".json"

        # Check if file exists
        if os.path.exists(filename):
            overwrite = input(f"⚠️  {filename} already exists. Overwrite? [y/N]: ").strip().lower()
            if overwrite != "y":
                print("❌ Save cancelled")
                return False

        # Save file
        try:
            with open(filename, "w") as f:
                json.dump(json_config, f, indent=2)

            print(f"✓ Saved to {filename}")

            # Show how to use it
            print("\n" + "=" * 70)
            print("USAGE")
            print("=" * 70)
            print("\nTo use this configuration:")
            print(f"  eink-template-gen layout --file {filename}")
            print("\nTo preview before generating:")
            print(f"  eink-template-gen layout --file {filename} --dry-run")
            print("=" * 70)

            return True

        except IOError as e:
            print(f"❌ Error saving file: {e}")
            return False

    def _suggest_filename(self) -> str:
        """Suggest a filename based on configuration"""
        template = self.config.get("template", "template")
        device = self.config.get("device", "device")

        # Create descriptive name
        parts = [template, device]

        if "lines" in self.config:
            parts.append(f"{self.config['lines']}-lines")
        elif "spacing" in self.config:
            spacing_clean = self.config["spacing"].replace(".", "_")
            parts.append(spacing_clean)

        if self.config.get("major_every"):
            parts.append(f"major{self.config['major_every']}")

        if self.config.get("line_numbers"):
            parts.append("numbered")

        filename = "-".join(parts) + ".json"
        return filename

    def _build_json_config(self) -> dict:
        """
        Build a JSON configuration from wizard settings.

        The format depends on whether it's a simple template or needs
        a layout structure.
        """
        template_type = self.config["template"]

        # For simple templates, we can use a simpler format
        if template_type in TEMPLATE_REGISTRY and template_type not in ["multi", "layout"]:
            return self._build_simple_json()

        # For multi-cell or complex layouts, use full layout format
        elif template_type == "multi":
            return self._build_multi_json()

        # For already-layout templates, this shouldn't happen
        else:
            return self._build_simple_json()

    def _build_simple_json(self) -> dict:
        """
        Build JSON for a simple single-template page.

        This creates a single-region layout that can be used with
        the 'layout' command.
        """
        config = {
            "device": self.config["device"],
            "auto_adjust_spacing": True,
            "margin_mm": self.config["margin_mm"],
        }

        # Add header/footer
        if self.config.get("header"):
            config["header"] = self.config["header"]
        if self.config.get("footer"):
            config["footer"] = self.config["footer"]

        # Determine spacing
        if "lines" in self.config:
            # Convert line count to actual spacing
            device_config = get_device(self.config["device"])
            margin_mm = self.config["margin_mm"]
            mm2px = device_config["dpi"] / 25.4
            margin_px = round(margin_mm * mm2px)

            h_lines, v_lines = parse_line_count_spec(self.config["lines"])
            spacing_px, _, _ = calculate_spacing_from_line_count_with_margins(
                device_config["height"], h_lines, margin_px
            )
            spacing_mm = spacing_px / mm2px

            config["master_spacing_mm"] = round(spacing_mm, 3)
            config["_note"] = f"Spacing calculated to fit {self.config['lines']} lines"
        else:
            # Use specified spacing
            spacing_str = self.config["spacing"]
            spacing_mm = float(spacing_str.replace("mm", "").replace("px", ""))
            config["master_spacing_mm"] = spacing_mm

        # Build single-region layout
        region = {
            "name": f"{self.config['template'].title()} Page",
            "region_rect": [0, 0, 1.0, 1.0],  # Full page
            "template": self.config["template"],
        }

        # Add template-specific kwargs
        kwargs = {}

        if self.config.get("line_width_px"):
            kwargs["line_width_px"] = self.config["line_width_px"]

        if self.config.get("dot_radius_px"):
            kwargs["dot_radius_px"] = self.config["dot_radius_px"]

        if self.config.get("major_every"):
            kwargs["major_every"] = self.config["major_every"]
            if self.config.get("major_width_add_px"):
                kwargs["major_width_add_px"] = self.config["major_width_add_px"]

        if self.config.get("crosshair_size"):
            kwargs["crosshair_size"] = self.config["crosshair_size"]

        if self.config.get("no_crosshairs"):
            kwargs["no_crosshairs"] = True

        # Line numbers
        if self.config.get("line_numbers"):
            region["line_number_config"] = {
                "side": self.config.get("line_numbers_side", "left"),
                "interval": self.config.get("line_numbers_interval", 5),
                "margin_px": self.config.get("line_numbers_margin_px", 40),
                "font_size": self.config.get("line_numbers_font_size", 18),
                "grey": self.config.get("line_numbers_grey", 8),
            }

        # Cell labels
        if self.config.get("cell_labels"):
            region["cell_label_config"] = {
                "y_axis_side": self.config.get("cell_labels_y_side", "left"),
                "y_axis_padding_px": self.config.get("cell_labels_y_padding_px", 10),
                "x_axis_side": self.config.get("cell_labels_x_side", "bottom"),
                "x_axis_padding_px": self.config.get("cell_labels_x_padding_px", 10),
                "font_size": self.config.get("cell_labels_font_size", 16),
                "grey": self.config.get("cell_labels_grey", 10),
            }

        # Axis labels
        if self.config.get("axis_labels"):
            region["axis_label_config"] = {
                "origin": self.config.get("axis_labels_origin", "topLeft"),
                "interval": self.config.get("axis_labels_interval", 5),
                "y_axis_side": self.config.get("axis_labels_y_side", "left"),
                "y_axis_padding_px": self.config.get("axis_labels_y_padding_px", 10),
                "x_axis_side": self.config.get("axis_labels_x_side", "bottom"),
                "x_axis_padding_px": self.config.get("axis_labels_x_padding_px", 10),
                "font_size": self.config.get("axis_labels_font_size", 16),
                "grey": self.config.get("axis_labels_grey", 10),
            }

        if kwargs:
            region["kwargs"] = kwargs

        config["page_layout"] = [region]

        return config

    def _build_multi_json(self) -> dict:
        """
        Build JSON for multi-cell grid layout.

        This is more complex as we need to calculate region positions.
        """
        rows = self.config.get("rows", 2)
        cols = self.config.get("columns", 2)

        config = {
            "device": self.config["device"],
            "auto_adjust_spacing": True,
            "margin_mm": self.config["margin_mm"],
        }

        # Determine spacing
        if "lines" in self.config:
            # This is complex for multi-cell - would need to fit lines in each cell
            # For now, fall back to a reasonable default
            config["master_spacing_mm"] = 6
            config["_note"] = "Line count mode not fully supported for multi-cell in JSON export"
        else:
            spacing_str = self.config["spacing"]
            spacing_mm = float(spacing_str.replace("mm", "").replace("px", ""))
            config["master_spacing_mm"] = spacing_mm

        # Add header/footer
        if self.config.get("header"):
            config["header"] = self.config["header"]
        if self.config.get("footer"):
            config["footer"] = self.config["footer"]

        # Calculate region positions
        # Account for gaps
        gap_ratio = 0.01  # 1% gap between cells (simplified)

        cell_width = (1.0 - (cols - 1) * gap_ratio) / cols
        cell_height = (1.0 - (rows - 1) * gap_ratio) / rows

        regions = []

        for r in range(rows):
            for c in range(cols):
                x_start = c * (cell_width + gap_ratio)
                y_start = r * (cell_height + gap_ratio)

                region = {
                    "name": f"Cell R{r+1}C{c+1}",
                    "region_rect": [x_start, y_start, cell_width, cell_height],
                    "template": self.config["template"],
                }

                # Add kwargs (same for all cells in wizard's case)
                kwargs = {}

                if self.config.get("line_width_px"):
                    kwargs["line_width_px"] = self.config["line_width_px"]

                if self.config.get("dot_radius_px"):
                    kwargs["dot_radius_px"] = self.config["dot_radius_px"]

                if self.config.get("major_every"):
                    kwargs["major_every"] = self.config["major_every"]

                if kwargs:
                    region["kwargs"] = kwargs

                regions.append(region)

        config["page_layout"] = regions

        return config

    def _show_full_preview(self):
        """Show detailed preview"""
        # This would call the same preview logic as --dry-run
        # For now, just show what we have
        print("\n" + "=" * 70)
        print("DETAILED PREVIEW")
        print("=" * 70)
        print("\nThis would show the full dry-run preview...")
        print("(Implementation would call _build_preview_summary)")
        input("\nPress Enter to continue...")

    def _save_as_command(self):
        """Generate and show the equivalent CLI command"""
        print("\n" + "=" * 70)
        print("EQUIVALENT COMMAND")
        print("=" * 70)

        cmd_parts = ["eink-template-gen", self.config["template"]]

        # Add flags
        if "spacing" in self.config:
            cmd_parts.append(f"--spacing {self.config['spacing']}")
        elif "lines" in self.config:
            cmd_parts.append(f"--lines {self.config['lines']}")

        cmd_parts.append(f"--device {self.config['device']}")
        cmd_parts.append(f"--margin {self.config['margin_mm']}")

        if self.config.get("major_every"):
            cmd_parts.append(f"--major-every {self.config['major_every']}")

        if self.config.get("line_numbers"):
            cmd_parts.append(f"--line-numbers {self.config['line_numbers_interval']}")
            if self.config.get("line_numbers_side") != "left":
                cmd_parts.append(f"--line-numbers-side {self.config['line_numbers_side']}")

        if self.config.get("cell_labels"):
            cmd_parts.append("--cell-labels")

        if self.config.get("axis_labels"):
            cmd_parts.append("--axis-labels")
            if self.config.get("axis_labels_interval") != 5:
                cmd_parts.append(f"--axis-labels-interval {self.config['axis_labels_interval']}")

        if self.config.get("dot_radius_px") and self.config["dot_radius_px"] != 1.5:
            cmd_parts.append(f"--dot-radius-px {self.config['dot_radius_px']}")

        if self.config.get("header"):
            cmd_parts.append(f"--header {self.config['header']}")

        if self.config.get("footer"):
            cmd_parts.append(f"--footer {self.config['footer']}")

        cmd = " ".join(cmd_parts)

        print(f"\n{cmd}\n")
        print("You can copy this command to use later or in scripts.")

        # Offer to save to file
        save = input("\nSave to file? [y/N]: ").strip().lower()
        if save == "y":
            filename = input("Filename [template-command.sh]: ").strip()
            if not filename:
                filename = "template-command.sh"

            with open(filename, "w") as f:
                f.write("#!/bin/bash\n")
                f.write("# Generated by eink-template-gen wizard\n")
                f.write(f"# {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(cmd + "\n")

            os.chmod(filename, 0o755)  # Make executable
            print(f"✓ Saved to {filename}")

        input("\nPress Enter to continue...")

    def _build_args_from_config(self) -> argparse.Namespace:
        """Convert wizard config to argparse Namespace for compatibility"""
        # This allows us to use existing generation functions
        args_dict = {
            "command": self.config["template"],
            "device": self.config["device"],
            "margin": self.config.get("margin_mm"),
            "output_dir": "out",
            "filename": None,
            "true_scale": False,
            "enforce_margins": False,
            "header": self.config.get("header"),
            "footer": self.config.get("footer"),
        }

        # Add spacing
        if "lines" in self.config:
            args_dict["lines"] = self.config["lines"]
            args_dict["spacing"] = "6"  # Dummy value, won't be used
        else:
            args_dict["spacing"] = self.config["spacing"]
            args_dict["lines"] = None

        # Add template-specific args
        if self.config.get("major_every"):
            args_dict["major_every"] = self.config["major_every"]
            args_dict["major_width_add_px"] = 1.5

        if self.config.get("line_numbers"):
            args_dict["line_numbers_interval"] = self.config["line_numbers_interval"]
            args_dict["line_numbers_side"] = self.config.get("line_numbers_side", "left")
            args_dict["line_numbers_margin_px"] = 40
            args_dict["line_numbers_font_size"] = 18
            args_dict["line_numbers_grey"] = 8

        if self.config.get("cell_labels"):
            args_dict["cell_labels"] = True
            args_dict["cell_labels_y_side"] = "left"
            args_dict["cell_labels_y_padding_px"] = 10
            args_dict["cell_labels_x_side"] = "bottom"
            args_dict["cell_labels_x_padding_px"] = 10
            args_dict["cell_labels_font_size"] = 16
            args_dict["cell_labels_grey"] = 10

        if self.config.get("axis_labels"):
            args_dict["axis_labels"] = True
            args_dict["axis_labels_origin"] = "topLeft"
            args_dict["axis_labels_interval"] = self.config.get("axis_labels_interval", 5)
            args_dict["axis_labels_y_side"] = "left"
            args_dict["axis_labels_y_padding_px"] = 10
            args_dict["axis_labels_x_side"] = "bottom"
            args_dict["axis_labels_x_padding_px"] = 10
            args_dict["axis_labels_font_size"] = 16
            args_dict["axis_labels_grey"] = 10

        if self.config.get("dot_radius_px"):
            args_dict["dot_radius_px"] = self.config["dot_radius_px"]

        # Set template_type for single templates
        if self.config["template"] in TEMPLATE_REGISTRY:
            args_dict["template_type"] = self.config["template"]

        # Add default values for other expected args
        args_dict["line_width_px"] = 0.5
        args_dict["crosshair_size"] = 4
        args_dict["no_crosshairs"] = False

        return argparse.Namespace(**args_dict)


def run_wizard_and_generate():
    """Run the wizard and generate the template"""
    wizard = TemplateWizard()
    config = wizard.run()

    if not config:
        print("\n❌ Template generation cancelled.")
        return

    # Convert wizard config to args
    args = wizard._build_args_from_config()

    # Generate using existing handlers
    print("\n" + "=" * 70)
    print("GENERATING TEMPLATE")
    print("=" * 70)

    try:
        if args.command in TEMPLATE_REGISTRY:
            handle_single_template_generation(args)
        elif args.command == "multi":
            handle_multi_template_generation(args)
        elif args.command == "title":
            handle_cover_generation(args)
        elif args.command == "layout":
            handle_json_generation(args)
        else:
            print(f"❌ Unknown template type: {args.command}")
    except Exception as e:
        print(f"\n❌ Error generating template: {e}")
        import traceback

        traceback.print_exc()
