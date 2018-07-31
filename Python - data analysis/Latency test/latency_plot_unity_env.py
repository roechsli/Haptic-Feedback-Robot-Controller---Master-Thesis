"""
This program reads the oscilloscope data that has been measured for latency tests and plots it

Version: 1.0
Roman Oechslin
Master Thesis - University of Tokyo
2018 July 18
"""
import os
import pandas as pd
import csv
import numpy as np
import matplotlib.pyplot as plt


#scope3 from real robot testing is best
directory = "osc_data/"
PHOTO_MIN_LEFT = 600#640
PHOTO_MAX_LEFT = 790#840
PHOTO_MIN_RIGHT = 700
PHOTO_MAX_RIGHT = 880
MAX_DISPLACEMENT_UM = 1800
PHOTO_MIN_LEFT = 550#640
PHOTO_MAX_LEFT = 725#840
PHOTO_MIN_RIGHT = 600
PHOTO_MAX_RIGHT = 720
MAX_DISPLACEMENT_UM = 5000

def sensor2dist(sensor_value, min_val, max_val):
  # maps the measured value to the distance (assumed linearity) in micrometers
  return (MAX_DISPLACEMENT_UM - (sensor_value - min_val) * MAX_DISPLACEMENT_UM / (max_val - min_val) ) / 1000


for filename in os.listdir(directory):
    print(filename)
    # plotting
    df = pd.read_csv(directory + filename, delimiter=',')

    for i in range(len(df.iloc[:,3]) -3):
        # convert sensor values to mm
        #print(i)
        #df.iloc[i + 3,3] = 5-(float (df.iloc[i + 3,3])-1.37)/(2.77-1.37)*5
        df.iloc[i + 3,3] = sensor2dist(float (df.iloc[i + 3,3])/5*1024, PHOTO_MIN_RIGHT, PHOTO_MAX_RIGHT)
        df.iloc[i + 3,0] = float (df.iloc[i + 3, 0])
        df.iloc[i + 3,1] = float (df.iloc[i + 3, 1])
        df.iloc[i + 3,2] = float (df.iloc[i + 3, 2])

    #Osc3: joystick (A0) in channel 1 and feedback (current mode) in channel 2; dist sensor (A2) in channel 3
    time_vec = df.iloc[3:,0] - df.iloc[3,0]
    #joystick_vec = df.iloc[3:,1]/3.3*2 - 0.8
    joystick_vec = df.iloc[3:,1]/3.3*2 - 1
    feedback_vec = ((df.iloc[3:,2]/5*1024) - 81)/492 / 1024 * MAX_DISPLACEMENT_UM
    sensor_dist_vec = df.iloc[3:,3]
    fig = plt.figure()#figsize=(15.0, 6.5))
    fig.suptitle('Unity simulation testing')
    plt.subplot(311)
    plt.plot(time_vec, joystick_vec)  # plot reference
    """Scope3 vertical lines
    plt.vlines(1.275, -1, 1, 'r')
    plt.vlines(4.06, -1, 1, 'r')
    plt.vlines(7.94, -1, 1, 'g')"""
    plt.xlabel('Time [s]')
    plt.ylabel('Joystick commands [-]')
    # plot left and right sensor data,zoom and save
    plt.subplot(312)
    plt.plot(time_vec, feedback_vec)
    """Scope3 vertical lines
    plt.vlines(2.02, 0, 2, 'r')
    plt.vlines(4.74, 0, 2, 'r')
    plt.vlines(7.98, 0, 2, 'g')"""
    plt.xlabel('Time [s]')
    plt.ylabel('Desired compression [mm]')
    plt.subplot(313)
    plt.plot(time_vec, sensor_dist_vec)
    """Scope3 vertical lines
    plt.vlines(2.235, 0, 1.9, 'r')
    plt.vlines(4.844, 0, 1.9, 'r')
    plt.vlines(8.065, 0, 1.9, 'g')"""
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
