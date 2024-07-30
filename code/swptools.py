import numpy as np
import scipy.integrate as integ

def extract_chunks(trigger_data, threshold = 1, schmidt = 10, TEST=[]):
    '''Partitions wave data into chunks.

    - number of chunks is proportional to the spinning waveplate's frequency.
    '''
    triggers = np.array([])
    deadzone = 0

    # deadzone is a buffer of arbitrary length to prevent the same delta being read twice, creating micro chunks.
    for d in range(len(trigger_data)-1):
        deadzone = max(0, deadzone-1)
        # iterates along trigger_data until difference jumps dramatically (delta > 1).
        # TODO: could be better implemented using the diff() function?
        if trigger_data[d+1] - trigger_data[d] > threshold and deadzone == 0:
            #print(f'Data around trigger y1: {TEST[d-5:d+5:1]}')
            #print(f'Data around trigger y2: {trigger_data[d-2:d+5:1]}')
            triggers = np.append(triggers,int(d))
            deadzone = schmidt

    return triggers.astype(int)


def get_stokes_from_chunk(chunk, wp_ret = np.pi/2, phs_ofst = 0, verbose = True):
    '''For a given chunk, reverse engineers Stokes vector of the form S = [S0, S1, S2, S3] where S0 is the intensity of the optical beam, S1 preponderance of linear horizontal polarization over linear vertical polarization, S2 preponderance of linear +45 polarization over linear -45 polarization, S3 preponderance of right-circular polarization over left-circular polarization.

See section 3 "Extracting the Stokes Vectors" of polarimeter_analysis.pdf for further mathematical description of function.


Parameters:
    wp_ret (float): The waveplate retardance from swpsettings (default = pi/2).
    phs_ofst (float): Trigger phase delay from swpsettings (default = 0).
    verbose (boolean): Enables logging (currently to terminal).

Returns:
    stokes_vector (array_like): Calculated Stokes vector containing the four Stokes parameters S0, S1, S2, and S3.
    '''

    a0,b0,c0,d0,n0 = 0,0,0,0,0
    wt = np.linspace(0,2*np.pi,len(chunk))

    # Calculating coefficients of equation (21) in polarimeter_analysis.pdf
    a0 = integ.simpson(chunk,x=wt)/(2*np.pi)
    n0 = integ.simpson(chunk*np.cos(2*(wt-phs_ofst)),x=wt)/np.pi   # not found in eq. (21) -- used for alignment check
    b0 = integ.simpson(chunk*np.sin(2*(wt-phs_ofst)),x=wt)/np.pi
    c0 = integ.simpson(chunk*np.cos(4*(wt-phs_ofst)),x=wt)/np.pi
    d0 = integ.simpson(chunk*np.sin(4*(wt-phs_ofst)),x=wt)/np.pi

    cos_delta = np.cos(wp_ret)
    sin_delta = np.sin(wp_ret)

    # Calculating results of equations (22a-d) in polarimeter_analysis.pdf
    # S0 = 2*(a0 - c0*(1+cos_delta)/(1-cos_delta))    # total intensity of optical beam
    S1 = 4*c0/(1-cos_delta)                         # preponderance of LHP over LVP
    S2 = 4*d0/(1-cos_delta)                       # preponderance of L+45P over L-45P
    S3 = -2*b0/sin_delta                            # preponderance of RCP over LCP
    S0 = 2*a0 - (1+cos_delta)*S1/2

    normalization_factor = S0

    if normalization_factor == 0:
        if verbose:
            print('Error! S0 = 0. Something went terribly wrong! (Intensity (S0) is zero!)')
        normalization_factor = 1 #This is probably sketchy

    # TODO: My understanding at the moment is that the calibration technique used in calibrate_trigger_delay
    #       is by minimizing the cos(2w) component. So, shouldn't this printf() warning also indicate the 
    #       possibliblity the user didn't run the calibration?
    if n0 > np.sqrt(S1**2 + S2**2 + S3**2)*1e-3 and verbose:
        print(f'Warning, large cos(2w) conponent detected ({n0}). Check alignment!')

    return np.array([S0,S1,S2,S3])/normalization_factor


def get_polarization_ellipse(S, num_points = 200, scale_by_dop = True, verbose = True):
    '''Given an array of Stokes vectors, return x,y points for their polarization ellipse. 

    - num_points: number of points in x,y arrays
    - scale_by_dop: Scale down ellipse for partial polarization
    - verbose: enable logging (currently to terminal)
    '''
    DOP = np.sqrt(S[1]**2 + S[2]**2 + S[3]**2)/S[0]
    S = S/S[0]
    for stokes_vector in S:
        if abs(stokes_vector) > 1:
            if verbose:
                print(f'WARNING: S[{np.where(S[::]==stokes_vector)[0][0]}] is greater than 100% Clipping to 1.')
            stokes_vector = stokes_vector/abs(stokes_vector)

    if scale_by_dop:
        S1 = S[1]/DOP
        S2 = S[2]/DOP
        S3 = S[3]/DOP
    else:
        S1 = S[1]
        S2 = S[2]
        S3 = S[3]

    psi = 0.5*np.arctan2(S2,S1)
    chi = 0.5*np.arcsin(S3)

    # TODO: Find out what 'a' is supposed to be doing... only used in b/a.. which is just b... ???
    a = 1
    b = np.tan(chi)

    ba = b/a
    rot = np.matrix([[np.cos(psi), -1*np.sin(psi)],
                     [np.sin(psi), np.cos(psi)]])
    x1, x2, y1, y2 = [], [], [], []

    #create an x array for plotting ellipse y values
    x = np.linspace(-a, a, num_points)

    for x in x:
        #cartesian equation of an ellipse
        Y1 = ba*np.sqrt(a**2-x**2)
        #Y1 reflection about the x-axis
        #rotate the ellipse by psi
        XY1 = np.matrix([[x],
                         [Y1]])
        XY2 = np.matrix([[x],
                         [-Y1]])
        y1.append(float((rot*XY1)[1]))
        x1.append(float((rot*XY1)[0]))
        y2.append(float((rot*XY2)[1]))
        x2.append(float((rot*XY2)[0]))

    #x2, y2 reversed in order so that there is continuity in the ellipse (no line through the middle)
    x = (x1+x2[::-1])
    y = (y1+y2[::-1])

    return np.array(x)*DOP, np.array(y)*DOP


#TODO: It might be nice to pull all simulation calculations out of polvis.py
#      so that if someone wants to change the simulation variables they can do
#      it without having to dig through multiple files. polvis.py can just have
#      one call that returns multiple values that are then used. This will also 
#      help keep polvis.py clean and straight forward for more generic users.
def simulate_polarization_data(sim_S, w, t, sig_level = 1, ns_level = 0, digitize_mV = 0, v_bias = 0, dphi = np.pi/2, ofst = 0):
    """Generates simulated polarization data from a given simulated array of Stokes vectors.
        - w: sim angular frequency
        - t: sim time domain
        - sig_level:
        - ns_level: sim noise level
        - digitize_mv:
        - v_bias: sim background voltage from ambient light on photodiode
        - dphi: sim waveplate retardance
        - ofst: sim trigger phase offset
        Output:
        - trace: simulated array of input voltages from photodiode
    """
    num_points = len(t)

    # Constructing coefficients from equation (21) of polarimeter_analysis.pdf
    a = sim_S[0]/2 + (1+np.cos(dphi))*sim_S[1]/4
    b = -sim_S[3]*np.sin(dphi)/2
    c = (1-np.cos(dphi))*sim_S[1]/4
    d = (1-np.cos(dphi))*sim_S[2]/4

    ns = ns_level*np.random.randn(num_points)
    trace = (a + b*np.sin(2*(w*t - ofst)) + c*np.cos(4*(w*t - ofst)) + d*np.sin(4*(w*t - ofst)))*sig_level + ns + v_bias

    if digitize_mV > 0:
        trace = np.around(trace*1000/digitize_mV)*digitize_mV/1000

    return trace

