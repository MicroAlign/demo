#!/opt/homebrew/bin/python3.9
# !/usr/local/bin/python3.6
# !/usr/local/bin/python3.8
from mac import Mac
import unittest

device = Mac("/dev/cu.usbserial-AB0NR1P8")
# device = Mac("/dev/ttyUSB0")


class TestMac(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.__device = Mac("/dev/cu.usbserial-AB0NR1P8")

    def setUp(self):
        self.__device.move_absolute(2, "x", 0)
        self.__device.move_absolute(2, "y", 0)
        self.__device.set_origin(2, "x")
        self.__device.set_origin(2, "y")

    def test_move_absolute(self):
        print('Test move_absolute()')
        self.assertEqual([2.3, 0.0], self.__device.move_absolute(2, "x", 2.3))
        self.assertEqual(
            [2.3, -1.2], self.__device.move_absolute(2, "y", -1.2))
        self.assertEqual(2.3, self.__device.get_position(2, "x"))
        self.assertEqual(2.3, self.__device.get_relative_position(2, "x"))
        self.assertEqual(-1.2, self.__device.get_position(2, "y"))
        self.assertEqual(-1.2, self.__device.get_relative_position(2, "y"))

    def test_move_relative(self):
        print('Test move_relative()')
        self.__device.move_absolute(2, "x", -1.1)
        self.__device.move_absolute(2, "y", 2)
        self.assertEqual([-1.1, 2.0], self.__device.set_origin(2, "x"))
        self.assertEqual([-1.1, 2.0], self.__device.set_origin(2, "y"))
        self.assertEqual([1.2, 2.0], self.__device.move_relative(2, "x", 2.3))
        self.assertEqual(
            [1.2, 0.8], self.__device.move_relative(2, "y", -1.2))
        self.assertEqual(1.2, self.__device.get_position(2, "x"))
        self.assertEqual(2.3, self.__device.get_relative_position(2, "x"))
        self.assertEqual(0.8, self.__device.get_position(2, "y"))
        self.assertEqual(-1.2, self.__device.get_relative_position(2, "y"))

    def test_move_step(self):
        print('Test move_step()')
        self.assertEqual([0.2, 0.0], self.__device.move_absolute(2, "x", 0.2))
        self.assertEqual(
            [0.2, -0.2], self.__device.move_absolute(2, "y", -0.2))
        self.assertEqual([0.2, 0.0], self.__device.move_step(2, "y", 0.2))
        self.assertEqual(0.2, self.__device.get_position(2, "x"))
        self.assertEqual(0.0, self.__device.get_position(2, "y"))

    def test_get_power(self):
        print('Test get_power')
        power = self.__device.get_power(3)
        self.assertTrue(power >= 0)
        self.assertTrue(power < 4096)


if __name__ == "__main__":
    unittest.main()
