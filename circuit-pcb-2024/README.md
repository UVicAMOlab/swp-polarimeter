# Spinning Waveplate Polarimeter Photodiode Circuit

This directory contains the KiCad 8.0 files for the SWP's photodiode circuit, as well as the files necessary to order the circuit board from PCBWay and parts from DigiKey. 

There is also a PDF that goes in depth into how the circuit works, how it is laid out, and how to go about modifying it.

### Note: The circuit and all files are open source. You are free to use them as you would like, I only ask you keep them open source.

# Ordering your own

To order your own photodiode circuit, you need accounts on DigiKey as well as PCBWay. Other PCB manufacturers work, but you may need to send them different files. As of July 2024, excluding shipping, the parts cost less than $15, and the boards cost $5.

## DigiKey

SWPBOM.csv is a bill of materials for this circuit. You can drag and drop this file into DigiKey's 'Upload a file' option within the cart. On the columns labeled 'Qty' and 'DigiKey Part Number,' select 'Quantity' and 'DigiKey Part Number' respectively. You may also want to select 'Customer Reference' on the 'Reference' column. This way, the bags will be labeled with part numbers, making soldering easy. Then, all the items for one board will be added to your cart.

Digikey may give you a better value option (10 resistors can cost less than 3), and you can do this. No loss saving money!

## PCBWay

SWPGerbers.zip is a zipped Gerber file generated to PCBWay's standards. You don't need to unzip this, you can simply input it directly into PCBWay. Input 40mm x 50mm for the PCB size, 2-layer and a quantity of 5. Everything else should be default settings. You can choose to use a different solder mask colour to get a different style board!

# More Info

The SWPPhotodiodeGuide.pdf file gives a detailed description of the circuit and how to use it. If you want to edit the KiCad files, it's best to read this beforehand

## Editing

You are free to download the KiCad files and open them in KiCad 8.0 or newer. Suggestions for editing are given in SWPPhotodiodeGuide.pdf.

*Owen Sandner*
