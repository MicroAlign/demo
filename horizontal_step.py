import microalign.controller
import time

# Fiber number to toggle back and forth
fiber_nr = 2
controller = microalign.controller.Controller(8)

try:
    while True:
        controller.set_bias(fiber_nr, 0, 4095)
        print("Fiber {} step (0, 4095)".format(fiber_nr))
        time.sleep(1)
        controller.set_bias(fiber_nr, 4095, 0)
        print("Fiber {} step (4095, 0)".format(fiber_nr))
        time.sleep(1)
except KeyboardInterrupt:
    print("Fiber {} returned to middle (2048, 2048)".format(fiber_nr))
    controller.set_bias(fiber_nr, 2048, 2048)