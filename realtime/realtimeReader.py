import time, re
from datetime import datetime
import argparse

import sys
import matplotlib.pyplot as plt
import numpy as np
from scipy.io import wavfile
from scipy import signal
import pyedflib
from pyedflib import highlevel
from datetime import datetime
import cv2
from PIL import Image as im

from matplotlib.backends.backend_agg import FigureCanvas

def follow(thefile):
    thefile.seek(0,2)
    while True:
        line = thefile.readline()
        if not line:
            time.sleep(0.1)
            continue
        yield line

# regex for the eeg values
pattern = r'^(-?\d+(\.\d+)?(?:[eE][-+]?\d+)?,\s?){14}-?\d+(\.\d+)?(?:[eE][-+]?\d+)?,\s?(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3})$'

frequency = 100
def makeImage(window):
    images =  []
    labels = []
    
    signals = np.zeros([4,len(window)])

    window = list(window)
    for x in range(len(window)):
        sign = window[x]
        splStr = window[x].split(", ")
        values = []
        for i in splStr[1:5]:
            values.append(float(i))
        for i in range(len(values)):
            if values[i] > 60:
                values[i] = 0
        signals[0:3,x] = values[0:3]
        # signals[1,x] = float(splStr[2])
        # signals[2,x] = float(splStr[3])
        # signals[3,x] = float(splStr[4])
    

    prc_overlap = .9
    #Getting signal data for 4 second period
    



    f, t, image = signal.spectrogram(signals,frequency, nperseg = frequency, noverlap = frequency*prc_overlap)
    image = np.transpose(image,(1,2,0))

    #updating information containers
    package = [f,t,image]
    images.append(package)

    
    # Create a matplotlib figure for rendering
    images = []
    for i in range(4):
        fig, ax = plt.subplots()
        fig.tight_layout()
        ax.axis("off")
        im = ax.pcolormesh(t, f, image[:, :, i], shading='gouraud')
        ax.set_ylim(0, 40)
        
        canvas = FigureCanvas(fig)
        
        # Convert the figure to an image
        canvas.draw()
        
        img = np.array(canvas.renderer.buffer_rgba(), dtype='uint8')
        images.append(img)
        plt.close(fig)
    # Display the image using OpenCV
    # cv2.imshow('Spectrogram', img)
    # cv2.waitKey(1)  # Add a short delay to allow the image to be displayed
    model_image = combine_4(images)
    print(model_image.shape)
    cv2.imshow('Spectrogram', model_image)
    cv2.waitKey(1)  # Add a short delay to allow the image to be displayed

    # plt.pcolormesh(t, f, image[:,:,0])
    # plt.show()
    # plt.ylim(0,40)

def crop_white_border(image):
    mask = np.all(image >= [250, 250, 250, 255], axis=-1)
    coords = np.argwhere(~mask)
    if coords.size == 0:  # If the image is completely white
        return image
    x_min, y_min = coords.min(axis=0)
    x_max, y_max = coords.max(axis=0) + 1
    cropped = image[x_min:x_max, y_min:y_max]
    return cropped


def combine_4(images):
    assert(len(images)) == 4
    img1 = crop_white_border(images[0])
    img2 = crop_white_border(images[1])
    img3 = crop_white_border(images[2])
    img4 = crop_white_border(images[3])
    
    images_row_1 = np.concatenate([img1, img2], axis=1)
    images_row_2 = np.concatenate([img3, img4], axis=1)
    combined_image = np.concatenate([images_row_1, images_row_2], axis=0)
    
    resized_image = cv2.resize(combined_image, (128, 128))
    
    return resized_image


def main(filepath):
    logfile = open(filepath,"r")
    loglines = follow(logfile)
    
    waitSend = ""
    waitCount = 0
    
    window = []
    windowTime = []
    
    for line in loglines:
        waitSend += line
        match = re.fullmatch(pattern, waitSend.strip())
        if match:
            # Extract timestamp from the match
            timestamp_str = match.group(4)

            # Convert timestamp to datetime object
            dt_object = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f')

            # Convert datetime object to integer representing time
            time_integer = int(dt_object.timestamp())

            window.append(waitSend)
            windowTime.append(time_integer)
            
            prTest = False
            while time_integer - windowTime[0] > 4:
                prTest = True
                window.pop(0)
                windowTime.pop(0)

            # The Queue window contains the last 4 seconds of brain activity
            if prTest:
                makeImage(window)
                
            #test print:
            #print(window[0])

            
            waitSend = ""
        elif waitCount > 3:
            waitSend = ""
        waitCount += 1

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process EEG data from a file.')
    parser.add_argument('filepath', type=str, help='Path to the EEG data file')

    args = parser.parse_args()
    main(args.filepath)