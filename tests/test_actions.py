from unittest.mock import MagicMock, patch

from eink_template_gen import actions


def test_handle_list_devices():
    """Test handle_list_devices"""
    with patch("builtins.print") as mock_print:
        actions.handle_list_devices()
        mock_print.assert_any_call("Available devices:")

        # Check for Manta device details
        manta_found = False
        for call in mock_print.call_args_list:
            if "manta" in call[0][0] and "1920" in call[0][0] and "2560" in call[0][0]:
                manta_found = True
                break
        assert manta_found, "Manta device details not found in output"


def test_handle_set_default_device():
    """Test handle_set_default_device"""
    with patch("eink_template_gen.actions.set_default_device") as mock_set:
        args = MagicMock()
        args.device = "manta"
        actions.handle_set_default_device(args)
        mock_set.assert_called_with("manta")


def test_handle_set_default_margin():
    """Test handle_set_default_margin"""
    with patch("eink_template_gen.actions.set_default_margin") as mock_set:
        args = MagicMock()
        args.margin_mm = 10
        actions.handle_set_default_margin(args)
        mock_set.assert_called_with(10)


def test_handle_list_templates():
    """Test handle_list_templates"""
    with patch("builtins.print") as mock_print:
        actions.handle_list_templates()

        output = ""
        for call in mock_print.call_args_list:
            output += call[0][0] + "\n"

        assert "Available single templates:" in output
        assert "  lined" in output
        assert "Available cover patterns:" in output
        assert "  truchet" in output
        assert "Complex layout commands:" in output
        assert "  multi" in output
        assert "  layout" in output


def test_handle_show_spacing_info():
    """Test handle_show_spacing_info"""
    with patch("eink_template_gen.actions.print_spacing_info") as mock_print:
        args = MagicMock()
        args.device = "manta"
        args.spacing = "6mm"
        actions.handle_show_spacing_info(args)
        mock_print.assert_called_with("6mm", 300, "Supernote Manta")
