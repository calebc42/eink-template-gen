import os

import pytest

from eink_template_gen.utils import (
    calculate_adjusted_margins,
    generate_filename,
    mm_to_px,
    parse_spacing,
    px_to_mm,
    snap_spacing_to_clean_pixels,
)


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
