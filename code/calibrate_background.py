import json
import numpy as np
import os
from daqhats import mcc118, hats
from daqhats_utils import select_hat_device, chan_list_to_mask

# Sets the location of storing parameters.
daq_settings_file = 'settings/daqsettings.json'
swp_settings_file = 'settings/swpsettings.json'

# Asks for user input to ensure only background light is getting through
print("Please Block Light Source.")
input("Press Enter To Continue")

# Initializes parameters for scanning with the DAQHat. Goal is to collect one sample over timeout time.
if not os.path.isfile(daq_settings_file):
    print(f'Error: simulation file {daq_settings_file} not found.')
    print('Run \'gen_default_json.py\' to generate default file first.')
    exit()
else:
    with open(daq_settings_file,'r') as f:
        daq_params = json.load(f)
        samples_per_channel = daq_params['samples_per_channel']
        scan_rate = daq_params['scan_rate']
        channels = daq_params['channels']
        timeout = daq_params['timeout']

        channel_mask = chan_list_to_mask(channels)
        num_channels = len(channels)
        address = select_hat_device(hats.HatIDs.MCC_118)
        hat = mcc118(address)
        options = hats.OptionFlags.CONTINUOUS

# Begin and collect sample data of background.
hat.a_in_scan_start(channel_mask, samples_per_channel, scan_rate, options)
read_result = hat.a_in_scan_read(samples_per_channel, timeout)
# Reads data from device.
input_data = read_result.data[::2]
hat.a_in_scan_stop()
hat.a_in_scan_cleanup()

bg_level = np.mean(input_data)

with open(swp_settings_file,'r') as f:
    params = json.load(f)
    print(f'Background Light set from '+str(round(params['bg_level'],3)) + ' to ' + str(round(bg_level,3)))
    params['bg_level'] = bg_level
with open(swp_settings_file,'w') as f:
    json.dump(params, f)


