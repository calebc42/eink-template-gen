import argparse
import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from .actions import (
    _build_preview_summary,
    handle_cover_generation,
    handle_multi_template_generation,
    handle_single_template_generation,
)
from .config import get_default_device, get_default_margin
from .devices import get_device, list_devices
from .templates import TEMPLATE_REGISTRY, AlignmentUnits
from .utils import (
    SpacingResult,
    calculate_page_margins,
    calculate_spacing_from_line_count,
    calculate_spacing_from_line_count_with_margins,
    get_clean_spacing_options,
    parse_line_count_spec,
    parse_spacing,
)


class TemplateWizard:
    """Interactive wizard for template creation"""

    # --- Custom exception for "back" signal ---
    class BackSignal(Exception):
        """Signal to go back one step."""

    def __init__(self):
        self.config = {}
        # self.history is no longer needed, the state machine handles it

    # --- Helper for all input prompts ---
    def _prompt(self, text: str, default: Optional[str] = None) -> str:
        """
        Wrapper for input() that handles 'back' and 'default' logic.
        Raises BackSignal if the user wants to go back.
        """
        if default is not None:
            prompt = f"\n{text} [{default}]: "
        else:
            prompt = f"\n{text}: "

        choice = input(prompt).strip()

        if choice.lower() in ["b", "back"]:
            print("⬅️  Going back...")
            raise self.BackSignal()

        if not choice and default is not None:
            return default

        return choice

    # --- Main run method is now a state machine ---
    def run(self) -> Optional[Dict[str, Any]]:
        """
        Run the interactive wizard state machine.
        Returns config dict or None if cancelled.
        """
        print("\n" + "=" * 70)
        print("TEMPLATE WIZARD")
        print("=" * 70)
        print("\nThis wizard will guide you through creating a custom template.")
        print("Press Ctrl+C at any time to cancel.")
        print("Type 'back' or 'b' at any prompt to go to the previous step.")

        # Define the steps of the wizard
        steps = [
            self._select_device,
            self._select_template_type,
            self._configure_spacing,
            self._configure_margins,
            self._configure_template_options,
            self._configure_advanced_features,
            self._review_and_confirm,
        ]
        current_step = 0

        while 0 <= current_step < len(steps):
            step_function = steps[current_step]

            try:
                # Each step function now returns a status:
                # "next", "back", "cancel", "done", or "restart"
                result = step_function()

                if result == "back":
                    if current_step > 0:
                        current_step -= 1
                    # Stay at step 0 if already there
                elif result == "cancel":
                    print("\n\n Wizard cancelled.")
                    return None
                elif result == "done":
                    # Final review step is done, return the config
                    return self.config
                elif result == "restart":
                    # Final review wants to start over
                    print("\n🔄 Starting over...\n")
                    current_step = 0
                    self.config = {}
                else:
                    # Default is "next"
                    current_step += 1

            except (KeyboardInterrupt, EOFError):
                print("\n\n Wizard cancelled.")
                return None
            except self.BackSignal:
                # User typed "back", go to previous step
                if current_step > 0:
                    current_step -= 1
                # Stay at step 0 if already there

        return None  # Wizard exited loop without "done"

    def _select_device(self):
        """Step 1: Device selection"""
        print("\n" + "=" * 70)
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
                prompt_text = f"Select device [1-{len(devices)}] (Enter for default)"
                choice = self._prompt(prompt_text, default=default_device)
                if choice == default_device:
                    self.config["device"] = default_device
                    device_config = get_device(default_device)
                    print(f"✓ Using {device_config['name']}")
                    return "next"
            else:
                prompt_text = f"Select device [1-{len(devices)}]"
                choice = self._prompt(prompt_text)

            try:
                idx = int(choice) - 1
                if 0 <= idx < len(devices):
                    self.config["device"] = devices[idx]
                    device_config = get_device(devices[idx])
                    print(f"✓ Selected {device_config['name']}")
                    return "next"
                else:
                    print(f"  Please enter a number between 1 and {len(devices)}")
            except ValueError:
                print(f" Please enter a number between 1 and {len(devices)}")

    def _select_template_type(self):
        """Step 2: Template type selection"""
        print("\n" + "=" * 70)
        print("STEP 2: Template Type")
        print("=" * 70)

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
            choice = self._prompt(f"Select template type [1-{len(all_templates)}]")
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(all_templates):
                    selected_template = all_templates[idx]

                    # --- NEW: Handle special 'layout' case ---
                    if selected_template == "layout":
                        print("\n" + "-" * 70)
                        print(" The 'layout' command is for generating templates from an")
                        print("   existing JSON file. This wizard helps you create new")
                        print("   templates or save them as JSON files.")
                        print("\n   To use an existing JSON file, please run:")
                        print("   eink-template-gen layout --file your_file.json")
                        print("-" * 70)
                        return "cancel"

                    self.config["template"] = selected_template
                    print(f"✓ Selected {selected_template}")
                    self._show_template_description(selected_template)
                    return "next"
                else:
                    print(f" Please enter a number between 1 and {len(all_templates)}")
            except ValueError:
                print(f"  Please enter a number between 1 and {len(all_templates)}")

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
            "multi": "Multiple sections in a grid layout (e.g., 2x2)",
            "hybrid-lined-dotgrid": "Split page with lined and dotgrid sections",
            "title": "Decorative title page with patterns",
            "layout": "Complex custom layout from JSON file (not used in wizard)",
        }
        desc = descriptions.get(template_type, "No description available")
        print(f"   → {desc}")

    def _configure_spacing(self):
        """Step 3: Spacing configuration"""
        print("\n" + "=" * 70)
        print("STEP 3: Spacing Configuration")
        print("=" * 70)

        # Skip this step for 'multi' and 'title' which have their own spacing logic
        template_type = self.config["template"]
        if template_type in ["multi", "title", "hybrid-lined-dotgrid"]:
            print(f"ℹ:  Spacing for '{template_type}' will be configured in the next step.")
            return "next"

        print("\nYou can specify spacing in two ways:")
        print("  1. Distance between lines (e.g., '6mm' or '71px')")
        print("  2. Number of lines to fit (e.g., '40' or '40x30' for grids)")

        print("\nRecommended spacings:")
        print("  • Writing: 6-8mm")
        print("  • Bullet journal: 5mm")

        while True:
            choice = self._prompt(
                "Spacing mode:\n  1. Distance (mm/px)\n  2. Line count\n\nSelect [1-2]", default="1"
            )

            if choice == "1":
                return self._configure_spacing_distance()
            elif choice == "2":
                return self._configure_spacing_linecount()
            else:
                print("  Please enter 1 or 2")

    def _configure_spacing_distance(self):
        """Configure spacing by distance"""
        device_config = get_device(self.config["device"])
        dpi = device_config["dpi"]

        print("\nEnter spacing (e.g., '6mm', '7.5mm', or '71px')")
        print("\nPixel-perfect options for this device:")
        clean_options = get_clean_spacing_options(dpi, min_mm=4, max_mm=12, step_mm=0.5)
        for mm, px in clean_options[:8]:  # Show first 8
            print(f"  • {mm}mm ({px}px)")

        while True:
            spacing = self._prompt("Spacing", default="6mm")
            if not spacing:
                print(" Please enter a spacing value")
                continue

            try:
                spacing_px, original_mm, adjusted_mm, was_adjusted, mode = parse_spacing(
                    spacing, dpi, auto_adjust=True
                )

                self.config["spacing"] = spacing
                print(f"✓ Spacing: {spacing}")

                if was_adjusted:
                    print(
                        f"  Note: Will be adjusted to {adjusted_mm:.3f}mm ({int(spacing_px)}px) for pixel-perfect alignment"
                    )

                return "next"
            except Exception as e:
                print(f" Invalid spacing: {e}")

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
            lines = self._prompt("Line count")
            if not lines:
                print("  Please enter a line count")
                continue

            try:
                h_lines, v_lines = parse_line_count_spec(lines)

                self.config["lines"] = lines
                print(f"✓ Will fit {lines} lines")

                device_config = get_device(self.config["device"])
                margin_mm = self.config.get("margin_mm", 0)
                mm2px = device_config["dpi"] / 25.4
                margin_px = round(margin_mm * mm2px)

                spacing_px, _, _ = calculate_spacing_from_line_count_with_margins(
                    device_config["height"], h_lines, margin_px
                )

                spacing_mm = spacing_px / mm2px
                print(f"  → Spacing will be {spacing_px:.1f}px ({spacing_mm:.2f}mm)")

                return "next"
            except ValueError as e:
                print(f"  {e}")

    def _configure_margins(self):
        """Step 4: Margin configuration"""
        print("\n" + "=" * 70)
        print("STEP 4: Margins")
        print("=" * 70)

        device_config = get_device(self.config["device"])
        default_margin = device_config.get("default_margin_mm", get_default_margin())

        print(f"\nDefault margin for this device: {default_margin}mm")
        print("Margins provide whitespace around the edges.")

        if "lines" in self.config:
            print("\nNote: In line-count mode, margins default to 0mm.")
            print("      Use custom margin to add space *around* your fitted content.")
            default_text = "0"
        else:
            default_text = str(default_margin)

        while True:
            choice = self._prompt("Margin in mm", default=default_text)

            try:
                margin = float(choice)
                if margin < 0:
                    print(" Margin cannot be negative")
                    continue
                if margin > 50:
                    print("  That's a very large margin. Are you sure? (max 50mm)")
                    continue

                self.config["margin_mm"] = margin
                print(f"✓ Margins: {margin}mm")
                return "next"
            except ValueError:
                print("  Please enter a valid number")

    # --- REFACTORED: Expanded template options ---
    def _configure_template_options(self):
        """Step 5: Template-specific options"""
        template_type = self.config["template"]

        print("\n" + "=" * 70)
        print(f"STEP 5: Options for '{template_type}'")
        print("=" * 70)

        # Call specific configuration functions
        if template_type in ["lined", "grid"]:
            self._configure_major_lines()

        if template_type == "lined":
            self._configure_line_numbers()

        if template_type == "grid":
            self._configure_grid_labels()

        if template_type == "dotgrid":
            self._configure_dot_size()
            self._configure_major_lines()  # Dotgrids can also have major lines (crosshairs)

        if template_type == "manuscript":
            self._configure_manuscript_options()

        if template_type == "music-staff":
            self._configure_music_options()

        if template_type == "multi":
            return self._configure_multi_options()  # Returns its own status

        if template_type == "hybrid-lined-dotgrid":
            self._configure_hybrid_options()

        # ... etc for other template types

        if template_type == "title":
            print("ℹ: Title page options (text, frame, etc.) are not yet")
            print("   supported in the wizard. You can add them in the saved JSON.")

        return "next"

    def _configure_major_lines(self):
        """Configure major line emphasis"""
        print("\nMajor lines are thicker lines that help with counting.")
        choice = self._prompt("Add major lines?", default="N").lower()

        if choice == "y":
            while True:
                interval_str = self._prompt("Make every Nth line major", default="5")
                try:
                    interval = int(interval_str)
                    if interval < 2:
                        print("  Interval must be at least 2")
                        continue
                    self.config["major_every"] = interval
                    print(f"✓ Major lines every {interval}")
                    break
                except ValueError:
                    print("  Please enter a valid number")

    def _configure_line_numbers(self):
        """Configure line numbering"""
        print("\nLine numbers appear in the margin.")
        choice = self._prompt("Add line numbers?", default="N").lower()

        if choice == "y":
            interval_str = self._prompt("Number every Nth line", default="5")
            interval = int(interval_str) if interval_str.isdigit() else 5

            side = self._prompt("Side [left/right]", default="left").lower()
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

        choice = self._prompt(
            "Label style:\n  1. Cell labels\n  2. Axis labels\n  3. None\n\nSelect [1-3]",
            default="3",
        )

        if choice == "1":
            self.config["cell_labels"] = True
            print("✓ Cell labels enabled")
        elif choice == "2":
            self.config["axis_labels"] = True
            interval_str = self._prompt("Label every Nth line", default="5")
            self.config["axis_labels_interval"] = int(interval_str) if interval_str.isdigit() else 5
            print(f"✓ Axis labels every {self.config['axis_labels_interval']}")

    def _configure_dot_size(self):
        """Configure dot radius"""
        print("\nDot size affects visibility on the page. Recommended: 1.0-2.0px")
        choice = self._prompt("Dot radius in pixels", default="1.5")

        try:
            radius = float(choice)
            if 0.5 <= radius <= 5.0:
                self.config["dot_radius_px"] = radius
                print(f"✓ Dot radius: {radius}px")
            else:
                print("  Invalid range. Using default (1.5px).")
                self.config["dot_radius_px"] = 1.5
        except ValueError:
            print("  Invalid number. Using default (1.5px).")
            self.config["dot_radius_px"] = 1.5

    def _configure_manuscript_options(self):
        """Configure manuscript (4-line) options"""
        print("\nManuscript paper has 3 lines per set (ascender, midline, baseline).")
        print("The spacing you chose (e.g., 8mm) is for the *entire set*.")

        style = self._prompt("Midline style [dashed/dotted]", default="dashed").lower()
        self.config["midline_style"] = style if style in ["dashed", "dotted"] else "dashed"
        print(f"✓ Midline style: {self.config['midline_style']}")

    def _configure_music_options(self):
        """Configure music staff options"""
        print("\nMusic staves are 5-line groups.")

        # Spacing (line-to-line)
        spacing_str = self._prompt("Spacing between lines in a staff (e.g., 2mm)", default="2mm")
        self.config["spacing"] = spacing_str
        print(f"✓ Staff line spacing: {spacing_str}")

        # Gap (staff-to-staff)
        gap_str = self._prompt("Gap between staves (e.g., 10mm)", default="10mm")
        try:
            self.config["staff_gap_mm"] = float(gap_str.replace("mm", ""))
            print(f"✓ Staff gap: {self.config['staff_gap_mm']}mm")
        except ValueError:
            self.config["staff_gap_mm"] = 10.0
            print("  Invalid number. Using default (10mm).")

    def _configure_hybrid_options(self):
        """Configure hybrid template options"""
        print("\nHybrid template is split 60% lined, 40% dotgrid by default.")

        spacing_str = self._prompt("Spacing for both sides (e.g., 6mm)", default="6mm")
        self.config["spacing"] = spacing_str
        print(f"✓ Spacing: {spacing_str}")

        ratio_str = self._prompt("Split ratio (0.1 to 0.9)", default="0.6")
        try:
            ratio = float(ratio_str)
            if 0.1 <= ratio <= 0.9:
                self.config["split_ratio"] = ratio
                print(f"✓ Split ratio: {ratio*100:.0f}% / {(1-ratio)*100:.0f}%")
            else:
                self.config["split_ratio"] = 0.6
                print("  Invalid range. Using default (0.6).")
        except ValueError:
            self.config["split_ratio"] = 0.6
            print("  Invalid number. Using default (0.6).")

    def _configure_multi_options(self):
        """Configure multi-cell grid options"""
        print("\nConfigure your multi-cell grid layout.")

        # Rows
        while True:
            rows_str = self._prompt("Number of rows", default="2")
            try:
                self.config["rows"] = int(rows_str)
                if self.config["rows"] < 1:
                    print("  Must be at least 1 row")
                    continue
                break
            except ValueError:
                print("  Please enter a valid number")

        # Columns
        while True:
            cols_str = self._prompt("Number of columns", default="2")
            try:
                self.config["columns"] = int(cols_str)
                if self.config["columns"] < 1:
                    print("  Must be at least 1 column")
                    continue
                break
            except ValueError:
                print("  Please enter a valid number")

        print(f"✓ Grid layout: {self.config['rows']} rows × {self.config['columns']} columns")

        # Spacing
        spacing_str = self._prompt("Global spacing for all cells (e.g., 5mm)", default="5mm")
        self.config["spacing"] = spacing_str
        print(f"✓ Global spacing: {spacing_str}")

        # Uniform or Mixed
        print("\nAre all cells the same template type?")
        choice = self._prompt(
            "  1. Yes (Uniform grid)\n  2. No (Mixed grid)\n\nSelect [1-2]", default="1"
        )

        if choice == "2":
            # Mixed grid
            num_cells = self.config["rows"] * self.config["columns"]
            print(f"\nPlease enter {num_cells} template types, separated by commas.")
            print("Example: lined,grid,dotgrid,manuscript")
            print("Valid types: lined, dotgrid, grid, manuscript, hexgrid, isometric, blank")

            while True:
                types_str = self._prompt(f"Enter {num_cells} types")
                cell_types = [t.strip() for t in types_str.split(",")]
                if len(cell_types) != num_cells:
                    print(f" Expected {num_cells} types, but got {len(cell_types)}")
                    continue
                # You could add validation for each type here
                self.config["cell_types"] = types_str
                print("✓ Cell types set")
                break
        else:
            # Uniform grid
            print("\nSelect the template type for all cells:")
            valid_types = [
                "lined",
                "dotgrid",
                "grid",
                "manuscript",
                "hexgrid",
                "isometric",
                "blank",
            ]
            for i, t in enumerate(valid_types, 1):
                print(f"  {i}. {t}")

            while True:
                type_choice = self._prompt(f"Select [1-{len(valid_types)}]", default="1")
                try:
                    idx = int(type_choice) - 1
                    if 0 <= idx < len(valid_types):
                        self.config["uniform_template"] = valid_types[idx]
                        print(f"✓ All cells will be '{valid_types[idx]}'")
                        break
                    else:
                        print("  Invalid selection")
                except ValueError:
                    print("  Please enter a number")

        return "next"

    def _configure_advanced_features(self):
        """Step 6: Advanced features"""
        print("\n" + "=" * 70)
        print("STEP 6: Advanced Features (Optional)")
        print("=" * 70)

        choice = self._prompt("Add header separator?", default="N").lower()
        if choice == "y":
            self._select_separator("header")

        choice = self._prompt("Add footer separator?", default="N").lower()
        if choice == "y":
            self._select_separator("footer")

        return "next"

    def _select_separator(self, position: str):
        """Select separator style"""
        styles = ["bold", "double", "wavy", "dashed", "dotted"]
        print(f"\n{position.capitalize()} separator styles:")
        for i, style in enumerate(styles, 1):
            print(f"  {i}. {style}")

        choice = self._prompt(f"Select style [1-{len(styles)}]", default="1")
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(styles):
                self.config[position] = styles[idx]
                print(f"✓ {position.capitalize()} separator: {styles[idx]}")
        except ValueError:
            print(f" Invalid choice, skipping {position} separator")

    # --- REFACTORED: Updated review menu ---
    def _review_and_confirm(self) -> Optional[Dict[str, Any]]:
        """Step 7: Review and confirm"""
        print("\n" + "=" * 70)
        print("STEP 7: Review & Confirm")
        print("=" * 70)
        print("\nYour template configuration:")
        print("-" * 70)

        try:
            device_config = get_device(self.config["device"])
            print(f" Device: {device_config['name']}")
            print(
                f"   {device_config['width']}×{device_config['height']}px @ {device_config['dpi']}dpi"
            )
            print(f" Template: {self.config['template']}")
            if "lines" in self.config:
                print(f" Lines: {self.config['lines']} (spacing calculated automatically)")
            elif "spacing" in self.config:
                print(f" Spacing: {self.config['spacing']}")
            print(f" Margins: {self.config['margin_mm']}mm")

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
            if self.config.get("rows"):
                options.append(f"Grid: {self.config['rows']}x{self.config['columns']}")
            if self.config.get("uniform_template"):
                options.append(f"Cell Type: {self.config['uniform_template']} (uniform)")
            if self.config.get("cell_types"):
                options.append(f"Cell Types: {self.config['cell_types']} (mixed)")

            if options:
                print("\n Features:")
                for opt in options:
                    print(f"   • {opt}")
        except Exception as e:
            print(f"Error building preview: {e}. Configuration might be incomplete.")
            print(f"   Current config: {self.config}")

        print("\n" + "-" * 70)
        print("\nWhat would you like to do?")
        print("  1. Generate template now")
        print("  2. Preview full details (dry-run)")
        print("  3. Save as JSON config file")
        print("  4. Show as CLI command")
        print("  5. Start over")
        print("  6. Cancel")

        while True:
            choice = self._prompt("Select [1-6]", default="1")
            if choice == "1":
                return "done"  # Signals run() to return config
            elif choice == "2":
                self._show_full_preview()
                continue  # Go back to the review menu
            elif choice == "3":
                saved = self._save_as_json()
                if saved:
                    gen_now = self._prompt("Generate template now?", default="N").lower()
                    if gen_now == "y":
                        return "done"
                    return "cancel"  # User saved, but doesn't want to generate
                continue  # Go back to review menu if save failed
            elif choice == "4":
                self._save_as_command()
                continue  # Go back to the review menu
            elif choice == "5":
                return "restart"
            elif choice == "6":
                return "cancel"
            else:
                print("Please enter 1-6")

    def _save_as_json(self) -> bool:
        """Generate and save JSON configuration"""
        print("\n" + "=" * 70)
        print("SAVE AS JSON")
        print("=" * 70)

        json_config = self._build_json_config()
        print("\nGenerated JSON configuration:")
        print("-" * 70)
        print(json.dumps(json_config, indent=2))
        print("-" * 70)

        save = self._prompt("Save this configuration?", default="Y").lower()
        if save == "n":
            return False

        default_name = self._suggest_filename()
        filename = self._prompt("Filename", default=default_name)
        if not filename.endswith(".json"):
            filename += ".json"

        if os.path.exists(filename):
            overwrite = self._prompt(f"{filename} already exists. Overwrite?", default="N").lower()
            if overwrite != "y":
                print("Save cancelled")
                return False

        try:
            with open(filename, "w") as f:
                json.dump(json_config, f, indent=2)
            print(f"✓ Saved to {filename}")
            print("\nTo use this configuration, run:")
            print(f"  eink-template-gen layout --file {filename}")
            return True
        except IOError as e:
            print(f"Error saving file: {e}")
            return False

    def _suggest_filename(self) -> str:
        """Suggest a filename based on configuration"""
        template = self.config.get("template", "template")
        device = self.config.get("device", "device")
        parts = [template, device]

        if "lines" in self.config:
            parts.append(f"{self.config['lines']}-lines")
        elif "spacing" in self.config:
            spacing_clean = self.config["spacing"].replace(".", "_").replace(" ", "")
            parts.append(spacing_clean)
        if self.config.get("major_every"):
            parts.append(f"major{self.config['major_every']}")
        if self.config.get("line_numbers"):
            parts.append("numbered")

        return "-".join(parts) + ".json"

    def _build_json_config(self) -> dict:
        """
        Build a JSON configuration from wizard settings.
        This now converts all wizard types to the 'layout' format.
        """
        config = {
            "device": self.config["device"],
            "auto_adjust_spacing": True,
            "margin_mm": self.config["margin_mm"],
        }

        if self.config.get("header"):
            config["header"] = self.config["header"]
        if self.config.get("footer"):
            config["footer"] = self.config["footer"]

        if "lines" in self.config:
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
        elif "spacing" in self.config:
            spacing_str = self.config["spacing"]
            try:
                spacing_mm = float(spacing_str.replace("mm", "").replace("px", ""))
                config["master_spacing_mm"] = spacing_mm
            except ValueError:
                config["master_spacing_mm"] = 6  # fallback
        else:
            config["master_spacing_mm"] = 6  # fallback

        # Build layout based on template type
        template_type = self.config["template"]

        if template_type == "multi":
            config["page_layout"] = self._build_multi_json_layout()
        elif template_type == "hybrid-lined-dotgrid":
            config["page_layout"] = self._build_hybrid_json_layout()
        else:
            # All other types are a single full-page region
            config["page_layout"] = self._build_simple_json_layout()

        return config

    def _build_simple_json_layout(self) -> List[Dict]:
        """Builds a page_layout array for a single full-page region"""
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
        if self.config.get("midline_style"):
            kwargs["midline_style"] = self.config["midline_style"]
        if self.config.get("staff_gap_mm"):
            kwargs["staff_gap_mm"] = self.config["staff_gap_mm"]

        if kwargs:
            region["kwargs"] = kwargs

        # Add decorations
        if self.config.get("line_numbers"):
            region["line_number_config"] = {
                "side": self.config.get("line_numbers_side", "left"),
                "interval": self.config.get("line_numbers_interval", 5),
            }
        if self.config.get("cell_labels"):
            region["cell_label_config"] = {}  # Use defaults
        if self.config.get("axis_labels"):
            region["axis_label_config"] = {
                "interval": self.config.get("axis_labels_interval", 5),
            }

        return [region]

    def _build_hybrid_json_layout(self) -> List[Dict]:
        """Builds a page_layout array for a hybrid template"""
        ratio = self.config.get("split_ratio", 0.6)

        # Simplified JSON for hybrid doesn't exist, build a 2-region layout
        # This requires more complex logic to account for pixel-based gaps
        # For the wizard, we'll create a simple 2-column layout

        left_width = ratio - 0.01  # Small gap
        right_width = 1.0 - ratio - 0.01  # Small gap

        region_left = {
            "name": "Lined Section",
            "region_rect": [0, 0, left_width, 1.0],
            "template": "lined",
            "kwargs": {"line_width_px": 0.5},
        }
        region_right = {
            "name": "Dotgrid Section",
            "region_rect": [ratio + 0.01, 0, right_width, 1.0],
            "template": "dotgrid",
            "kwargs": {"dot_radius_px": 1.5},
        }
        return [region_left, region_right]

    def _build_multi_json_layout(self) -> List[Dict]:
        """Builds a page_layout array for a multi-cell grid"""
        rows = self.config.get("rows", 2)
        cols = self.config.get("columns", 2)

        # Simplified gap calculation for JSON
        gap_ratio = 0.01  # 1% gap
        cell_width = (1.0 - (cols - 1) * gap_ratio) / cols
        cell_height = (1.0 - (rows - 1) * gap_ratio) / rows

        regions = []
        cell_types_str = self.config.get("cell_types")
        cell_types = [t.strip() for t in cell_types_str.split(",")] if cell_types_str else []
        uniform_type = self.config.get("uniform_template", "blank")

        idx = 0
        for r in range(rows):
            for c in range(cols):
                x_start = c * (cell_width + gap_ratio)
                y_start = r * (cell_height + gap_ratio)

                cell_type = uniform_type
                if cell_types and idx < len(cell_types):
                    cell_type = cell_types[idx]

                region = {
                    "name": f"Cell R{r+1}C{c+1}",
                    "region_rect": [
                        round(x_start, 4),
                        round(y_start, 4),
                        round(cell_width, 4),
                        round(cell_height, 4),
                    ],
                    "template": cell_type,
                }

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
                idx += 1

        return regions

    # --- Stubbed Functions ---

    def _show_full_preview(self):
        """Show detailed preview by building args and calling summary"""
        print("\n" + "=" * 70)
        print("DETAILED PREVIEW (Dry-Run)")
        print("=" * 70)

        try:
            # Build the mock 'args' object
            args = self._build_args_from_config()

            # Build the mock 'context' object
            # This requires recalculating spacing and margins
            context = {}
            device_config = get_device(args.device)
            context["device_config"] = device_config
            context["device_id"] = args.device
            context["dpi"] = device_config["dpi"]
            context["width"] = device_config["width"]
            context["height"] = device_config["height"]
            context["margin_mm"] = args.margin

            context["using_line_count_mode"] = args.lines is not None
            if args.lines:
                h_lines, v_lines = parse_line_count_spec(args.lines)
                context["h_lines"] = h_lines
                context["v_lines"] = v_lines
                margin_px = round(args.margin * (context["dpi"] / 25.4))

                h_spacing_px, h_is_fractional = calculate_spacing_from_line_count(
                    context["height"] - (2 * margin_px), h_lines, enforce_exact=False
                )
                context["spacing_result"] = SpacingResult(h_spacing_px, 0, False, 0)
                context["is_fractional"] = h_is_fractional
            else:
                context["spacing_result"] = parse_spacing(
                    args.spacing, context["dpi"], not args.true_scale
                )

            # Build template kwargs
            template_kwargs = self._build_template_kwargs_from_config()

            # Calculate alignment and margins
            alignment = AlignmentUnits.from_template_config(
                args.template_type,
                context["spacing_result"].pixels,
                context["dpi"],
                template_kwargs,
            )
            context["margins"] = calculate_page_margins(
                context["width"],
                context["height"],
                context["dpi"],
                context["margin_mm"],
                alignment.vertical,
                alignment.horizontal,
                template_kwargs.get("major_every"),
                False,  # force_major_alignment
            )

            # Call the preview summary function
            summary = _build_preview_summary(context, args, template_kwargs)
            print(summary)

        except Exception as e:
            print(f"Error building preview: {e}")
            import traceback

            traceback.print_exc()

        input("\nPress Enter to continue...")

    def _save_as_command(self):
        """Generate and show the equivalent CLI command"""
        print("\n" + "=" * 70)
        print("EQUIVALENT COMMAND")
        print("=" * 70)

        cmd_parts = ["eink-template-gen", self.config["template"]]

        if "spacing" in self.config:
            cmd_parts.append(f"--spacing \"{self.config['spacing']}\"")
        elif "lines" in self.config:
            cmd_parts.append(f"--lines \"{self.config['lines']}\"")

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

        if self.config.get("midline_style") and self.config["midline_style"] != "dashed":
            cmd_parts.append(f"--midline-style {self.config['midline_style']}")

        if self.config.get("staff_gap_mm") and self.config["staff_gap_mm"] != 10:
            cmd_parts.append(f"--staff-gap-mm {self.config['staff_gap_mm']}")

        if self.config.get("split_ratio") and self.config["split_ratio"] != 0.6:
            cmd_parts.append(f"--split-ratio {self.config['split_ratio']}")

        if self.config.get("rows"):
            cmd_parts.append(f"--rows {self.config['rows']}")
        if self.config.get("columns"):
            cmd_parts.append(f"--columns {self.config['columns']}")
        if self.config.get("uniform_template"):
            cmd_parts.append(f"--type {self.config['uniform_template']}")
        if self.config.get("cell_types"):
            cmd_parts.append(f"--cell-types \"{self.config['cell_types']}\"")

        if self.config.get("header"):
            cmd_parts.append(f"--header {self.config['header']}")
        if self.config.get("footer"):
            cmd_parts.append(f"--footer {self.config['footer']}")

        cmd = " ".join(cmd_parts)

        print(f"\n{cmd}\n")
        print("You can copy this command to use later or in scripts.")

        save = self._prompt("Save to file?", default="N").lower()
        if save == "y":
            filename = self._prompt("Filename", default="template-command.sh")

            try:
                with open(filename, "w") as f:
                    f.write("#!/bin/bash\n")
                    f.write("# Generated by eink-template-gen wizard\n")
                    f.write(f"# {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    f.write(cmd + " $@\n")  # Add $@ to pass through extra args

                os.chmod(filename, 0o755)  # Make executable
                print(f"Saved to {filename}")
            except IOError as e:
                print(f"Error saving file: {e}")

        input("\nPress Enter to continue...")

    def _build_template_kwargs_from_config(self) -> dict:
        """Helper to build the kwargs dict for preview"""
        kwargs = {}
        if self.config.get("line_width_px"):
            kwargs["line_width_px"] = self.config["line_width_px"]
        if self.config.get("dot_radius_px"):
            kwargs["dot_radius_px"] = self.config["dot_radius_px"]
        if self.config.get("major_every"):
            kwargs["major_every"] = self.config["major_every"]
        if self.config.get("line_numbers"):
            kwargs["line_number_config"] = {
                "interval": self.config["line_numbers_interval"],
                "side": self.config["line_numbers_side"],
            }
        if self.config.get("cell_labels"):
            kwargs["cell_label_config"] = {}
        if self.config.get("axis_labels"):
            kwargs["axis_label_config"] = {"interval": self.config["axis_labels_interval"]}
        return kwargs

    def _build_args_from_config(self) -> argparse.Namespace:
        """Convert wizard config to argparse Namespace for compatibility"""
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
            "preview": False,
        }

        if "lines" in self.config:
            args_dict["lines"] = self.config["lines"]
            args_dict["spacing"] = "6"  # Dummy
        else:
            args_dict["spacing"] = self.config.get("spacing", "6mm")
            args_dict["lines"] = None

        # Add template-specific args
        args_dict["major_every"] = self.config.get("major_every")
        args_dict["major_width_add_px"] = 1.5  # default

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

        args_dict["dot_radius_px"] = self.config.get("dot_radius_px", 1.5)
        args_dict["line_width_px"] = 0.5  # default
        args_dict["crosshair_size"] = 4  # default
        args_dict["no_crosshairs"] = False

        # Manuscript/Music/Hybrid
        args_dict["midline_style"] = self.config.get("midline_style", "dashed")
        args_dict["ascender_opacity"] = 0.3  # default
        args_dict["staff_gap_mm"] = self.config.get("staff_gap_mm", 10)
        args_dict["split_ratio"] = self.config.get("split_ratio", 0.6)
        args_dict["section_gap_mm"] = self.config.get("section_gap_mm")

        # Multi
        args_dict["rows"] = self.config.get("rows")
        args_dict["columns"] = self.config.get("columns")
        args_dict["template"] = self.config.get("uniform_template")  # For uniform multi
        args_dict["cell_types"] = self.config.get("cell_types")  # For mixed multi
        args_dict["section_gap_cols"] = None
        args_dict["section_gap_rows"] = None
        args_dict["orientation"] = "horizontal"

        # Title
        # (This is incomplete as title has many args, but wizard skips them)
        args_dict["title"] = self.config.get("template")

        # Set template_type for single templates
        if self.config["template"] in TEMPLATE_REGISTRY:
            args_dict["template_type"] = self.config["template"]

        return argparse.Namespace(**args_dict)


def run_wizard_and_generate():
    """Run the wizard and generate the template"""
    wizard = TemplateWizard()
    config = wizard.run()

    if not config:
        # User cancelled
        return

    # Convert wizard config to args
    args = wizard._build_args_from_config()

    # Generate using existing handlers
    print("\n" + "=" * 70)
    print("GENERATING TEMPLATE")
    print("=" * 70)

    try:
        if args.command == "multi":
            handle_multi_template_generation(args)
        elif args.command == "title":
            handle_cover_generation(args)
        elif args.command == "layout":
            # This shouldn't be reachable if _select_template_type is correct
            print("'layout' command cannot be run from the wizard.")
        elif args.command in TEMPLATE_REGISTRY:
            handle_single_template_generation(args)
        else:
            print(f"Unknown template type: {args.command}")
    except Exception as e:
        print(f"\n Error generating template: {e}")
        import traceback

        traceback.print_exc()
