from eink_template_gen.separator_config import parse_separator_config


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
