"""
==================================================================
AUTHOR: HIEN VU
LAST MODIFIED: 20-07-18
==================================================================
Obtain standardisation to account for light source using a 
'perfect' mirror
INPUT: image containing diffraction spectrum of standard source
OUTPUT: spectra and intensity in pixels as standard spectrum.csv, 
			and plotted spectra as standardspectrum.jpg
USAGE: 	execute from terminal
			`python3 standard -f path-to-image`

==================================================================
"""

import matplotlib.pyplot as plt
import cv2
import argparse
from scipy import signal
import csv

CALIB = 829/475 # pixel/wavelength calibration from mercury lamp (from calib.py)

# Parse arguments
ap = argparse.ArgumentParser()
ap.add_argument("-f", "--file", help = "path to the calibration image")
args = vars(ap.parse_args())
filename = args["file"]

# get bnw image
image = cv2.imread(filename)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# boundaries of signal - set manually
low = 1516
high = 1534
left = 1354
right = 1392


### look for highest brightness pixel row from signal
intensities = []
pix = []
for i in range(low, high):
	intensity = 0
	for j in range(left,right):
		intensity += gray[i][j]
	intensities.append(intensity)
	pix.append(i)

# centre of signals
y = pix[intensities.index(max(intensities))]
x = (left+right)/2


### look for spectrum
intensities = []
pix = []

# for each row in the image until centre of eye
for i in range(0, y+1):
	intensity = 0
	# for each pixel in section containing spectrum
	for j in range(left, right):
		# get brightness
		intensity += gray[i][j]
	pix.insert(0, y-i)
	intensities.insert(0, intensity)
	# spectrum is indexed from 0 at the centre of the eye
	#output.write(str(y-i)+","+str(intensity)+"\n")


# calibrate standard for wavelengths
# Only get the most relevant parts of the spectrum
def calibrate(spec):
	# Calibrate using values from mercury lamp
	pixels, input_intensities = zip(*spec)
	wav = []
	intensities = []
	# for each wavelength, find the associated pixel and intensity
	for w in range(400,700):
		pix = round(w*CALIB)
		intensities.append(spec[pix][1])
		wav.append(w)
	# normalise 0-1 scaling
	imax = max(intensities)
	imin = min(intensities)
	normal = [(i/imax)*10 for i in intensities]
	# smooth using Savitzky Golay
	smooth = signal.savgol_filter(normal, 11, 3)
	result = []
	for j in range(len(wav)):
		result.append([wav[j], smooth[j]])
	return result


spec = list(zip(pix,intensities))
final_standard = calibrate(spec)
x, y = zip(*final_standard)

# write to new csv file
standcsv = open("standardspectrum.csv", 'w')
writer = csv.writer(standcsv)
for entry in final_standard:
	writer.writerow(entry)
standcsv.close()


plt.figure(figsize=(12,8))
plt.plot(x, y)
plt.title("Standard spectrum")
plt.xlabel("Wavelength")
plt.ylabel("Intensity")
plt.savefig("standardspectrum.jpg")
plt.show()
