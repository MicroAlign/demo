try:
    from parse import parse
    import serial
except Exception as exception:
    print(exception)
    print("FATAL ERROR: Make sure that the following package are installed")
    print(" - pyserial")
    print(" - parse")
    exit()


class Messenger:
    def __init__(self, serial_device):
        self.__serial_obj = serial.Serial(serial_device, 115200)
        self.__serial_obj.timeout = 1

    def __del__(self):
        self.__serial_obj.close()

    def send_bias(self, fiber_nr, bias_left, bias_right):
        command_str = "WRITE {} {} {}\n".format(
            fiber_nr, bias_left, bias_right)
        self.__serial_obj.write(bytes(command_str, 'utf-8'))
        ans = self.__serial_obj.readline()
        if ans.decode('utf-8') == "OK\n":
            return 0
        else:
            print("Something went wrong while setting the bias. Received:")
            print(ans)
            return -1

    def read_coupling(self, fiber_nr, number_of_samples):
        command_str = "READ {} {}\n".format(fiber_nr, number_of_samples)
        self.__serial_obj.write(bytes(command_str, 'utf-8'))
        ans = self.__serial_obj.readline().decode('utf-8')
        try:
            min_max_ave_split = parse("{} {} {}\n", ans)
        except Exception as excpetion:
            print(exception)
            return -1
        return [int(min_max_ave_split[0]),
                int(min_max_ave_split[1]),
                int(min_max_ave_split[2])]


class Fiber:
    __MAX_X = 11.00001
    __MAX_Y = 20.00001
    __TANGENT_ALPHA = __MAX_Y / __MAX_X
    __MAX_BIAS = 4095
    __HALF_BIAS = __MAX_BIAS / 2.0
    __SCALE_X = __MAX_X / __MAX_BIAS * 2.0 * __TANGENT_ALPHA
    __SCALE_Y = __MAX_Y / __HALF_BIAS

    @classmethod
    def rounder(cls, val):
        return round(val * 100) / 100

    def __init__(self):
        self.__position_x = 0.0
        self.__position_y = 0.0
        self.__origin_x = 0.0
        self.__origin_y = 0.0
        self.__bias_left = 0.0
        self.__bias_right = 0.0

    def set_origin(self, axis):
        if axis == "x":
            self.__origin_x = self.__position_x
        elif axis == "y":
            self.__origin_y = self.__position_y
        else:
            print("ERROR: Invalid axis")
        print(
            f'Origin set to (x, y): ({self.__origin_x:.2f}, {self.__origin_y:.2f})')

    def bias_to_position(self, bias_left, bias_right):
        x = (bias_left - bias_right) / \
            self.__TANGENT_ALPHA / 2.0 * self.__SCALE_X
        y = ((bias_left + bias_right) / 2.0 -
             self.__HALF_BIAS) * self.__SCALE_Y
        return [x, y]

    def get_position(self):
        pos_x = self.__position_x
        pos_y = self.__position_y
        return [Fiber.rounder(pos_x), Fiber.rounder(pos_y)]

    def get_relative_position(self):
        rel_x = self.__position_x - self.__origin_x
        rel_y = self.__position_y - self.__origin_y
        return [Fiber.rounder(rel_x), Fiber.rounder(rel_y)]

    def set_position(self, x, y):
        rounded_x = Fiber.rounder(x)
        rounded_y = Fiber.rounder(y)
        bias_left = (
            rounded_y /
            self.__SCALE_Y +
            self.__TANGENT_ALPHA *
            rounded_x /
            self.__SCALE_X +
            self.__HALF_BIAS)
        bias_right = (
            rounded_y /
            self.__SCALE_Y -
            self.__TANGENT_ALPHA *
            rounded_x /
            self.__SCALE_X +
            self.__HALF_BIAS)
        if(bias_left >= 0) and (bias_left <= self.__MAX_BIAS) and (bias_right >= 0) and (bias_right <= self.__MAX_BIAS):
            self.__position_x = rounded_x
            self.__position_y = rounded_y
            self.__bias_left = bias_left
            self.__bias_right = bias_right
            return True
        else:
            print("Error: position outside range")
            return False

    def set_relative_position(self, rel_x, rel_y):
        return self.set_position(
            self.__origin_x + rel_x,
            self.__origin_y + rel_y)

    def get_origin(self):
        return [self.__origin_x, self.__origin_y]

    def get_bias(self):
        return [self.__bias_left, self.__bias_right]


class Mac:
    __NUM_OF_FIBERS = 8

    def __init__(self, serial_device):
        self.__msgr = Messenger(serial_device)
        self.__fibers = [Fiber() for i in range(self.__NUM_OF_FIBERS)]

    def __get_bias(self, fiber_nr):
        return self.__fibers[fiber_nr - 1].get_bias()

    def __get_position(self, fiber_nr):
        return self.__fibers[fiber_nr - 1].get_position()

    def __get_relative_position(self, fiber_nr):
        return self.__fibers[fiber_nr - 1].get_relative_position()

    def __get_origin(self, fiber_nr):
        return self.__fibers[fiber_nr - 1].get_origin()

    def __set_position(self, fiber_nr, new_x, new_y):
        return self.__fibers[fiber_nr - 1].set_position(new_x, new_y)

    def __set_relative_position(self, fiber_nr, new_x, new_y):
        return self.__fibers[fiber_nr - 1].set_relative_position(new_x, new_y)

    def __set_origin(self, axis, fiber_nr):
        return self.__fibers[fiber_nr - 1].set_origin(axis)

    def __is_invalid_fiber_number(self, fiber_nr):
        if (fiber_nr < 1 or fiber_nr > self.__NUM_OF_FIBERS):
            print(
                f"Error - fiber number out of range (1-{self.__NUM_OF_FIBERS})")
            return True
        return False

    def move_step(self, fiber_nr, axis, delta_um):
        if (self.__is_invalid_fiber_number(fiber_nr)):
            return None
        print(f'Moving fiber `{fiber_nr}` by `{delta_um}` um along `{axis}`')
        curr_x, curr_y = self.__get_position(fiber_nr)
        new_x = curr_x
        new_y = curr_y
        if axis == "x":
            new_x += delta_um
        elif axis == "y":
            new_y += delta_um
        else:
            print(f'ERROR: Invalid axis `{axis}`')
            return [curr_x, curr_y]
        if self.__set_position(fiber_nr, new_x, new_y):
            new_bias_left, new_bias_right = self.__get_bias(fiber_nr)
            self.__msgr.send_bias(
                fiber_nr,
                round(new_bias_left),
                round(new_bias_right))
        return self.__get_position(fiber_nr)

    def move_absolute(self, fiber_nr, axis, pos_um):
        if (self.__is_invalid_fiber_number(fiber_nr)):
            return None
        print(f'Moving fiber `{fiber_nr}` to `{pos_um}{axis}`')
        curr_x, curr_y = self.__get_position(fiber_nr)
        new_x = curr_x
        new_y = curr_y
        if axis == "x":
            new_x = pos_um
        elif axis == "y":
            new_y = pos_um
        else:
            print(f'ERROR: Invalid axis `{axis}`')
            return [curr_x, curr_y]
        if self.__set_position(fiber_nr, new_x, new_y):
            new_bias_left, new_bias_right = self.__get_bias(fiber_nr)
            self.__msgr.send_bias(
                fiber_nr,
                round(new_bias_left),
                round(new_bias_right))
        return self.__get_position(fiber_nr)

    def move_relative(self, fiber_nr, axis, rel_um):
        if (self.__is_invalid_fiber_number(fiber_nr)):
            return None
        print(f'Moving fiber `{fiber_nr}` to relative `{rel_um}{axis}`')
        curr_rel_x, curr_rel_y = self.__get_relative_position(fiber_nr)
        new_rel_x = curr_rel_x
        new_rel_y = curr_rel_y
        if axis == "x":
            new_rel_x = rel_um
        elif axis == "y":
            new_rel_y = rel_um
        else:
            print(f'ERROR: Invalid axis `{axis}`')
            return [curr_rel_x, curr_rel_y]
        if self.__set_relative_position(fiber_nr, new_rel_x, new_rel_y):
            new_bias_left, new_bias_right = self.__get_bias(fiber_nr)
            self.__msgr.send_bias(
                fiber_nr,
                round(new_bias_left),
                round(new_bias_right))
        return self.__get_position(fiber_nr)

    def set_origin(self, fiber_nr, axis):
        if (self.__is_invalid_fiber_number(fiber_nr)):
            return None
        self.__set_origin(axis, fiber_nr)
        return self.__get_position(fiber_nr)

    def get_position(self, fiber_nr, axis):
        if (self.__is_invalid_fiber_number(fiber_nr)):
            return None
        curr_x, curr_y = self.__get_position(fiber_nr)
        if axis == "x":
            return curr_x
        if axis == "y":
            return curr_y
        print(f'ERROR: Invalid axis `{axis}`')

    def get_relative_position(self, fiber_nr, axis):
        if (self.__is_invalid_fiber_number(fiber_nr)):
            return None
        rel_x, rel_y = self.__get_relative_position(fiber_nr)
        if axis == "x":
            return rel_x
        if axis == "y":
            return rel_y
        print(f'ERROR: Invalid axis `{axis}`')

    def get_power(self, pd_nr, nr_of_samples=1):
        if (self.__is_invalid_fiber_number(pd_nr)):
            return None
        return self.__msgr.read_coupling(pd_nr, nr_of_samples)[2]

    def get_power_3(self, pd_nr, nr_of_samples):
        if (self.__is_invalid_fiber_number(pd_nr)):
            return None
        return self.__msgr.read_coupling(pd_nr, nr_of_samples)
