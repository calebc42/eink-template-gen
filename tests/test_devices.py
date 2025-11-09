import pytest

from eink_template_gen.devices import get_device, list_devices, snap_to_eink_greyscale


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
