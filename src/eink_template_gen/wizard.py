import argparse
import json
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
                elif result == "cancel":
                    print("\n\n Wizard cancelled.")
                    return None
                elif result == "done":
                    return self.config
                elif result == "restart":
                    print("\n🔄 Starting over...\n")
                    current_step = 0
                    self.config = {}
                else:
                    current_step += 1

            except (KeyboardInterrupt, EOFError):
                print("\n\n Wizard cancelled.")
                return None
            except self.BackSignal:
                if current_step > 0:
                    current_step -= 1

        return None

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

        template_type = self.config["template"]
        if template_type in ["multi", "title", "hybrid-lined-dotgrid"]:
            print(f"ℹ:  Spacing for '{template_type}' will be configured in the next step.")
            return "next"

        print("\nYou can specify spacing in two ways:")
        print("  1. Distance between lines (e.g., '6mm' or '71px')")
        print("  2. Number of lines to fit (e.g., '40' or '40x30' for grids)")

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
        clean_options = get_clean_spacing_options(dpi, min_mm=4, max_mm=12, step_mm=0.5)
        for mm, px in clean_options[:8]:
            print(f"  • {mm}mm ({px}px)")

        while True:
            spacing = self._prompt("Spacing", default="6mm")
            if not spacing:
                continue

            try:
                parse_spacing(spacing, dpi, auto_adjust=True)
                self.config["spacing"] = spacing
                print(f"✓ Spacing: {spacing}")
                return "next"
            except Exception as e:
                print(f" Invalid spacing: {e}")

    def _configure_spacing_linecount(self):
        """Configure spacing by line count"""
        template_type = self.config["template"]

        if template_type in ["grid", "dotgrid"]:
            print("\nFor grids, enter 'HxV' (e.g., '40x30')")
        else:
            print("\nEnter number of lines (e.g., '40')")

        while True:
            lines = self._prompt("Line count")
            if not lines:
                continue

            try:
                parse_line_count_spec(lines)
                self.config["lines"] = lines
                print(f"✓ Will fit {lines} lines")
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

        if "lines" in self.config:
            default_text = "0"
        else:
            default_text = str(default_margin)

        while True:
            choice = self._prompt("Margin in mm", default=default_text)
            try:
                margin = float(choice)
                if margin < 0:
                    continue
                self.config["margin_mm"] = margin
                print(f"✓ Margins: {margin}mm")
                return "next"
            except ValueError:
                print("  Please enter a valid number")

    def _configure_template_options(self):
        """Step 5: Template-specific options"""
        template_type = self.config["template"]

        print("\n" + "=" * 70)
        print(f"STEP 5: Options for '{template_type}'")
        print("=" * 70)

        if template_type in ["lined", "grid"]:
            self._configure_major_lines()
        if template_type == "lined":
            self._configure_line_numbers()
        if template_type == "grid":
            self._configure_grid_labels()
        if template_type == "dotgrid":
            self._configure_dot_size()
            self._configure_major_lines()
        if template_type == "manuscript":
            self._configure_manuscript_options()
        if template_type == "music-staff":
            self._configure_music_options()
        if template_type == "multi":
            return self._configure_multi_options()
        if template_type == "hybrid-lined-dotgrid":
            self._configure_hybrid_options()

        return "next"

    def _configure_major_lines(self):
        """Configure major line emphasis"""
        choice = self._prompt("Add major lines? (y/n)", default="N").lower()
        if choice == "y":
            while True:
                interval_str = self._prompt("Make every Nth line major", default="5")
                try:
                    interval = int(interval_str)
                    self.config["major_every"] = interval
                    break
                except ValueError:
                    print("  Please enter a valid number")

    def _configure_line_numbers(self):
        """Configure line numbering"""
        choice = self._prompt("Add line numbers? (y/n)", default="N").lower()
        if choice == "y":
            interval_str = self._prompt("Number every Nth line", default="5")
            interval = int(interval_str) if interval_str.isdigit() else 5
            side = self._prompt("Side [left/right]", default="left").lower()
            self.config["line_numbers"] = True
            self.config["line_numbers_interval"] = interval
            self.config["line_numbers_side"] = side

    def _configure_grid_labels(self):
        """Configure grid cell/axis labels"""
        choice = self._prompt(
            "Label style:\n  1. Cell labels\n  2. Axis labels\n  3. None\n\nSelect [1-3]",
            default="3",
        )
        if choice == "1":
            self.config["cell_labels"] = True
        elif choice == "2":
            self.config["axis_labels"] = True
            interval_str = self._prompt("Label every Nth line", default="5")
            self.config["axis_labels_interval"] = int(interval_str) if interval_str.isdigit() else 5

    def _configure_dot_size(self):
        """Configure dot radius"""
        choice = self._prompt("Dot radius in pixels", default="1.5")
        try:
            self.config["dot_radius_px"] = float(choice)
        except ValueError:
            self.config["dot_radius_px"] = 1.5

    def _configure_manuscript_options(self):
        """Configure manuscript (4-line) options"""
        style = self._prompt("Midline style [dashed/dotted]", default="dashed").lower()
        self.config["midline_style"] = style if style in ["dashed", "dotted"] else "dashed"

    def _configure_music_options(self):
        """Configure music staff options"""
        spacing_str = self._prompt("Spacing between lines in a staff (e.g., 2mm)", default="2mm")
        self.config["spacing"] = spacing_str
        gap_str = self._prompt("Gap between staves (e.g., 10mm)", default="10mm")
        try:
            self.config["staff_gap_mm"] = float(gap_str.replace("mm", ""))
        except ValueError:
            self.config["staff_gap_mm"] = 10.0

    def _configure_hybrid_options(self):
        """Configure hybrid template options"""
        spacing_str = self._prompt("Spacing for both sides (e.g., 6mm)", default="6mm")
        self.config["spacing"] = spacing_str
        ratio_str = self._prompt("Split ratio (0.1 to 0.9)", default="0.6")
        try:
            self.config["split_ratio"] = float(ratio_str)
        except ValueError:
            self.config["split_ratio"] = 0.6

    def _configure_multi_options(self):
        """Configure multi-cell grid options"""
        while True:
            rows_str = self._prompt("Number of rows", default="2")
            try:
                self.config["rows"] = int(rows_str)
                break
            except ValueError:
                pass
        while True:
            cols_str = self._prompt("Number of columns", default="2")
            try:
                self.config["columns"] = int(cols_str)
                break
            except ValueError:
                pass

        spacing_str = self._prompt("Global spacing for all cells (e.g., 5mm)", default="5mm")
        self.config["spacing"] = spacing_str

        choice = self._prompt(
            "  1. Yes (Uniform grid)\n  2. No (Mixed grid)\n\nAre all cells the same type?", 
            default="1"
        )

        if choice == "2":
            num_cells = self.config["rows"] * self.config["columns"]
            while True:
                types_str = self._prompt(f"Enter {num_cells} types separated by commas")
                cell_types = [t.strip() for t in types_str.split(",")]
                if len(cell_types) == num_cells:
                    self.config["cell_types"] = types_str
                    break
        else:
            valid_types = ["lined", "dotgrid", "grid", "manuscript", "hexgrid", "isometric", "blank"]
            for i, t in enumerate(valid_types, 1):
                print(f"  {i}. {t}")
            type_choice = self._prompt("Select cell type [1-7]", default="1")
            idx = int(type_choice) - 1 if type_choice.isdigit() else 0
            self.config["uniform_template"] = valid_types[idx]

        return "next"

    def _configure_advanced_features(self):
        """Step 6: Advanced features"""
        print("\n" + "=" * 70)
        print("STEP 6: Advanced Features")
        print("=" * 70)

        choice = self._prompt("Add header separator? (y/n)", default="N").lower()
        if choice == "y":
            self._select_separator("header")

        choice = self._prompt("Add footer separator? (y/n)", default="N").lower()
        if choice == "y":
            self._select_separator("footer")

        return "next"

    def _select_separator(self, position: str):
        """Select separator style"""
        styles = ["bold", "double", "wavy", "dashed", "dotted"]
        for i, style in enumerate(styles, 1):
            print(f"  {i}. {style}")
        choice = self._prompt(f"Select {position} style [1-5]", default="1")
        try:
            idx = int(choice) - 1
            self.config[position] = styles[idx]
        except (ValueError, IndexError):
            pass

    def _review_and_confirm(self) -> Optional[Dict[str, Any]]:
        """Step 7: Review and confirm"""
        print("\n" + "=" * 70)
        print("STEP 7: Review & Confirm")
        print("=" * 70)
        
        for k, v in self.config.items():
            print(f"  {k}: {v}")

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
                return "done"
            elif choice == "2":
                self._show_full_preview()
                continue
            elif choice == "3":
                if self._save_as_json():
                    return "cancel"
                continue
            elif choice == "4":
                self._save_as_command()
                continue
            elif choice == "5":
                return "restart"
            elif choice == "6":
                return "cancel"

    def _show_full_preview(self):
        """Show detailed preview by building args and calling summary"""
        print("\n" + "=" * 70)
        print("DETAILED PREVIEW (Dry-Run)")
        print("=" * 70)

        try:
            args = self._build_args_from_config()
            context = {}
            device_config = get_device(args.device)
            context["device_config"] = device_config
            context["device_id"] = args.device
            context["dpi"] = device_config["dpi"]
            context["width"] = device_config["width"]
            context["height"] = device_config["height"]
            context["margin_mm"] = args.margin
            mm2px = context["dpi"] / 25.4

            context["using_line_count_mode"] = args.lines is not None
            if args.lines:
                h_lines, v_lines = parse_line_count_spec(args.lines)
                context["h_lines"] = h_lines
                context["v_lines"] = v_lines
                margin_px = round(args.margin * mm2px)

                h_spacing_px, h_is_fractional = calculate_spacing_from_line_count(
                    context["height"] - (2 * margin_px), h_lines, enforce_exact=False
                )
                context["spacing_result"] = SpacingResult(
                    pixels=h_spacing_px, 
                    mm=h_spacing_px / mm2px, 
                    was_adjusted=False, 
                    original_mm=h_spacing_px / mm2px
                )
                context["is_fractional"] = h_is_fractional
            else:
                res = parse_spacing(args.spacing, context["dpi"], not args.true_scale)
                context["spacing_result"] = SpacingResult(
                    pixels=res[0],
                    original_mm=res[1],
                    mm=res[2],
                    was_adjusted=res[3]
                )

            template_kwargs = self._build_template_kwargs_from_config()
            
            # Use master template for preview alignment
            master_type = self.config["template"]
            if master_type == "multi":
                master_type = self.config.get("uniform_template") or (self.config.get("cell_types") or "blank").split(",")[0].strip()

            alignment = AlignmentUnits.from_template_config(
                master_type,
                context["spacing_result"].pixels,
                context["dpi"],
                template_kwargs,
            )
            context["margins"] = calculate_page_margins(
                context["width"], context["height"], context["dpi"],
                context["margin_mm"], alignment.vertical, alignment.horizontal,
                template_kwargs.get("major_every"), False,
            )

            summary = _build_preview_summary(context, args, template_kwargs)
            print(summary)

        except Exception as e:
            print(f"Error building preview: {e}")
            import traceback
            traceback.print_exc()

        input("\nPress Enter to continue...")

    def _save_as_json(self) -> bool:
        """Generate and save JSON configuration"""
        json_config = self._build_json_config()
        filename = self._prompt("Filename", default="template.json")
        try:
            with open(filename, "w") as f:
                json.dump(json_config, f, indent=2)
            print(f"✓ Saved to {filename}")
            return True
        except IOError as e:
            print(f"Error: {e}")
            return False

    def _save_as_command(self):
        """Generate and show the equivalent CLI command"""
        cmd = f"eink-template-gen {self.config['template']} --device {self.config['device']}"
        print(f"\nCommand: {cmd}\n")
        input("Press Enter to continue...")

    def _build_json_config(self) -> dict:
        return {"device": self.config["device"], "margin_mm": self.config["margin_mm"]}

    def _build_template_kwargs_from_config(self) -> dict:
        """Build template kwargs for preview logic"""
        kwargs = {}
        # RESTORE: Default line width for correct preview/drawing
        kwargs["line_width_px"] = self.config.get("line_width_px", 0.5)
        
        if self.config.get("major_every"):
            kwargs["major_every"] = self.config["major_every"]
        if self.config.get("line_numbers"):
            kwargs["line_number_config"] = {
                "interval": self.config["line_numbers_interval"],
                "side": self.config["line_numbers_side"],
            }
        if self.config.get("dot_radius_px"):
            kwargs["dot_radius_px"] = self.config["dot_radius_px"]
        return kwargs

    def _build_args_from_config(self) -> argparse.Namespace:
        """Convert wizard config to Namespace for generation handlers"""
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
            "template_type": self.config["template"],
            "lines": self.config.get("lines"),
            "spacing": self.config.get("spacing", "6mm"),
            # RESTORE: Drawing defaults expected by actions.py and templates.py
            "line_width_px": 0.5,
            "crosshair_size": 4,
            "no_crosshairs": False,
            "major_width_add_px": 1.5,
        }
        
        # Populate template-specific configuration
        args_dict.update({
            "major_every": self.config.get("major_every"),
            "line_numbers_interval": self.config.get("line_numbers_interval"),
            "line_numbers_side": self.config.get("line_numbers_side", "left"),
            # Numbers margin/font defaults
            "line_numbers_margin_px": 40,
            "line_numbers_font_size": 18,
            "line_numbers_grey": 8,
            "dot_radius_px": self.config.get("dot_radius_px", 1.5),
            "midline_style": self.config.get("midline_style", "dashed"),
            "staff_gap_mm": self.config.get("staff_gap_mm", 10),
            "split_ratio": self.config.get("split_ratio", 0.6),
            "rows": self.config.get("rows"),
            "columns": self.config.get("columns"),
            "template": self.config.get("uniform_template"),
            "cell_types": self.config.get("cell_types"),
        })
        return argparse.Namespace(**args_dict)


def run_wizard_and_generate():
    """Run the wizard and generate the template"""
    wizard = TemplateWizard()
    config = wizard.run()

    if not config:
        return

    args = wizard._build_args_from_config()
    print("\n" + "=" * 70)
    print("GENERATING TEMPLATE")
    print("=" * 70)

    try:
        if args.command == "multi":
            handle_multi_template_generation(args)
        elif args.command == "title":
            handle_cover_generation(args)
        elif args.command in TEMPLATE_REGISTRY:
            handle_single_template_generation(args)
        else:
            print(f"Unknown template type: {args.command}")
    except Exception as e:
        print(f"\n Error generating template: {e}")
        import traceback
        traceback.print_exc()
