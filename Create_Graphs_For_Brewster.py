import numpy as np
from matplotlib import pyplot as plt

exp_data = np.array([0.3482230514, 0.7005177426, 0.8637483034, 0.8929798524, 0.9170603792, 0.9214647926, 0.9456340673, 0.9851871167, 0.9619319023, 0.9514940958, 0.912387237, 0.889808833, 0.8446880903, 0.7823460983, 0.7327070615, 0.6606916085, 0.4077252758])
exp_loc = np.array([50, 60, 68, 70, 72, 74, 76, 77, 78, 80, 82, 84, 86, 88, 90, 92, 100])

exp_loc = exp_loc - np.full(17, 20.5)

x_err = np.full(17, 0.5)
y_err = np.array([0.0002616823219, 0.0005409843794, 0.000120352871, 0.000127979947, 0.0005109382147, 0.0010698079633, 0.0001667562615, 0.0001794071076, 0.0001788475161, 0.0001509068692, 0.00008580983905, 0.0001316971969, 0.00008726874688, 0.00006993811744, 0.0001016841748, 0.0002023579431, 0.0001231443392])
Ss = np.array([np.array([1, -0.2832322519, -0.202487943, -0.005047187408]), np.array([1,-0.5972598247, -0.3660178394, 0.001774616833]), np.array([1, -0.8001464902, -0.3252620206, -4.39E-04]), np.array([1, -0.8404834658, -0.3014521699, 0.008905654411]), np.array([1, -0.853378721, -0.335642656, 0.002028977891]), np.array([1, -0.8494620735, -0.3569864949, 0.001480202715]), np.array([1,-0.8669435472, -0.3775676408, 0.004066025581]), np.array([1, -0.9013902096, -0.3973767665, 0.01138639302]), np.array([1, -0.8895029105, -0.3661401734, -0.001358576317]), np.array([1, -0.8511239425, -0.4252392083, 0.007668718148]), np.array([1, -0.8038534886, -0.4314852044, 0.006411446679]), np.array([1, -0.8027909664, -0.3836338733, 0.008914564723]), np.array([1, -0.7974228095, -0.2784359789, -0.006564402098]), np.array([1,-0.7464786055, -0.2340849915, 0.0008396893151]), np.array([1, -0.6972255884, -0.2250671364, -0.006270837306]), np.array([1, -0.6314167958, -0.1943358718,-0.006026005324]), np.array([1, -0.4073370026, 0.01750139884, -0.0001581697837])])

def uncert(delt, sig, s):
    un_sig = sig/np.cos(delt) - sig

    ds1 = -np.sin(sig)/(1-np.cos(sig))*s[1]
    ds2 = -np.sin(sig)/(1-np.cos(sig))*s[2]
    ds3 = np.cos(sig)/(np.sin(sig))*s[3]
    ds0 = (-(1/2)*ds1 + (np.sin(sig)/2)*s[1] - (np.cos(sig)/2)*ds1)

    P = np.sqrt((s[1]/s[0])**2 + (s[2]/s[0])**2 + (s[3]/s[0])**2)
    dp = (1/P)*(s[1]*((ds1)/s[0] - s[1]*ds0/s[0]**2) + s[2]*((ds2)/s[0] - s[2]*(ds0)/s[0]**2) + s[3]*((ds3)/s[0] - s[3]*ds0/s[0]**2))
    out = np.abs(dp*un_sig)
    return out

for i in range(y_err.size):
    y_err[i] = np.sqrt((y_err[i]**2 + uncert(30*np.pi/180, 1.364, Ss[i])**2))


def theory_DOP(th_i, n1, n2):
    th_i = np.pi*th_i/180
    th_t = np.arcsin((n1/n2)*np.sin(th_i))
    r_s = (n1*np.cos(th_i) - n2*np.cos(th_t))/(n1*np.cos(th_i) + n2*np.cos(th_t))
    r_p = (n1*np.cos(th_t) - n2*np.cos(th_i))/(n1*np.cos(th_t) + n2*np.cos(th_i))

    # As s-pol and p-pol have no well-defined phase between them, the DOP is approximately the difference
    # divided by the sum or the intensities (ie no +45 or circ possible). (Is - Ip / Is + Ip).

    Rs = r_s**2; Rp = r_p**2
    DOP = (1*Rs - 1*Rp)/(1.0*Rs + 1*Rp)
    return DOP


our_DOP = lambda th: theory_DOP(th, 1, 1.52)

ths = np.linspace(20, 90, 1000)

plt.rcParams.update({'font.size': 12})
plt.plot(ths, our_DOP(ths), label = "Theory")
plt.errorbar(exp_loc, exp_data, y_err, x_err, ecolor="orange", capsize=2, fmt = ".", label = "Experimental")

plt.xlim((25, 85))
plt.ylim(0,1.05)

plt.xlabel("Angle of Incidence [degrees]")
plt.ylabel("Degree of Polarization")
plt.grid(True)
plt.legend(loc = "upper left")
plt.show()


