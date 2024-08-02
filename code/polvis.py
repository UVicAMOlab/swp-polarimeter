# polvis.py
# 
# # Import vital packages/tools.
import swptools as swp
import numpy as np
from matplotlib import pyplot as plt, animation
import json
import os.path
import csv
import datetime

# When run_offline = True, simulated polarization data will be used.
run_offline = True
# Save data log in file specified within swp_settings_file.
# Select either Poincare sphere (poincare = True) or trace (poincare = False) for display.
do_save = False
poincare = True

if not run_offline:
    from daqhats import mcc118, hats
    from daqhats_utils import select_hat_device, chan_list_to_mask

# Store locations of generated simulation parameters, daq settings and spinning waveplate settings (json files).
sim_settings_file = 'settings/simsettings.json'
daq_settings_file = 'settings/daqsettings.json'
swp_settings_file = 'settings/swpsettings.json'

if run_offline:
    # Print error if the simulation settings path is not an existing regular file. File must be in location specified. 
    # Suggests generation of a default json file.
    if not os.path.isfile(sim_settings_file):
        print(f'Error: simulation file {sim_settings_file} not found.')
        print('Run \'gen_default_json.py\' to generate default file first.')
        exit()
    else:
        # Retrieving hardcoded simulation parameters from json file.
        with open(sim_settings_file,'r') as f:
            simpams = json.load(f)
            sim_digitize = simpams['sim_digitize']
            sim_siglevel = simpams['sim_siglevel']
            sim_ns_level = simpams['sim_ns_level']
            sim_DOP = simpams['sim_DOP']
            sim_bg_level = simpams['sim_bg_level']
            sim_wp_phi = simpams['sim_wp_phi']
            sim_trigger_phase = simpams['sim_trigger_phase']
            sim_poltype = simpams['sim_poltype']
            if sim_poltype == 'right':
                sim_S = np.array([1,0,0,1])
            elif sim_poltype == 'lin':
                sim_S = np.array([1,1,0,0])
            else:
                sim_S = np.array([1,np.sqrt(.3),np.sqrt(.3),np.sqrt(.4)])
                
# Print error if the Data Acquisition System (DAQ) settings path is not an existing regular file. 
# File must be in location specified. Suggests generation of a default json file.
if not os.path.isfile(daq_settings_file):
    print(f'Error: simulation file {sim_settings_file} not found.')
    print('Run \'gen_default_json.py\' to generate default file first.')
    
    exit()

else:
    # Retrieving hardcoded DAQ parameters from json file. 
    with open(daq_settings_file,'r') as f:
        daqpams = json.load(f)
        num_samples = daqpams['samples_per_channel']
        scan_rate = daqpams['scan_rate']
        channels = daqpams['channels']
        timeout = daqpams['timeout']
        # Defines sampling period, total sampling time and a time array of same length as samples.
        period = 1/scan_rate
        total_time = period*num_samples
        t = np.linspace(0, total_time-period, num_samples)
        
        # Communicating DAQ channels and address.
        if not run_offline:
            channel_mask = chan_list_to_mask(channels)
            num_channels = len(channels)
            address = select_hat_device(hats.HatIDs.MCC_118)
            hat = mcc118(address)
            options = hats.OptionFlags.CONTINUOUS

# Print error if the spinning wave plate (SWP) settings path is not an existing regular file. 
# File must be in location specified. Suggests generation of a default json file.
if not os.path.isfile(swp_settings_file):
    print(f'Error: settings file {swp_settings_file} not found.')
    print('Run \'gen_default_json.py\' to generate default file first.')
    exit()

else:

    # Retrieving hardcoded SWP settings from json file. 
    with open(swp_settings_file,'r') as f:
        swp_params = json.load(f)
        trigger_phase = swp_params['trigger_phase']
        wp_phi = swp_params['wp_phi']
        auto_scale_y_trace = swp_params['auto_scale_y_trace']
        bg_level = swp_params['bg_level']
        data_log_file = "data/" + swp_params['log_data_file']

if do_save:
    try:
        with open(data_log_file, "r") as file:
            print("CSV File Exists")
    except:
        print("Creating New CSV File")
        with open(data_log_file, 'w') as file:
            writer = csv.writer(file)
            field = ["Timestamp", "S0", "S1", "S2", "S3", "DOP"]
            writer.writerow(field)

# Setting up figure canvas.
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 5))
# Initiating plots.
ln1, = ax1.plot([], [], lw=2)
bar = ax2.bar([0, 1, 2, 3], [0, 0, 0, 0], align='center')
bar2 = ax2.bar([0, 1, 2, 3], [0, 0, 0, 0], align='edge',alpha = .3)

# ===== Axis 3 is eith scope trace or Poincare sphere
if poincare:
    ax3.get_xaxis().set_ticks([])
    ax3.get_yaxis().set_ticks([])
    ax3.axis('off')
    # ax3.get_zaxis().set_ticks([])
    ax3 = fig.add_subplot(1,3,3, projection = '3d')
    pt = ax3.scatter([0.5],[0.5],[0.707],facecolor='tab:blue',s=100)

    tht = np.linspace(0, 2 * np.pi, 360)
    ax3.plot([-1, 1], [0, 0], [0, 0], lw=2, color='black')
    ax3.plot([0, 0], [-1, 1], [0, 0], lw=2, color='black')
    ax3.plot([0, 0], [0, 0], [-1, 1], lw=2, color='black')
    ax3.plot(np.cos(tht), np.sin(tht), 0 * tht, color='lightgray', alpha=0.6)

    # ... and Wireframe
    ax3.plot(np.cos(tht), 0 * tht, np.sin(tht), color='black', alpha=0.5)
    ax3.plot(0 * tht, np.sin(tht), np.cos(tht), color='black', alpha=0.5)
    ax3.plot(np.sin(tht), np.cos(tht), 0 * tht, color='black', alpha=0.5)
    for phi0 in np.linspace(-np.pi / 2, np.pi / 2, 12):
        ax3.plot(np.cos(tht) * np.cos(phi0), np.sin(tht) * np.cos(phi0), np.sin(phi0), color='lightgray', alpha=0.4)

    # Label the axes
    ax3.text(1.4, 0, 0, 'H', color='tab:red', fontsize=20)
    ax3.text(-1., 0, 0, 'V', color='tab:red', fontsize=20)
    ax3.text(0, -1.3, 0, '-45', color='tab:red', fontsize=20)
    ax3.text(0, 0.8, 0, '+45', color='tab:red', fontsize=20)
    ax3.text(0, 0, 1.0, 'R', color='tab:red', fontsize=20)
    ax3.text(0, 0, -1.1, 'L', color='tab:red', fontsize=20)

    ln3, = ax3.plot(np.array([0,0.5]),np.array([0,0.0]),np.array([0,0.0]),color='tab:red',lw=3)

else:
    ln3, = ax3.plot([],[], lw=2, label = 'trace')
    pt = ax3.plot([],[], label = 'dummy')

# Initiating text variables.
txt1 = ax2.text(-.5250,-.970,'',fontsize = 12)
txt2 = ax1.text(-.95, 0.9, '', fontsize = 12, color = 'blue')
txt_err = ax1.text(-1.25,-1.35,'', fontsize = 10, color = 'red')


def init_animation():
    '''
    Initiates the animation for subplots including all visualization aids.
    '''
    # Graph parameters for polarization ellipse.
    ax1.set_xlim(-1.0, 1.0)
    ax1.set_ylim(-1.0, 1.0)
    ax1.set_xlabel('$E_x$')
    ax1.set_ylabel('$E_y$')
    ax1.set_title('Polarization Ellipse')
    ax1.grid()
    ax1.set_aspect('equal')

    # Add unit circle around polarization ellipse.
    t_circ = np.linspace(0,2*np.pi,1000)
    x = [np.cos(T) for T in t_circ]
    y = [np.sin(T) for T in t_circ]
    ax1.plot(x,y, color = 'gray', linestyle = '--', alpha = 0.5)

    # Graph parameters for bar graph.
    ax2.set_xlim(-0.6, 3.6)
    ax2.set_ylim(-1.0, 1.0)
    ax2.set_xticks([0, 1, 2, 3])
    ax2.set_xticklabels(['S0', 'S1', 'S2', 'S3'])
    ax2.set_xlabel('Normalized Stokes Parameters')
    ax2.set_title('Stokes Parameters')
    ax2.set_aspect(2.1)

    # Graph parameters for photodiode trace or poincare sphere.
    if not poincare:
        ax3.set_xlim(-1, 6)
        ax3.set_ylim(0, 12)
        ax3.set_xlabel('Sample Number in Data Block')
        ax3.set_ylabel('Voltage [V]')
        ax3.plot([0, num_samples],[2,2],linestyle='dashed', color='black')
        ax3.plot([0, num_samples], [10, 10], linestyle='dashed', color='black')
        ax3.set_title('Trace')
        ax3.grid()
        ax3.set_aspect(int(1000/6))
    else:
        ax3.set_title("Poincare Sphere")
        # define points for poincare sphere
        u = np.linspace(0.0, 2 * np.pi, 20)
        v = np.linspace(0.0, np.pi, 40)
        lu = np.size(u)
        lv = np.size(v)
        X = np.zeros((lu, lv))
        Y = np.zeros((lu, lv))
        Z = np.zeros((lu, lv))

        for uu in range(0, lu):
            for vv in range(0, lv):
                X[uu, vv] = np.cos(u[uu]) * np.sin(v[vv])
                Y[uu, vv] = np.sin(u[uu]) * np.sin(v[vv])
                Z[uu, vv] = np.cos(v[vv])

        # Plot the surface
        srf = ax3.plot_surface(X, Y, Z, alpha=.1, color='lightgray')

        ax3.view_init(elev=30, azim=30)
        ax3.set_aspect('auto')
    return ln1, bar, txt1, ln3, pt, txt_err

def fetch_input_data(idx):
    '''
    If run_offline, generates and returns simulated input data.
    If not run_offline, fetches live input data from raspberry pi mcc118 using daqhats and returns the 
    zeroed difference between the input and background.
    '''
    # OFFLINE SCENARIO
    
    # Define simulated angle phi and angular frequency [rad/s]. 
    if run_offline:
        sim_phi = float(idx/18.)
        w = 2*np.pi*5100/60     

        # Demonstrates different polarization types by cycling the simulated Stokes vectors
        # every 50 frames from elliptical -> linear -> circular
        
        # *** Not wanted in final version -- is that all offline sim code or just this "demo"? -WS ***
        if np.mod(int(idx/50),3) == 0:
            sim_S = 3*np.array([1, sim_DOP*np.cos(sim_phi)/2, sim_DOP*np.sin(sim_phi)/2, sim_DOP*np.sqrt(3)/2])

        elif np.mod(int(idx/50),3) == 1:            
            sim_S = 3*np.array([1, sim_DOP*np.cos(sim_phi), sim_DOP*np.sin(sim_phi), 0])

        else:
            sim_S = 3*np.array([1,0,0,sim_DOP])
        
        # Stores the simulated data input through external function along with trigger data.
        input_data = swp.simulate_polarization_data(sim_S, w, t, sim_siglevel, sim_ns_level, sim_digitize, sim_bg_level, sim_wp_phi, sim_trigger_phase)
        trigger_data = 5*(np.mod(w*t, 2*np.pi) < np.pi/12)
    
    # Begins input data scan through mcc118 hat and reads in list.
    # Stores input data and subtracts background data/light incident on photodetector.
    # *** bg_level is currently from gen_default_json and hardcoded in, need to change that -WS ***
    else:
        hat.a_in_scan_start(channel_mask, num_samples, scan_rate, options)
        read_result = hat.a_in_scan_read(num_samples, timeout)

        input_data = abs(np.array(read_result.data[::2])) - bg_level
        trigger_data = read_result.data[1::2]

        hat.a_in_scan_stop()
        hat.a_in_scan_cleanup()

    return input_data, trigger_data, idx

def animate_fun(idx):
    
    '''
    Partitions input data into chunks and reverse engineers Stokes vectors from chunks.
    
    Determines the degree of polarization (DOP) from the calculated Stokes vectors.
    
    Updates plots and text on canvas.
    '''
    
    global phs, t, sim_S
    estr = 'warnings: '

    # Retrieving input data, trigger data and the current frame index.
    input_data, trigger_data, idx = fetch_input_data(idx)

    # Separating data into "chunks" and retrieving total number of chunks created (based on swp frequency).
    chunk_border_indices = swp.extract_chunks(trigger_data, TEST = input_data)
    num_chunks = len(chunk_border_indices)-1
    
    # Holds rolling average of points per chunk (PPC). Used for accuracy warning.
    # For each chunk we calculate the 0, 2w, and 4w components, averaged over all chunks.
    Nroll = 0 
    
    # Creating chunks and calculating Stokes vectors of each chunk (see "polarimeter_analysis" doc). 
    S = np.zeros(4)
    for k in range(num_chunks):
        chunk = np.array(input_data[chunk_border_indices[k]:chunk_border_indices[k+1]]) - bg_level
        S += swp.get_stokes_from_chunk(chunk, wp_ret=wp_phi, phs_ofst=trigger_phase, verbose=False)
        # Update (PPC)
        Nroll = (Nroll*k + len(chunk))/(k+1)
    
    S /= num_chunks
    S /= S[0]
    
    # Calculating degree of polarization (DOP).
    DOP = np.sqrt(S[1]**2 + S[2]**2 + S[3]**2)
    
    # Saving if specified.
    if do_save: 
        with open(data_log_file,'a') as file:
            tnow = datetime.datetime.now()
            inwriter = csv.writer(file)
            inwriter.writerow([f"{tnow}, {S[0]}, {S[1]}, {S[2]}, {S[3]}, {DOP}"])

    # Possible warnings.
    if Nroll < 180:
        estr+=f'PPC too low ({int(Nroll)})    '
    if DOP-1 > .03:
        estr += f'Unphysical DOP ({round(DOP,3)})    '
    if np.mean(input_data) < 0.08:
        estr += f'Light level too low    '
    if num_chunks < 3:
        estr += f'Insufficient chunks    '
    if not run_offline and (np.mean(input_data) < 2 or max(input_data) > 10):
        estr += f'Signal voltage out of range (adjust gain)      '
    # Displaying error(s) and DOP on canvas.
    txt_err.set_text(f'({round(np.mean(input_data),2)},{round(S[1],2)},{round(S[2],2)},{round(S[3],2)})\n'+estr)
    
    txt1.set_text(f'DOP: {round(DOP,3)}')
    
    # Simulation error added to canvas if offline.
    if run_offline:
        sim_error = 100*abs(DOP - sim_DOP)/sim_DOP
        txt2.set_text(f'Error: {round(sim_error,1)}%')
    
    # Mean input added to canvas if online.
    else:
        txt2.set_text(f'Mean Signal: {np.mean(input_data)}')
    
    #Updating plots.
    for i in range(len(S)):
        bar[i].set_height(S[i])
        #if run_offline:
           # bar2[i].set_height(sim_S[i]/sim_S[0])

    x, y = swp.get_polarization_ellipse(S)
    ln1.set_data(x,y)

    if not poincare:
        ln3.set_data(range(len(input_data)),3*input_data)
        ax3.set_xlim(0, len(input_data))
    else:
        dtx = np.array([0,S[1]])
        dty = np.array([0,S[2]])
        dtz = np.array([0,S[3]])
        ln3.set_data(dtx, dty)
        ln3.set_3d_properties(dtz)
        pt._offsets3d = ([S[1]], [S[2]], [S[3]])

    return ln1, bar, txt1, ln3,

# Begins animation.
annie = animation.FuncAnimation(fig, animate_fun, init_func=init_animation, interval=150, cache_frame_data=False)
plt.show()
 
