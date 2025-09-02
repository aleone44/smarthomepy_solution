import unittest
import mock.GPIO as GPIO
from unittest.mock import patch, PropertyMock, Mock
from mock.adafruit_bmp280 import Adafruit_BMP280_I2C
from mock.senseair_s8 import SenseairS8
from src.smart_room import SmartRoom


class TestSmartRoomManageWindow(unittest.TestCase):

    @patch.object(Adafruit_BMP280_I2C, "temperature", new_callable=PropertyMock)
    @patch.object(SmartRoom, "change_servo_angle")
    def test_open_window_when_indoor_colder_than_outdoor_by_more_than_2(self, mock_servo: Mock, mock_temp: PropertyMock):
        smart_room = SmartRoom()
        smart_room.window_open = False
        mock_temp.side_effect = [20, 23]  # indoor, outdoor

        smart_room.manage_window()

        mock_servo.assert_called_once_with(12)
        self.assertTrue(smart_room.window_open)

    @patch.object(Adafruit_BMP280_I2C, "temperature", new_callable=PropertyMock)
    @patch.object(SmartRoom, "change_servo_angle")
    def test_close_window_when_indoor_hotter_than_outdoor_by_more_than_2(self, mock_servo: Mock, mock_temp: PropertyMock):
        smart_room = SmartRoom()
        smart_room.window_open = True
        mock_temp.side_effect = [27, 24]  # indoor, outdoor

        smart_room.manage_window()

        mock_servo.assert_called_once_with(2)
        self.assertFalse(smart_room.window_open)

    @patch.object(Adafruit_BMP280_I2C, "temperature", new_callable=PropertyMock)
    @patch.object(SmartRoom, "change_servo_angle")
    def test_window_stays_closed_indor_temperature_not_in_range(self, mock_servo: Mock, mock_temp: PropertyMock):
        smart_room = SmartRoom()
        smart_room.window_open = True
        mock_temp.side_effect = [17.9, 30]  # indoor out of range

        smart_room.manage_window()

        mock_servo.assert_called_once_with(2)
        self.assertFalse(smart_room.window_open)

    @patch.object(Adafruit_BMP280_I2C, "temperature", new_callable=PropertyMock)
    @patch.object(SmartRoom, "change_servo_angle")
    def test_window_stays_closed_outdoor_temperature_not_in_range(self, mock_servo: Mock, mock_temp: PropertyMock):
        smart_room = SmartRoom()
        smart_room.window_open = True
        mock_temp.side_effect = [22, 31.1]  # outdoor out of range

        smart_room.manage_window()

        mock_servo.assert_called_once_with(2)
        self.assertFalse(smart_room.window_open)

    @patch.object(Adafruit_BMP280_I2C, "temperature", new_callable=PropertyMock)
    @patch.object(SmartRoom, "change_servo_angle")
    def test_window_remains_unchanged_if_temperature_difference_less_than_2(self, mock_servo: Mock, mock_temp: PropertyMock):
        smart_room = SmartRoom()
        smart_room.window_open = True
        mock_temp.side_effect = [22, 23.5]  # diff < 2

        smart_room.manage_window()

        mock_servo.assert_not_called()
        self.assertTrue(smart_room.window_open)

    @patch.object(Adafruit_BMP280_I2C, "temperature", new_callable=PropertyMock)
    @patch.object(SmartRoom, "change_servo_angle")
    def test_window_closed_if_temperatures_out_of_range_and_already_closed(self, mock_servo: Mock, mock_temp: PropertyMock):
        smart_room = SmartRoom()
        smart_room.window_open = False
        mock_temp.side_effect = [17, 31]

        smart_room.manage_window()

        mock_servo.assert_called_once_with(2)
        self.assertFalse(smart_room.window_open)

