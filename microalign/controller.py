from parse import parse
import serial
import serial.tools.list_ports

IDN_STRING = "*IDN?\n"
EXPECTED_IDN = "MicroAlign BV., Model MAC"

class Controller:
    """
    Initialize the connection with the controller. Automatically connects to the controller connected over Serial.

    Args:
        num_fibers: Number of fibers on this controller. This is a hardware parameter and is only used during automatic alignment.

    Raises:
        ValueError: If no MicroAlign controller is detected.
    """
    def __init__(self, num_fibers):
        self._open_serial()
        self._num_fibers = num_fibers

    def __del__(self):
        if self.__serial_obj is not None:
            self.__serial_obj.close()

    def _open_serial(self):
        self.__serial_obj = None
        for port in serial.tools.list_ports.comports():
            try:
                serial_obj = serial.Serial(port.device, 115200)
                serial_obj.timeout = 1
                serial_obj.write(bytes(IDN_STRING, 'utf-8'))
                ans = serial_obj.readline()
                if ans.decode('utf-8') == "STOPPED\n":
                    print("Warning: Device found in algorithm-running state.");
                    serial_obj.write(bytes(IDN_STRING, 'utf-8'))
                    ans = serial_obj.readline()
                if ans.decode('utf-8').startswith(EXPECTED_IDN):
                    print("+ Connection established with Controller")
                    self.__serial_obj = serial_obj
                    return
            except Exception as e:
                print("Device not found or resource busy")
        if self.__serial_obj is None:
            raise(ValueError("Could not find MicroAlign Controller connected over serial"))
        
    """
    Set the left and right bias for the specified fiber.

    Args:
        fiber_nr: Fiber to set bias for. (1 based indexing, e.g. 1,2,3,...)
        bias_left: Left bias to apply. [0-4095]
        bias_right: Right bias to apply. [0-4095]
    Returns:
        0 if succesfull. -1 if an error occured.
    """
    def set_bias(self, fiber_nr, bias_left, bias_right): 
        command_str = "WRITE {} {} {}\n".format(
            fiber_nr, bias_left, bias_right)
        self.__serial_obj.write(bytes(command_str, 'utf-8'))
        ans = self.__serial_obj.readline()
        if ans.decode('utf-8') == "OK\n":
            return 0
        else:
            print("Something went wrong while setting the bias. Received:")
            print(ans.decode('utf-8'))
            return -1

    """
    Read the coupling of a specified fiber. Averaged over a number of measured samples

    Args:
        fiber_nr: Fiber to read coupling for. (1 based, e.g. 1,2,3,...)
        number_of_samples: Number of samples to average measurements over.
    Returns:
        (Minimum coupling over measurement window, Maximum coupling over measurement window, Average coupling over measurement window.)
        These measuremenets are in a linear scale.

    """
    def read_coupling(self, fiber_nr, number_of_samples):
        command_str = "READ {} {}\n".format(fiber_nr, number_of_samples)
        self.__serial_obj.write(bytes(command_str, 'utf-8'))
        ans = self.__serial_obj.readline().decode('utf-8')
        try:
            min_max_ave_split = parse("{} {} {}\n", ans)
        except Exception as excpetion:
            print(excpetion)
            return -1
        return [int(min_max_ave_split[0]),
                int(min_max_ave_split[1]),
                int(min_max_ave_split[2])]
    
    """
    Instruct the controller to start the algorithmic alignment of all fibers.

    Args:
        num_samples: Number of samples to average the measurements of coupled power over.
        min_step: Minimum step size, in bits, to adjust the position of the fibers. This has to be at least 3 bits smaller than the initial step size.
        hysteresis_kick: Optional parameter describing the amount of hysteresis kick to apply. Default: 0
        initial_step: Optional initial step size in bits. Default: 9. Can be <=12.

    Raises:
        RuntimeError: If the controller rejects the algorithm start command.
    """
    def start_alignment(self, num_samples, min_step, hysteresis_kick=None, initial_step=None):
        command = "START {} {}".format(num_samples, min_step)
        if hysteresis_kick is not None:
            command += " {}".format(hysteresis_kick)
        if hysteresis_kick is None and initial_step is not None:
            command += " 0"
        if initial_step is not None:
            command += " {}".format(initial_step)
        command += "\n"
        self.__serial_obj.write(bytes(command, 'utf-8'))
        ans = self.__serial_obj.readline()
        if ans.decode('utf-8') != "STARTING\n":
            raise(RuntimeError("Could not start algorithm. Received: {}".format(ans.decode('utf-8'))))
        
    """
    Perform one alignment step, moving the fibers and measuring the optical power.

    Returns:
        (coupling_vec, bias_left_vec, bias_right_vec): Lists with information. The index of each element corresponds to the fiber number minus 1.
        coupling_vec: A list containing the coupling of each fiber.
        bias_left_vec: Left bias applied to each fiber.
        bias_right_vec: Right bias applied to each fiber.

        Raises:
            RuntimeError: If the controller rejects the continuation of the alignment or returns unexpected data.

    """
    def continue_alignment(self):
        self.__serial_obj.write(b"NEXT\n")
        coupling_data = self.__serial_obj.readline().decode('utf-8')
        self.__serial_obj.write(b"NEXT\n")
        bias_data = self.__serial_obj.readline().decode('utf-8')
        coupling_vec = [0 for i in range(self._num_fibers)]
        bias_left_vec = [0 for i in range(self._num_fibers)]
        bias_right_vec = [0 for i in range(self._num_fibers)]

        #Parse coupling data
        coupling_split = coupling_data.split('F')
        if coupling_split[0].strip('\0') != "coupling:":
            print(coupling_split)
            raise(RuntimeError("Expected 'coupling:', found", coupling_split[0]))
        for reading in range(1, len(coupling_split)):
            reading_split = parse('{}C{}', coupling_split[reading])
            fiber_index = int(reading_split[0])
            coupling_value = int(reading_split[1])
            coupling_vec[fiber_index -
                                1] = coupling_value
            
        #Parse bias data
        bias_split = bias_data.split('F')
        if bias_split[0].strip('\0') != "bias:":
            print(bias_split)
            raise(RuntimeError("Expected 'bias:', found", bias_split[0]))
        for reading in range(1, len(bias_split)):
            reading_split = parse('{}L{}R{}', bias_split[reading])
            fiber_index = int(reading_split[0])
            bias_value_left = int(reading_split[1])
            bias_value_right = int(reading_split[2])
            bias_left_vec[fiber_index -
                                    1] = bias_value_left
            bias_right_vec[fiber_index -
                                    1] = bias_value_right
            
        return coupling_vec, bias_left_vec, bias_right_vec
            

    """
    Stop the alignment.
    Raises:
        RuntimeError: If the controller rejects the command
    """
    def stop_alignment(self):
        self.__serial_obj.write(b"STOP\n")
        if self.__serial_obj.readline().decode('utf-8') != "STOPPED\n":
            raise(RuntimeError("Error stopping alignment"))


