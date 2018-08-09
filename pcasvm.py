"""
==================================================================
AUTHOR: HIEN VU
LAST MODIFIED: 27-05-18
==================================================================
Performs principal component analysis and support vector machine
classification on NAE spectral data
INPUT: 		spectrain.csv (containing training data)
			spectest.csv (containing test data)
OUTPUT: 	PCA plot
			PCA explained variance ratio
			SVM plots showing decision boundaries four 4 kernels 
			Test data prediction accuracy
USAGE: execute from terminal
			`python3 pcasvm.py`
			`python3 pcasvm.py -t test-image`

Modified from Towards Data Science, Galarnyk M. Original code available at 
https://towardsdatascience.com/pca-using-python-scikit-learn-e653f8989e60
==================================================================
"""

import csv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from svm import *
from main_functions import *

"""
# Import test data
with open('data/spectest.csv', 'r') as f2:
	reader2 = csv.reader(f2)
	raw = list(reader2)
testdata = np.asarray([row[2:] for row in raw])
ytest = testdata[1:, 0]
xtest = testdata[1:, 2:].astype(np.float)
"""


##########################################################
################### TRAINING DATA ########################

# IMPORT AND CLEAN DATA
with open('data/spectrain.csv', 'r') as f:
	reader = csv.reader(f)
	raw = list(reader)
data = np.asarray([row[1:] for row in raw])
y = data[1:, 0]
x = data[1:, 2:].astype(np.float)
idx = [i for i in range(len(y))]

# STANDARDISE/NORMALISE FEATURES (mean=0, std=1)
scaler = StandardScaler()
scaler.fit(x)
x = scaler.transform(x)

# PCA
pca = PCA(n_components=2)
pca.fit(x)		# fit to training data
principalComponents = pca.transform(x)			# transform test data
principalDf = pd.DataFrame(data = principalComponents
			 , columns = ['principal component 1', 'principal component 2'])

# Compose new dataframe
targetDf = pd.DataFrame(data=y, index=idx, columns=['target'])
finalDf = pd.concat([principalDf, targetDf], axis = 1)

# Save PCA training data to csv
f = open("data/PCA_2component_train.csv", 'w')
writer = csv.writer(f)
writer.writerow(['principal component 1','principal component 2','target'])
for i in range(len(principalComponents)):
	writer.writerow(principalComponents[i].tolist()+[y[i]])
f.close()

# Plot PCA
fig = plt.figure(figsize = (8,8))
ax = fig.add_subplot(1,1,1) 
ax.set_xlabel('Principal Component 1', fontsize = 15)
ax.set_ylabel('Principal Component 2', fontsize = 15)
ax.set_title('NAE Spectra PCA (2 Components)', fontsize = 20)

targets = ['B', 'R', 'G']
colors = ['b', 'r', 'g']
for target, color in zip(targets,colors):
	indices = finalDf['target'] == target
	ax.scatter(finalDf.loc[indices, 'principal component 1']
			   , finalDf.loc[indices, 'principal component 2']
			   , c=color, edgecolors='k')
ax.legend(targets)
ax.grid()
plt.savefig("2 component PCA.jpg")
plt.show()

# accounts for how much variance?
print("PCA EXPLAINED VARIANCE RATIO: %s" % pca.explained_variance_ratio_)

# TRAIN SVM MODEL
models = pca_svm("data/PCA_2component_train.csv")


##########################################################
################## TRAINING DATA #########################
"""
# IMPORT NEW TEST DATA BY RUNNING NAE SPECTRA FINDER
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", help = "path to the normal image file")
args = vars(ap.parse_args())
image = args["image"]
main(image)
"""
import os
import cv2

path = "../scanner/data/"
c = 0

MAX = 100

while True:
	dirs = os.listdir( path )
	for file in dirs:
		image_path = path + "file" + str( c ) +".jpg"

		if file == "file" + str( c ) +".jpg":
			if c > (MAX - 1):
				j = c - MAX
				os.remove( path + "file" + str( j ) + ".jpg" )
			
			# wait until file is written
			while cv2.imread(image_path) is None:
			  g=0
			# execute main for new image
			main(image_path)
			c += 1

			with open('data/spectest.csv', 'r') as f3:
				reader3 = csv.reader(f3)
				raw = list(reader3)
			testdata = np.asarray([row[1:] for row in raw])
			ytest = testdata[1:, 0]
			xtest = testdata[1:, 2:].astype(np.float)

			# STANDARDISE/NORMALISE FEATURES 
			xtest = scaler.transform(xtest) # transform the test data to scale to training set
			# PCA
			testprincipalComponents = pca.transform(xtest)
			# Save PCA test data to csv
			testf = open("data/PCA_2component_test.csv", 'w')
			writer2 = csv.writer(testf)
			writer2.writerow(['principal component 1','principal component 2','target'])
			for i in range(len(testprincipalComponents)):
				writer2.writerow(testprincipalComponents[i].tolist()+[ytest[i]])
			testf.close()

			# Prediction for test data
			accuracy = predict("data/PCA_2component_test.csv", models)
			#print("SVM MODELS PREDICTION ACCURACY: %s" % accuracy)

##########################################################
