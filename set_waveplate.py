import numpy as np
from matplotlib import pyplot as plt
from daqhats import mcc118, hats
from daqhats_utils import select_hat_device, chan_list_to_mask
import swptools as swp
import json
import os.path
import scipy.optimize as opt

# NOTE: "Calibrate_Background.py" and "Calibrate_trigger_delay.py" Required Before This File Is Reliable
daq_settings_file = 'settings/daqsettings.json'
swp_settings_file = 'settings/swpsettings.json'
v_min = 0.0
v_max = 0.0
bg_level = 0.0
phi = 0

# Grab Sampling Data from Json File
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
# Initialize background from swp_settings
if not os.path.isfile(swp_settings_file):
	print(f'Error: simulation file {swp_settings_file} not found.')
	print('Run \'gen_default_json.py\' to generate default file first.')
	exit()
else:
	with open(swp_settings_file,'r') as f:
		swp_params = json.load(f)
		bg_level = swp_params["bg_level"]
		phi = swp_params["trigger_phase"]

def s(wt, A, B):
	return A*np.sin(wt-phi) + B

num_traces = 9
maxs = np.zeros(9)
mins = np.zeros(9)
for trace in range(num_traces):
	hat.a_in_scan_start(channel_mask, samples_per_channel, scan_rate, options)
	read_result = hat.a_in_scan_read(samples_per_channel, timeout)
	# Reads data from device.
	input_data = read_result.data[::2]
	trigger_data = read_result.data[1::2]

	chunk_border_indices = swp.extract_chunks(trigger_data)
	num_chunks = len(chunk_border_indices) - 1

	hat.a_in_scan_stop()
	hat.a_in_scan_cleanup()

	for k in range(num_chunks):
		chunk = input_data[chunk_border_indices[k]:chunk_border_indices[k + 1]]
		wt = np.linspace(0, 2 * np.pi, len(chunk))
		vars = opt.curve_fit(s, wt, chunk)[0]
		maxs[trace] = vars[1] + vars[0]
		mins[trace] = vars[1] - vars[0]

v_max = np.mean(maxs)
v_min = np.mean(mins)

eta = (v_min-bg_level)/(v_max-bg_level)
phs = np.arccos(2*eta-1)
with open(swp_settings_file,'r') as f:
	params = json.load(f)
	print(f'Waveplate phase retardance set from '+str(round(params['wp_phi'],3)) + ' to ' + str(round(phs,3)))
	params['wp_phi'] = phs

with open(swp_settings_file,'w') as f:
	json.dump(params, f)
