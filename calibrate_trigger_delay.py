# run_cal_phase.py

# Grab a trace with several periods and determine phase offset by minimizing cos(2wt) term

import numpy as np
from matplotlib import pyplot as plt
from daqhats import mcc118, OptionFlags, HatIDs, HatError
from daqhats_utils import select_hat_device, chan_list_to_mask
import swptools as swp
import json
import os.path

daq_settings_file = 'settings/daqsettings.json'
swp_settings_file = 'settings/swpsettings.json'
sim_settings_file = 'settings/sim_settings_file.json'

if not os.path.isfile(daq_settings_file):
    print(f'Error: simulation file {sim_settings_file} not found.')
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
        address = select_hat_device(HatIDs.MCC_118)
        hat = mcc118(address)
        options = OptionFlags.CONTINUOUS


num_samples = samples_per_channel
period = 1/scan_rate
total_time = period*num_samples
t = np.linspace(0, total_time-period, num_samples)

# Why 9 traces?
num_traces = 9
phase_zeros = np.zeros(num_traces)

for trace in range(num_traces):
    hat.a_in_scan_start(channel_mask, samples_per_channel, scan_rate, options)
    read_result = hat.a_in_scan_read(samples_per_channel, timeout)

    input_data = read_result.data[::2]
    trigger_data = read_result.data[1::2]  

    chunk_border_indecies = swp.extract_triggers(trigger_data)
    num_chunks = len(chunk_border_indecies)-1

    hat.a_in_scan_stop()
    hat.a_in_scan_cleanup()
    
    enns = np.array([]) # what is this??? TODO: rename enns variable
    phases = np.linspace(0, 2*np.pi, 1000)
    
    # Calculating 1000 cos(2wt) terms per
    for phs in phases:
        n0 = 0
        for k in range(num_chunks):
            chunk = input_data[chunk_border_indecies[k]:chunk_border_indecies[k+1]]
            wt = np.linspace(0, 2*np.pi, len(chunk))
            n0 += np.trapz(chunk*np.cos(2*(wt-phs)), wt)
        # Dividing by num_chunks for scaling in later plot???
        enns = np.append(enns, n0/num_chunks) 

    '''
    Could use a cleaner implementation using something like
    zero_crossings = np.where(np.diff(np.sign(enns)))[0]
    however this doesnt account for exact zeros being present in the array and
    will miscount them. 
    Could noise variation in input_data cause multiple close zero crossings to 
    be read?
    '''
    # Finding where cos(2wt) crosses zero
    zero_crossings = np.array([])
    for k in range(len(enns)-2):
        if (enns[k] <= 0 and enns[k+1] > 0) or (enns[k] >= 0 and enns[k+1] < 0):
            zero_crossings = np.append(k, zero_crossings)

    zero_crossings = zero_crossings.astype(int)
    print((phases[zero_crossings]))

    phase_zeros[trace] = min(phases[zero_crossings])


print(phase_zeros)
phase_zeros_mean = np.mean(phase_zeros)
phase_zeros_standard_deviation = np.sqrt(np.var(phase_zeros))
phase_zeros_standard_error = phase_zeros_standard_deviation/np.sqrt(num_traces)

print('Zero crossing:' + str(round(phase_zeros_mean,3)) + '+/-' +str(round(phase_zeros_standard_error,3)))
print('Updating settings file ' + swp_settings_file)

with open('settings/swpsettings.json','r') as f:
    swp_params = json.load(f)
    print(f'Waveplate offset changed from '+str(round(swp_params['trigger_phase'],3)) + ' to ' + str(round(phase_zeros_mean,3)))
    swp_params['trigger_phase'] = phase_zeros_mean

with open('settings/swpsettings.json','w') as f:
    json.dump(swp_params, f)

fig, (ax1,ax2) = plt.subplots(1, 2, figsize = [13,4])

ax1.plot(phases, enns)
ax1.grid(True)
ax2.plot(t, input_data, lw=2)
ax2.plot(t, trigger_data, '--', lw=1)
ax1.plot(phase_zeros_mean, 0, 'o')
plt.show()

print('done')
