import numpy as np
from matplotlib import pyplot as plt
from daqhats import mcc118, hats
from daqhats_utils import select_hat_device, chan_list_to_mask
import swptools as swp
import json
import os.path
import scipy.signal as sig

daq_settings_file = 'settings/daqsettings.json'
swp_settings_file = 'settings/swpsettings.json'
v_min = 0.0
v_max = 0.0
bg_level = 0.0
phi = 0

# Define function for filtering
def lowpass(data: np.ndarray, cutoff: float, sample_rate: float, poles: int = 5):
	sos = sig.butter(poles, cutoff, 'lowpass', fs=sample_rate, output='sos')
	filtered_data = sig.sosfiltfilt(sos, data)
	return filtered_data

