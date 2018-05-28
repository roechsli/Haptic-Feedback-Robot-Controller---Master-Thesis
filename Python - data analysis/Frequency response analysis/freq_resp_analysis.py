import os
import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from pylab import *
from math import atan2

INTMAX = 65535

def get_freq_from_filename(filename):
    if filename[0] == "f" and filename[-8:] == "_csv.csv":
        return filename[1:-8]
    else:
        return ""


directory = "fra_logs/"
for file in os.listdir(directory):

    if ".csv" not in file:
        continue
    frequency = float (get_freq_from_filename(file))

    # to restrict to first file only
    if "f1.25_csv" not in file:
        continue # write pass if all files should be treated

    df = pd.read_csv(directory + file, delimiter=';')
    #print(df.iloc[:, 3])

    for i in range(len(df.iloc[:,3]) -1):
        if df.iloc[i,3] > df.iloc[i+1,3]:
            df.iloc[i:,3] = df.iloc[i:,3] + INTMAX
        print(df.iloc[i,3])


    plt.plot(df.iloc[:, 3],df.iloc[:, 1])
    #fig = plt.figure()
    #fig.suptitle(titles[i] + ', Frequency of ' + frequency + ' Hz')
    #plt.xlabel('Time [s]')
    #plt.ylabel(ylabel[i])
    #fig.savefig('figs/f' + frequency + '/plot_' + titles[i] + '.jpg')
    #plt.close(fig)
    plt.show()



    #save left and right sensor data, plot and zoom

    #calculate input magnitude

    #calculate left sensor magnitude and phase offset

    #calculate right sensor magnitude and phase offset

#plot Bode diagram (freq_vec, magn_vec) and (freq_vec, phase_offset_vec)
#save figures

