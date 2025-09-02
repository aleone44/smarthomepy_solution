import unittest
import mock.GPIO as GPIO
from unittest.mock import patch, PropertyMock
from unittest.mock import Mock

from mock.adafruit_bmp280 import Adafruit_BMP280_I2C
from mock.senseair_s8 import SenseairS8
from src.smart_room import SmartRoom


class TestSmartRoom(unittest.TestCase):
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

    @patch.object(Adafruit_BMP280_I2C, "temperature", new_callable=PropertyMock)
    @patch.object(SmartRoom, "change_servo_angle")
    def test_open_window_when_indoor_colder_than_outdoor_by_more_than_2(self, mock_servo: Mock,
                                                                        mock_temp: PropertyMock):
        smart_room = SmartRoom()
        smart_room.window_open = False
        mock_temp.side_effect = [20, 23]  # indoor, outdoor

        smart_room.manage_window()

        mock_servo.assert_called_once_with(12)
        self.assertTrue(smart_room.window_open)

    @patch.object(Adafruit_BMP280_I2C, "temperature", new_callable=PropertyMock)
    @patch.object(SmartRoom, "change_servo_angle")
    def test_close_window_when_indoor_hotter_than_outdoor_by_more_than_2(self, mock_servo: Mock,
                                                                         mock_temp: PropertyMock):
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
    def test_window_remains_unchanged_if_temperature_difference_less_than_2(self, mock_servo: Mock,
                                                                            mock_temp: PropertyMock):
        smart_room = SmartRoom()
        smart_room.window_open = True
        mock_temp.side_effect = [22, 23.5]  # diff < 2

        smart_room.manage_window()

        mock_servo.assert_not_called()
        self.assertTrue(smart_room.window_open)

    @patch.object(Adafruit_BMP280_I2C, "temperature", new_callable=PropertyMock)
    @patch.object(SmartRoom, "change_servo_angle")
    def test_window_closed_if_temperatures_out_of_range_and_already_closed(self, mock_servo: Mock,
                                                                           mock_temp: PropertyMock):
        smart_room = SmartRoom()
        smart_room.window_open = False
        mock_temp.side_effect = [17, 31]

        smart_room.manage_window()

        mock_servo.assert_called_once_with(2)
        self.assertFalse(smart_room.window_open)

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