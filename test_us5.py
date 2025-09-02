import unittest
import mock.GPIO as GPIO
from unittest.mock import patch, Mock
from mock.adafruit_bmp280 import Adafruit_BMP280_I2C
from mock.senseair_s8 import SenseairS8
from src.smart_room import SmartRoom


class TestSmartRoomMonitorAirQuality(unittest.TestCase):

    @patch.object(GPIO, "output")
    @patch.object(SenseairS8, "co2")
    def test_turn_on_fan_when_co2_above_or_equal_800(self, mock_co2: Mock, mock_gpio: Mock):
        smart_room = SmartRoom()
        smart_room.fan_on = False
        mock_co2.return_value = 800

        smart_room.monitor_air_quality()

        mock_gpio.assert_called_once_with(smart_room.FAN_PIN, True)
        self.assertTrue(smart_room.fan_on)

    @patch.object(GPIO, "output")
    @patch.object(SenseairS8, "co2")
    def test_turn_off_fan_when_co2_below_500(self, mock_co2: Mock, mock_gpio: Mock):
        smart_room = SmartRoom()
        smart_room.fan_on = True
        mock_co2.return_value = 499

        smart_room.monitor_air_quality()

        mock_gpio.assert_called_once_with(smart_room.FAN_PIN, False)
        self.assertFalse(smart_room.fan_on)

    @patch.object(GPIO, "output")
    @patch.object(SenseairS8, "co2")
    def test_do_nothing_when_co2_between_500_and_799_and_fan_on(self, mock_co2: Mock, mock_gpio: Mock):
        smart_room = SmartRoom()
        smart_room.fan_on = True
        mock_co2.return_value = 600

        smart_room.monitor_air_quality()

        mock_gpio.assert_not_called()
        self.assertTrue(smart_room.fan_on)

    @patch.object(GPIO, "output")
    @patch.object(SenseairS8, "co2")
    def test_do_nothing_when_co2_between_500_and_799_and_fan_off(self, mock_co2: Mock, mock_gpio: Mock):
        smart_room = SmartRoom()
        smart_room.fan_on = False
        mock_co2.return_value = 700

        smart_room.monitor_air_quality()

        mock_gpio.assert_not_called()
        self.assertFalse(smart_room.fan_on)

    @patch.object(GPIO, "output")
    @patch.object(SenseairS8, "co2")
    def test_fan_remains_on_when_co2_above_800_and_already_on(self, mock_co2: Mock, mock_gpio: Mock):
        smart_room = SmartRoom()
        smart_room.fan_on = True
        mock_co2.return_value = 900

        smart_room.monitor_air_quality()

        mock_gpio.assert_not_called()
        self.assertTrue(smart_room.fan_on)

    @patch.object(GPIO, "output")
    @patch.object(SenseairS8, "co2")
    def test_fan_remains_off_when_co2_below_500_and_already_off(self, mock_co2: Mock, mock_gpio: Mock):
        smart_room = SmartRoom()
        smart_room.fan_on = False
        mock_co2.return_value = 400

        smart_room.monitor_air_quality()

        mock_gpio.assert_not_called()
        self.assertFalse(smart_room.fan_on)