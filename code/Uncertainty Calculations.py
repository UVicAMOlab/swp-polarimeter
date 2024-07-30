import numpy as np
import matplotlib.pyplot as plt

a = np.linspace(-0.1, 0.1, 50)
s0 = np.full(5,1)
s1 = np.array([-1,0,0,1/np.sqrt(3), -1/np.sqrt(2)])
s2 = np.array([0,-1,0,1/np.sqrt(3), 0])
s3 = np.array([0,0,1,1/np.sqrt(3), -1/2])
delta = np.pi/2

def s1p(a,i):
    out = np.cos(4*a)*s1[i] + np.sin(4*a)*s2[i]
    return out

def s2p(a,i):
    out = np.cos(4 * a) * s2[i] - np.sin(4 * a) * s1[i]
    return out

def s3p(a,i):
    out = np.cos(2 * a) * s3[i]
    return out

def s0p(a,i):
    out = s0[i] - ((1 - np.cos(delta))/2)*((np.cos(4*a) - 1)*s1[i] + np.sin(4*a)*s2[i])
    return out

for i in range(len(s0)):
   # plt.plot(a, s1p(a,i), label = "s1(a)")
   # plt.plot(a, s2p(a,i), label= "s2(a)")
    #plt.plot(a, s3p(a,i), label= "s3(a)")
   # plt.plot(a, s0p(a,i), label="s0(a)")
    plt.plot(a, np.sqrt(s1p(a,i)**2 + s2p(a,i)**2 + s3p(a,i)**2)/s0p(a,i), label="pol")
    plt.legend()
    plt.show()

