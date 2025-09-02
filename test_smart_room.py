import unittest
import mock.GPIO as GPIO
from unittest.mock import patch, PropertyMock
from unittest.mock import Mock

from mock.adafruit_bmp280 import Adafruit_BMP280_I2C
from mock.senseair_s8 import SenseairS8
from src.smart_room import SmartRoom


class TestSmartRoom(unittest.TestCase):

    @patch.object(GPIO, "input")
    def test_room_occupancy(self, mock_distance_sensor: Mock):
        smart_room = SmartRoom()
        mock_distance_sensor.return_value = True
        self.assertTrue(smart_room.check_room_occupancy())

    @patch.object(GPIO, "input")
    def test_not_room_occupancy(self, mock_distance_sensor: Mock):
        smart_room = SmartRoom()
        mock_distance_sensor.return_value = False
        self.assertFalse(smart_room.check_room_occupancy())

    @patch.object(GPIO, "input")
    def test_enough_light(self, mock_photoresistor: Mock):
        smart_room = SmartRoom()
        mock_photoresistor.return_value = True
        self.assertTrue(smart_room.check_enough_light())

    @patch.object(GPIO, "input")
    def test_not_enough_light(self, mock_photoresistor: Mock):
        smart_room = SmartRoom()
        mock_photoresistor.return_value = False
        self.assertFalse(smart_room.check_enough_light())

    @patch.object(GPIO, "input")
    @patch.object(GPIO, "output")
    def test_smartbulb_on_when_person_detected_and_not_enough_light(self, mock_lightbulb: Mock, mock_sensors: Mock):
        smart_room = SmartRoom()
        mock_sensors.side_effect = [True, False]
        smart_room.manage_light_level()
        mock_lightbulb.assert_called_with(SmartRoom.LED_PIN, True)
        self.assertTrue(smart_room.light_on)

    @patch.object(GPIO, "input")
    @patch.object(GPIO, "output")
    def test_smartbulb_off_when_person_detected_and_enough_light(self, mock_lightbulb: Mock, mock_sensors: Mock):
        smart_room = SmartRoom()
        mock_sensors.side_effect = [True, True]
        smart_room.manage_light_level()
        mock_lightbulb.assert_called_with(SmartRoom.LED_PIN, False)
        self.assertFalse(smart_room.light_on)

    @patch.object(GPIO, "input")
    @patch.object(GPIO, "output")
    def test_smartbulb_off_when_person_not_detected_and_enough_light(self, mock_lightbulb: Mock, mock_sensors: Mock):
        smart_room = SmartRoom()
        mock_sensors.side_effect = [False, True]
        smart_room.manage_light_level()
        mock_lightbulb.assert_called_with(SmartRoom.LED_PIN, False)
        self.assertFalse(smart_room.light_on)

    @patch.object(GPIO, "input")
    @patch.object(GPIO, "output")
    def test_smartbulb_off_when_person_not_detected_and_not_enough_light(self, mock_lightbulb: Mock, mock_sensors: Mock):
        smart_room = SmartRoom()
        mock_sensors.side_effect = [False, False]
        smart_room.manage_light_level()
        mock_lightbulb.assert_called_with(SmartRoom.LED_PIN, False)
        self.assertFalse(smart_room.light_on)

    @patch.object(Adafruit_BMP280_I2C, "temperature", new_callable=PropertyMock)
    def test_read_temperatures(self, mock_temperature_sensors):
        smart_room = SmartRoom()
        mock_temperature_sensors.side_effect = [21, 33]
        self.assertEqual(21, smart_room.bmp280_indor.temperature)
        self.assertEqual(33, smart_room.bmp280_outdoor.temperature)

    @patch.object(Adafruit_BMP280_I2C, "temperature", new_callable=PropertyMock)
    @patch.object(SmartRoom, "change_servo_angle")
    def test_window_stays_closed_indor_temperature_not_in_range(self, mock_servo: Mock, mock_temperature_sensors: Mock):
        smart_room = SmartRoom()
        mock_temperature_sensors.side_effect = [17.9, 30]
        smart_room.manage_window()
        mock_servo.assert_not_called()
        self.assertFalse(smart_room.window_open)

    @patch.object(Adafruit_BMP280_I2C, "temperature", new_callable=PropertyMock)
    @patch.object(SmartRoom, "change_servo_angle")
    def test_window_stays_closed_outdoor_temperature_not_in_range(self, mock_servo: Mock, mock_temperature_sensors: Mock):
        smart_room = SmartRoom()
        mock_temperature_sensors.side_effect = [18, 30.1]
        smart_room.manage_window()
        mock_servo.assert_not_called()
        self.assertFalse(smart_room.window_open)

    @patch.object(Adafruit_BMP280_I2C, "temperature", new_callable=PropertyMock)
    @patch.object(SmartRoom, "change_servo_angle")
    def test_window_opens(self, mock_servo: Mock, mock_temperature_sensors: Mock):
        smart_room = SmartRoom()
        mock_temperature_sensors.side_effect = [18, 20.1]
        smart_room.manage_window()
        mock_servo.assert_called_with(12)
        self.assertTrue(smart_room.window_open)

    @patch.object(Adafruit_BMP280_I2C, "temperature", new_callable=PropertyMock)
    @patch.object(SmartRoom, "change_servo_angle")
    def test_window_closes(self, mock_servo: Mock, mock_temperature_sensors: Mock):
        smart_room = SmartRoom()
        mock_temperature_sensors.side_effect = [30, 27.9]
        smart_room.manage_window()
        mock_servo.assert_called_with(2)
        self.assertFalse(smart_room.window_open)

    @patch.object(SenseairS8, "co2")
    @patch.object(GPIO, "output")
    def test_turn_on_fan_when_needed(self, mock_switch: Mock, mock_co2_sensor: Mock):
        smart_room = SmartRoom()
        smart_room.fan_on = False
        mock_co2_sensor.return_value = 800
        smart_room.monitor_air_quality()
        mock_switch.assert_called_with(smart_room.FAN_PIN, True)
        self.assertTrue(smart_room.fan_on)

    @patch.object(SenseairS8, "co2")
    @patch.object(GPIO, "output")
    def test_turn_off_fan_when_needed(self, mock_switch: Mock, mock_co2_sensor: Mock):
        smart_room = SmartRoom()
        smart_room.fan_on = True
        mock_co2_sensor.return_value = 499
        smart_room.monitor_air_quality()
        mock_switch.assert_called_with(smart_room.FAN_PIN, False)
        self.assertFalse(smart_room.fan_on)

    @patch.object(SenseairS8, "co2")
    @patch.object(GPIO, "output")
    def test_fan_already_turned_on(self, mock_switch: Mock, mock_co2_sensor: Mock):
        smart_room = SmartRoom()
        smart_room.fan_on = True
        mock_co2_sensor.return_value = 801
        smart_room.monitor_air_quality()
        mock_switch.assert_not_called()
        self.assertTrue(smart_room.fan_on)

    @patch.object(SenseairS8, "co2")
    @patch.object(GPIO, "output")
    def test_fan_already_turned_off(self, mock_switch: Mock, mock_co2_sensor: Mock):
        smart_room = SmartRoom()
        smart_room.fan_on = False
        mock_co2_sensor.return_value = 498
        smart_room.monitor_air_quality()
        mock_switch.assert_not_called()
        self.assertFalse(smart_room.fan_on)
