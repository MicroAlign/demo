import sys
try:
    import matplotlib.pyplot as plt
except BaseException:
    print("FATAL ERROR: Make sure that the following libraries are installed")
    print(" - matplotlib")
    sys.exit()
import numpy as np
import os
import time
import math
from lib.aligner import Aligner

# Number of steps that the algorithm has to perform
number_of_steps = 140
# Number of samples for each power measurement over which min, max, and
# average are computed
number_of_samples = 5
# 2^min_step_bits is the minimum step size
min_step_bits = 5  # 0-7
# USB device (Use COMx for Windows)
usb_device = "/dev/cu.usbserial-AB0NQ3DC"

########################################
# NOTE: Do not change NUM_OF_FIBERS - it's hardware dependent.
NUM_OF_FIBERS = 8
# Initialize Aligner
algr = Aligner(
    usb_device,
    NUM_OF_FIBERS,
    number_of_steps,
    number_of_samples,
    min_step_bits,
)

# Run algorithm and collect results
start_time = time.time()
failed_to_start = algr.start_alignment()
if failed_to_start:
    sys.exit()
elapsed_time = time.time() - start_time
algr.stop_alignment()

coupling_vec = algr.get_coupling_vec()
step_vec = np.linspace(0, elapsed_time, number_of_steps)

position_x_vec = algr.get_position_x_vec()
position_y_vec = algr.get_position_y_vec()
bias_left_vec = algr.get_bias_left_vec()
bias_right_vec = algr.get_bias_right_vec()

normalized_coupling_vec = [[math.log10((coupling_vec[j][i] + 1) / 4096.0) * 10.0
                            for i in range(number_of_steps)] for j in range(NUM_OF_FIBERS)]

# Coupling plotter
plt_legend = []
for fiber_index in range(NUM_OF_FIBERS):
    plt.plot(step_vec, normalized_coupling_vec[fiber_index])
    plt_legend.append("Fiber {}".format(fiber_index + 1))

plt.xlabel("Iteration Number [1]")
plt.ylabel("Normalized coupling (dB)")
plt.legend(plt_legend)
plt.grid()
if (len(sys.argv) == 2):
    file_name = '/home/antonio/tmp/test-{}_coupling.png'.format(sys.argv[1])
    plt.savefig(file_name)

# Position plotter
domain_x = [0, 2047, 0, -2048, 0]
domain_y = [2047, 0, -2048, 0, 2047]

for fiber_index in range(NUM_OF_FIBERS):
    plt.figure()
    plt.title("Fiber {}".format(fiber_index + 1))
    plt.plot(domain_x, domain_y)
    plt.xlabel("Position x (A.U.)")
    plt.ylabel("Position y (A.U.)")
    for step in range(1, len(step_vec)):
        plt.plot(position_x_vec[fiber_index][step - 1:step + 1],
                 position_y_vec[fiber_index][step - 1:step + 1],
                 alpha=0.1,
                 color='black')
    if (len(sys.argv) == 2):
        file_name = '/home/antonio/tmp/test-{}_fiber-{}.png'.format(
            sys.argv[1], fiber_index + 1)
        plt.savefig(file_name)

# Voltage plotter
for fiber_index in range(NUM_OF_FIBERS):
    plt.figure()
    plt.title("Fiber {}".format(fiber_index + 1))
    plt.xlabel("time [s]")
    plt.ylabel("Bias (A.U.)")
    plt.ylim((0, 4095))
    plt.plot(step_vec, bias_left_vec[fiber_index], drawstyle='steps-pre')
    plt.plot(step_vec, bias_right_vec[fiber_index], drawstyle='steps-pre')

plt.show()
