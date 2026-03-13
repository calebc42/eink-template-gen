import os
import tempfile

import cairo
import pytest

from eink_template_gen.devices import get_device
from eink_template_gen.separators import SEPARATOR_STYLES
from eink_template_gen.templates import (
    create_cell_grid_template,
    create_column_template,
    create_json_layout_template,
    create_template_surface,
)
from eink_template_gen.utils import (
    calculate_adjusted_margins,
    snap_spacing_to_clean_pixels,
)


@pytest.fixture
def temp_output_dir():
    """Create a temporary directory for test outputs"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def standard_device():
    """Standard device config for testing"""
    return get_device("manta")


@pytest.fixture
def sample_json_layout():
    """Sample JSON layout configuration"""
    return {
        "device": "manta",
        "margin_mm": 10,
        "master_spacing_mm": 6,
        "output_filename": "test_layout.png",
        "header": "bold",
        "footer": "bold",
        "page_layout": [
            {
                "name": "Title",
                "region_rect": [0, 0, 1.0, 0.10],
                "template": "lined",
                "spacing_mm": 8,
                "kwargs": {"line_width_px": 1.0},
            },
            {
                "name": "Notes",
                "region_rect": [0, 0.10, 1.0, 0.90],
                "template": "dotgrid",
                "spacing_mm": 6,
                "kwargs": {"dot_radius_px": 1.5},
            },
        ],
    }


class TestMultiColumnLayouts:
    """Test multi-column and multi-row layouts"""

    def test_column_template_2x1(self, standard_device):
        """Test 2-column layout"""
        surface = create_column_template(
            width=standard_device["width"],
            height=standard_device["height"],
            dpi=standard_device["dpi"],
            spacing_mm=6,
            margin_mm=10,
            num_columns=2,
            num_rows=1,
            column_gap_mm=6,
            row_gap_mm=6,
            base_template="lined",
            template_kwargs={"line_width_px": 0.5},
            auto_adjust_spacing=True,
            force_major_alignment=False,
        )

        assert isinstance(surface, cairo.ImageSurface)

    def test_column_template_2x2(self, standard_device):
        """Test 2x2 grid layout"""
        surface = create_column_template(
            width=standard_device["width"],
            height=standard_device["height"],
            dpi=standard_device["dpi"],
            spacing_mm=6,
            margin_mm=10,
            num_columns=2,
            num_rows=2,
            column_gap_mm=6,
            row_gap_mm=6,
            base_template="dotgrid",
            template_kwargs={"dot_radius_px": 1.5},
            auto_adjust_spacing=True,
            force_major_alignment=False,
        )

        assert isinstance(surface, cairo.ImageSurface)

    def test_cell_grid_template_mixed(self, standard_device):
        """Test multi-type cell grid"""
        cell_definitions = [
            [
                {"type": "lined", "kwargs": {"line_width_px": 0.5}},
                {"type": "dotgrid", "kwargs": {"dot_radius_px": 1.5}},
            ],
            [
                {"type": "grid", "kwargs": {"line_width_px": 0.5}},
                {"type": "manuscript", "kwargs": {"line_width_px": 0.5}},
            ],
        ]

        surface = create_cell_grid_template(
            width=standard_device["width"],
            height=standard_device["height"],
            dpi=standard_device["dpi"],
            spacing_mm=6,
            margin_mm=10,
            cell_definitions=cell_definitions,
            column_gap_mm=6,
            row_gap_mm=6,
            auto_adjust_spacing=True,
            force_major_alignment=False,
        )

        assert isinstance(surface, cairo.ImageSurface)


class TestJSONLayouts:
    """Test JSON-based layout generation"""

    def test_json_layout_basic(self, sample_json_layout, standard_device):
        """Test basic JSON layout generation"""
        surface = create_json_layout_template(
            sample_json_layout,
            standard_device,
            margin_mm=10,
            auto_adjust=True,
            force_major_alignment=False,
        )

        assert isinstance(surface, cairo.ImageSurface)
        assert surface.get_width() == standard_device["width"]
        assert surface.get_height() == standard_device["height"]

    def test_json_layout_missing_device(self, sample_json_layout, standard_device):
        """Test JSON layout with missing device key"""
        config = sample_json_layout.copy()
        del config["device"]

        # Should still work if device_config is provided
        surface = create_json_layout_template(
            config, standard_device, margin_mm=10, auto_adjust=True, force_major_alignment=False
        )
        assert isinstance(surface, cairo.ImageSurface)

    def test_json_layout_invalid_region_rect(self, sample_json_layout, standard_device):
        """Test JSON layout with invalid region rect"""
        config = sample_json_layout.copy()
        config["page_layout"][0]["region_rect"] = [0, 0, 1.0]  # Missing height

        with pytest.raises(ValueError, match="missing 'region_rect'"):
            create_json_layout_template(
                config, standard_device, margin_mm=10, auto_adjust=True, force_major_alignment=False
            )


class TestPixelPerfection:
    """Test that templates achieve pixel-perfect alignment"""

    def test_spacing_is_integer_pixels(self, standard_device):
        """Test that adjusted spacing results in integer pixels"""
        dpi = standard_device["dpi"]

        for spacing_mm in [2, 4, 6, 8, 10]:
            adjusted_mm, spacing_px, was_adjusted = snap_spacing_to_clean_pixels(spacing_mm, dpi)

            # Spacing should be an integer
            assert spacing_px == round(
                spacing_px
            ), f"Spacing {spacing_mm}mm -> {spacing_px}px is not integer"

    def test_margin_adjustment_eliminates_gaps(self):
        """Test that margin adjustment eliminates leftover space"""
        # Test case: 1000px content, 71px spacing
        content_height = 1000
        spacing_px = 71
        base_margin = 50

        top, bottom = calculate_adjusted_margins(content_height, spacing_px, base_margin)

        # Calculate adjusted content area
        adjusted_content = content_height - (top - base_margin) - (bottom - base_margin)

        # Should be evenly divisible by spacing
        num_lines = adjusted_content / spacing_px
        assert num_lines == int(num_lines), "Adjusted margins don't eliminate gaps"


class TestSeparators:
    """Test separator line styles"""

    def test_all_separator_styles(self, standard_device):
        """Test that all separator styles work without errors"""
        # Get valid styles (exclude None)
        styles = [s for s in SEPARATOR_STYLES if s is not None]

        for style in styles:
            surface = create_template_surface(
                template_type="lined",
                device_config=standard_device,
                spacing_str="6mm",
                margin_mm=10,
                auto_adjust_spacing=True,
                force_major_alignment=False,
                header=style,
                footer=style,
                template_kwargs={"line_width_px": 0.5},
            )

            assert isinstance(surface, cairo.ImageSurface), f"Failed with separator style: {style}"


class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_very_small_spacing(self, standard_device):
        """Test with very small spacing"""
        surface = create_template_surface(
            template_type="lined",
            device_config=standard_device,
            spacing_str="1mm",
            margin_mm=10,
            auto_adjust_spacing=True,
            force_major_alignment=False,
            header=None,
            footer=None,
            template_kwargs={"line_width_px": 0.5},
        )

        assert isinstance(surface, cairo.ImageSurface)

    def test_very_large_spacing(self, standard_device):
        """Test with very large spacing"""
        surface = create_template_surface(
            template_type="lined",
            device_config=standard_device,
            spacing_str="50mm",
            margin_mm=10,
            auto_adjust_spacing=True,
            force_major_alignment=False,
            header=None,
            footer=None,
            template_kwargs={"line_width_px": 0.5},
        )

        assert isinstance(surface, cairo.ImageSurface)

    def test_zero_margin(self, standard_device):
        """Test with zero margin"""
        surface = create_template_surface(
            template_type="lined",
            device_config=standard_device,
            spacing_str="6mm",
            margin_mm=0,
            auto_adjust_spacing=True,
            force_major_alignment=False,
            header=None,
            footer=None,
            template_kwargs={"line_width_px": 0.5},
        )

        assert isinstance(surface, cairo.ImageSurface)

    def test_large_margin(self, standard_device):
        """Test with large margin"""
        surface = create_template_surface(
            template_type="lined",
            device_config=standard_device,
            spacing_str="6mm",
            margin_mm=100,
            auto_adjust_spacing=True,
            force_major_alignment=False,
            header=None,
            footer=None,
            template_kwargs={"line_width_px": 0.5},
        )

        assert isinstance(surface, cairo.ImageSurface)

    def test_thick_lines(self, standard_device):
        """Test with very thick lines"""
        surface = create_template_surface(
            template_type="lined",
            device_config=standard_device,
            spacing_str="6mm",
            margin_mm=10,
            auto_adjust_spacing=True,
            force_major_alignment=False,
            header=None,
            footer=None,
            template_kwargs={"line_width_px": 10.0},
        )

        assert isinstance(surface, cairo.ImageSurface)


@pytest.mark.slow
class TestPerformance:
    """Test performance and resource usage"""

    def test_generation_time(self, standard_device):
        """Test that template generation completes in reasonable time"""
        import time

        start = time.time()
        create_template_surface(
            template_type="lined",
            device_config=standard_device,
            spacing_str="6mm",
            margin_mm=10,
            auto_adjust_spacing=True,
            force_major_alignment=False,
            header=None,
            footer=None,
            template_kwargs={"line_width_px": 0.5},
        )
        duration = time.time() - start

        # Should complete in under 5 seconds
        assert duration < 5.0, f"Generation took {duration:.2f}s, expected < 5s"

    def test_multiple_generations(self, standard_device):
        """Test generating multiple templates in sequence"""
        import time

        iterations = 10
        start = time.time()

        for _ in range(iterations):
            surface = create_template_surface(
                template_type="lined",
                device_config=standard_device,
                spacing_str="6mm",
                margin_mm=10,
                auto_adjust_spacing=True,
                force_major_alignment=False,
                header=None,
                footer=None,
                template_kwargs={"line_width_px": 0.5},
            )
            del surface

        duration = time.time() - start
        avg_time = duration / iterations

        assert avg_time < 1.0, f"Average generation time {avg_time:.2f}s, expected < 1s"


class TestFileOutput:
    """Test file output functionality"""

    def test_save_to_png(self, standard_device, temp_output_dir):
        """Test saving template to PNG file"""
        surface = create_template_surface(
            template_type="lined",
            device_config=standard_device,
            spacing_str="6mm",
            margin_mm=10,
            auto_adjust_spacing=True,
            force_major_alignment=False,
            header=None,
            footer=None,
            template_kwargs={"line_width_px": 0.5},
        )

        filepath = os.path.join(temp_output_dir, "test_output.png")
        surface.write_to_png(filepath)

        assert os.path.exists(filepath)
        assert os.path.getsize(filepath) > 0

    def test_consistent_output(self, standard_device, temp_output_dir):
        """Test that same parameters produce identical output"""
        # Generate twice
        surface1 = create_template_surface(
            template_type="lined",
            device_config=standard_device,
            spacing_str="6mm",
            margin_mm=10,
            auto_adjust_spacing=True,
            force_major_alignment=False,
            header=None,
            footer=None,
            template_kwargs={"line_width_px": 0.5},
        )

        surface2 = create_template_surface(
            template_type="lined",
            device_config=standard_device,
            spacing_str="6mm",
            margin_mm=10,
            auto_adjust_spacing=True,
            force_major_alignment=False,
            header=None,
            footer=None,
            template_kwargs={"line_width_px": 0.5},
        )

        # Save both
        path1 = os.path.join(temp_output_dir, "test1.png")
        path2 = os.path.join(temp_output_dir, "test2.png")
        surface1.write_to_png(path1)
        surface2.write_to_png(path2)

        # Files should have same size (rough check)
        size1 = os.path.getsize(path1)
        size2 = os.path.getsize(path2)
        assert size1 == size2
