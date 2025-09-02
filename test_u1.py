import unittest
import mock.GPIO as GPIO
from unittest.mock import patch, PropertyMock
from unittest.mock import Mock

from mock.adafruit_bmp280 import Adafruit_BMP280_I2C
from mock.senseair_s8 import SenseairS8
from src.smart_room import SmartRoom


class TestSmartRoomOccupancy(unittest.TestCase):

    @patch.object(GPIO, "input")
    def test_room_occupancy_person_detected(self, mock_distance_sensor: Mock):
        """Deve restituire True se il sensore infrarosso rileva una persona."""
        mock_distance_sensor.return_value = True
        smart_room = SmartRoom()

        result = smart_room.check_room_occupancy()

        self.assertTrue(result)
        mock_distance_sensor.assert_called_once_with(smart_room.INFRARED_PIN)

    @patch.object(GPIO, "input")
    def test_room_occupancy_no_person_detected(self, mock_distance_sensor: Mock):
        """Deve restituire False se il sensore infrarosso non rileva nessuno."""
        mock_distance_sensor.return_value = False
        smart_room = SmartRoom()

        result = smart_room.check_room_occupancy()

        self.assertFalse(result)
        mock_distance_sensor.assert_called_once_with(smart_room.INFRARED_PIN)

    @patch.object(GPIO, "input")
    def test_room_occupancy_called_with_correct_pin(self, mock_distance_sensor: Mock):
        """Deve interrogare il pin corretto (22) del sensore."""
        smart_room = SmartRoom()
        smart_room.check_room_occupancy()

        mock_distance_sensor.assert_called_once_with(smart_room.INFRARED_PIN)