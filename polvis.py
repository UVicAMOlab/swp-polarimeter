# ps_polvis.py

# When run_offline, simulated polarization data will be used. 
run_offline = False

# Save data log in file specified within swp_settings_file.
do_save = False

import swptools as swp
import numpy as np
from matplotlib import pyplot as plt, animation
import json
import os.path
if not run_offline:
    from daqhats import mcc118, OptionFlags, HatIDs
    from daqhats_utils import select_hat_device, chan_list_to_mask	

sim_settings_file = 'settings/simsettings.json'
daq_settings_file = 'settings/daqsettings.json'
swp_settings_file = 'settings/swpsettings.json'

# Load simulation data from json file
if run_offline:
    if not os.path.isfile(sim_settings_file):
        print(f'Error: simulation file {sim_settings_file} not found.')
        print('Run \'gen_default_json.py\' to generate default file first.')
        exit()
    else:
        with open(sim_settings_file,'r') as f:
            simpams = json.load(f)
            sim_digitize = simpams['sim_digitize']
            sim_siglevel = simpams['sim_siglevel']
            sim_ns_level = simpams['sim_ns_level']
            sim_DOP = simpams['sim_DOP']
            sim_bg_level = simpams['sim_vbias']
            sim_wp_phi = simpams['wp_phase']
            sim_trigger_phase = simpams['sim_phase_offset']
            sim_poltype = simpams['sim_poltype']

            if sim_poltype == 'right':
                sim_S = np.array([1,0,0,1])
            elif sim_poltype == 'lin':
                sim_S = np.array([1,1,0,0])
            else:
                sim_S = np.array([1,np.sqrt(.3),np.sqrt(.3),np.sqrt(.4)])

if not os.path.isfile(daq_settings_file):
    print(f'Error: simulation file {sim_settings_file} not found.')
    print('Run \'gen_default_json.py\' to generate default file first.')
    exit
else:
    with open(daq_settings_file,'r') as f:
        daqpams = json.load(f)
        num_samples = daqpams['samples_per_channel']
        scan_rate = daqpams['scan_rate']
        channels = daqpams['channels']
        timeout = daqpams['timeout']

        period = 1/scan_rate
        total_time = period*num_samples
        t = np.linspace(0, total_time-period, num_samples)

        if not run_offline:
            channel_mask = chan_list_to_mask(channels)
            num_channels = len(channels)
            address = select_hat_device(HatIDs.MCC_118)
            hat = mcc118(address)
            options = OptionFlags.CONTINUOUS

if not os.path.isfile(swp_settings_file):
    print(f'Error: settings file {swp_settings_file} not found.')
    print('Run \'gen_default_json.py\' to generate default file first.')
    exit()
else:
    # TODO: auto_scale_y_trace doesn't have an obvious purpose--investigate and 
    #       rename or remove accordingly.
    with open(swp_settings_file,'r') as f:
        swp_params = json.load(f)
        trigger_phase = swp_params['trigger_phase']
        wp_phi = swp_params['wp_phi']
        auto_scale_y_trace = swp_params['auto_scale_y_trace']
        bg_level = swp_params['bg_level']
        data_log_file = swp_params['log_data_file']

        if data_log_file != '':
            do_save = True
            with open(data_log_file,'w') as f:
                f.write('')


# Set up plot canvas
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 5))
# Plots
ln1, = ax1.plot([], [], lw=2)
bar = ax2.bar([0, 1, 2, 3], [0, 0, 0, 0], align='center')
bar2 = ax2.bar([0, 1, 2, 3], [0, 0, 0, 0], align='edge',alpha = .3)
ln3, = ax3.plot([],[], lw=2, label = 'trace')
#text variables to update
txt1 = ax1.text(-.95,0.9,'',fontsize = 12)
txt2 = ax1.text(-.95, 0.8, '', fontsize = 12, color = 'blue')
txt_err = ax1.text(-1.25,-1.35,'', fontsize = 10, color = 'red')

def init_animation():        
    #graph parameters for Ellipse
    ax1.set_xlim(-1.0, 1.0)
    ax1.set_ylim(-1.0, 1.0)
    ax1.set_xlabel('$E_x$')
    ax1.set_ylabel('$E_y$')
    ax1.set_title('Polarization Ellipse')
    ax1.grid()
    ax1.set_aspect('equal')

    #add unit circle around ellipse
    t_circ = np.linspace(0,2*np.pi,1000)
    x = [np.cos(T) for T in t_circ]
    y = [np.sin(T) for T in t_circ]
    ax1.plot(x,y, color = 'gray', linestyle = '--', alpha = 0.5)

    #graph parameters for Bar graph
    ax2.set_xlim(-0.6, 3.6)
    ax2.set_ylim(-1.05, 1.05)
    ax2.set_xticks([0, 1, 2, 3])
    ax2.set_xticklabels(['S0', 'S1', 'S2', 'S3'])
    ax2.set_xlabel('Stokes Parameter')
    #ax2.set_ylabel('Value of Stokes Parameter')
    ax2.set_title('Stokes Parameters')

    #graph parameters for Trace
    ax3.set_xlim(-1,1000)
    ax3.set_ylim(0,3)
    ax3.set_title('Trace')
    ax3.grid()

    return ln1, bar, txt1, ln3, txt_err

def fetch_input_data(idx):
    '''
    If run_offline, generates simulated input data.
    If not run_offline, fetches live input data from raspberry pi mcc118 using daqhats.
    '''
    if run_offline:
        sim_phi = float(idx/18.)
        w = 2*np.pi*5100/60        

        if np.mod(int(idx/50),3) == 0:
            sim_S = 3*np.array([1, sim_DOP*np.cos(sim_phi)/np.sqrt(2), sim_DOP*np.sin(sim_phi)/np.sqrt(2), sim_DOP/np.sqrt(2)])
#            estr = 'ellip-pol. '+estr
        elif np.mod(int(idx/50),3) == 1:            
            sim_S = 3*np.array([1, sim_DOP*np.cos(sim_phi), sim_DOP*np.sin(sim_phi), 0])
#            estr = 'lin-pol. '+estr
        else:
            sim_S = 3*np.array([1,0,0,sim_DOP])
#            estr = 'circ-pol. '+estr

        input_data = swp.simulate_polarization_data(sim_S, w, t, sim_siglevel, sim_ns_level, sim_digitize, sim_bg_level, sim_wp_phi, sim_trigger_phase)
        trigger_data = 5*(np.mod(w*t, 2*np.pi) < np.pi/12)
    else:
        hat.a_in_scan_start(channel_mask, num_samples, scan_rate, options)
        read_result = hat.a_in_scan_read(num_samples, timeout)

        input_data = abs(np.array(read_result.data[::2])) - bg_level
        trigger_data = read_result.data[1::2]
        #print(f'input_data: {input_data}'); print(f'trigger_data: {trigger_data}')

        hat.a_in_scan_stop()
        hat.a_in_scan_cleanup()

    return input_data, trigger_data, idx


# TODO: Find out what idx is and what it does. Any way to avoid it?
#       seems to only be used when run_offline
def animate_fun(idx):
    global phs, t, sim_S
    estr = 'warnings: '

    input_data, trigger_data, idx = fetch_input_data(idx)

# I'm rewriting this part of the algorithm, if only because I'm too stoopid to git it. - AM
    chunk_border_indecies = swp.extract_triggers(trigger_data, TEST = input_data)
    #print(f'Data around trigger: {input_data[d-1:d+3:1]}')
    num_chunks = len(chunk_border_indecies)-1

    Nroll = 0 # Holds rolling average of pts per chunk (PPC). Used for accuracy warning.
    # For each chunk we calculate the 0,2w, and 4w comonents, averaged over all chunks

    S = np.zeros(4)

    for k in range(num_chunks):
        chunk = np.array(input_data[chunk_border_indecies[k]:chunk_border_indecies[k+1]])
        S += swp.get_stokes_from_chunk(chunk, wp_ret=wp_phi, phs_ofst=trigger_phase, verbose=False)
        Nroll = (Nroll*k + len(chunk))/(k+1) # Update (PPC)
    #computing Stokes Parameters from Fourier Shenanigans (see analysis document)
    S /= num_chunks
    S /= S[0]

    DOP = np.sqrt(S[1]**2 + S[2]**2 + S[3]**2)
    if do_save: 
        with open(data_log_file,'a') as f:
            f.write(f'{S[1]},{S[2]},{S[3]},{DOP}\n')

# All kinds of warnings!!!
    if Nroll < 180:
        # print('Warning: insufficient points per revolution for accurate data - slow\'er down!')
        estr+=f'PPC too low ({int(Nroll)})    '
    if DOP-1 > .03:
        # print(f'Warning: Possible unphysical DOP = {round(DOP,2)} measured...')
        estr += f'Unphysical DOP ({round(DOP,3)})    '

    if np.mean(input_data) < 0.08:
        estr += f'Light level too low    '

    if num_chunks < 3:
        estr += f'Insufficient chunks    '

    txt_err.set_text(f'({round(np.mean(input_data),2)},{round(S[1],2)},{round(S[2],2)},{round(S[3],2)})\n'+estr)

    txt1.set_text(f'DOP: {round(DOP,3)}')
    if run_offline:
        sim_error = 100*abs(DOP - sim_DOP)/sim_DOP
        txt2.set_text(f'Error: {round(sim_error,1)}%')
    else:
        txt2.set_text(f'Mean Signal: {np.mean(input_data)}')

# TODO: Why is this different for simulation and for real data? Is there a 
#       better way to implement simulated data that will require less code?
    for i in range(len(S)):
        bar[i].set_height(S[i])
        if run_offline:
            bar2[i].set_height(sim_S[i]/sim_S[0])


    x, y = swp.get_polarization_ellipse(S)
    ln1.set_data(x,y)

    ln3.set_data(range(len(input_data)),input_data)
    ax3.set_xlim(0, len(input_data))
    # ln3.set_data(range(len(chunk)),chunk)
    # if auto_scale_y_trace:
    #     ax3.set_ylim(min(chunk) + 0.001, max(chunk) +0.001)
    # ax3.set_xlim(0, len(chunk))

    return ln1, bar, txt1, ln3,

annie = animation.FuncAnimation(fig, animate_fun, init_func=init_animation, interval=150)
plt.show()
 