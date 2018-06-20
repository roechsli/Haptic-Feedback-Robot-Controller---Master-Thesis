"""
This program reads out the raw data saved in hexadecimal format in the text files and converts it to
integer values and saves it as _csv.csv files.
It also plots the tracking behavior of PID system with respect to reference

Version: 1.0
Roman Oechslin
Master Thesis - University of Tokyo

"""
import os
import pandas as pd
import csv
import numpy as np
import matplotlib.pyplot as plt


PLOT_BOOL = True

directory = "C:/Users/Oechslin/Documents/Haptic_Controller_Code/Data/Frequency response/20180620 - FRA4 Voltage follower\initial_tests/"
INTMAX = 65535
PHOTO_MIN_LEFT = 650
PHOTO_MAX_LEFT = 830
PHOTO_MIN_RIGHT = 700
PHOTO_MAX_RIGHT = 870

def convert2dec(filename):
    source = open(directory + filename, "r")
    destination = open(directory + filename[:-8] + "_dec" + ".csv", "w")
    num_lines = sum(1 for line in open(directory + filename))
    print(num_lines)
    for line in source:
        buf = ""
        for character in line:
            if character == ";":
                destination.write(str(int(buf, 16)) + ";")
                buf = ""
            elif character == "\n":
                destination.write("\n")
                buf = ""
            else:
                buf = buf + character
    source.close()
    destination.close()
    return filename[:-8] + "_dec" + ".csv"

def map_to_255(receptor_value, min_val, max_val):
    # this is the same function as in arduino code, that maps the measured value
    # to the range [0..255] =  [normal..compressed]
    converted = (receptor_value - min_val) * 51 / (max_val - min_val) * 5
    converted = 255 - converted
    return converted


for filename in os.listdir(directory):
    if "hex" not in filename:
        continue
    print(filename)
    dec_file = convert2dec(filename)

    df = pd.read_csv(directory + dec_file, delimiter=';')
    # make timeline continuous and not overflow and change from [us] to [s]
    for i in range(len(df.iloc[:, 3]) - 1):
        if df.iloc[i, 3] > df.iloc[i + 1, 3]:
            df.iloc[i + 1:, 3] = df.iloc[i + 1:, 3] + INTMAX
    for i in range(len(df.iloc[:,3])):
        df.iloc[i, 3] = df.iloc[i, 3] / 1000000  # convert to seconds

    if PLOT_BOOL:
        print("plotting")
        fig = plt.figure()
        plt.plot(df.iloc[:, 3],df.iloc[:, 0])  # plot reference
        fig.suptitle('Reference tracking with PID')
        plt.xlabel('Time [s]')
        plt.ylabel('Compression reference [-]')
        # plot left and right sensor data,zoom and save
        plt.plot(df.iloc[:, 3], map_to_255(df.iloc[:, 1], PHOTO_MIN_LEFT, PHOTO_MAX_LEFT))
        plt.plot(df.iloc[:, 3], map_to_255(df.iloc[:, 2], PHOTO_MIN_RIGHT, PHOTO_MAX_RIGHT))
        #plt.axis([2.9, 3.6, 0, 255])
        plt.legend(["distance reference", "left sensor", "right sensor"])
        """
        figure_directory = 'figs/f' + frequency
        if not os.path.exists(figure_directory):
            os.makedirs(figure_directory)
        fig.savefig(figure_directory + '/plot_sensor_zoom.jpg')
        plt.close(fig)
        """
        plt.show()
