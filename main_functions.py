"""
==================================================================
AUTHOR: HIEN VU
LAST MODIFIED: 20-04-18
==================================================================
Locates the eyes and extracts spectrum from both left and right eyes
Adds eye data to training database with label
INPUT: image (.jpg .png .tiff) containing eyeshine signal, class c
OUTPUT: spectral data in spec.csv
USAGE: execute from terminal
			`python3 main.py -i path-to-image -c class`
==================================================================
"""


from find_eye import *
from find_pairs import *
from get_spectrum import *
from get_colour import *
import matplotlib.pyplot as plt
import csv
import cv2
import os
import warnings
warnings.filterwarnings(action="ignore", module="scipy", message="^internal gelsd")

def main(filename):
	# load the image
	image = cv2.imread(filename)
	orig = image.copy()
	new = image.copy()

	# for training data
	#ID = args["class"]

	# find pairs of eyes
	contours = find_eye(image)
	[con_pairs, pair_det] = find_pairs(image, contours)
	num_pairs = len(con_pairs)
	fname = filename
	print("\n\n============================================================")
	print("========================= RESULTS ==========================")
	print("\tSEARCHED " + str(fname))
	print("\tFOUND " + str(num_pairs) + " PAIR/S")


	colours = [(255,0,0),(0,0,255),(0,255,0),(255,255,0),(255,0,255),(0,255,255),(100,200,100),(100,0,200),(200,100,200),(200,100,100)]
	i=0
	# circle around the pairs found in the image
	for pair in con_pairs:
		i+=1
		col = colours[i%10]
		if len(pair)==2:
			for eye in pair:
				(cX, cY), radius = cv2.minEnclosingCircle(eye)
				cv2.circle(new, (int(cX), int(cY)), int(radius+8), col, 5)
		else:
			pass
	# save circled image
	cv2.imwrite(fname[0:-4]+"_circled.jpg", new)
	
	# set up new databases

	# spectrum
	fields2 = ['file','ID','L/R']
	fields2 = fields2 + list(range(400, 700))
	f2 = open("data/spectest.csv", 'w')
	writer = csv.writer(f2)
	writer.writerow(fields2)
	f2.close()
	

	# For each pair
	for i in range(0, num_pairs):
		# get eye details for the pair
		con1, con2 = con_pairs[i][0], con_pairs[i][1]
		pair = pair_det[i]
		eye1, eye2 = pair[0], pair[1]


		### IPD and colour
		# interpupillary distance (relative to pupil width)
		w1, w2 = eye1[3][0]-eye1[2][0], eye2[3][0]-eye2[2][0]
		ave_w = (w1+w2) / 2
		dist = math.sqrt((eye2[0]-eye1[0])**2 + (eye2[1]-eye1[1])**2) / ave_w

		# get colour
		col1 = get_colour(orig, eye1[0:2], ave_w/2)
		col2 = get_colour(orig, eye2[0:2], ave_w/2)
		ave_col = ave_eye_colours(col1, col2)
		r,g,b = ave_col
		hue = get_hue(ave_col)

		# print results
		print("------------------------------------------------------------")
		print("\tNAE Pair " + str(i+1))
		print("\tInterpupillary distance: " + str(dist))
		print("\tColour (hue): " + str(hue))
		print("\tColour (RGB): " + str(ave_col))

		### Spectrum
		# get spectrum
		[spec1, spec2] = get_spectrum(pair, orig)

		# graph spectrum
		x1, y1 = zip(*spec1)
		x2, y2 = zip(*spec2)
		plt.plot(x1,y1)
		plt.plot(x2,y2, 'red')
		plt.title("NAE Spectrum - file: %s" % filename)
		plt.xlabel("Wavelength (nm)")
		plt.ylabel("Intensity")
		plt.savefig(filename[:-4]+'graph.jpg')
		plt.show()

		# add spectrum to spec database
		f2 = open("data/spectest.csv", 'a')
		writer = csv.writer(f2)
		writer.writerow([fname,0,'L']+list(y1))
		writer.writerow([fname,0,'R']+list(y2))
		f2.close()
		


