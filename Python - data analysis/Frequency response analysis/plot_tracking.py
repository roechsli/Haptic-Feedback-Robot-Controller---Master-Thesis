"""
This program reads out the raw data saved in hexadecimal format in the text files and converts it to
integer values and saves it as _csv.csv files.
It also plots the tracking behavior of PID system with respect to reference

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

PLOT_BOOL = False
CONVERT_TO_DEC = True

directory = "C:/Users/Oechslin/Documents/Haptic_Controller_Code/Data/Frequency response/" \
            "20180620 - FRA4 Voltage follower/initial_tests/"
INTMAX = 65535
PHOTO_MIN_LEFT = 650
PHOTO_MAX_LEFT = 830
PHOTO_MIN_RIGHT = 700
PHOTO_MAX_RIGHT = 870
MAX_DISPLACEMENT_UM = 1800


def convert2dec(my_file):
    source = open(directory + my_file, "r")
    destination = open(directory + my_file[:-8] + "_dec" + ".csv", "w")
    num_lines = sum(1 for line in open(directory + my_file))
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
    return my_file[:-8] + "_dec" + ".csv"


def sensor2dist(sensor_value, min_val, max_val):
    # maps the measured value to the distance (assumed linearity) in micrometers
    return (MAX_DISPLACEMENT_UM - (sensor_value - min_val) * MAX_DISPLACEMENT_UM / (max_val - min_val)) / 1000


for filename in os.listdir(directory):
    print(filename)
    if CONVERT_TO_DEC:
        if "hex" in filename:
            print("converting " + filename)
            dec_file = convert2dec(filename)

    if PLOT_BOOL:
        if "dec" in filename:
            dec_file = filename
        else:
            continue

    if "fourth" not in filename:  # skip all files except this one
        continue

    print("plotting " + dec_file)
    # plotting
    df = pd.read_csv(directory + dec_file, delimiter=';')
    # make timeline continuous and not overflow and change from [us] to [s]
    for i in range(len(df.iloc[:, 3]) - 1):
        if df.iloc[i, 3] > df.iloc[i + 1, 3]:
            df.iloc[i + 1:, 3] = df.iloc[i + 1:, 3] + INTMAX
    for i in range(len(df.iloc[:, 3])):
        df.iloc[i, 3] = df.iloc[i, 3] / 1000000  # convert to seconds
        df.iloc[i, 0] = df.iloc[i, 0] / 1000  # convert reference to mm
        # convert sensor values to mm
        df.iloc[i, 1] = sensor2dist(df.iloc[i, 1], PHOTO_MIN_LEFT, PHOTO_MAX_LEFT)
        df.iloc[i, 2] = sensor2dist(df.iloc[i, 2], PHOTO_MIN_RIGHT, PHOTO_MAX_RIGHT)

    if PLOT_BOOL:
        fig = plt.figure()
        plt.plot(df.iloc[:, 3], df.iloc[:, 0])  # plot reference
        fig.suptitle('Reference tracking with PID')
        plt.xlabel('Time [s]')
        plt.ylabel('Compression reference [-]')
        # plot left and right sensor data,zoom and save
        plt.plot(df.iloc[:, 3], df.iloc[:, 1])
        plt.plot(df.iloc[:, 3], df.iloc[:, 2])
        plt.legend(["distance reference", "left sensor", "right sensor"])
        """
        figure_directory = 'figs/f' + frequency
        if not os.path.exists(figure_directory):
            os.makedirs(figure_directory)
        fig.savefig(figure_directory + '/plot_sensor_zoom.jpg')
        plt.close(fig)
        """
        plt.show()
