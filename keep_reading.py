from microalign.controller import Controller
import numpy as np
from matplotlib import pyplot as plt

# Photo detector value/mW
PD_VOLTAGE_TO_MILLIWATTS_FACTOR = 3259/1 

#window size for plotting
WINDOW_SIZE = 30
# Number of samples for each power measurement over which min, max, and
# average are computed
number_of_samples = 10

########################################
NUM_OF_FIBERS = 8
device = Controller(NUM_OF_FIBERS)

lin_ave_vec = [1 for i in range(NUM_OF_FIBERS)]
log_ave_vec = [0 for i in range(NUM_OF_FIBERS)]
for fiber_nr in range(NUM_OF_FIBERS):
    if device.set_bias(fiber_nr + 1, 2048, 2048) == -1:
        raise(RuntimeError("Could not set bias"))

power_matrix = np.empty((NUM_OF_FIBERS, WINDOW_SIZE))
power_matrix[:] = np.nan

line_specs = ['-', '-', '-', '-', '--', '--', '--', '--', '--']
line_colors = ['k', 'b', 'r', 'g', 'k', 'b', 'r', 'g']

plt.ion()

fig = plt.figure()
ax = fig.add_subplot(111)
ax.grid()
ax.set_xlabel("Time [samples]")
lines = ax.plot(np.arange(-WINDOW_SIZE, 0, 1), np.transpose(power_matrix))
for i, line in enumerate(lines):
    line.set_linestyle(line_specs[i])
    line.set_color(line_colors[i])
    line.set_label('Fiber ' + str(i+1))

ax.legend(loc=2)
ax.set_ylabel('Coupled power [dB]')
while True:
    power_matrix = np.roll(power_matrix, -1, 1)
    #for data_point in range(WINDOW_SIZE):
    for fiber_nr in range(NUM_OF_FIBERS):
        lin_ave = device.read_coupling(fiber_nr + 1, number_of_samples)[2] + 1
        log_ave = 10 * np.log10(lin_ave / PD_VOLTAGE_TO_MILLIWATTS_FACTOR)

        power_matrix[fiber_nr][-1] = log_ave
        for i in range(NUM_OF_FIBERS):
            lines[i].set_ydata(power_matrix[i])
            
    ax.set_ylim(np.nanmin(power_matrix)-0.5, np.nanmax(power_matrix)+0.5)
    ax.set_xlim(-WINDOW_SIZE, 0)
    fig.canvas.draw()
    fig.canvas.flush_events()

