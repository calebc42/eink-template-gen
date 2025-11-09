from unittest.mock import mock_open, patch

from eink_template_gen import config


@patch("platformdirs.user_config_dir", return_value="/tmp/config")
def test_get_config_file(mock_user_config_dir):
    """Test get_config_file"""
    from pathlib import Path

    assert config.get_config_file() == Path("/tmp/config/config.json")


@patch("builtins.open", new_callable=mock_open, read_data='{"default_device": "manta"}')
@patch("pathlib.Path.exists", return_value=True)
def test_load_config(mock_exists, mock_open):
    """Test _load_config"""
    assert config._load_config() == {"default_device": "manta"}


@patch("builtins.open", new_callable=mock_open)
def test_save_config(mock_open):
    """Test _save_config"""
    assert config._save_config({"default_device": "manta"})


@patch("eink_template_gen.config._load_config", return_value={"default_device": "manta"})
def test_get_config_value(mock_load_config):
    """Test get_config_value"""
    assert config.get_config_value("default_device") == "manta"
    assert config.get_config_value("non_existent_key", default="default") == "default"


@patch("eink_template_gen.config._load_config", return_value={})
@patch("eink_template_gen.config._save_config", return_value=True)
def test_set_config_value(mock_save_config, mock_load_config):
    """Test set_config_value"""
    assert config.set_config_value("default_device", "manta")
    mock_save_config.assert_called_with({"default_device": "manta"})


@patch("eink_template_gen.config.get_config_value", return_value="manta")
def test_get_default_device(mock_get_config_value):
    """Test get_default_device"""
    assert config.get_default_device() == "manta"


@patch("eink_template_gen.config.set_config_value", return_value=True)
def test_set_default_device(mock_set_config_value):
    """Test set_default_device"""
    assert config.set_default_device("manta")
    mock_set_config_value.assert_called_with("default_device", "manta")


@patch("eink_template_gen.config.get_config_value", return_value=10.0)
def test_get_default_margin(mock_get_config_value):
    """Test get_default_margin"""
    assert config.get_default_margin() == 10.0


@patch("eink_template_gen.config.set_config_value", return_value=True)
def test_set_default_margin(mock_set_config_value):
    """Test set_default_margin"""
    assert config.set_default_margin(10.0)
    mock_set_config_value.assert_called_with("default_margin", 10.0)
