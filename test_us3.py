import unittest
import mock.GPIO as GPIO
from unittest.mock import patch, PropertyMock
from unittest.mock import Mock

from mock.adafruit_bmp280 import Adafruit_BMP280_I2C
from mock.senseair_s8 import SenseairS8
from src.smart_room import SmartRoom


class TestSmartRoomLightManagement(unittest.TestCase):

    @patch.object(GPIO, "output")
    @patch.object(SmartRoom, "check_enough_light")
    @patch.object(SmartRoom, "check_room_occupancy")
    def test_light_turned_on_when_occupied_and_not_enough_light(
        self, mock_occupancy, mock_light, mock_gpio_output
    ):
        """Deve accendere la luce quando c'è una persona e la luce è insufficiente."""
        mock_occupancy.return_value = True
        mock_light.return_value = False
        room = SmartRoom()

        room.manage_light_level()

        mock_gpio_output.assert_called_once_with(room.LED_PIN, True)
        self.assertTrue(room.light_on)

    @patch.object(GPIO, "output")
    @patch.object(SmartRoom, "check_enough_light")
    @patch.object(SmartRoom, "check_room_occupancy")
    def test_light_turned_off_when_occupied_and_enough_light(
        self, mock_occupancy, mock_light, mock_gpio_output
    ):
        """Deve spegnere la luce quando c'è una persona ma la luce è sufficiente."""
        mock_occupancy.return_value = True
        mock_light.return_value = True
        room = SmartRoom()

        room.manage_light_level()

        mock_gpio_output.assert_called_once_with(room.LED_PIN, False)
        self.assertFalse(room.light_on)

    @patch.object(GPIO, "output")
    @patch.object(SmartRoom, "check_enough_light")
    @patch.object(SmartRoom, "check_room_occupancy")
    def test_light_turned_off_when_not_occupied_and_not_enough_light(
        self, mock_occupancy, mock_light, mock_gpio_output
    ):
        """Deve spegnere la luce quando non c'è nessuno, anche se la luce è insufficiente."""
        mock_occupancy.return_value = False
        mock_light.return_value = False
        room = SmartRoom()

        room.manage_light_level()

        mock_gpio_output.assert_called_once_with(room.LED_PIN, False)
        self.assertFalse(room.light_on)

    @patch.object(GPIO, "output")
    @patch.object(SmartRoom, "check_enough_light")
    @patch.object(SmartRoom, "check_room_occupancy")
    def test_light_turned_off_when_not_occupied_and_enough_light(
        self, mock_occupancy, mock_light, mock_gpio_output
    ):
        """Deve spegnere la luce quando non c'è nessuno e la luce è sufficiente."""
        mock_occupancy.return_value = False
        mock_light.return_value = True
        room = SmartRoom()

        room.manage_light_level()

        mock_gpio_output.assert_called_once_with(room.LED_PIN, False)
        self.assertFalse(room.light_on)