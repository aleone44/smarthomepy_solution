import unittest
import mock.GPIO as GPIO
from unittest.mock import patch, PropertyMock
from unittest.mock import Mock

from mock.adafruit_bmp280 import Adafruit_BMP280_I2C
from mock.senseair_s8 import SenseairS8
from src.smart_room import SmartRoom


class TestSmartRoomLightDetection(unittest.TestCase):

    @patch.object(GPIO, "input")
    def test_check_enough_light_returns_true_when_light_is_sufficient(self, mock_photoresistor: Mock):
        """Deve restituire True se c'è abbastanza luce nella stanza."""
        mock_photoresistor.return_value = True
        smart_room = SmartRoom()

        result = smart_room.check_enough_light()

        self.assertTrue(result)
        mock_photoresistor.assert_called_once_with(smart_room.PHOTO_PIN)

    @patch.object(GPIO, "input")
    def test_check_enough_light_returns_false_when_light_is_insufficient(self, mock_photoresistor: Mock):
        """Deve restituire False se non c'è abbastanza luce nella stanza."""
        mock_photoresistor.return_value = False
        smart_room = SmartRoom()

        result = smart_room.check_enough_light()

        self.assertFalse(result)
        mock_photoresistor.assert_called_once_with(smart_room.PHOTO_PIN)

    @patch.object(GPIO, "input")
    def test_check_enough_light_called_with_correct_pin(self, mock_photoresistor: Mock):
        """Verifica che venga usato il pin PHOTO_PIN (13) per leggere la luce."""
        smart_room = SmartRoom()
        smart_room.check_enough_light()

        mock_photoresistor.assert_called_once_with(smart_room.PHOTO_PIN)

    @patch.object(GPIO, "input")
    def test_check_enough_light_raises_exception_if_sensor_fails(self, mock_photoresistor: Mock):
        """Gestione resiliente: il metodo propaga un'eccezione se il sensore fallisce."""
        mock_photoresistor.side_effect = RuntimeError("Photoresistor disconnected")
        smart_room = SmartRoom()

        with self.assertRaises(RuntimeError):
            smart_room.check_enough_light()