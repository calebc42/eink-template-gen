#!/usr/bin/env python3
"""
Generate JSON Example Library - Creates a collection of practical JSON layout examples
"""

import json
from pathlib import Path
from typing import Any, Dict

OUTPUT_DIR = "examples/json_layouts"


class JSONExampleLibrary:
    """Creates a library of JSON layout examples"""

    def __init__(self, output_dir: str = OUTPUT_DIR):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.examples = []

    def save_example(self, filename: str, config: Dict[str, Any], description: str, category: str):
        """Save a JSON example and track it"""
        filepath = self.output_dir / filename
        with open(filepath, "w") as f:
            json.dump(config, f, indent=2)

        self.examples.append(
            {
                "filename": filename,
                "description": description,
                "category": category,
                "path": str(filepath),
            }
        )
        print(f"Created: {filepath}")

    def generate_note_taking_examples(self):
        """Generate note-taking layouts"""
        category = "Note Taking"
        print(f"\n{'='*60}\n{category}\n{'='*60}")

        # Classic Cornell Notes
        self.save_example(
            "cornell_notes_classic.json",
            {
                "device": "manta",
                "margin_mm": 12,
                "master_spacing_mm": 7,
                "header": "bold",
                "footer": "bold",
                "page_layout": [
                    {
                        "name": "Header/Title",
                        "region_rect": [0, 0, 1.0, 0.12],
                        "template": "lined",
                        "spacing_mm": 10,
                        "kwargs": {"line_width_px": 1.2},
                    },
                    {
                        "name": "Cue Column",
                        "region_rect": [0, 0.12, 0.25, 0.68],
                        "template": "lined",
                        "spacing_mm": 7,
                        "kwargs": {"line_width_px": 0.5},
                    },
                    {
                        "name": "Notes Column",
                        "region_rect": [0.25, 0.12, 0.75, 0.68],
                        "template": "lined",
                        "spacing_mm": 7,
                        "kwargs": {"line_width_px": 0.5},
                    },
                    {
                        "name": "Summary",
                        "region_rect": [0, 0.80, 1.0, 0.20],
                        "template": "lined",
                        "spacing_mm": 7,
                        "kwargs": {"line_width_px": 0.5},
                    },
                ],
            },
            "Classic Cornell note-taking system with header, cue column, notes area, and summary",
            category,
        )

        # Cornell with Dot Grid Cues
        self.save_example(
            "cornell_dotgrid_cues.json",
            {
                "device": "manta",
                "margin_mm": 10,
                "master_spacing_mm": 6,
                "header": "double",
                "page_layout": [
                    {"name": "Title Area", "region_rect": [0, 0, 1.0, 0.10], "template": "blank"},
                    {
                        "name": "Cue Column (Dot Grid)",
                        "region_rect": [0, 0.10, 0.30, 0.75],
                        "template": "dotgrid",
                        "spacing_mm": 6,
                        "kwargs": {"dot_radius_px": 1.5},
                    },
                    {
                        "name": "Notes Column",
                        "region_rect": [0.30, 0.10, 0.70, 0.75],
                        "template": "lined",
                        "spacing_mm": 6,
                        "kwargs": {"line_width_px": 0.5},
                    },
                    {
                        "name": "Summary Area",
                        "region_rect": [0, 0.85, 1.0, 0.15],
                        "template": "lined",
                        "spacing_mm": 6,
                        "kwargs": {"line_width_px": 0.5},
                    },
                ],
            },
            "Cornell notes with dot grid cue column for sketches and diagrams",
            category,
        )

        # Two Column Notes
        self.save_example(
            "two_column_simple.json",
            {
                "device": "manta",
                "margin_mm": 10,
                "master_spacing_mm": 7,
                "page_layout": [
                    {
                        "name": "Left Column",
                        "region_rect": [0, 0, 0.5, 1.0],
                        "template": "lined",
                        "spacing_mm": 7,
                        "kwargs": {"line_width_px": 0.5},
                    },
                    {
                        "name": "Right Column",
                        "region_rect": [0.5, 0, 0.5, 1.0],
                        "template": "lined",
                        "spacing_mm": 7,
                        "kwargs": {"line_width_px": 0.5},
                    },
                ],
            },
            "Simple two-column layout for parallel note-taking or comparisons",
            category,
        )

        # Three Column Notes
        self.save_example(
            "three_column_notes.json",
            {
                "device": "manta",
                "margin_mm": 8,
                "master_spacing_mm": 6,
                "header": "bold",
                "page_layout": [
                    {
                        "name": "Left Column",
                        "region_rect": [0, 0, 0.33, 1.0],
                        "template": "lined",
                        "spacing_mm": 6,
                        "kwargs": {"line_width_px": 0.5},
                    },
                    {
                        "name": "Middle Column",
                        "region_rect": [0.33, 0, 0.34, 1.0],
                        "template": "lined",
                        "spacing_mm": 6,
                        "kwargs": {"line_width_px": 0.5},
                    },
                    {
                        "name": "Right Column",
                        "region_rect": [0.67, 0, 0.33, 1.0],
                        "template": "lined",
                        "spacing_mm": 6,
                        "kwargs": {"line_width_px": 0.5},
                    },
                ],
            },
            "Three-column layout for comparative notes or multi-subject organization",
            category,
        )

    def generate_planning_examples(self):
        """Generate planning and productivity layouts"""
        category = "Planning & Productivity"
        print(f"\n{'='*60}\n{category}\n{'='*60}")

        # Daily Planner
        self.save_example(
            "daily_planner.json",
            {
                "device": "manta",
                "margin_mm": 10,
                "master_spacing_mm": 6,
                "header": "double",
                "footer": "bold",
                "page_layout": [
                    {"name": "Date & Title", "region_rect": [0, 0, 1.0, 0.08], "template": "blank"},
                    {
                        "name": "Time Schedule",
                        "region_rect": [0, 0.08, 0.25, 0.60],
                        "template": "lined",
                        "spacing_mm": 8,
                        "kwargs": {"line_width_px": 0.5},
                    },
                    {
                        "name": "Tasks & Notes",
                        "region_rect": [0.25, 0.08, 0.75, 0.60],
                        "template": "lined",
                        "spacing_mm": 6,
                        "kwargs": {"line_width_px": 0.5},
                    },
                    {
                        "name": "Notes/Reflections",
                        "region_rect": [0, 0.68, 1.0, 0.32],
                        "template": "dotgrid",
                        "spacing_mm": 5,
                        "kwargs": {"dot_radius_px": 1.5},
                    },
                ],
            },
            "Daily planner with time schedule, task list, and reflection area",
            category,
        )

        # Weekly Dashboard
        self.save_example(
            "weekly_dashboard.json",
            {
                "device": "manta",
                "margin_mm": 8,
                "master_spacing_mm": 5,
                "header": "bold",
                "page_layout": [
                    {"name": "Week Header", "region_rect": [0, 0, 1.0, 0.10], "template": "blank"},
                    {
                        "name": "Monday",
                        "region_rect": [0, 0.10, 0.33, 0.45],
                        "template": "lined",
                        "spacing_mm": 5,
                        "kwargs": {"line_width_px": 0.5},
                    },
                    {
                        "name": "Tuesday",
                        "region_rect": [0.33, 0.10, 0.34, 0.45],
                        "template": "lined",
                        "spacing_mm": 5,
                        "kwargs": {"line_width_px": 0.5},
                    },
                    {
                        "name": "Wednesday",
                        "region_rect": [0.67, 0.10, 0.33, 0.45],
                        "template": "lined",
                        "spacing_mm": 5,
                        "kwargs": {"line_width_px": 0.5},
                    },
                    {
                        "name": "Thursday",
                        "region_rect": [0, 0.55, 0.33, 0.45],
                        "template": "lined",
                        "spacing_mm": 5,
                        "kwargs": {"line_width_px": 0.5},
                    },
                    {
                        "name": "Friday",
                        "region_rect": [0.33, 0.55, 0.34, 0.45],
                        "template": "lined",
                        "spacing_mm": 5,
                        "kwargs": {"line_width_px": 0.5},
                    },
                    {
                        "name": "Weekend",
                        "region_rect": [0.67, 0.55, 0.33, 0.45],
                        "template": "dotgrid",
                        "spacing_mm": 5,
                        "kwargs": {"dot_radius_px": 1.5},
                    },
                ],
            },
            "Weekly dashboard with sections for each day of the week",
            category,
        )

        # Goal Tracker
        self.save_example(
            "goal_tracker.json",
            {
                "device": "manta",
                "margin_mm": 10,
                "master_spacing_mm": 7,
                "header": "bold",
                "page_layout": [
                    {
                        "name": "Goal Title",
                        "region_rect": [0, 0, 1.0, 0.12],
                        "template": "lined",
                        "spacing_mm": 10,
                        "kwargs": {"line_width_px": 1.5},
                    },
                    {
                        "name": "Action Steps",
                        "region_rect": [0, 0.12, 0.60, 0.50],
                        "template": "lined",
                        "spacing_mm": 7,
                        "kwargs": {"line_width_px": 0.5},
                    },
                    {
                        "name": "Progress Grid",
                        "region_rect": [0.60, 0.12, 0.40, 0.50],
                        "template": "grid",
                        "spacing_mm": 7,
                        "kwargs": {"line_width_px": 0.5},
                    },
                    {
                        "name": "Notes & Reflections",
                        "region_rect": [0, 0.62, 1.0, 0.38],
                        "template": "lined",
                        "spacing_mm": 7,
                        "kwargs": {"line_width_px": 0.5},
                    },
                ],
            },
            "Goal tracking page with action steps, progress grid, and reflection space",
            category,
        )

        # Habit Tracker
        self.save_example(
            "habit_tracker.json",
            {
                "device": "manta",
                "margin_mm": 8,
                "master_spacing_mm": 5,
                "header": "bold",
                "page_layout": [
                    {"name": "Month Header", "region_rect": [0, 0, 1.0, 0.08], "template": "blank"},
                    {
                        "name": "Habit List",
                        "region_rect": [0, 0.08, 0.30, 0.92],
                        "template": "lined",
                        "spacing_mm": 8,
                        "kwargs": {"line_width_px": 0.5},
                    },
                    {
                        "name": "Tracking Grid",
                        "region_rect": [0.30, 0.08, 0.70, 0.92],
                        "template": "grid",
                        "spacing_mm": 5,
                        "kwargs": {"line_width_px": 0.5, "major_every": 7},
                    },
                ],
            },
            "Monthly habit tracker with list of habits and daily tracking grid",
            category,
        )

    def generate_creative_examples(self):
        """Generate creative and design layouts"""
        category = "Creative & Design"
        print(f"\n{'='*60}\n{category}\n{'='*60}")

        # Storyboard 2x3
        self.save_example(
            "storyboard_2x3.json",
            {
                "device": "manta",
                "margin_mm": 10,
                "master_spacing_mm": 10,
                "page_layout": [
                    {
                        "name": "Frame 1",
                        "region_rect": [0, 0, 0.5, 0.33],
                        "template": "grid",
                        "spacing_mm": 10,
                        "kwargs": {"line_width_px": 0.25},
                    },
                    {
                        "name": "Frame 2",
                        "region_rect": [0.5, 0, 0.5, 0.33],
                        "template": "grid",
                        "spacing_mm": 10,
                        "kwargs": {"line_width_px": 0.25},
                    },
                    {
                        "name": "Frame 3",
                        "region_rect": [0, 0.33, 0.5, 0.34],
                        "template": "grid",
                        "spacing_mm": 10,
                        "kwargs": {"line_width_px": 0.25},
                    },
                    {
                        "name": "Frame 4",
                        "region_rect": [0.5, 0.33, 0.5, 0.34],
                        "template": "grid",
                        "spacing_mm": 10,
                        "kwargs": {"line_width_px": 0.25},
                    },
                    {
                        "name": "Frame 5",
                        "region_rect": [0, 0.67, 0.5, 0.33],
                        "template": "grid",
                        "spacing_mm": 10,
                        "kwargs": {"line_width_px": 0.25},
                    },
                    {
                        "name": "Frame 6",
                        "region_rect": [0.5, 0.67, 0.5, 0.33],
                        "template": "grid",
                        "spacing_mm": 10,
                        "kwargs": {"line_width_px": 0.25},
                    },
                ],
            },
            "2x3 storyboard grid for animation or comic planning",
            category,
        )

        # Comic Panel Layout
        self.save_example(
            "comic_panels.json",
            {
                "device": "manta",
                "margin_mm": 8,
                "master_spacing_mm": 8,
                "page_layout": [
                    {"name": "Title Panel", "region_rect": [0, 0, 1.0, 0.15], "template": "blank"},
                    {
                        "name": "Large Panel",
                        "region_rect": [0, 0.15, 0.65, 0.50],
                        "template": "grid",
                        "spacing_mm": 10,
                        "kwargs": {"line_width_px": 0.25},
                    },
                    {
                        "name": "Small Panel 1",
                        "region_rect": [0.65, 0.15, 0.35, 0.25],
                        "template": "grid",
                        "spacing_mm": 10,
                        "kwargs": {"line_width_px": 0.25},
                    },
                    {
                        "name": "Small Panel 2",
                        "region_rect": [0.65, 0.40, 0.35, 0.25],
                        "template": "grid",
                        "spacing_mm": 10,
                        "kwargs": {"line_width_px": 0.25},
                    },
                    {
                        "name": "Bottom Panel",
                        "region_rect": [0, 0.65, 1.0, 0.35],
                        "template": "grid",
                        "spacing_mm": 10,
                        "kwargs": {"line_width_px": 0.25},
                    },
                ],
            },
            "Comic book panel layout with varied panel sizes",
            category,
        )

        # Design Wireframe
        self.save_example(
            "design_wireframe.json",
            {
                "device": "manta",
                "margin_mm": 8,
                "master_spacing_mm": 5,
                "page_layout": [
                    {
                        "name": "Design Area",
                        "region_rect": [0, 0, 0.70, 1.0],
                        "template": "grid",
                        "spacing_mm": 5,
                        "kwargs": {"line_width_px": 0.5, "major_every": 5},
                    },
                    {
                        "name": "Notes",
                        "region_rect": [0.70, 0, 0.30, 1.0],
                        "template": "lined",
                        "spacing_mm": 6,
                        "kwargs": {"line_width_px": 0.5},
                    },
                ],
            },
            "Wireframe design template with grid and notes section",
            category,
        )

        # Sketch and Notes
        self.save_example(
            "sketch_notes.json",
            {
                "device": "manta",
                "margin_mm": 10,
                "master_spacing_mm": 5,
                "page_layout": [
                    {
                        "name": "Sketch Area",
                        "region_rect": [0, 0, 1.0, 0.65],
                        "template": "dotgrid",
                        "spacing_mm": 5,
                        "kwargs": {"dot_radius_px": 1.0},
                    },
                    {
                        "name": "Notes Area",
                        "region_rect": [0, 0.65, 1.0, 0.35],
                        "template": "lined",
                        "spacing_mm": 7,
                        "kwargs": {"line_width_px": 0.5},
                    },
                ],
            },
            "Sketch and notes layout with large dot grid area and lined notes",
            category,
        )

    def generate_technical_examples(self):
        """Generate technical and engineering layouts"""
        category = "Technical & Engineering"
        print(f"\n{'='*60}\n{category}\n{'='*60}")

        # Engineering Notebook
        self.save_example(
            "engineering_notebook.json",
            {
                "device": "manta",
                "margin_mm": 10,
                "master_spacing_mm": 5,
                "header": "double",
                "footer": "bold",
                "page_layout": [
                    {
                        "name": "Title & Date",
                        "region_rect": [0, 0, 1.0, 0.08],
                        "template": "lined",
                        "spacing_mm": 8,
                        "kwargs": {"line_width_px": 1.0},
                    },
                    {
                        "name": "Diagram Area",
                        "region_rect": [0, 0.08, 0.50, 0.60],
                        "template": "grid",
                        "spacing_mm": 5,
                        "kwargs": {"line_width_px": 0.5, "major_every": 5},
                    },
                    {
                        "name": "Calculations",
                        "region_rect": [0.50, 0.08, 0.50, 0.60],
                        "template": "grid",
                        "spacing_mm": 5,
                        "kwargs": {"line_width_px": 0.5},
                    },
                    {
                        "name": "Notes",
                        "region_rect": [0, 0.68, 1.0, 0.32],
                        "template": "lined",
                        "spacing_mm": 6,
                        "kwargs": {"line_width_px": 0.5},
                    },
                ],
            },
            "Engineering notebook with diagram area, calculation grid, and notes",
            category,
        )

        # Isometric Design
        self.save_example(
            "isometric_technical.json",
            {
                "device": "manta",
                "margin_mm": 8,
                "master_spacing_mm": 5,
                "header": "bold",
                "page_layout": [
                    {
                        "name": "Title",
                        "region_rect": [0, 0, 1.0, 0.08],
                        "template": "lined",
                        "spacing_mm": 10,
                        "kwargs": {"line_width_px": 1.0},
                    },
                    {
                        "name": "Isometric Drawing",
                        "region_rect": [0, 0.08, 0.75, 0.92],
                        "template": "isometric",
                        "spacing_mm": 5,
                        "kwargs": {"line_width_px": 0.5},
                    },
                    {
                        "name": "Dimensions",
                        "region_rect": [0.75, 0.08, 0.25, 0.92],
                        "template": "lined",
                        "spacing_mm": 6,
                        "kwargs": {"line_width_px": 0.5},
                    },
                ],
            },
            "Isometric drawing template with dimensions column",
            category,
        )

        # Circuit Design
        self.save_example(
            "circuit_design.json",
            {
                "device": "manta",
                "margin_mm": 10,
                "master_spacing_mm": 5,
                "page_layout": [
                    {
                        "name": "Circuit Diagram",
                        "region_rect": [0, 0, 0.65, 0.70],
                        "template": "grid",
                        "spacing_mm": 5,
                        "kwargs": {"line_width_px": 0.5, "major_every": 10},
                    },
                    {
                        "name": "Component List",
                        "region_rect": [0.65, 0, 0.35, 0.70],
                        "template": "lined",
                        "spacing_mm": 6,
                        "kwargs": {"line_width_px": 0.5},
                    },
                    {
                        "name": "Notes & Calculations",
                        "region_rect": [0, 0.70, 1.0, 0.30],
                        "template": "grid",
                        "spacing_mm": 5,
                        "kwargs": {"line_width_px": 0.5},
                    },
                ],
            },
            "Circuit design layout with diagram area, component list, and calculations",
            category,
        )

        # Lab Notebook
        self.save_example(
            "lab_notebook.json",
            {
                "device": "manta",
                "margin_mm": 12,
                "master_spacing_mm": 7,
                "header": "double",
                "footer": "double",
                "page_layout": [
                    {
                        "name": "Experiment Title",
                        "region_rect": [0, 0, 1.0, 0.10],
                        "template": "lined",
                        "spacing_mm": 10,
                        "kwargs": {"line_width_px": 1.2},
                    },
                    {
                        "name": "Hypothesis & Method",
                        "region_rect": [0, 0.10, 0.50, 0.40],
                        "template": "lined",
                        "spacing_mm": 7,
                        "kwargs": {"line_width_px": 0.5},
                    },
                    {
                        "name": "Data Table",
                        "region_rect": [0.50, 0.10, 0.50, 0.40],
                        "template": "grid",
                        "spacing_mm": 7,
                        "kwargs": {"line_width_px": 0.5},
                    },
                    {
                        "name": "Observations",
                        "region_rect": [0, 0.50, 0.60, 0.50],
                        "template": "lined",
                        "spacing_mm": 7,
                        "kwargs": {"line_width_px": 0.5},
                    },
                    {
                        "name": "Diagram/Graph",
                        "region_rect": [0.60, 0.50, 0.40, 0.50],
                        "template": "grid",
                        "spacing_mm": 5,
                        "kwargs": {"line_width_px": 0.5, "major_every": 5},
                    },
                ],
            },
            "Lab notebook with sections for hypothesis, data, observations, and diagrams",
            category,
        )

    def generate_music_examples(self):
        """Generate music-related layouts"""
        category = "Music"
        print(f"\n{'='*60}\n{category}\n{'='*60}")

        # Music Composition
        self.save_example(
            "music_composition.json",
            {
                "device": "manta",
                "margin_mm": 10,
                "master_spacing_mm": 2,
                "header": "bold",
                "page_layout": [
                    {"name": "Title", "region_rect": [0, 0, 1.0, 0.08], "template": "blank"},
                    {
                        "name": "Music Staves",
                        "region_rect": [0, 0.08, 1.0, 0.70],
                        "template": "music_staff",
                        "spacing_mm": 2,
                        "kwargs": {"line_width_px": 0.75, "staff_gap_mm": 15},
                    },
                    {
                        "name": "Lyrics/Notes",
                        "region_rect": [0, 0.78, 1.0, 0.22],
                        "template": "lined",
                        "spacing_mm": 8,
                        "kwargs": {"line_width_px": 0.5},
                    },
                ],
            },
            "Music composition sheet with staves and lyrics section",
            category,
        )

        # Song Writing
        self.save_example(
            "songwriting.json",
            {
                "device": "manta",
                "margin_mm": 10,
                "master_spacing_mm": 7,
                "header": "bold",
                "page_layout": [
                    {"name": "Song Title", "region_rect": [0, 0, 1.0, 0.10], "template": "blank"},
                    {
                        "name": "Lyrics Left",
                        "region_rect": [0, 0.10, 0.50, 0.60],
                        "template": "lined",
                        "spacing_mm": 8,
                        "kwargs": {"line_width_px": 0.5, "major_every": 4},
                    },
                    {
                        "name": "Chords/Structure",
                        "region_rect": [0.50, 0.10, 0.50, 0.60],
                        "template": "lined",
                        "spacing_mm": 8,
                        "kwargs": {"line_width_px": 0.5},
                    },
                    {
                        "name": "Notes & Ideas",
                        "region_rect": [0, 0.70, 1.0, 0.30],
                        "template": "dotgrid",
                        "spacing_mm": 5,
                        "kwargs": {"dot_radius_px": 1.5},
                    },
                ],
            },
            "Songwriting template with lyrics, chord notation, and ideas section",
            category,
        )

        # Practice Log
        self.save_example(
            "music_practice_log.json",
            {
                "device": "manta",
                "margin_mm": 10,
                "master_spacing_mm": 2,
                "header": "bold",
                "page_layout": [
                    {"name": "Week Header", "region_rect": [0, 0, 1.0, 0.08], "template": "blank"},
                    {
                        "name": "Practice Notes",
                        "region_rect": [0, 0.08, 0.40, 0.50],
                        "template": "lined",
                        "spacing_mm": 7,
                        "kwargs": {"line_width_px": 0.5},
                    },
                    {
                        "name": "Staff for Examples",
                        "region_rect": [0.40, 0.08, 0.60, 0.50],
                        "template": "music_staff",
                        "spacing_mm": 2,
                        "kwargs": {"line_width_px": 0.75, "staff_gap_mm": 12},
                    },
                    {
                        "name": "Goals & Progress",
                        "region_rect": [0, 0.58, 1.0, 0.42],
                        "template": "lined",
                        "spacing_mm": 7,
                        "kwargs": {"line_width_px": 0.5},
                    },
                ],
            },
            "Music practice log with notes, staff for examples, and goals tracking",
            category,
        )

    def generate_gaming_examples(self):
        """Generate gaming and RPG layouts"""
        category = "Gaming & RPG"
        print(f"\n{'='*60}\n{category}\n{'='*60}")

        # D&D Character Sheet Style
        self.save_example(
            "rpg_character_notes.json",
            {
                "device": "manta",
                "margin_mm": 8,
                "master_spacing_mm": 6,
                "header": "bold",
                "page_layout": [
                    {
                        "name": "Character Name",
                        "region_rect": [0, 0, 1.0, 0.08],
                        "template": "blank",
                    },
                    {
                        "name": "Stats & Info",
                        "region_rect": [0, 0.08, 0.30, 0.40],
                        "template": "lined",
                        "spacing_mm": 7,
                        "kwargs": {"line_width_px": 0.5},
                    },
                    {
                        "name": "Character Portrait",
                        "region_rect": [0.30, 0.08, 0.35, 0.40],
                        "template": "grid",
                        "spacing_mm": 5,
                        "kwargs": {"line_width_px": 0.25},
                    },
                    {
                        "name": "Equipment",
                        "region_rect": [0.65, 0.08, 0.35, 0.40],
                        "template": "lined",
                        "spacing_mm": 6,
                        "kwargs": {"line_width_px": 0.5},
                    },
                    {
                        "name": "Notes & Background",
                        "region_rect": [0, 0.48, 1.0, 0.52],
                        "template": "lined",
                        "spacing_mm": 6,
                        "kwargs": {"line_width_px": 0.5},
                    },
                ],
            },
            "RPG character sheet with stats, portrait area, equipment, and notes",
            category,
        )

        # Hex Map with Notes
        self.save_example(
            "hex_map_campaign.json",
            {
                "device": "manta",
                "margin_mm": 8,
                "master_spacing_mm": 8,
                "header": "double",
                "footer": "double",
                "page_layout": [
                    {"name": "Map Title", "region_rect": [0, 0, 1.0, 0.08], "template": "blank"},
                    {
                        "name": "Hex Map",
                        "region_rect": [0, 0.08, 0.65, 0.70],
                        "template": "hexgrid",
                        "spacing_mm": 8,
                        "kwargs": {"line_width_px": 0.5},
                    },
                    {
                        "name": "Location Key",
                        "region_rect": [0.65, 0.08, 0.35, 0.70],
                        "template": "lined",
                        "spacing_mm": 6,
                        "kwargs": {"line_width_px": 0.5},
                    },
                    {
                        "name": "Campaign Notes",
                        "region_rect": [0, 0.78, 1.0, 0.22],
                        "template": "lined",
                        "spacing_mm": 6,
                        "kwargs": {"line_width_px": 0.5},
                    },
                ],
            },
            "Hex map for RPG campaigns with location key and notes",
            category,
        )

        # Session Notes
        self.save_example(
            "rpg_session_notes.json",
            {
                "device": "manta",
                "margin_mm": 10,
                "master_spacing_mm": 7,
                "header": "bold",
                "page_layout": [
                    {
                        "name": "Session Info",
                        "region_rect": [0, 0, 1.0, 0.10],
                        "template": "lined",
                        "spacing_mm": 8,
                        "kwargs": {"line_width_px": 0.8},
                    },
                    {
                        "name": "Story Events",
                        "region_rect": [0, 0.10, 0.65, 0.90],
                        "template": "lined",
                        "spacing_mm": 7,
                        "kwargs": {"line_width_px": 0.5},
                    },
                    {
                        "name": "Quick Map/Sketches",
                        "region_rect": [0.65, 0.10, 0.35, 0.45],
                        "template": "grid",
                        "spacing_mm": 5,
                        "kwargs": {"line_width_px": 0.5},
                    },
                    {
                        "name": "NPCs & Loot",
                        "region_rect": [0.65, 0.55, 0.35, 0.45],
                        "template": "lined",
                        "spacing_mm": 6,
                        "kwargs": {"line_width_px": 0.5},
                    },
                ],
            },
            "RPG session notes with story events, map area, and NPC tracking",
            category,
        )

        # Battle Map Grid
        self.save_example(
            "battle_map.json",
            {
                "device": "manta",
                "margin_mm": 5,
                "master_spacing_mm": 5,
                "force_major_alignment": True,
                "page_layout": [
                    {
                        "name": "Battle Grid",
                        "region_rect": [0, 0, 1.0, 1.0],
                        "template": "grid",
                        "spacing_mm": 5,
                        "kwargs": {
                            "line_width_px": 0.5,
                            "major_every": 5,
                            "major_width_add_px": 1.0,
                        },
                    }
                ],
            },
            "Full-page battle map grid with major line markers every 5 squares",
            category,
        )

    def generate_learning_examples(self):
        """Generate learning and study layouts"""
        category = "Learning & Study"
        print(f"\n{'='*60}\n{category}\n{'='*60}")

        # Language Learning
        self.save_example(
            "language_practice.json",
            {
                "device": "manta",
                "margin_mm": 10,
                "master_spacing_mm": 8,
                "header": "bold",
                "page_layout": [
                    {
                        "name": "Vocabulary Header",
                        "region_rect": [0, 0, 1.0, 0.08],
                        "template": "lined",
                        "spacing_mm": 10,
                        "kwargs": {"line_width_px": 1.0},
                    },
                    {
                        "name": "Word/Phrase",
                        "region_rect": [0, 0.08, 0.35, 0.92],
                        "template": "lined",
                        "spacing_mm": 8,
                        "kwargs": {"line_width_px": 0.5},
                    },
                    {
                        "name": "Translation",
                        "region_rect": [0.35, 0.08, 0.35, 0.92],
                        "template": "lined",
                        "spacing_mm": 8,
                        "kwargs": {"line_width_px": 0.5},
                    },
                    {
                        "name": "Example/Notes",
                        "region_rect": [0.70, 0.08, 0.30, 0.92],
                        "template": "lined",
                        "spacing_mm": 8,
                        "kwargs": {"line_width_px": 0.5},
                    },
                ],
            },
            "Language learning template with word, translation, and example columns",
            category,
        )

        # Math Practice
        self.save_example(
            "math_practice.json",
            {
                "device": "manta",
                "margin_mm": 10,
                "master_spacing_mm": 5,
                "header": "bold",
                "page_layout": [
                    {
                        "name": "Topic Header",
                        "region_rect": [0, 0, 1.0, 0.08],
                        "template": "lined",
                        "spacing_mm": 10,
                        "kwargs": {"line_width_px": 1.0},
                    },
                    {
                        "name": "Problem Solving",
                        "region_rect": [0, 0.08, 0.55, 0.92],
                        "template": "grid",
                        "spacing_mm": 5,
                        "kwargs": {"line_width_px": 0.5, "major_every": 5},
                    },
                    {
                        "name": "Notes & Formulas",
                        "region_rect": [0.55, 0.08, 0.45, 0.92],
                        "template": "lined",
                        "spacing_mm": 7,
                        "kwargs": {"line_width_px": 0.5},
                    },
                ],
            },
            "Math practice sheet with grid for problem solving and notes section",
            category,
        )

        # Study Guide
        self.save_example(
            "study_guide.json",
            {
                "device": "manta",
                "margin_mm": 10,
                "master_spacing_mm": 7,
                "header": "double",
                "page_layout": [
                    {
                        "name": "Topic Title",
                        "region_rect": [0, 0, 1.0, 0.08],
                        "template": "lined",
                        "spacing_mm": 10,
                        "kwargs": {"line_width_px": 1.2},
                    },
                    {
                        "name": "Key Concepts",
                        "region_rect": [0, 0.08, 0.50, 0.45],
                        "template": "lined",
                        "spacing_mm": 7,
                        "kwargs": {"line_width_px": 0.5},
                    },
                    {
                        "name": "Diagrams",
                        "region_rect": [0.50, 0.08, 0.50, 0.45],
                        "template": "dotgrid",
                        "spacing_mm": 5,
                        "kwargs": {"dot_radius_px": 1.5},
                    },
                    {
                        "name": "Summary Notes",
                        "region_rect": [0, 0.53, 1.0, 0.47],
                        "template": "lined",
                        "spacing_mm": 7,
                        "kwargs": {"line_width_px": 0.5},
                    },
                ],
            },
            "Study guide with key concepts, diagram area, and summary notes",
            category,
        )

        # Flashcard Planning
        self.save_example(
            "flashcard_planning.json",
            {
                "device": "manta",
                "margin_mm": 8,
                "master_spacing_mm": 6,
                "page_layout": [
                    {
                        "name": "Card 1 Front",
                        "region_rect": [0, 0, 0.5, 0.25],
                        "template": "lined",
                        "spacing_mm": 8,
                        "kwargs": {"line_width_px": 0.5},
                    },
                    {
                        "name": "Card 1 Back",
                        "region_rect": [0.5, 0, 0.5, 0.25],
                        "template": "lined",
                        "spacing_mm": 6,
                        "kwargs": {"line_width_px": 0.5},
                    },
                    {
                        "name": "Card 2 Front",
                        "region_rect": [0, 0.25, 0.5, 0.25],
                        "template": "lined",
                        "spacing_mm": 8,
                        "kwargs": {"line_width_px": 0.5},
                    },
                    {
                        "name": "Card 2 Back",
                        "region_rect": [0.5, 0.25, 0.5, 0.25],
                        "template": "lined",
                        "spacing_mm": 6,
                        "kwargs": {"line_width_px": 0.5},
                    },
                    {
                        "name": "Card 3 Front",
                        "region_rect": [0, 0.5, 0.5, 0.25],
                        "template": "lined",
                        "spacing_mm": 8,
                        "kwargs": {"line_width_px": 0.5},
                    },
                    {
                        "name": "Card 3 Back",
                        "region_rect": [0.5, 0.5, 0.5, 0.25],
                        "template": "lined",
                        "spacing_mm": 6,
                        "kwargs": {"line_width_px": 0.5},
                    },
                    {
                        "name": "Card 4 Front",
                        "region_rect": [0, 0.75, 0.5, 0.25],
                        "template": "lined",
                        "spacing_mm": 8,
                        "kwargs": {"line_width_px": 0.5},
                    },
                    {
                        "name": "Card 4 Back",
                        "region_rect": [0.5, 0.75, 0.5, 0.25],
                        "template": "lined",
                        "spacing_mm": 6,
                        "kwargs": {"line_width_px": 0.5},
                    },
                ],
            },
            "Flashcard planning sheet with front/back pairs for 4 cards",
            category,
        )

    def generate_specialized_examples(self):
        """Generate specialized and mixed layouts"""
        category = "Specialized"
        print(f"\n{'='*60}\n{category}\n{'='*60}")

        # Meeting Notes
        self.save_example(
            "meeting_notes.json",
            {
                "device": "manta",
                "margin_mm": 10,
                "master_spacing_mm": 7,
                "header": "double",
                "footer": "bold",
                "page_layout": [
                    {
                        "name": "Meeting Info",
                        "region_rect": [0, 0, 1.0, 0.10],
                        "template": "lined",
                        "spacing_mm": 8,
                        "kwargs": {"line_width_px": 0.8},
                    },
                    {
                        "name": "Attendees",
                        "region_rect": [0, 0.10, 0.25, 0.20],
                        "template": "lined",
                        "spacing_mm": 6,
                        "kwargs": {"line_width_px": 0.5},
                    },
                    {
                        "name": "Agenda",
                        "region_rect": [0.25, 0.10, 0.75, 0.20],
                        "template": "lined",
                        "spacing_mm": 6,
                        "kwargs": {"line_width_px": 0.5},
                    },
                    {
                        "name": "Discussion Notes",
                        "region_rect": [0, 0.30, 1.0, 0.45],
                        "template": "lined",
                        "spacing_mm": 7,
                        "kwargs": {"line_width_px": 0.5},
                    },
                    {
                        "name": "Action Items",
                        "region_rect": [0, 0.75, 1.0, 0.25],
                        "template": "lined",
                        "spacing_mm": 7,
                        "kwargs": {"line_width_px": 0.5, "major_every": 3},
                    },
                ],
            },
            "Meeting notes with info header, attendees, agenda, notes, and action items",
            category,
        )

        # Recipe Card
        self.save_example(
            "recipe_template.json",
            {
                "device": "manta",
                "margin_mm": 10,
                "master_spacing_mm": 7,
                "header": "bold",
                "page_layout": [
                    {
                        "name": "Recipe Name",
                        "region_rect": [0, 0, 1.0, 0.12],
                        "template": "lined",
                        "spacing_mm": 10,
                        "kwargs": {"line_width_px": 1.2},
                    },
                    {
                        "name": "Ingredients",
                        "region_rect": [0, 0.12, 0.35, 0.50],
                        "template": "lined",
                        "spacing_mm": 7,
                        "kwargs": {"line_width_px": 0.5},
                    },
                    {
                        "name": "Photo/Sketch",
                        "region_rect": [0.35, 0.12, 0.65, 0.50],
                        "template": "grid",
                        "spacing_mm": 10,
                        "kwargs": {"line_width_px": 0.25},
                    },
                    {
                        "name": "Instructions",
                        "region_rect": [0, 0.62, 1.0, 0.28],
                        "template": "lined",
                        "spacing_mm": 7,
                        "kwargs": {"line_width_px": 0.5},
                    },
                    {
                        "name": "Notes/Variations",
                        "region_rect": [0, 0.90, 1.0, 0.10],
                        "template": "lined",
                        "spacing_mm": 6,
                        "kwargs": {"line_width_px": 0.5},
                    },
                ],
            },
            "Recipe template with ingredients, photo area, instructions, and notes",
            category,
        )

        # Fitness Tracker
        self.save_example(
            "fitness_tracker.json",
            {
                "device": "manta",
                "margin_mm": 10,
                "master_spacing_mm": 6,
                "header": "bold",
                "page_layout": [
                    {"name": "Week Header", "region_rect": [0, 0, 1.0, 0.08], "template": "blank"},
                    {
                        "name": "Workout Log",
                        "region_rect": [0, 0.08, 0.60, 0.70],
                        "template": "lined",
                        "spacing_mm": 7,
                        "kwargs": {"line_width_px": 0.5},
                    },
                    {
                        "name": "Tracking Grid",
                        "region_rect": [0.60, 0.08, 0.40, 0.70],
                        "template": "grid",
                        "spacing_mm": 6,
                        "kwargs": {"line_width_px": 0.5},
                    },
                    {
                        "name": "Notes/Goals",
                        "region_rect": [0, 0.78, 1.0, 0.22],
                        "template": "lined",
                        "spacing_mm": 6,
                        "kwargs": {"line_width_px": 0.5},
                    },
                ],
            },
            "Fitness tracker with workout log, tracking grid, and goals section",
            category,
        )

        # Book Reading Notes
        self.save_example(
            "reading_notes.json",
            {
                "device": "manta",
                "margin_mm": 10,
                "master_spacing_mm": 7,
                "header": "bold",
                "page_layout": [
                    {
                        "name": "Book Title & Info",
                        "region_rect": [0, 0, 1.0, 0.12],
                        "template": "lined",
                        "spacing_mm": 9,
                        "kwargs": {"line_width_px": 0.8},
                    },
                    {
                        "name": "Chapter/Page Notes",
                        "region_rect": [0, 0.12, 0.70, 0.88],
                        "template": "lined",
                        "spacing_mm": 7,
                        "kwargs": {"line_width_px": 0.5},
                    },
                    {
                        "name": "Key Quotes",
                        "region_rect": [0.70, 0.12, 0.30, 0.44],
                        "template": "lined",
                        "spacing_mm": 6,
                        "kwargs": {"line_width_px": 0.5},
                    },
                    {
                        "name": "Mind Map/Connections",
                        "region_rect": [0.70, 0.56, 0.30, 0.44],
                        "template": "dotgrid",
                        "spacing_mm": 5,
                        "kwargs": {"dot_radius_px": 1.5},
                    },
                ],
            },
            "Book reading notes with main notes, key quotes, and mind map area",
            category,
        )

        # Travel Journal
        self.save_example(
            "travel_journal.json",
            {
                "device": "manta",
                "margin_mm": 10,
                "master_spacing_mm": 6,
                "header": "double",
                "page_layout": [
                    {
                        "name": "Date & Location",
                        "region_rect": [0, 0, 1.0, 0.10],
                        "template": "lined",
                        "spacing_mm": 10,
                        "kwargs": {"line_width_px": 1.0},
                    },
                    {
                        "name": "Sketch/Photo Space",
                        "region_rect": [0, 0.10, 0.50, 0.45],
                        "template": "dotgrid",
                        "spacing_mm": 5,
                        "kwargs": {"dot_radius_px": 1.0},
                    },
                    {
                        "name": "Quick Notes",
                        "region_rect": [0.50, 0.10, 0.50, 0.45],
                        "template": "lined",
                        "spacing_mm": 6,
                        "kwargs": {"line_width_px": 0.5},
                    },
                    {
                        "name": "Journal Entry",
                        "region_rect": [0, 0.55, 1.0, 0.45],
                        "template": "lined",
                        "spacing_mm": 7,
                        "kwargs": {"line_width_px": 0.5},
                    },
                ],
            },
            "Travel journal with sketch area, quick notes, and journal entry space",
            category,
        )

    def generate_readme(self):
        """Generate a README for the JSON examples"""
        readme_path = self.output_dir / "README.md"

        with open(readme_path, "w") as f:
            f.write("# JSON Layout Examples Library\n\n")
            f.write("This library contains practical JSON layout templates for various use cases.\n\n")
            f.write("## Usage\n\n")
            f.write("Generate any template using:\n")
            f.write("```bash\n")
            f.write("eink-template-gen layout --file <json_file>\n")
            f.write("```\n\n")
            f.write("## Categories\n\n")

            # Group by category
            categories = {}
            for ex in self.examples:
                cat = ex["category"]
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(ex)

            # Table of contents
            for cat in categories.keys():
                anchor = cat.lower().replace(" ", "-").replace("&", "")
                f.write(f"- [{cat}](#{anchor})\n")
            f.write("\n---\n\n")

            # Write each category
            for cat, examples in categories.items():
                f.write(f"## {cat}\n\n")
                for ex in examples:
                    f.write(f"### {ex['filename']}\n\n")
                    f.write(f"{ex['description']}\n\n")
                    f.write("```bash\n")
                    f.write(f"eink-template-gen layout --file {ex['filename']}\n")
                    f.write("```\n\n")
                f.write("---\n\n")

            f.write("## Summary\n\n")
            f.write(f"Total templates: {len(self.examples)}\n\n")
            f.write(
                "All templates are designed for the Manta device but can be customized by editing the JSON files.\n"
            )

        print(f"\n📄 README generated: {readme_path}")

    def generate_all(self):
        """Generate all example categories"""
        print("=" * 60)
        print("JSON Example Library Generator")
        print("=" * 60)

        self.generate_note_taking_examples()
        self.generate_planning_examples()
        self.generate_creative_examples()
        self.generate_technical_examples()
        self.generate_music_examples()
        self.generate_gaming_examples()
        self.generate_learning_examples()
        self.generate_specialized_examples()

        self.generate_readme()

        print("\n" + "=" * 60)
        print("Generation Complete!")
        print("=" * 60)
        print(f"Total examples: {len(self.examples)}")
        print(f"Output directory: {self.output_dir}")
        print("=" * 60)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Generate a library of JSON layout examples")
    parser.add_argument("--output-dir", default=OUTPUT_DIR, help=f"Output directory (default: {OUTPUT_DIR})")
    parser.add_argument(
        "--categories",
        nargs="+",
        choices=[
            "notes",
            "planning",
            "creative",
            "technical",
            "music",
            "gaming",
            "learning",
            "specialized",
            "all",
        ],
        default=["all"],
        help="Which categories to generate (default: all)",
    )

    args = parser.parse_args()

    library = JSONExampleLibrary(args.output_dir)

    if "all" in args.categories:
        library.generate_all()
    else:
        if "notes" in args.categories:
            library.generate_note_taking_examples()
        if "planning" in args.categories:
            library.generate_planning_examples()
        if "creative" in args.categories:
            library.generate_creative_examples()
        if "technical" in args.categories:
            library.generate_technical_examples()
        if "music" in args.categories:
            library.generate_music_examples()
        if "gaming" in args.categories:
            library.generate_gaming_examples()
        if "learning" in args.categories:
            library.generate_learning_examples()
        if "specialized" in args.categories:
            library.generate_specialized_examples()

        library.generate_readme()

    print(f"\n✅ All JSON examples saved to: {library.output_dir}")


if __name__ == "__main__":
    main()
