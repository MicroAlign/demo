from lib.messenger import Messenger
import sys

try:
    import matplotlib.pyplot as plt
except Exception as exception:
    print(exception)
    print("FATAL ERROR: Make sure that the following package are installed")
    print(" - matplotlib")
    sys.exit()

# USB device (Use COMx for Windows)
usb_device = "/dev/cu.usbserial-AB0NQ3DC"
# Fiber to move
fiber_nr = 1
# Number of samples for each power measurement over which min, max, and
# average are computed
number_of_samples = 5
# Step size used for scanning
step_size = 20

########################################
msgr = Messenger(usb_device)
bias_vec = range(0, 4095, step_size)
step_vec = range(0, len(bias_vec))
min_vec = [0 for i in step_vec]
max_vec = [0 for i in step_vec]
ave_vec = [0 for i in step_vec]

for step in step_vec:
    msgr.set_bias(fiber_nr, bias_vec[step], bias_vec[step])       # => WRITE
    min_ave_max = msgr.read_coupling(fiber_nr, number_of_samples) # => READ
    print(min_ave_max)
    min_vec[step] = min_ave_max[0]
    max_vec[step] = min_ave_max[1]
    ave_vec[step] = min_ave_max[2]

plt.plot(step_vec, min_vec)
plt.plot(step_vec, max_vec)
plt.plot(step_vec, ave_vec)
plt.show()
