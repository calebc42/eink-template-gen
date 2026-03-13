#!/usr/bin/env python3
"""
Generate Example Library - Creates a comprehensive set of example templates
showcasing the various features and options of eink-template-gen
"""

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List

# Configuration
OUTPUT_DIR = "examples/templates"
DEVICE = "manta"  # Default device for examples
MAIN_SCRIPT = "src/eink_template_gen/__main__.py"  # Path to main script


class ExampleGenerator:
    """Manages generation of example templates"""

    def __init__(
        self, output_dir: str = OUTPUT_DIR, device: str = DEVICE, main_script: str = MAIN_SCRIPT
    ):
        self.output_dir = Path(output_dir)
        self.device = device
        self.main_script = main_script
        self.examples: List[Dict[str, Any]] = []

    def run_command(self, cmd: List[str], category: str, description: str) -> bool:
        """Execute a command and track it"""
        print(f"Generating: {description}")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            self.examples.append(
                {
                    "output": result.stdout,
                    "category": category,
                    "description": description,
                    "command": " ".join(cmd),
                    "status": "success",
                }
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"  ❌ Failed: {e.stderr}")
            self.examples.append(
                {
                    "category": category,
                    "description": description,
                    "command": " ".join(cmd),
                    "status": "failed",
                    "error": e.stderr,
                }
            )
            return False

    def build_cmd(self, subcommand_args: List[str]) -> List[str]:
        """Build complete command with device and output-dir in correct position"""
        return (
            ["python", self.main_script]
            + subcommand_args
            + ["--device", self.device, "--output-dir", str(self.output_dir)]
        )

    def generate_lined_examples(self):
        """Generate lined template examples"""
        category = "Lined Templates"
        print(f"\n{'='*60}\n{category}\n{'='*60}")

        # Basic lined
        self.run_command(
            self.build_cmd(["lined", "--spacing", "6mm", "--filename", "lined_basic_6mm"]),
            category,
            "Basic lined template (6mm spacing)",
        )

        # Lined with major lines
        self.run_command(
            self.build_cmd(
                [
                    "lined",
                    "--spacing",
                    "6mm",
                    "--major_every",
                    "5",
                    "--filename",
                    "lined_6mm_major_every_5",
                ]
            ),
            category,
            "Lined with every 5th line bold",
        )

        # Lined with line numbers
        self.run_command(
            self.build_cmd(
                [
                    "lined",
                    "--spacing",
                    "6mm",
                    "--line-numbers",
                    "--line-numbers-interval",
                    "5",
                    "--filename",
                    "lined_with_numbers",
                ]
            ),
            category,
            "Lined with line numbers (every 5th)",
        )

        # Lined with exact line count
        self.run_command(
            self.build_cmd(["lined", "--lines", "40", "--filename", "lined_exactly_40_lines"]),
            category,
            "Lined with exactly 40 lines",
        )

        # Lined with custom margin
        self.run_command(
            self.build_cmd(
                ["lined", "--spacing", "6mm", "--margin", "15", "--filename", "lined_15mm_margins"]
            ),
            category,
            "Lined with 15mm margins",
        )

    def generate_grid_examples(self):
        """Generate grid template examples"""
        category = "Grid Templates"
        print(f"\n{'='*60}\n{category}\n{'='*60}")

        # Basic grid
        self.run_command(
            self.build_cmd(["grid", "--spacing", "5mm", "--filename", "grid_basic_5mm"]),
            category,
            "Basic grid (5mm spacing)",
        )

        # Grid with major lines
        self.run_command(
            self.build_cmd(
                [
                    "grid",
                    "--spacing",
                    "5mm",
                    "--major_every",
                    "5",
                    "--filename",
                    "grid_major_every_5",
                ]
            ),
            category,
            "Grid with major lines every 5",
        )

        # Grid with crosshairs
        self.run_command(
            self.build_cmd(
                [
                    "grid",
                    "--spacing",
                    "5mm",
                    "--major_every",
                    "5",
                    "--crosshair_size",
                    "5",
                    "--filename",
                    "grid_with_crosshairs",
                ]
            ),
            category,
            "Grid with crosshairs at major intersections",
        )

        # Grid with cell labels
        self.run_command(
            self.build_cmd(
                ["grid", "--spacing", "10mm", "--cell-labels", "--filename", "grid_cell_labels"]
            ),
            category,
            "Grid with A,B,C / 1,2,3 cell labels",
        )

        # Grid with axis labels
        self.run_command(
            self.build_cmd(
                [
                    "grid",
                    "--spacing",
                    "5mm",
                    "--axis-labels",
                    "--axis-labels-interval",
                    "5",
                    "--filename",
                    "grid_axis_labels",
                ]
            ),
            category,
            "Grid with axis numbering (0,5,10...)",
        )

        # Exact grid size
        self.run_command(
            self.build_cmd(["grid", "--lines", "30x40", "--filename", "grid_30x40_cells"]),
            category,
            "Grid with exactly 30x40 cells",
        )

    def generate_dotgrid_examples(self):
        """Generate dot grid examples"""
        category = "Dot Grid Templates"
        print(f"\n{'='*60}\n{category}\n{'='*60}")

        # Basic dot grid
        self.run_command(
            self.build_cmd(["dotgrid", "--spacing", "5mm", "--filename", "dotgrid_basic_5mm"]),
            category,
            "Basic dot grid (5mm spacing)",
        )

        # Dot grid with larger dots
        self.run_command(
            self.build_cmd(
                [
                    "dotgrid",
                    "--spacing",
                    "5mm",
                    "--dot_radius_px",
                    "2.5",
                    "--filename",
                    "dotgrid_large_dots",
                ]
            ),
            category,
            "Dot grid with larger dots (2.5px radius)",
        )

        # Dot grid with major crosshairs
        self.run_command(
            self.build_cmd(
                [
                    "dotgrid",
                    "--spacing",
                    "5mm",
                    "--major_every",
                    "5",
                    "--crosshair_size",
                    "6",
                    "--filename",
                    "dotgrid_with_crosshairs",
                ]
            ),
            category,
            "Dot grid with crosshairs every 5 dots",
        )

    def generate_specialty_examples(self):
        """Generate specialty template examples"""
        category = "Specialty Templates"
        print(f"\n{'='*60}\n{category}\n{'='*60}")

        # Manuscript
        self.run_command(
            self.build_cmd(["manuscript", "--spacing", "8mm", "--filename", "manuscript_8mm"]),
            category,
            "Manuscript (4-line handwriting guide)",
        )

        # French ruled
        self.run_command(
            self.build_cmd(["french_ruled", "--spacing", "8mm", "--filename", "french_ruled_8mm"]),
            category,
            "French ruled (Seyès) template",
        )

        # Music staff
        self.run_command(
            self.build_cmd(
                [
                    "music_staff",
                    "--spacing",
                    "2mm",
                    "--staff_gap_mm",
                    "12",
                    "--filename",
                    "music_staff",
                ]
            ),
            category,
            "Music staff (2mm line spacing, 12mm staff gap)",
        )

        # Isometric
        self.run_command(
            self.build_cmd(["isometric", "--spacing", "5mm", "--filename", "isometric_5mm"]),
            category,
            "Isometric grid (5mm spacing)",
        )

        # Hexagonal
        self.run_command(
            self.build_cmd(["hexgrid", "--spacing", "8mm", "--filename", "hexgrid_8mm"]),
            category,
            "Hexagonal grid (8mm spacing)",
        )

        # Hybrid lined/dotgrid
        self.run_command(
            self.build_cmd(
                [
                    "hybrid_lined_dotgrid",
                    "--spacing",
                    "6mm",
                    "--split-ratio",
                    "0.6",
                    "--filename",
                    "hybrid_lined_dotgrid",
                ]
            ),
            category,
            "Hybrid lined/dotgrid (60/40 split)",
        )

    def generate_multi_examples(self):
        """Generate multi-cell grid examples"""
        category = "Multi-Cell Grids"
        print(f"\n{'='*60}\n{category}\n{'='*60}")

        # 2x2 uniform grid
        self.run_command(
            self.build_cmd(
                [
                    "multi",
                    "--rows",
                    "2",
                    "--columns",
                    "2",
                    "--type",
                    "dotgrid",
                    "--spacing",
                    "5mm",
                    "--filename",
                    "multi_2x2_dotgrid",
                ]
            ),
            category,
            "2x2 uniform dot grid",
        )

        # 1x2 mixed types
        self.run_command(
            self.build_cmd(
                [
                    "multi",
                    "--rows",
                    "1",
                    "--columns",
                    "2",
                    "--cell_types",
                    "lined,grid",
                    "--spacing",
                    "6mm",
                    "--filename",
                    "multi_1x2_lined_grid",
                ]
            ),
            category,
            "1x2 mixed: lined + grid",
        )

        # 2x2 all different
        self.run_command(
            self.build_cmd(
                [
                    "multi",
                    "--rows",
                    "2",
                    "--columns",
                    "2",
                    "--cell_types",
                    "lined,dotgrid,grid,manuscript",
                    "--spacing",
                    "5mm",
                    "--filename",
                    "multi_2x2_mixed",
                ]
            ),
            category,
            "2x2 mixed: lined, dotgrid, grid, manuscript",
        )

        # 3x1 with section gaps
        self.run_command(
            self.build_cmd(
                [
                    "multi",
                    "--rows",
                    "3",
                    "--columns",
                    "1",
                    "--type",
                    "lined",
                    "--spacing",
                    "7mm",
                    "--section-gap-rows",
                    "10",
                    "--filename",
                    "multi_3x1_with_gaps",
                ]
            ),
            category,
            "3x1 lined sections with 10mm gaps",
        )

    def generate_title_examples(self):
        """Generate title page examples"""
        category = "Title Pages"
        print(f"\n{'='*60}\n{category}\n{'='*60}")

        # Truchet tiles
        self.run_command(
            self.build_cmd(
                [
                    "title",
                    "--type",
                    "truchet",
                    "--spacing",
                    "10mm",
                    "--truchet-seed",
                    "42",
                    "--truchet-variant",
                    "classic",
                    "--filename",
                    "title_truchet_classic",
                ]
            ),
            category,
            "Truchet tiles - classic variant",
        )

        # Truchet cross variant
        self.run_command(
            self.build_cmd(
                [
                    "title",
                    "--type",
                    "truchet",
                    "--spacing",
                    "8mm",
                    "--truchet-seed",
                    "123",
                    "--truchet-variant",
                    "cross",
                    "--filename",
                    "title_truchet_cross",
                ]
            ),
            category,
            "Truchet tiles - cross variant",
        )

        # Diagonal truchet pattern (FIXED: was "diagonal", should be "diagonal_truchet")
        self.run_command(
            self.build_cmd(
                [
                    "title",
                    "--type",
                    "diagonal_truchet",
                    "--spacing",
                    "5mm",
                    "--diag-fill-grey1",
                    "0",
                    "--diag-fill-grey2",
                    "15",
                    "--filename",
                    "title_diagonal",
                ]
            ),
            category,
            "Diagonal truchet pattern",
        )

        # Contour lines
        self.run_command(
            self.build_cmd(
                [
                    "title",
                    "--type",
                    "contour_lines",
                    "--noise-scale",
                    "0.02",
                    "--contour-interval",
                    "0.1",
                    "--noise-seed",
                    "456",
                    "--filename",
                    "title_contour_lines",
                ]
            ),
            category,
            "Topographic contour lines",
        )

        # Noise field
        self.run_command(
            self.build_cmd(
                [
                    "title",
                    "--type",
                    "noise_field",
                    "--noise-scale",
                    "0.03",
                    "--greyscale-levels",
                    "8",
                    "--noise-seed",
                    "789",
                    "--filename",
                    "title_noise_field",
                ]
            ),
            category,
            "Perlin noise field (8 grey levels)",
        )

        # Title with text
        self.run_command(
            self.build_cmd(
                [
                    "title",
                    "--type",
                    "truchet",
                    "--spacing",
                    "10mm",
                    "--truchet-seed",
                    "999",
                    "--title-text",
                    "My Notebook",
                    "--title-font-size",
                    "48",
                    "--filename",
                    "title_with_text",
                ]
            ),
            category,
            "Truchet tiles with title text",
        )

    def generate_advanced_examples(self):
        """Generate advanced feature examples"""
        category = "Advanced Features"
        print(f"\n{'='*60}\n{category}\n{'='*60}")

        # Header/footer separators (FIXED: was "double-line", should be "double")
        self.run_command(
            self.build_cmd(
                [
                    "lined",
                    "--spacing",
                    "7mm",
                    "--header-sep",
                    "double",
                    "--footer-sep",
                    "dotted",
                    "--filename",
                    "lined_with_separators",
                ]
            ),
            category,
            "Lined with header/footer separators",
        )

        # Vertical orientation
        self.run_command(
            self.build_cmd(
                [
                    "multi",
                    "--rows",
                    "1",
                    "--columns",
                    "2",
                    "--type",
                    "lined",
                    "--spacing",
                    "7mm",
                    "--orientation",
                    "vertical",
                    "--filename",
                    "multi_vertical_lined",
                ]
            ),
            category,
            "Multi-cell with vertical line orientation",
        )

        # Force major alignment (grid)
        self.run_command(
            self.build_cmd(
                [
                    "grid",
                    "--spacing",
                    "5mm",
                    "--major_every",
                    "5",
                    "--force-major-alignment",
                    "--filename",
                    "grid_force_alignment",
                ]
            ),
            category,
            "Grid with forced major line alignment",
        )

    def create_json_examples(self):
        """Create example JSON layout files"""
        category = "JSON Layouts"
        print(f"\n{'='*60}\nCreating JSON Layout Files\n{'='*60}")

        json_dir = self.output_dir / "json_examples"
        json_dir.mkdir(parents=True, exist_ok=True)

        # Cornell notes layout (FIXED: changed from "sections" to "page_layout")
        cornell_layout = {
            "device": self.device,
            "spacing_mm": 7,
            "page_layout": [
                {"height_ratio": 0.15, "columns": [{"width_ratio": 1.0, "template_type": "blank"}]},
                {
                    "height_ratio": 0.75,
                    "columns": [
                        {"width_ratio": 0.25, "template_type": "lined"},
                        {"width_ratio": 0.75, "template_type": "lined"},
                    ],
                },
                {"height_ratio": 0.10, "columns": [{"width_ratio": 1.0, "template_type": "blank"}]},
            ],
        }

        cornell_path = json_dir / "cornell_notes.json"
        with open(cornell_path, "w") as f:
            json.dump(cornell_layout, f, indent=2)
        print(f"Created: {cornell_path}")

        # Generate from Cornell layout
        self.run_command(
            self.build_cmd(
                ["layout", "--file", str(cornell_path), "--filename", "layout_cornell_notes"]
            ),
            category,
            "Cornell notes layout from JSON",
        )

        # Dashboard layout (FIXED: changed from "sections" to "page_layout")
        dashboard_layout = {
            "device": self.device,
            "spacing_mm": 5,
            "page_layout": [
                {
                    "height_ratio": 0.3,
                    "columns": [
                        {"width_ratio": 0.5, "template_type": "dotgrid"},
                        {"width_ratio": 0.5, "template_type": "grid"},
                    ],
                },
                {"height_ratio": 0.7, "columns": [{"width_ratio": 1.0, "template_type": "lined"}]},
            ],
        }

        dashboard_path = json_dir / "dashboard.json"
        with open(dashboard_path, "w") as f:
            json.dump(dashboard_layout, f, indent=2)
        print(f"Created: {dashboard_path}")

        # Generate from dashboard layout
        self.run_command(
            self.build_cmd(
                ["layout", "--file", str(dashboard_path), "--filename", "layout_dashboard"]
            ),
            category,
            "Dashboard layout from JSON",
        )

    def generate_all(self):
        """Generate all examples"""
        print("=" * 60)
        print("E-Ink Template Generator - Example Library Creator")
        print("=" * 60)

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Generate all example categories
        self.generate_lined_examples()
        self.generate_grid_examples()
        self.generate_dotgrid_examples()
        self.generate_specialty_examples()
        self.generate_multi_examples()
        self.generate_title_examples()
        self.generate_advanced_examples()
        self.create_json_examples()

        # Summary
        total = len(self.examples)
        successful = sum(1 for ex in self.examples if ex["status"] == "success")

        print("\n" + "=" * 60)
        print("Generation Complete!")
        print("=" * 60)
        print(f"Total examples: {total}")
        print(f"Successful: {successful}")
        print(f"Failed: {total - successful}")
        print(f"\nOutput directory: {self.output_dir}")
        print("=" * 60)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate a comprehensive library of example templates"
    )
    parser.add_argument(
        "--output-dir",
        default=OUTPUT_DIR,
        help=f"Output directory for examples (default: {OUTPUT_DIR})",
    )
    parser.add_argument(
        "--device", default=DEVICE, help=f"Target device for all examples (default: {DEVICE})"
    )
    parser.add_argument(
        "--main-script", default=MAIN_SCRIPT, help=f"Path to main script (default: {MAIN_SCRIPT})"
    )
    parser.add_argument(
        "--categories",
        nargs="+",
        choices=[
            "lined",
            "grid",
            "dotgrid",
            "specialty",
            "multi",
            "title",
            "advanced",
            "json",
            "all",
        ],
        default=["all"],
        help="Which categories to generate (default: all)",
    )

    args = parser.parse_args()

    generator = ExampleGenerator(args.output_dir, args.device, args.main_script)

    categories = args.categories
    if "all" in categories:
        generator.generate_all()
    else:
        generator.output_dir.mkdir(parents=True, exist_ok=True)

        if "lined" in categories:
            generator.generate_lined_examples()
        if "grid" in categories:
            generator.generate_grid_examples()
        if "dotgrid" in categories:
            generator.generate_dotgrid_examples()
        if "specialty" in categories:
            generator.generate_specialty_examples()
        if "multi" in categories:
            generator.generate_multi_examples()
        if "title" in categories:
            generator.generate_title_examples()
        if "advanced" in categories:
            generator.generate_advanced_examples()
        if "json" in categories:
            generator.create_json_examples()


if __name__ == "__main__":
    main()
