from microalign.controller import Controller

import numpy as np
import matplotlib.pyplot as plt


# Photo detector value/mW
PD_VOLTAGE_TO_MILLIWATTS_FACTOR = 3259/1 

# Fiber to move
fiber_nr = 1
# Number of samples for each power measurement over which min, max, and
# average are computed
number_of_samples = 5
# Step size used for scanning
step_size = 20

# The left bias foltage is swept, while the right bias is kept constant.
# Select which constant value to use. (Middle is 2048)
right_bias = 2048

########################################
NUM_OF_FIBERS = 8
device = Controller(NUM_OF_FIBERS)
bias_left = np.arange(0, 4095, step_size)
bias_right = right_bias * np.ones(bias_left.shape, dtype=np.int32)
deviation_vec = (bias_left/4095.0)*200.0-100.0
num_of_steps = len(bias_left)
step_vec = range(0, num_of_steps)
min_vec = np.array([0 for i in step_vec])
max_vec = np.array([0 for i in step_vec])
ave_vec = np.array([0 for i in step_vec])

for step in step_vec:
    print("Step {}/{}".format(step + 1, num_of_steps))
    device.set_bias(fiber_nr, bias_left[step], bias_right[step])
    [min_vec[step], max_vec[step], ave_vec[step]] = device.read_coupling(fiber_nr, number_of_samples)

min_vec_dB = 10* np.log10(min_vec / PD_VOLTAGE_TO_MILLIWATTS_FACTOR)
max_vec_dB = 10* np.log10(max_vec / PD_VOLTAGE_TO_MILLIWATTS_FACTOR)
ave_vec_dB = 10* np.log10(ave_vec / PD_VOLTAGE_TO_MILLIWATTS_FACTOR)

plt.plot(deviation_vec, min_vec_dB, label="Minimum")
plt.plot(deviation_vec, max_vec_dB, label="Maximum")
plt.plot(deviation_vec, ave_vec_dB, label="Average")
plt.xlabel("Deviation from central position [%]")
plt.ylabel("Optical Power [dBm]")
plt.grid()
plt.legend(loc='lower center')
plt.title("Fiber {}".format(fiber_nr))

plt.show()
device.set_bias(fiber_nr, 2048, 2048)