import cairo
import pytest

from eink_template_gen.templates import (
    TEMPLATE_REGISTRY,
    create_template_surface,
)


@pytest.fixture
def standard_device():
    """Standard device config for testing"""
    from eink_template_gen.devices import get_device

    return get_device("manta")


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
