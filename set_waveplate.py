import json
import numpy as np

# Enter max, min, and bg voltage here
v_min = 0.84
v_max = 3.4
v_bg = 3.2e-2


eta = (v_min-v_bg)/(v_max-v_bg)
phs = np.arccos(2*eta-1)
with open('settings/swpsettings.json','r') as f:
	params = json.load(f)
	print(f'Waveplate phase retardance set from '+str(round(params['wp_phi'],3)) + ' to ' + str(round(phs,3)))
	params['wp_phi'] = phs

with open('settings/swpsettings.json','w') as f:
	json.dump(params, f)
