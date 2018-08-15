"""
This program reads out the raw data saved in hexadecimal format in the text files and converts it to
integer values and saves it as _csv.csv files.
It also plots the hysteresis behavior of the system with respect to reference

Version: 1.01
Roman Oechslin
Master Thesis - University of Tokyo
Date: August 2018

"""
import os
import pandas as pd
import csv
import numpy as np
import matplotlib.pyplot as plt
import pickle

PLOT_BOOL = False
CONVERT_TO_DEC = True

directory = "C:/Users/Oechslin/Documents/Haptic_Controller_Code/Python - data analysis/hysteresis_test/test2_20180731/"


INTMAX = 65535
PHOTO_MIN_LEFT = 550
PHOTO_MAX_LEFT = 780
PHOTO_MIN_RIGHT = 600
PHOTO_MAX_RIGHT = 763
MAX_DISPLACEMENT_UM = 5


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


def sensor2dist(sensor_value, min_val, max_val):
    # maps the measured value to the distance (assumed linearity) in micrometers
    return MAX_DISPLACEMENT_UM - (sensor_value - min_val) * MAX_DISPLACEMENT_UM / (max_val - min_val)


for filename in os.listdir(directory):
    print(filename)
    dec_file = ""
    if CONVERT_TO_DEC:
        if "hex" in filename:
            print("converting " + filename)
            dec_file = convert2dec(filename)
        else:
            continue

    if PLOT_BOOL:
        if "dec" in filename:
            dec_file = filename
        else:
            continue

    if "3" not in filename:  # skip all files except this one
        continue

    print("plotting " + dec_file)
    # plotting
    df = pd.read_csv(directory + dec_file, delimiter=';')
    # make timeline continuous and not overflow and change from [us] to [s]
    print(df.iloc[0:round(len(df.iloc[:, 1])/2):100, 1])
    if PLOT_BOOL:
        fig = plt.figure()
        stepsize = 1
        #plt.plot(df.iloc[:, 3],df.iloc[:, 0]/1000)  # plot reference
        plt.plot(df.iloc[0:round(len(df.iloc[:, 0])/2):stepsize, 0]/1000,
                 sensor2dist(df.iloc[0:round(len(df.iloc[:, 1])/2):stepsize, 1],
                             PHOTO_MIN_LEFT, PHOTO_MAX_LEFT), 'b.')
        plt.plot(df.iloc[round(len(df.iloc[:, 0])/2)+1:-1:stepsize, 0]/1000,
                 sensor2dist(df.iloc[round(len(df.iloc[:, 1])/2)+1:-1:stepsize, 1],
                             PHOTO_MIN_LEFT, PHOTO_MAX_LEFT), 'r.')  # input to output

        fig.suptitle('Reference tracking with P')
        plt.xlabel('Compression reference [mm]')
        plt.ylabel('Measured distance [mm]')
        plt.ylim([-0.5, 2.75])
        plt.xlim([-0.1, 5.3])
        #plt.ylim([-0.5, 5.2])
        #plt.xlim([-0.5, 5.2])
        plt.legend(["Compression", "Decompression"])
        """
        figure_directory = 'figs/f' + frequency
        if not os.path.exists(figure_directory):
            os.makedirs(figure_directory)
        fig.savefig(figure_directory + '/plot_sensor_zoom.jpg')
        
        plt.close(fig)
        """
        plt.show()
        with open(directory + 'fig_raw.pkl', "wb") as fp:
            pickle.dump(fig, fp, protocol=4)
