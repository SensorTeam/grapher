"""
==================================================================
AUTHOR: HIEN VU
LAST MODIFIED: 27-05-18
==================================================================
Finds NAEs in image and returns spectra generated from diffraction grating
get_spectrum() returns matrix of pixel and intensity for eye spectrum (L/R)
==================================================================
"""

import math
import numpy as np
import cv2
import csv
import colorsys as cs 
from scipy import signal


##################################################################

CALIB = 829/475 # pixel/wavelength calibration from mercury lamp (from calib.py)
CALIB = 1.754310483		# mercury lamp, 3 point calibration
#CALIB = 665/546.1		# iphone video from thesis
STANDARD = "standardisation/standardspectrum.csv"	# standard spectrum using EO2 mirror/retroreflector

##################################################################

def standardise(intensities):
	# open standard file - must be only wavelengths 400-699
	with open(STANDARD, 'r') as f:
		reader = csv.reader(f)
		raw = list(reader)
	# store into array of intensities of wavelengths 400-699
	standard = np.asarray([row[1] for row in raw]).astype(float)
	# for each intensity, make it a percentage of the standard
	standardised = [intensities[i]/standard[i] for i in range(len(intensities))]
	return standardised


# Only get the relevant parts of the spectrum
# Calibrate to convert pixels to wavelength
# Standardise as percentage of light source
# Normalise 0-1 scaling
def calibrate(spec, calib):
	# Calibrate using values from mercury lamp
	pixels, input_intensities = zip(*spec)
	wav = []
	intensities = []
	# for each wavelength, find the associated pixel and intensity
	for w in range(400,700):
		pix = round(w*calib)
		#i = spec[pix-adjust][1]
		intensities.append(spec[pix][1])
		wav.append(w)
	# standardise
	#standardised = standardise(intensities)
	standardised = intensities
	# normalise 0-1 scaling
	imax = max(standardised)
	imin = min(standardised)
	normal = [(i-imin)/(imax-imin) for i in standardised]		# 0-1 scaling
	#normal = [i/imax for i in standardised]					# maximum scaling
	#normal = standardised
	# smooth using Savitzky Golay
	smooth = signal.savgol_filter(normal, 11, 3)
	result = []
	for j in range(len(wav)):
		result.append([wav[j], smooth[j]])
	return result


# Convert RGB to HSV and return hue
def get_hue(colour):
	rr,gg,bb = colour
	r,g,b = rr/255, gg/255, bb/255
	M = max(r,g,b)
	m = min(r,g,b)
	c = M - m
	if c == 0:
		hue = 0
	elif M == r:
		#g, b = int(round(g)), int(round(b))
		hue = ((g-b)/c)%6
	elif M == g:
		hue = (b-r)/c + 2
	elif M == b:
		hue = (r-g)/c + 4
	hue = hue*60
	return hue


# Returns the spectrum (pixel v intensity) for an eye given the left and right boundaries
# Intensity is total intensity all pixels in that row
def eye_spectrum(y, left, right, image):
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	#[x, y, extL, extR, extT, extB] = eye
	spectrum = []
	# for each row in the image until centre of eye
	for i in range(0, y+1):
		intensity = 0
		# for each pixel in section containing spectrum
		for j in range(left, right):
			# get brightness
			#intensity += gray[i][j]
			intensity += math.sqrt((image[i,j][0])**2+(image[i,j][1])**2+(image[i,j][2])**2)
		# spectrum is indexed from 0 at the centre of the eye
		spectrum.insert(0, [y-i, intensity])
	# calibrate using calibration from mercury lamp
	final_spec = calibrate(spectrum, CALIB)
	return final_spec


# Calls eye_spectrum() for each eye
	# pair = [eye1, eye2]
	# eye1 = [x, y, extL, extR, extT, extB]
def get_spectrum(pair, image):
	eye1, eye2 = pair

	width1, width2 = eye1[3][0]-eye1[2][0], eye2[3][0]-eye2[2][0]
	cen = math.floor( (eye1[0]+eye2[0]) / 2 )
	
	# find y
	y1 = get_centre(eye1, image)
	y2 = get_centre(eye2, image)

	spec1 = eye_spectrum(y1, math.floor(eye1[2][0]-width1/2), cen, image)
	spec2 = eye_spectrum(y2, cen, math.ceil(eye2[3][0]+width2/2)+1, image)
	return [spec1, spec2]


# Gets brightest pixel row
def get_centre(eye, image):
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	[x,y,left,right,low,high] = eye
	left = left[0]
	right = right[0]
	low = low[1]
	high = high[1]
	intensities = []
	pix = []
	for i in range(low, high):
		intensity = 0
		for j in range(left,right):
			intensity += gray[i][j]
		intensities.append(intensity)
		pix.append(i)
	ind = intensities.index(max(intensities))
	return(pix[ind])
