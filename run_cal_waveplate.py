import numpy as np

I_bg = .15
I_min = .78
I_max = 2.72

eta = (I_min-I_bg)/(I_max-I_bg)
sig = 2*eta-1
print(f'retardance = arccos({round(sig,3)}) = {round(np.arccos(sig),3)}')
