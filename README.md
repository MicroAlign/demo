# DEMO scripts

For testing, the following scripts are provided:
- `py/run_algorithm.py` - performs the alignment using `MAMS`'s internal algorithm
- `py/keep_reading.py`  - reads continuously the power from the photodiodes and prints them
- `py/vertical_scan.py` - moves a fiber along the vertical axis and reads the coupled power

Please, make sure that the serial port in use is correctly set in each script (e.g. `COM...` on Windows, `/dev/ttyUSB...` on Linux, `/dev/cu.usbserial-...` on MacOS).
