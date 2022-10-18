import sys
try:
    from parse import parse
    import serial
except Exception as exception:
    print(exception)
    print("FATAL ERROR: Make sure that the following package are installed")
    print(" - pyserial")
    print(" - parse")
    sys.exit()


class Messenger:
    def __init__(self, serial_device):
        self.__serial_obj = serial.Serial(serial_device, 115200)
        self.__serial_obj.timeout = 1

    def __del__(self):
        self.__serial_obj.close()

    def set_bias(self, fiber_nr, bias_left, bias_right): 
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


