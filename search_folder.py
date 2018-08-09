import os
from main import *
from pcasvm import *
import cv2

path = "../scanner/data/"
i = 0

MAX = 100

while True:
    dirs = os.listdir( path )
    for file in dirs:
        image_path = path + "file" + str( i ) +".jpg"
        if file == "file" + str( i ) +".jpg":
            if i > (MAX - 1):
                j = i - MAX
                os.remove( path + "file" + str( j ) + ".jpg" )
            i += 1
            # wait until file is written
            while cv2.imread(image_path) is None:
              g=0
            # execute main for new image
            main(image_path)


