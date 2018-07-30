"""
==================================================================
AUTHOR: HIEN VU
LAST MODIFIED: 12-06-18
==================================================================
Obtain calibration for spectrum from an image (mercury lamp spectrum)
INPUT: image containing diffraction spectrum of calibration source
OUTPUT: spectra and intensity in pixels as calibrationspectrum.csv, 
			and plotted spectra as calibrationspectrum.jpg
USAGE: 	execute from terminal
			`python3 calib.py -f path-to-image`
To obtain calibration values, using output files and look for peaks 
at known wavelengths. For example, for a mercury lamp, use peak at 
546.1nm. Take corresponding pixel value to input to get_spectrum.py
==================================================================
"""

import matplotlib.pyplot as plt
import cv2
import argparse
import math

# Parse arguments
ap = argparse.ArgumentParser()
ap.add_argument("-f", "--file", help = "path to the calibration image")
args = vars(ap.parse_args())
filename = args["file"]

# get bnw image
image = cv2.imread(filename)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# boundaries of signal - set manually
low = 1640
high = 1653
left = 1222
right = 1236


### look for highest brightness pixel row from signal
intensities = []
pix = []
for i in range(low, high):
	intensity = 0
	for j in range(left,right):
		#intensity += gray[i][j]
		#intensity += image[i,j][0]+image[i,j][1]+image[i,j][2]
		intensity += 0.0722*((image[i,j][0])**2)+0.7152*((image[i,j][1])**2)+0.2126*((image[i,j][2])**2)
	intensities.append(intensity)
	pix.append(i)

# centre of signals
y = pix[intensities.index(max(intensities))]
x = (left+right)/2


### look for spectrum
intensities = []
pix = []
# write result spectra to file
output = open("mercuryspectrum3.csv", "w")
output.write("pixel,intensity\n")

# for each row in the image until centre of eye
for i in range(0, y+1):
	intensity = 0
	# for each pixel in section containing spectrum
	for j in range(left, right):
		# get brightness
		#intensity += gray[i][j]
		#intensity += 0.33*image[i,j][0]+0.33*image[i,j][1]+0.34*image[i,j][2]
		intensity += 0.0722*((image[i,j][0])**2)+0.7152*((image[i,j][1])**2)+0.2126*((image[i,j][2])**2)
	pix.insert(0, y-i)
	intensities.insert(0, intensity)
	# spectrum is indexed from 0 at the centre of the eye
	output.write(str(y-i)+","+str(intensity)+"\n")
	

output.close()
plt.figure(figsize=(12,8))
plt.plot(pix, intensities)
plt.title("Calibration Spectrum")
plt.xlabel("Pixels")
plt.ylabel("Intensity")
plt.savefig("mercuryspectrum3.jpg")
plt.show()
