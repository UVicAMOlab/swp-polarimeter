import numpy as np
#from scipy import integrate as sp

def get_stokes_from_chunk(chunk, wp_ret = np.pi/2, phs_ofst = 0, verbose = True):
    '''
    Reverse engineers Stoke's vectors from a given chunks data.
    - wp_ret: ??? wave plate phase (from swpsettings)
    - phs_ofst: trigger phase (from swpsettings)
    - verbose: enable logging (currently to terminal)
    '''
    
    a0,b0,c0,d0,n0 = 0,0,0,0,0

    wt = np.linspace(0,2*np.pi,len(chunk))

    a0 = np.trapz(chunk,wt)/(2*np.pi)
    n0 = np.trapz(chunk*np.cos(2*(wt-phs_ofst)),wt)/np.pi
    b0 = np.trapz(chunk*np.sin(2*(wt-phs_ofst)),wt)/np.pi
    c0 = np.trapz(chunk*np.cos(4*(wt-phs_ofst)),wt)/np.pi
    d0 = np.trapz(chunk*np.sin(4*(wt-phs_ofst)),wt)/np.pi
    
    #a0 = sp.simpson(cnk,wt)/(2*np.pi)
    #n0 = sp.simpson(cnk*np.cos(2*(wt-phs_ofst)),wt)/np.pi
    #b0 = sp.simpson(cnk*np.sin(2*(wt-phs_ofst)),wt)/np.pi
    #c0 = sp.simpson(cnk*np.cos(4*(wt-phs_ofst)),wt)/np.pi
    #d0 = sp.simpson(cnk*np.sin(4*(wt-phs_ofst)),wt)/np.pi

    cd = np.cos(wp_ret)
    sd = np.sin(wp_ret)

    S0 = 2*(a0 - c0*(1+cd)/(1-cd))
    S1 = 4*c0/(1-cd)
    S2 = 4*d0/(1-cd)
    S3 = -2*b0/sd
    
    nrm = S0
    
    if nrm == 0:
        if verbose:
            print('Error! S0 = 0. Something went terribly wrong')
        nrm=1 #This is probably sketchy
    
    if n0 > np.sqrt(S1**2 + S2**2 + S3**2)*1e-3 and verbose:
        print(f'Warning, large cos(2w) conponent detected ({n0}). Check alignment!')
    
    return np.array([S0,S1,S2,S3])/nrm

def extract_triggers(triggerData, thrsh = 1, schmidt = 10, TEST=[]):
    '''
    - partitions wave data into chunks.
        - Iterates along wave trace array until (?????) reading jumps dramatically (delta > 1).
    - number of chunks is proportional to the spinning waveplate's frequency.
    - "deadzone" is a buffer of arbitrary length to prevent the same delta being read twice, creating micro chunks
    Perhaps would be better named extract_chunks()?
    '''
    triggers = np.array([])
    deadzone = 0
    for d in range(len(triggerData)-1):
        deadzone = max(0,deadzone-1)
        if triggerData[d+1] - triggerData[d] > thrsh and deadzone == 0:
            #print(f'Data around trigger y1: {TEST[d-5:d+5:1]}')
            #print(f'Data around trigger y2: {triggerData[d-2:d+5:1]}')
            triggers = np.append(triggers,int(d))
            deadzone = schmidt
    return triggers.astype(int)


def get_polarization_ellipse(S, n_points = 200, scale_by_dop = True, verbose = True):
    '''
    given a stokes vector, return x,y points for an ellipse
    - n_points: number of points in x,y arrays
    - scale_by_dop: Scale down ellipse for partial polarization
    - verbose: enable logging (currently to terminal)
    '''    
    
    S /= S[0]
    
    DPol = np.sqrt(sum(S[1:]**2))
    for k in S:
        if abs(k) > 1:
            if verbose:
                print(f'WARNING: S[{np.where(S[::]==k)[0][0]}] is greater than 100% Clipping to 1.')
            k = k/abs(k)

    if scale_by_dop:
        S1 = S[1]/DPol
        S2 = S[2]/DPol
        S3 = S[3]/DPol

    psi = 0.5*np.arctan2(S2,S1)
    chi = 0.5*np.arcsin(S3)
    
    # TODO: Find out what a is supposed to be doing... only used in b/a.. which is just b... ???
    a = 1
    b = np.tan(chi)
    
    ba = b/a
    rot = np.matrix([[np.cos(psi), -1*np.sin(psi)],
                     [np.sin(psi), np.cos(psi)]])
    x1, x2, y1, y2 = [], [], [], []
    
    #create an x array for plotting ellipse y values
    x = np.linspace(-a, a, n_points)

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

    #x2,y2 reversed in order so that there is continuity in the ellipse (no line through the middle)
    x = (x1+x2[::-1])
    y = (y1+y2[::-1])

    return np.array(x)*DPol, np.array(y)*DPol

def simulate_polarization_data(S0, w0, t0, sig_level = 1, ns_level = 0, digitize_mV = 0, v_bias = 0, dphi = np.pi/2, ofst = 0):
    '''
    Generates simulated polarimeter data.
    given stokes vector....
    - w0:
    - t0:
    - sig_level:
    - ns_level:
    - digitize_mv:
    - v_bias:
    - dphi:
    - ofst:
    
    Output:
    - trc: 
    '''
    Npts = len(t0)
    a = S0[0]/2 + (1+np.cos(dphi))*S0[1]/4
    b = -S0[3]*np.sin(dphi)/2
    c = (1-np.cos(dphi))*S0[1]/4
    d = (1-np.cos(dphi))*S0[2]/4
    ns = ns_level*np.random.randn(Npts)
    trc =  (a + b*np.sin(2*w0*t0 - 4*np.pi*ofst) + c*np.cos(4*w0*t0 - 8*np.pi*ofst) + d*np.sin(4*w0*t0 - 8*np.pi*ofst))*sig_level + ns + v_bias
    if digitize_mV > 0:
        trc = np.around(trc*1000/digitize_mV)*digitize_mV/1000
    return trc
 
