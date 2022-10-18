from mac import Mac
import unittest
import sys

FIBER_NUMBER = 2

class TestMac(unittest.TestCase):
    serial_name = ""

    @classmethod
    def setUpClass(cls):
       # Create device.
        cls.__device = Mac(cls.serial_name)

    def setUp(self):
        MAC = self.__device
        print("Reset fiber origin.")
        MAC.move_absolute(FIBER_NUMBER, "x", 0)
        MAC.move_absolute(FIBER_NUMBER, "y", 0)
        MAC.set_origin(FIBER_NUMBER, "x")
        MAC.set_origin(FIBER_NUMBER, "y")

    def test_move_absolute(self):
        MAC = self.__device
        print('Test move_absolute()')
        self.assertEqual([2.3, 0.0], MAC.move_absolute(
            FIBER_NUMBER, "x", 2.3))
        self.assertEqual(
            [2.3, -1.2], MAC.move_absolute(FIBER_NUMBER, "y", -1.2))
        self.assertEqual(2.3, MAC.get_position(FIBER_NUMBER, "x"))
        self.assertEqual(
            2.3, MAC.get_relative_position(
                FIBER_NUMBER, "x"))
        self.assertEqual(-1.2, MAC.get_position(FIBER_NUMBER, "y"))
        self.assertEqual(-1.2,
                         MAC.get_relative_position(FIBER_NUMBER, "y"))

    def test_move_relative(self):
        print('Test move_relative()')
        MAC = self.__device
        MAC.move_absolute(FIBER_NUMBER, "x", -1.1)
        MAC.move_absolute(FIBER_NUMBER, "y", 2)
        self.assertEqual(
            [-1.1, 2.0], MAC.set_origin(FIBER_NUMBER, "x"))
        self.assertEqual(
            [-1.1, 2.0], MAC.set_origin(FIBER_NUMBER, "y"))
        self.assertEqual([1.2, 2.0], MAC.move_relative(
            FIBER_NUMBER, "x", 2.3))
        self.assertEqual(
            [1.2, 0.8], MAC.move_relative(FIBER_NUMBER, "y", -1.2))
        self.assertEqual(1.2, MAC.get_position(FIBER_NUMBER, "x"))
        self.assertEqual(
            2.3, MAC.get_relative_position(
                FIBER_NUMBER, "x"))
        self.assertEqual(0.8, MAC.get_position(FIBER_NUMBER, "y"))
        self.assertEqual(-1.2,
                         MAC.get_relative_position(FIBER_NUMBER, "y"))

    def test_move_step(self):
        MAC = self.__device
        print('Test move_step()')
        self.assertEqual([0.2, 0.0], MAC.move_absolute(
            FIBER_NUMBER, "x", 0.2))
        self.assertEqual(
            [0.2, -0.2], MAC.move_absolute(FIBER_NUMBER, "y", -0.2))
        self.assertEqual([0.2, 0.0], MAC.move_step(
            FIBER_NUMBER, "y", 0.2))
        self.assertEqual(0.2, MAC.get_position(FIBER_NUMBER, "x"))
        self.assertEqual(0.0, MAC.get_position(FIBER_NUMBER, "y"))

    def test_get_power(self):
        MAC = self.__device
        print('Test get_power')
        power = MAC.get_power(3)
        self.assertTrue(power >= 0)
        self.assertTrue(power < 4096)


if __name__ == "__main__":
    if (len(sys.argv) < 2):
        print("Please specify serial port/device.")
        exit()
    TestMac.serial_name = sys.argv.pop()
    unittest.main()
