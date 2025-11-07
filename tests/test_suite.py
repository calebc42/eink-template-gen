# tests/test_suite.py
"""
Comprehensive test suite for eink-template-gen
Run with: python -m pytest tests/test_suite.py -v
"""

import os
import tempfile

import cairo
import pytest

# Import modules to test
from eink_template_gen.devices import get_device, list_devices, snap_to_eink_greyscale
from eink_template_gen.separator_config import parse_separator_config
from eink_template_gen.separators import SEPARATOR_STYLES
from eink_template_gen.templates import (
    TEMPLATE_REGISTRY,
    create_cell_grid_template,
    create_column_template,
    create_json_layout_template,
    create_template_surface,
)
from eink_template_gen.utils import (
    calculate_adjusted_margins,
    generate_filename,
    mm_to_px,
    parse_spacing,
    px_to_mm,
    snap_spacing_to_clean_pixels,
)

# ============================================================================
# FIXTURES
# ============================================================================


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


# ============================================================================
# UTILITY FUNCTION TESTS
# ============================================================================


class TestUtilityFunctions:
    """Test utility functions for correctness"""

    def test_mm_to_px_conversion(self):
        """Test millimeter to pixel conversion"""
        assert mm_to_px(25.4, 300) == pytest.approx(300.0)
        assert mm_to_px(10, 300) == pytest.approx(118.11, rel=0.01)
        assert mm_to_px(0, 300) == 0.0

    def test_px_to_mm_conversion(self):
        """Test pixel to millimeter conversion"""
        assert px_to_mm(300, 300) == pytest.approx(25.4)
        assert px_to_mm(118.11, 300) == pytest.approx(10.0, rel=0.01)
        assert px_to_mm(0, 300) == 0.0

    def test_mm_px_round_trip(self):
        """Test round-trip conversion mm -> px -> mm"""
        original_mm = 6.5
        dpi = 300
        px = mm_to_px(original_mm, dpi)
        result_mm = px_to_mm(px, dpi)
        assert result_mm == pytest.approx(original_mm)

    def test_snap_spacing_to_clean_pixels(self):
        """Test spacing adjustment for pixel perfection"""
        # Should adjust 6mm to nearest clean value
        adjusted_mm, spacing_px, was_adjusted = snap_spacing_to_clean_pixels(6.0, 300)
        assert spacing_px == round(spacing_px)  # Should be integer
        assert abs(adjusted_mm - 6.0) <= 0.5  # Within tolerance

        # Already clean value shouldn't adjust
        clean_mm = spacing_px / (300 / 25.4)
        adjusted_mm2, spacing_px2, was_adjusted2 = snap_spacing_to_clean_pixels(clean_mm, 300)
        assert not was_adjusted2

    def test_parse_spacing_mm_mode(self):
        """Test parsing spacing in mm mode"""
        spacing_px, orig_mm, adj_mm, adjusted, mode = parse_spacing("6mm", 300, True)
        assert mode == "mm"
        assert orig_mm == 6.0
        assert spacing_px == round(spacing_px)  # Should be integer after adjustment

    def test_parse_spacing_px_mode(self):
        """Test parsing spacing in px mode"""
        spacing_px, orig_mm, adj_mm, adjusted, mode = parse_spacing("71px", 300, True)
        assert mode == "px"
        assert spacing_px == 71.0
        assert not adjusted  # No adjustment in px mode

    def test_parse_spacing_no_unit(self):
        """Test parsing spacing without unit (defaults to mm)"""
        spacing_px, orig_mm, adj_mm, adjusted, mode = parse_spacing("6", 300, True)
        assert mode == "mm"
        assert orig_mm == 6.0

    def test_calculate_adjusted_margins(self):
        """Test margin adjustment calculation"""
        # Content area of 1000px with 10px spacing
        top, bottom = calculate_adjusted_margins(1000, 10, 50)

        # Should fit exactly 100 lines (1000/10)
        # No remainder, so margins should equal base
        assert top + bottom == 100  # base_margin * 2

        # Content area that doesn't divide evenly
        top2, bottom2 = calculate_adjusted_margins(1005, 10, 50)
        # 100 lines = 1000px used, 5px remainder
        assert top2 + bottom2 == 105  # 100 base + 5 remainder

    def test_generate_filename_basic(self):
        """Test basic filename generation"""
        filename = generate_filename("lined", spacing=6, spacing_mode="mm")
        assert filename == os.path.join("lined", "6mm.png")

        filename_px = generate_filename("lined", spacing=71, spacing_mode="px")
        assert filename_px == os.path.join("lined", "71px.png")

    def test_generate_filename_with_params(self):
        """Test filename generation with parameters"""
        filename = generate_filename(
            "grid",
            spacing=6,
            spacing_mode="mm",
            line_width_px=0.5,
            columns=2,
            rows=3,
            header="bold",
            footer="wavy",
        )
        assert "grid" in filename
        assert "6mm" in filename
        assert "2c" in filename
        assert "3r" in filename
        assert "h-bold" in filename
        assert "f-wavy" in filename


# ============================================================================
# DEVICE MANAGEMENT TESTS
# ============================================================================


class TestDeviceManagement:
    """Test device configuration management"""

    def test_get_device_valid(self):
        """Test retrieving valid device"""
        device = get_device("manta")
        assert device["width"] == 1920
        assert device["height"] == 2560
        assert device["dpi"] == 300

    def test_get_device_invalid(self):
        """Test retrieving invalid device raises error"""
        with pytest.raises(ValueError, match="Unknown device"):
            get_device("nonexistent_device")

    def test_list_devices(self):
        """Test listing available devices"""
        devices = list_devices()
        assert "manta" in devices
        assert "a5x" in devices
        assert "a6x" in devices
        assert len(devices) >= 3

    def test_snap_to_eink_greyscale_float(self):
        """Test snapping float greyscale values"""
        # Should snap to nearest palette value
        grey = snap_to_eink_greyscale(0.5)
        assert 0.0 <= grey <= 1.0

        # Should handle edge cases
        assert snap_to_eink_greyscale(0.0) == 0.0
        assert snap_to_eink_greyscale(1.0) == 1.0

    def test_snap_to_eink_greyscale_int(self):
        """Test snapping integer greyscale values (0-15)"""
        # Should convert 0-15 scale to float
        grey = snap_to_eink_greyscale(8)
        assert 0.0 <= grey <= 1.0

        # Edge cases
        assert snap_to_eink_greyscale(0) == 0.0
        assert snap_to_eink_greyscale(15) == 1.0


# ============================================================================
# SEPARATOR CONFIG TESTS
# ============================================================================


class TestSeparatorConfig:
    """Test separator configuration parsing"""

    def test_parse_separator_string(self):
        """Test parsing simple separator string"""
        style, kwargs = parse_separator_config("bold")
        assert style == "bold"
        assert kwargs == {}

    def test_parse_separator_with_params(self):
        """Test parsing separator with parameters"""
        style, kwargs = parse_separator_config("wavy(amplitude=15,wavelength=120)")
        assert style == "wavy"
        assert kwargs["amplitude"] == 15.0
        assert kwargs["wavelength"] == 120.0

    def test_parse_separator_dict(self):
        """Test parsing separator as dictionary"""
        config = {"style": "wavy", "amplitude": 15, "wavelength": 120}
        style, kwargs = parse_separator_config(config)
        assert style == "wavy"
        assert kwargs["amplitude"] == 15
        assert kwargs["wavelength"] == 120

    def test_parse_separator_none(self):
        """Test parsing None separator"""
        style, kwargs = parse_separator_config(None)
        assert style is None
        assert kwargs == {}


# ============================================================================
# TEMPLATE GENERATION TESTS
# ============================================================================


class TestTemplateGeneration:
    """Test template generation functions"""

    def test_lined_template_basic(self, standard_device):
        """Test basic lined template generation"""
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

        assert isinstance(surface, cairo.ImageSurface)
        assert surface.get_width() == standard_device["width"]
        assert surface.get_height() == standard_device["height"]

    def test_dotgrid_template_basic(self, standard_device):
        """Test basic dotgrid template generation"""
        surface = create_template_surface(
            template_type="dotgrid",
            device_config=standard_device,
            spacing_str="6mm",
            margin_mm=10,
            auto_adjust_spacing=True,
            force_major_alignment=False,
            header=None,
            footer=None,
            template_kwargs={"dot_radius_px": 1.5},
        )

        assert isinstance(surface, cairo.ImageSurface)
        assert surface.get_width() == standard_device["width"]
        assert surface.get_height() == standard_device["height"]

    def test_grid_template_basic(self, standard_device):
        """Test basic grid template generation"""
        surface = create_template_surface(
            template_type="grid",
            device_config=standard_device,
            spacing_str="6mm",
            margin_mm=10,
            auto_adjust_spacing=True,
            force_major_alignment=False,
            header=None,
            footer=None,
            template_kwargs={"line_width_px": 0.5},
        )

        assert isinstance(surface, cairo.ImageSurface)

    def test_all_template_types(self, standard_device):
        """Test that all registered template types work"""
        # Exclude hybrid as it requires special handling
        template_types = [t for t in TEMPLATE_REGISTRY.keys() if t != "hybrid_lined_dotgrid"]

        for template_type in template_types:
            # Determine appropriate kwargs
            if template_type in ["dotgrid"]:
                kwargs = {"dot_radius_px": 1.5}
            elif template_type == "music_staff":
                kwargs = {"line_width_px": 0.5, "staff_gap_mm": 10}
            else:
                kwargs = {"line_width_px": 0.5}

            surface = create_template_surface(
                template_type=template_type,
                device_config=standard_device,
                spacing_str="6mm",
                margin_mm=10,
                auto_adjust_spacing=True,
                force_major_alignment=False,
                header=None,
                footer=None,
                template_kwargs=kwargs,
            )

            assert isinstance(
                surface, cairo.ImageSurface
            ), f"Failed to generate {template_type} template"

    def test_template_with_separators(self, standard_device):
        """Test template with header/footer separators"""
        surface = create_template_surface(
            template_type="lined",
            device_config=standard_device,
            spacing_str="6mm",
            margin_mm=10,
            auto_adjust_spacing=True,
            force_major_alignment=False,
            header="bold",
            footer="wavy",
            template_kwargs={"line_width_px": 0.5},
        )

        assert isinstance(surface, cairo.ImageSurface)

    def test_template_with_major_lines(self, standard_device):
        """Test template with major line emphasis"""
        surface = create_template_surface(
            template_type="grid",
            device_config=standard_device,
            spacing_str="5mm",
            margin_mm=10,
            auto_adjust_spacing=True,
            force_major_alignment=False,
            header=None,
            footer=None,
            template_kwargs={"line_width_px": 0.5, "major_every": 5, "major_width_add_px": 1.5},
        )

        assert isinstance(surface, cairo.ImageSurface)

    def test_template_px_mode(self, standard_device):
        """Test template with exact pixel spacing"""
        surface = create_template_surface(
            template_type="lined",
            device_config=standard_device,
            spacing_str="71px",
            margin_mm=10,
            auto_adjust_spacing=True,
            force_major_alignment=False,
            header=None,
            footer=None,
            template_kwargs={"line_width_px": 0.5},
        )

        assert isinstance(surface, cairo.ImageSurface)

    def test_template_no_auto_adjust(self, standard_device):
        """Test template without automatic spacing adjustment"""
        surface = create_template_surface(
            template_type="lined",
            device_config=standard_device,
            spacing_str="6mm",
            margin_mm=10,
            auto_adjust_spacing=False,
            force_major_alignment=False,
            header=None,
            footer=None,
            template_kwargs={"line_width_px": 0.5},
        )

        assert isinstance(surface, cairo.ImageSurface)


# ============================================================================
# MULTI-COLUMN/ROW TESTS
# ============================================================================


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


# ============================================================================
# JSON LAYOUT TESTS
# ============================================================================


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

        with pytest.raises(ValueError, match="invalid or missing 'region_rect'"):
            create_json_layout_template(
                config, standard_device, margin_mm=10, auto_adjust=True, force_major_alignment=False
            )


# ============================================================================
# PIXEL PERFECTION TESTS
# ============================================================================


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


# ============================================================================
# SEPARATOR TESTS
# ============================================================================


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


# ============================================================================
# EDGE CASE TESTS
# ============================================================================


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


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================


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


# ============================================================================
# FILE OUTPUT TESTS
# ============================================================================


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


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
