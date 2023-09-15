# Setup
Please download/clone this repository locally. Make sure you have python installed on your machine (This code is tested using python 3.9.7)
Install the required packages by running `pip install -r requirements.txt`

# MicroAlign Python library
The folder `microalign` contains a simple library for comminicating with the MicroAlign controller.
The library is able to automatically detect the connected controller over Serial. It provides functions for communicating with the controller over Serial.

# Demonstration scripts
For demonstration purposes, the following scripts are provided:
- `run_algorithm.py` - performs the alignment of the optical fibers using the algorithm implemented on the controller. Live feedback of the coupled power and fiber positions is provided.
- `keep_reading.py`  - Continually reads the optical power of all connected fibers and plots the result. Can be used during the landing of the fibers.
- `vertical_scan.py` - moves a single fiber along the vertical axis and reads the coupled power. Finally plots the result
- `horizontal_scan.py` - Same as `vertical_scan.py`, but moves along the horizontal axis.
- `diagonal_scan.py` - Same as `vertical_scan.py`, but moves along a diagonal axis.

