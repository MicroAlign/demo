import sys
try:
    from parse import parse
    from serial import Serial
except Exception as exception:
    print(exception)
    print("FATAL ERROR: Make sure that the following package are installed")
    print(" - pyserial")
    print(" - parse")
    sys.exit()


class Aligner:
    def __init__(
            self,
            serial_device,
            number_of_fibers,
            number_of_steps,
            number_of_samples,
            min_step_bits,
    ):
        self.__serial_obj = Serial(serial_device, 115200)
        self.__serial_obj.timeout = 10
        self.__number_of_steps = number_of_steps
        self.__number_of_samples = number_of_samples
        self.__min_step_bits = min_step_bits
        self.__number_of_fibers = number_of_fibers
        self.__coupling_vec = [
            [0 for i in range(number_of_steps)] for j in range(self.__number_of_fibers)]
        self.__bias_left_vec = [
            [0 for i in range(number_of_steps)] for j in range(self.__number_of_fibers)]
        self.__bias_right_vec = [
            [0 for i in range(number_of_steps)] for j in range(self.__number_of_fibers)]
        self.__position_x_vec = [
            [0 for i in range(number_of_steps)] for j in range(self.__number_of_fibers)]
        self.__position_y_vec = [
            [0 for i in range(number_of_steps)] for j in range(self.__number_of_fibers)]

    def __del__(self):
        self.__serial_obj.close()

    def start_alignment(self):
        command_str = "START {} {}\n".format(
            self.__number_of_samples,
            self.__min_step_bits,
        )
        self.__serial_obj.write(bytes(command_str, 'utf-8'))
        ans = self.__serial_obj.readline()
        if ans.decode('utf-8') == "STARTING\n":
            print("Alignment started")
        else:
            print("Something went wrong while starting the alignment. Received:")
            print(ans)
            return -1

        coupling_index_vec = [0 for i in range(self.__number_of_fibers)]
        bias_index_vec = [0 for i in range(self.__number_of_fibers)]

        for step in range(self.__number_of_steps):
            print("---", step, "---")
            self.__serial_obj.write(b"NEXT\n")
            coupling_data = self.__serial_obj.readline().decode('utf-8')
            self.__serial_obj.write(b"NEXT\n")
            bias_data = self.__serial_obj.readline().decode('utf-8')
 # coupling_data looks like
 # 'coupling:F2C23F6C27...'
 # 'F2' means `fiber 2`,
 # 'C23' means `coupling 23` and is the corresponding coupling
 # ...
            coupling_split = coupling_data.split('F')
            if coupling_split[0].strip('\0') != "coupling:":
                print(coupling_split)
                print("Error; expected 'coupling:', found", coupling_split[0])
                break
            for reading in range(1, len(coupling_split)):
                reading_split = parse('{}C{}', coupling_split[reading])
                fiber_index = int(reading_split[0])
                coupling_value = int(reading_split[1])
                print("index: ", fiber_index, " coupling: ", coupling_value)
                coupling_index = coupling_index_vec[fiber_index - 1]
                self.__coupling_vec[fiber_index -
                                    1][coupling_index] = coupling_value
                coupling_index_vec[fiber_index - 1] += 1

# bias_data looks like
# 'F1L31R1375F1L255R1599...'
# 'F1' means `fiber 1`
# 'L31' means `left 31` and is the corresponding bias of the left cantilever
# 'R1375' means `right 1375` and is the corresponding bias of the right cantilever
# ...
            bias_split = bias_data.split('F')
            if bias_split[0].strip('\0') != "bias:":
                print(bias_split)
                print("Error; expected 'bias:', found", bias_split[0])
                break
            for reading in range(1, len(bias_split)):
                reading_split = parse('{}L{}R{}', bias_split[reading])
                fiber_index = int(reading_split[0])
                bias_value_left = int(reading_split[1])
                bias_value_right = int(reading_split[2])
                bias_index = bias_index_vec[fiber_index - 1]
                print("index: {}, bias left: {}, bias right: {}".format(
                    fiber_index, bias_value_left, bias_value_right))
                self.__bias_left_vec[fiber_index -
                                     1][bias_index] = bias_value_left
                self.__bias_right_vec[fiber_index -
                                      1][bias_index] = bias_value_right
                self.__position_x_vec[fiber_index - \
                    1][bias_index] = (bias_value_left - bias_value_right) / 2
                self.__position_y_vec[fiber_index - 1][bias_index] = (
                    bias_value_left + bias_value_right) / 2 - 2047
                bias_index_vec[fiber_index - 1] += 1

    def stop_alignment(self):
        self.__serial_obj.write(b"STOP\n")
        if self.__serial_obj.readline().decode('utf-8') == "OK\n":
            print("Alignment stopped")

    def get_coupling_vec(self):
        return self.__coupling_vec

    def get_bias_left_vec(self):
        return self.__bias_left_vec

    def get_bias_right_vec(self):
        return self.__bias_right_vec

    def get_position_x_vec(self):
        return self.__position_x_vec

    def get_position_y_vec(self):
        return self.__position_y_vec
