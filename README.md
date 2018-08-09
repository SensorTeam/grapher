# NAE Spectra CLassifier (Mk. 0)
Extracts spectra from new image and classifies using PCA and SVM

# Requirements

* `python3`
* `pip`
* `virtualenv`

# Usage

1. Setup a virtual environment using the command `virtualenv venv`
2. Activate the virtual environment using `source venv/bin/activate`
3. Install package dependencies using `pip install -r requirements.txt`
4. Execute using the following

## Create training database using photos:
	`python3 main.py -i path-to-image -c class

## Classification of new image
	`python3 pcasvm.py`
	place new image into ../scanner/data
