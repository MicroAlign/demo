from lib.messenger import Messenger
import sys
import math

# USB device (Use COMx for Windows)
usb_device = "/dev/cu.usbserial-AB0NQ3DC"
# Number of samples for each power measurement over which min, max, and
# average are computed
number_of_samples = 10

########################################
device = Messenger(usb_device)
NUM_OF_FIBERS = 8
lin_ave_vec = [1 for i in range(NUM_OF_FIBERS)]
log_ave_vec = [0 for i in range(NUM_OF_FIBERS)]
for fiber_nr in range(NUM_OF_FIBERS):
    if device.set_bias(fiber_nr + 1, 2048, 2048) == -1:
        sys.exit()

while True:
    for fiber_nr in range(NUM_OF_FIBERS):
        lin_ave = device.read_coupling(fiber_nr + 1, number_of_samples)[2] + 1
        log_ave = 10 * math.log(lin_ave / 4096, 10)
        lin_ave_vec[fiber_nr] = lin_ave
        log_ave_vec[fiber_nr] = log_ave
    print("\x1B[2J" + "\x1B[0;0H")
    for fiber_nr in range(NUM_OF_FIBERS):
        print(
            f'[{fiber_nr+1}]: {log_ave_vec[fiber_nr]:3.3f}   [{lin_ave_vec[fiber_nr]:4}]')
