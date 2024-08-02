import numpy as np
from matplotlib import pyplot as plt
from daqhats import mcc118, hats
from daqhats_utils import select_hat_device, chan_list_to_mask
import swptools as swp
import json
import os.path

# NOTE: "Calibrate_Background.py" and "Calibrate_trigger_delay.py" Required Before This File Is Reliable.
# NOTE: "Input Light Must Be Horizontally Polarized Prior During Calibration.
# If Polarization State is Unknown and Polarizers Unavailable, Polvis Can Be Run With Incorrect Settings to Determine
# Approximate Direction Or Trace Can Be Observed For Same Effect.

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

num_traces = 9
maxs = np.zeros(9)
mins = np.zeros(9)
savewt = []
savechunk = []
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
		maxs[trace] = np.percentile(chunk, 99)
		mins[trace] = np.percentile(chunk, 1)

		if k == num_chunks - 1:
			savewt = np.append(savewt, wt)
			savechunk = np.append(savechunk, chunk)

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

plt.plot(savewt, savechunk)
plt.show()

print('done')
