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
            while time_integer - windowTime[0] > 4:
                window.pop(0)
                windowTime.pop(0)

            # The Queue window contains the last 4 seconds of brain activity
            
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
    
frequency = 100
headers = "Sample Index, EXG Channel 0, EXG Channel 1, EXG Channel 2, EXG Channel 3, Accel Channel 0, Accel Channel 1, Accel Channel 2, Other, Other, Other, Other, Other, Timestamp, Other, Timestamp (Formatted)".split(', ')
def makeImage(window):
    #Generating spectogram
    f, t, image = signal.spectrogram(signals,frequency)
    # plt.plot(signals)
    image =np.transpose(image,(1,2,0))

    for count in range(4):
        plt.pcolormesh(t, f, image[:,:,count], shading='gouraud')
        plt.ylim(0,7)
        plt.show()