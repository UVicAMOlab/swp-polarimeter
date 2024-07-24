import numpy as np
from matplotlib import pyplot as plt

exp_data = np.array([0.6605, 0.79175, 0.95425, 0.81525, 0.731])
exp_loc = np.array([0.93375, 0.96866, 0.98611, 1.00356, 1.03847])

def theory_DOP(th_i, n1, n2):
    th_t = np.arcsin((n1/n2)*np.sin(th_i))
    r_s = (n1*np.cos(th_i) - n2*np.cos(th_t))/(n1*np.cos(th_i) + n2*np.cos(th_t))
    r_p = (n1*np.cos(th_t) - n2*np.cos(th_i))/(n1*np.cos(th_t) + n2*np.cos(th_i))

    # As s-pol and p-pol have no well-defined phase between them, the DOP is approximately the difference
    # divided by the sum or the intensities (ie no +45 or circ possible). (Is - Ip / Is + Ip).

    Rs = r_s**2; Rp = r_p**2
    DOP = (Rs - Rp)/(Rs + Rp)
    return DOP

our_DOP = lambda th: theory_DOP(th, 1, 1.52)

ths = np.linspace(0.1, np.pi/2, 50)

plt.plot(ths, our_DOP(ths))
plt.plot(exp_loc, exp_data)
plt.show()


