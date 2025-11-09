import cairo
import numpy as np
import pytest

from eink_template_gen.drawing import (
    draw_axis_labeling,
    draw_cell_labeling,
    draw_dot_grid,
    draw_dot_grid_with_crosshairs,
    draw_french_ruled,
    draw_grid,
    draw_hex_grid,
    draw_isometric_grid,
    draw_line_numbering,
    draw_lined_section,
    draw_manuscript_lines,
    draw_music_staff,
)


@pytest.fixture
def surface():
    """Create a Cairo surface for testing"""
    return cairo.ImageSurface(cairo.FORMAT_A8, 400, 400)


@pytest.fixture
def context(surface):
    """Create a Cairo context for testing"""
    return cairo.Context(surface)


class TestDrawingFunctions:
    """Test drawing functions"""

    def test_draw_lined_section(self, surface, context):
        """Test draw_lined_section"""
        draw_lined_section(context, 0, 400, 0, 400, 20, 1)

        # Check the output
        buf = surface.get_data()
        data = np.ndarray(shape=(400, 400), dtype=np.uint8, buffer=buf)

        # Check that there are 10 lines by checking for pixels in the expected y-coordinates
        for i in range(10):
            y = i * 20
            assert np.sum(data[y, :]) > 0

    def test_draw_dot_grid(self, surface, context):
        """Test draw_dot_grid"""
        draw_dot_grid(context, 0, 400, 0, 400, 20, 2)

        # Check the output
        buf = surface.get_data()
        data = np.ndarray(shape=(400, 400), dtype=np.uint8, buffer=buf)

        # Check a few dot positions
        for i in range(10):
            for j in range(10):
                y, x = i * 20, j * 20
                assert data[y, x] > 0

    def test_draw_grid(self, surface, context):
        """Test draw_grid"""
        draw_grid(context, 0, 400, 0, 400, 20, 1)

        # Check the output
        buf = surface.get_data()
        data = np.ndarray(shape=(400, 400), dtype=np.uint8, buffer=buf)

        # Check horizontal and vertical lines
        for i in range(10):
            y = i * 20
            assert np.sum(data[y, :]) > 0
            x = i * 20
            assert np.sum(data[:, x]) > 0

    def test_draw_manuscript_lines(self, surface, context):
        """Test draw_manuscript_lines"""
        draw_manuscript_lines(context, 0, 400, 0, 400, 30, 1)

        # Check the output
        buf = surface.get_data()
        data = np.ndarray(shape=(400, 400), dtype=np.uint8, buffer=buf)

        # Check that there are 6 groups of lines
        for i in range(6):
            y = i * 30
            assert np.sum(data[y, :]) > 0  # Ascender
            assert np.sum(data[y + 10, :]) > 0  # Midline
            assert np.sum(data[y + 20, :]) > 0  # Baseline
            assert np.sum(data[y + 30, :]) > 0  # Descender

    def test_draw_dot_grid_with_crosshairs(self, surface, context):
        """Test draw_dot_grid_with_crosshairs"""
        draw_dot_grid_with_crosshairs(
            context, 0, 400, 0, 400, 20, 2, major_every=5, crosshair_size=4
        )

        # Check the output
        buf = surface.get_data()
        data = np.ndarray(shape=(400, 400), dtype=np.uint8, buffer=buf)

        # Check that there are dots and crosshairs
        for i in range(10):
            for j in range(10):
                y, x = i * 20, j * 20
                assert data[y, x] > 0
                if i % 5 == 0 and j % 5 == 0:
                    assert data[y, x + 3] > 0

    def test_draw_french_ruled(self, surface, context):
        """Test draw_french_ruled"""
        draw_french_ruled(context, 0, 400, 0, 400, 10, 1)
        buf = surface.get_data()
        data = np.ndarray(shape=(400, 400), dtype=np.uint8, buffer=buf)
        assert np.sum(data) > 0

    def test_draw_music_staff(self, surface, context):
        """Test draw_music_staff"""
        draw_music_staff(context, 0, 400, 0, 400, 10, 300, 1, staff_gap_mm=5)
        buf = surface.get_data()
        data = np.ndarray(shape=(400, 400), dtype=np.uint8, buffer=buf)
        assert np.sum(data) > 0

    def test_draw_isometric_grid(self, surface, context):
        """Test draw_isometric_grid"""
        draw_isometric_grid(context, 0, 400, 0, 400, 20, 1)
        buf = surface.get_data()
        data = np.ndarray(shape=(400, 400), dtype=np.uint8, buffer=buf)
        assert np.sum(data) > 0

    def test_draw_hex_grid(self, surface, context):
        """Test draw_hex_grid"""
        draw_hex_grid(context, 0, 400, 0, 400, 20, 1)
        buf = surface.get_data()
        data = np.ndarray(shape=(400, 400), dtype=np.uint8, buffer=buf)
        assert np.sum(data) > 0

    def test_draw_line_numbering(self, surface, context):
        """Test draw_line_numbering"""
        config = {
            "side": "left",
            "interval": 1,
            "margin_px": 40,
            "font_size": 18,
            "grey": 8,
        }
        draw_line_numbering(context, 0, 400, 20, config)
        buf = surface.get_data()
        data = np.ndarray(shape=(400, 400), dtype=np.uint8, buffer=buf)
        assert np.sum(data) > 0

    def test_draw_cell_labeling(self, surface, context):
        """Test draw_cell_labeling"""
        canvas_size = 600
        margin = 100
        surface = cairo.ImageSurface(cairo.FORMAT_A8, canvas_size, canvas_size)
        context = cairo.Context(surface)

        config = {
            "y_axis_side": "left",
            "y_axis_padding_px": 20,
            "x_axis_side": "bottom",
            "x_axis_padding_px": 20,
            "font_size": 20,
            "grey": 0,  # Pure black
        }

        draw_cell_labeling(
            context,
            margin,
            canvas_size - margin,  # x_start, x_end
            margin,
            canvas_size - margin,  # y_start, y_end
            100,  # spacing
            config,
        )
        buf = surface.get_data()
        data = np.ndarray(shape=(canvas_size, canvas_size), dtype=np.uint8, buffer=buf)
        assert np.sum(data) > 0

    def test_draw_axis_labeling(self, surface, context):
        """Test draw_axis_labeling"""
        canvas_size = 600
        margin = 100
        surface = cairo.ImageSurface(cairo.FORMAT_A8, canvas_size, canvas_size)
        context = cairo.Context(surface)
        config = {
            "origin": "topLeft",
            "interval": 1,
            "x_axis_padding_px": 20,
            "x_axis_side": "bottom",
            "y_axis_padding_px": 20,
            "y_axis_side": "left",
            "font_size": 20,
            "grey": 0,
        }
        draw_axis_labeling(
            context,
            margin,
            canvas_size - margin,  # x_start, x_end
            margin,
            canvas_size - margin,  # y_start, y_end
            100,  # spacing
            config,
        )
        buf = surface.get_data()
        data = np.ndarray(shape=(canvas_size, canvas_size), dtype=np.uint8, buffer=buf)
        assert np.sum(data) > 0
