** Code Overview **
This folder contains all code used to for calibration, data collection, and analysis with the polarimeter. 

The file "gen_default_json.py" is used to initialize the files for storing settings. The created files "daq_settings.json" and "sim_settings.json" should be manually adjusted to the desired paramters of the device or simulation. In contrast, "swp_settings.json" will be populated mostly by the data collected during calibration. However, for data recording a filename must be manually entered in the log_data_file parameter. The files "calibrate_background.py", "calibrate_trigger_delay.py", and "set_waveplate.py" are used for calibration. For proper calibration procedures refer to "calibration_procedure.pdf" in the documentation folder. The file "estimate_motor_jitter.py" is used to validate the selected motor for use with the device; if the period changes by more than one digitally-discritized unit between consecutive rotations, then jitter should be considered an issue and the motor should be replaced. To run the device, "polvis.py" is used and the desired display, logging, and simulation/real-time options can be specified within the program. The files "swptools.py" and "daqhats_utils.py" contain custom libraries.

Before use, the daqhats library should be downloaded from https://github.com/mccdaq/daqhats and the contained folder daqhats should be moved or copied to this folder ("code"). 

Python 3.12 is required for operation. Required libraries are numpy, matplotlib.pyplot, datetime, 

All code is open sourced and can be downloaded or distributed freely.

**Brendan Mackey**