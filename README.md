## Spinning Waveplate Polarimeter

*Using a rotating quarter waveplate, a photodiode, and a few Python scripts, we can produce real-time visualization of the polarization state of incident light. This fully integrated system is easily calibrated and an affordable alternative to other fussy optical technologies making it ideal for research laboratories and educational environments.*


# Real-time Detection of Polarization of Incident Light

Initially, we use the API provided by the DAQ hat to acquire a fixed number of samples for processing; typically, this is 1000 samples at 20 ksps when the waveplate is spinning between 4500 to 5500 RPM. The raw data input is then divided into segments. Each segment is numerically integrated to determine the Fourier coefficients, and furthermore, the Stokes parameters and polarization state. To minimize any statistical errors, the mean result over several segments is considered and the display is refreshed at a rate of 4 Hz.

The reconstruction of the Stokes vector is achieved by calculating the incident intensity upon the rotating waveplate as a function of the rotation angle when aligned horizontally. We assume that the waveplate has some arbitrary retardance instead of considering a precisely calibrated quarter waveplate. Lastly, using the orthogonality of trigonometric functions we can extract the Stokes parameters S<sub>0</sub>, S<sub>1</sub>, S<sub>2</sub> and S<sub>3</sub>. Using the Stokes parameters, the degree of polarization of the incident light is also obtained through a trivial calculation.

Please see our more rigorous [explanation]#(REPLACE WITH PAPER LOCATION) and [analysis](https://github.com/UVicAMOlab/swp-polarimeter/blob/main/resources-and-documentation/analysis/Polarimeter_Analysis.pdf) for more details.

# Information Obtained from Polarimeter

The continuous data input through the Raspberry Pi's MCC DAQ hat along with the included software allows for the real-time determination and visualization of several polarization parameters. These include:

- Polarization ellipse/type of polarization (2D or 3D available)
- Stokes parameters as bar graph
- Poincaré sphere
- Degree of polarization
- Mean input signal over several segments of data
- Waveform incident on photodiode

# Getting Started

**PHYSICAL APPARATUS:**

Our spinning waveplate polarimeter utilizes a high-speed motor connected to an internally threaded rotating lens tube by a timing belt. Low friction ball bearings press-fit into the main base housing the lens tube. A polymer zero-order waveplate is threaded inside the tube. At the top of the timing belt, the upper gear contains a small magnet that is detected by the hall sensor which provides a reference angle and acquisition triggering. We chose a photodiode with an integrated transimpedance of 100 $k\Omega$ followed by a second non-inverting opamp with a variable gain from 1 to 11 via an accessible 10 $k\Omega$ potentiometer. The photodetection circuitry is housed by a 3D printed adapter plate which contains a thick polarizing sheet. The photodiode and hall sensor trigger outputs are sent into the Raspberry Pi computer which is modified with a 12 bit, 100 ksps data acquisition hat (DAQ).

All mechanical designs are open source and can be found in the [CAD-parts-2024 folder](https://github.com/UVicAMOlab/swp-polarimeter/blob/main/CAD-parts-2024).

**PCB:**

All PCB designs are open source. Designs and supplemental documentation can be found in the [circuit-pcb-2024 folder](https://github.com/UVicAMOlab/swp-polarimeter/blob/main/circuit-pcb-2024).

**CODE INSTALLATION:**

For code installation simply download the .zip file or clone the repository. All necessary code is provided in the [code folder](https://github.com/UVicAMOlab/swp-polarimeter/blob/main/code). Before operation, the [daqhats folder](https://github.com/mccdaq/daqhats/tree/master/daqhats) for operating the MCC 118 DAQ HAT must be downloaded and placed in the code folder.

## Operation Instructions

Once the apparatus has been assembled and the code is available through a computer with data acquisition it is time to begin aligning the laser beam onto the photodiode ensuring it is collimated and securely fastened. 

Please see our [calibration guide](https://github.com/UVicAMOlab/swp-polarimeter/tree/main/resources-and-documentation/calibration/SWP_Calibration_Guide.pdf) for detailed instructions on device calibration.

To access the user interface, ensure the laser is on and the polarimeter is running at your desired settings. Run the file "polvis.py" to view the real time visualization of the optical state of the incident light. Warnings printed by "polvis.py" will assist in troubleshooting by diagnosing issues and suggesting remedies.

# Known Limitations

**Non-Ideal Quarter Waveplate:**

Due to the dispersive and birefringent effects of light on the waveplate it is possible that the phase shift between the fast and slow axes may deviate from the quarter waveplate condition of $\delta=\pi/2$. This can lead to an incorrect reconstruction of the polarization state. Although calibration corrects for this wavelength-dependent phase retardance, small variation in the retardance may occur over several days while lasing at a fixed wavelength. Moreover, large variation is seen with changes to the incident wavelength. For this reason, waveplate phase retardance calibration should be performed before each session using the polarimeter.

**DC Offset:**

The issue of DC offset from background lighting and dark current is also present. Although our design does not fully correct for dark current, background light is zeroed allowing a vast reduction in total DC offset. Re-calibration for background lighting is at the discretion of the user once the apparatus is stationary in a lab setting.

**Non-Constant Rotation of Quarter Waveplate:**

In practice, the rotation of the quarter waveplate is non-constant. The polarimeter angle however must be known at all points along the trace so the sine and cosine quadratures can be determined. This is accomplished by inferring the angle through linear interpolation between triggers. Residual error arises when the angular velocity is non-constant making linear interpolation inaccurate. We have found that if the quarter waveplate rotates at a high RPM the system can be assumed intrinsically inertially stable meaning changes to angular speed will be gradual over several periods. For this reason, a powerful motor is a key design component.
