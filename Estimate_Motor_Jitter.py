
"""
Using calibrated settings, analyze variance of period for hall sensor triggers to determine
the uncertainty of the average rotational speed (or jitter) of the sensor. Use to validate the reliability
of the selected motor for use with this design.
"""

import numpy as np
from matplotlib import pyplot as plt
from daqhats import mcc118, hats
from daqhats_utils import select_hat_device, chan_list_to_mask
import swptools as swp
import json
import os.path
import time

# SET NUMBER OF SAMPLES HERE -> Dictated by Delay in seconds
delay = 1000
Rotation_Period = np.array([])
Timeout = delay + 5

# Initialize daq settings
daq_settings_file = 'settings/daqsettings.json'

if not os.path.isfile(daq_settings_file):
    print(f'Error: simulation file {daq_settings_file} not found.')
    print('Run \'gen_default_json.py\' to generate default file first.')
    exit()
else:
    with open(daq_settings_file, 'r') as f:
        daq_params = json.load(f)
        samples_per_channel = daq_params['samples_per_channel']
        scan_rate = daq_params['scan_rate']
        channels = daq_params['channels']

        channel_mask = chan_list_to_mask(channels)
        num_channels = len(channels)
        address = select_hat_device(hats.HatIDs.MCC_118)
        hat = mcc118(address)
        options = hats.OptionFlags.CONTINUOUS

sample_period = 1/scan_rate

# Read for as long as the timeout settings indicate. Isolate for period of each chunk.
hat.a_in_scan_start(channel_mask, samples_per_channel, scan_rate, options)
time.sleep(delay)
read_result = hat.a_in_scan_read(samples_per_channel, Timeout)

trigger_data = read_result.data[1::2]

chunk_border_indices = swp.extract_chunks(trigger_data)
num_chunks = len(chunk_border_indices)-1

hat.a_in_scan_stop()
hat.a_in_scan_cleanup()

for k in range(num_chunks):
    chunk_period = (chunk_border_indices[k+1] - chunk_border_indices[k])*sample_period
    Rotation_Period = np. append(Rotation_Period, chunk_period)

mean = np.mean(Rotation_Period)
std = np.std(Rotation_Period, ddof=1)
un_mean = std/np.sqrt(Rotation_Period.size)
maxval = max(Rotation_Period)
minval = min(Rotation_Period)

print(f"The Rotation Period is {np.around(mean,5)} +/- {np.around(un_mean,5)} with a standard deviation of {np.around(std,5)}, a maximium value of {np.around(maxval,5)} and a minimum value of {np.around(minval,5)}.")

sample_num = np.arange(0, Rotation_Period.size - 1, 1)
plt.plot(sample_num, Rotation_Period)
plt.show()