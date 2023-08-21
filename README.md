## Spinning Waveplate Polarimeter

*Using a rotating quarter-waveplate, a photodiode, and a few Python scripts, we can produce real-time visualization of the polarization state of incident light. This fully integrated system is easily calibrated and an affordable alternative to other fussy optical technologies making it ideal for research laboratories and educational environments.*

# Real-time Detection of Polarization of Incident Light

Initially, we use the API provided by the DAQ hat to acquire a fixed number of samples for processing; typically, this is 1000 samples at 20 ksps when the waveplate is spinning between 4500 to 5500 RPM. The raw data input is then divided into segments. Each segment is numerically integrated to determine the Fourier coefficients, and furthermore, the Stokes parameters and polarization state. To minimize any statistical errors, the mean result over several segments is considered and the display is refreshed at a rate of 4 Hz.

The reconstruction of the Stokes vector is achieved by calculating the incident intensity upon the rotating waveplate as a function of the rotation angle when aligned horizontally. We assume that the waveplate has some arbitrary retardance instead of considering a precisely calibrated quarter-waveplate. Lastly, using the orthogonality of trigonometric functions we can extract the Stokes parameters S<sub>0</sub>, S<sub>1</sub>, S<sub>2</sub> and S<sub>3</sub>. Using the Stokes parameters, the degree of polarization of the incident light is also obtained through a trivial calculation.

Please see our more rigorous [explanation](https://arxiv.org/pdf/2102.06114.pdf) and [analysis](https://github.com/UVicAMOlab/swp-polarimeter/blob/main/docs/analysis/polarimeter_analysis.pdf) for more details.

# Information Obtained from Polarimeter

The continuous data input through the Raspberry Pi's MCC DAQ hat along with the included software allows for the real-time determination and visualization of several polarization parameters. These include:

- Polarization ellipse/type of polarization (2D or 3D available)
- Stokes parameters as bar graph
- Degree of polarization
- Mean input signal over several segments of data
- Waveform incident on photodiode

# Getting Started

**PHYSICAL APPARATUS:**

Our spinning waveplate polarimeter utilizes a high-speed motor connected to an internally threaded rotating lens tube by a timing belt. Low friction ball bearings press-fit into the main base housing the lens tube. A polymer zero-order waveplate is threaded inside the tube. At the top of the timing belt, the upper gear contains a small magnet that is detected by the hall sensor which provides a reference angle and acquisition triggering. We chose a photodiode with an integrated transimpedance of 100 $k\Omega$ followed by a second non-inverting opamp with a variable gain from 1 to 11 via an accessible 10 $k\Omega$ potentiometer. The photodetection circuitry is housed by a 3D printed adapter plate which contains a thick polarizing sheet. The photodiode and hall sensor trigger outputs are sent into the Raspberry Pi computer which is modified with a 12 bit, 100 ksps data acquisition hat (DAQ).
    
![plot](./docs/analysis/Diagram.png)
Fig.1 - Diagram of polarimeter design.

**PCB:**
printing (Needs to be updated with new photodiode circuit design)

**CODE INSTALLATION:**

For code installation simply download the .zip file or clone the repository.

## Operation Instructions

Once the apparatus has been assembled and the code is available through a computer with data acquisition it is time to begin aligning the laser beam onto the photodiode ensuring it is collimated and securely fastened. 

Once aligned, shut off the laser and turn on the polarimeter with your desired parameters. Navigate to "gen_default_json.py" to create settings files for the DAQ hat, the spinning waveplate, and the offline simulation. Enter the desired values for each variable but know the background light, trigger delay and waveplate phase retardance parameters may be changed during calibration. Run gen_default_json.py. To determine background light entering the photodiode run *** to write the zeroing value into the spinning waveplate settings and the waveplate phase retardance calibration file. Next, open the file "set_waveplate.py" and adjust the voltage extrema for your specific setup and run the script. Next calibrate the trigger delay by running the file "calibrate_trigger_delay.py". This concludes the polarimeter setup and calibration. For further understanding of calibration methods used please see section *2.3* in this [paper](https://arxiv.org/pdf/2102.06114.pdf) and section *1* in this [document](https://github.com/UVicAMOlab/swp-polarimeter/blob/main/docs/analysis/polarimeter_analysis.pdf).

To access the user interface, ensure the laser is on and the polarimeter is running at your desired settings. Run the file "polvis.py" to view the real time visualization of the polarization state of the incident light. 

Warnings printed by "polvis.py" will assist in troubleshooting by diagnosing issues and suggesting remedies.

# Known Limitations
- how accurate is the polarimeter (say it again)

