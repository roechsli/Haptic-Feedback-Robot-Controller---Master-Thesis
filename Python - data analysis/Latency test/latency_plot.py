"""
This program reads the oscilloscope data that has been measured for latency tests and plots it for
 real robot environment

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


directory = "osc_data/"
PHOTO_MIN_LEFT = 600
PHOTO_MAX_LEFT = 790
PHOTO_MIN_RIGHT = 700
PHOTO_MAX_RIGHT = 880
MAX_DISPLACEMENT_UM = 1800


def sensor2dist(sensor_value, min_val, max_val):
    # maps the measured value to the distance (assumed linearity) in micrometers
    return (MAX_DISPLACEMENT_UM - (sensor_value - min_val) * MAX_DISPLACEMENT_UM / (max_val - min_val)) / 1000


for filename in os.listdir(directory):
    print(filename)
    # plotting
    df = pd.read_csv(directory + filename, delimiter=',')

    for i in range(len(df.iloc[:, 3]) - 3):
        # convert sensor values to mm
        df.iloc[i + 3, 3] = sensor2dist(float(df.iloc[i + 3, 3])/5*1024, PHOTO_MIN_LEFT, PHOTO_MAX_LEFT)
        #df.iloc[i + 3, 3] = sensor2dist(float(df.iloc[i + 3, 3])/5*1024, PHOTO_MIN_RIGHT, PHOTO_MAX_RIGHT)
        df.iloc[i + 3, 0] = float(df.iloc[i + 3, 0])
        df.iloc[i + 3, 1] = float(df.iloc[i + 3, 1])
        df.iloc[i + 3, 2] = float(df.iloc[i + 3, 2])

    #Osc3: joystick (A0) in channel 1 and feedback (current mode) in channel 2; dist sensor (A2) in channel 3
    time_vec = df.iloc[3:, 0] - df.iloc[3, 0]
    joystick_vec = df.iloc[3:, 1]/2.5 - 1
    feedback_vec = df.iloc[3:, 2]/5*1.8
    sensor_dist_vec = df.iloc[3:, 3]
    fig = plt.figure(figsize=(15.0, 6.5))
    fig.suptitle('Real robot testing')
    plt.subplot(311)
    plt.plot(time_vec, joystick_vec)  # plot reference

    plt.vlines(1.275, -1, 1, 'r')
    plt.vlines(4.06, -1, 1, 'r')
    plt.vlines(7.94, -1, 1, 'g')
    plt.xlabel('Time [s]')
    plt.ylabel('Joystick commands [-]')
    # plot left and right sensor data,zoom and save
    plt.subplot(312)
    plt.plot(time_vec, feedback_vec)

    plt.vlines(2.02, 0, 2, 'r')
    plt.vlines(4.74, 0, 2, 'r')
    plt.vlines(7.98, 0, 2, 'g')
    plt.xlabel('Time [s]')
    plt.ylabel('Desired compression [mm]')
    plt.subplot(313)
    plt.plot(time_vec, sensor_dist_vec)

    plt.vlines(2.235, 0, 1.9, 'r')
    plt.vlines(4.844, 0, 1.9, 'r')
    plt.vlines(8.065, 0, 1.9, 'g')
    plt.xlabel('Time [s]')
    plt.ylabel('Compression [mm]')
    #plt.axis([2.9, 3.6, 0, 255])
    #plt.legend(["joystick commands", "feedback", "distance"])

    figure_directory = 'figs/'
    if not os.path.exists(figure_directory):
        os.makedirs(figure_directory)
    #print (figure_directory + filename[:-4] + '_latency_plot.jpg')
    fig.savefig(figure_directory + filename[:-4] + '_latency_plot.jpg')
    #plt.close(fig)

    plt.show()
