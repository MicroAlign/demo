import matplotlib.pyplot as plt
import numpy as np

import time
from microalign.controller import Controller

# Photo detector value/mW
PD_VOLTAGE_TO_MILLIWATTS_FACTOR = 3259/1 

# Number of steps that the algorithm has to perform
number_of_steps = 140
# Number of samples for each power measurement over which min, max, and
# average are computed
number_of_samples = 5
# 2^min_step_bits is the minimum step size
min_step_bits = 5  # 0-7

initial_step_bits = 8 #min_step_bits+3-9

########################################
# NOTE: Do not change NUM_OF_FIBERS - it's hardware dependent.
NUM_OF_FIBERS = 8
# Initialize Aligner
controller = Controller(NUM_OF_FIBERS)

#Set up plotting
plt.ion()

couplings = np.empty((NUM_OF_FIBERS, number_of_steps))
couplings[:] = np.nan

x_positions = np.zeros((NUM_OF_FIBERS, 1))
y_positions = np.zeros((NUM_OF_FIBERS, 1))

power_fig = plt.figure()
power_ax = []
power_lines = []

position_fig = plt.figure()
position_ax = []
position_lines = []
for i in range(NUM_OF_FIBERS):
    new_ax = power_fig.add_subplot(2, 4, i+1)
    if i > 3:
        new_ax.set_xlabel("Alignment step")
    if i == 0 or i == 4:
        new_ax.set_ylabel("Optical power [dBm]")
    new_ax.grid()
    new_ax.set_title("Fiber {}".format(i+1))
    power_ax.append(new_ax)
    
    new_lines = power_ax[i].plot(couplings[i,:])
    power_lines.append(new_lines[0])

    new_ax = position_fig.add_subplot(2, 4, i+1)
    new_ax.set_xlim(-100, 100)
    new_ax.set_ylim(-100, 100)
    new_ax.set_title("Fiber {}".format(i+1))
    if i != 0 and i != 4:
        new_ax.set_yticklabels([])
    if i != 4:
        new_ax.set_xticklabels([])
    if i > 3:
        new_ax.set_xlabel("Hor. dev. [%]")
    if i == 0 or i == 4:
        new_ax.set_ylabel("Vertical deviation [%]")
    new_ax.grid(which='minor')
    new_ax.set_aspect('equal', adjustable='box')
    position_ax.append(new_ax)
    position_ax[i].plot([0, 100, 0, -100, 0], [-100, 0, 100, 0, -100])
    new_lines = position_ax[i].scatter(x_positions[i], y_positions[i])
    position_lines.append(new_lines)


# Run algorithm and collect results
start_time = time.time()
controller.start_alignment(number_of_samples, min_step_bits, initial_step=initial_step_bits)

for step in range(number_of_steps):
    coupling_vec, left_bias_vec, right_bias_vec = controller.continue_alignment()
    left_bias_vec = np.array(left_bias_vec)
    right_bias_vec = np.array(right_bias_vec)

    x_position_vec = (left_bias_vec - right_bias_vec) / 4095.0*100.0
    y_position_vec = (left_bias_vec + right_bias_vec) / 2/ 4095.0*200.0-100.0
    coupling_vec = np.array(coupling_vec)
    coupling_vec_dB = 10* np.log10(coupling_vec/PD_VOLTAGE_TO_MILLIWATTS_FACTOR)
    coupling_vec_dB[coupling_vec_dB == -np.inf] = -35
    couplings[:,step] = coupling_vec_dB
    #print(couplings)
    for i in range(NUM_OF_FIBERS):
        power_lines[i].set_ydata(couplings[i,:])
        power_ax[i].set_ylim(np.nanmin(couplings[i,:])-0.5, np.nanmax(couplings[i,:])+0.5)
        if step > 0:
            power_ax[i].set_xlim(0, step)

        position_lines[i].set_offsets(np.c_[x_position_vec[i],y_position_vec[i]])
        #position_lines[i].set_xdata(x_position_vec[i])
    power_fig.canvas.draw()
    power_fig.canvas.flush_events()

elapsed_time = time.time() - start_time
controller.stop_alignment()
print("Aligment took {} seconds".format(elapsed_time))

plt.ioff()
plt.show()
