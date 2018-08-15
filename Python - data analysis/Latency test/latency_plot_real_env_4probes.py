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
import matplotlib.pyplot as plt


directory = "osc_data/"
PHOTO_MIN_LEFT = 420
PHOTO_MAX_LEFT = 795
PHOTO_MIN_RIGHT = 550
PHOTO_MAX_RIGHT = 765
MAX_DISPLACEMENT_UM = 3000


def sensor2dist(sensor_value, min_val, max_val):
    # maps the measured value to the distance (assumed linearity) in micrometers
    return (MAX_DISPLACEMENT_UM - (sensor_value - min_val) * MAX_DISPLACEMENT_UM / (max_val - min_val)) / 1000


for filename in os.listdir(directory):
    print(filename)
    # plotting
    df = pd.read_csv(directory + filename, delimiter=',')

    for i in range(len(df.iloc[:, 3]) - 3):
        # convert sensor values to mm
        df.iloc[i + 3, 3] = sensor2dist(float(df.iloc[i + 3, 3])/5*1024, PHOTO_MIN_RIGHT, PHOTO_MAX_RIGHT)
        df.iloc[i + 3, 0] = float(df.iloc[i + 3, 0])
        df.iloc[i + 3, 1] = float(df.iloc[i + 3, 1])
        df.iloc[i + 3, 2] = float(df.iloc[i + 3, 2])
        df.iloc[i + 3, 4] = float(df.iloc[i + 3, 4])

    # Osc3: joystick (A0) in channel 1 and feedback (current mode) in channel 2; dist sensor (A2) in channel 3
    time_vec = df.iloc[3:, 0] - df.iloc[3, 0]
    joystick_vec = df.iloc[3:, 1]/2.5 - 1
    feedback_vec = df.iloc[3:, 2]/5*1.8
    sensor_dist_vec = df.iloc[3:, 3]
    real_current = df.iloc[3:, 4]
    fig = plt.figure(figsize=(15.0, 8.4))
    fig.suptitle('Real robot testing')
    plt.subplot(411)
    plt.plot(time_vec, joystick_vec)  # plot reference
    if "scope_13" in filename:
        plt.vlines(1.03, -1, 1, 'r')  # Go
        plt.vlines(2.51, -1, 1, 'r')  # Stop
        # plt.vlines(4.35, -1, 1, 'g')  # Ext. force
        # plt.vlines(5.91, -1, 1, 'g')  # Let go
        plt.vlines(6.54, -1, 1, 'r')  # Stop
        plt.vlines(7.18, -1, 1, 'k')  # Back
        plt.vlines(8.53, -1, 1, 'c')  # Stop
    elif "scope_14" in filename:
        """
        plt.vlines(0.09, -1, 1, 'r')  # Go
        plt.vlines(2.52, -1, 1, 'r')  # Stop
        # plt.vlines(4.35, -1, 1, 'g') # Ext. force
        # plt.vlines(5.91, -1, 1, 'g') # Let go
        plt.vlines(6.53, -1, 1, 'r')  # Stop
        plt.vlines(7.15, -1, 1, 'k')  # Back
        plt.vlines(8.43, -1, 1, 'c')  # Stop
        """
    else:
        plt.vlines(0.08, -1, 1, 'r')  # Go
        plt.vlines(1.69, -1, 1, 'r')  # Stop
        # plt.vlines(4.35, -1, 1, 'g') # Ext. force
        # plt.vlines(5.91, -1, 1, 'g') # Let go
        plt.vlines(6.53, -1, 1, 'r')  # Stop
        plt.vlines(7.55, -1, 1, 'k')  # Back
        plt.vlines(9.11, -1, 1, 'c')  # Stop
    plt.xlabel('Time [s]')
    plt.ylabel('Joystick commands [-]')
    # plot left and right sensor data,zoom and save

    plt.subplot(412)
    plt.plot(time_vec, real_current)
    if "scope_13" in filename:
        plt.vlines(1.34, 0, 2, 'r')  # Go
        plt.vlines(2.67, 0, 2, 'r')  # Stop
        plt.vlines(4.35, 0, 2, 'g')  # Ext. force
        plt.vlines(5.91, 0, 2, 'g')  # Let go
        plt.vlines(6.66, 0, 2, 'r')  # Stop
        plt.vlines(7.57, 0, 2, 'k')  # Back
        plt.vlines(8.66, 0, 2, 'c')  # Stop
    elif "scope_14" in filename:
        """
        plt.vlines(0.255, 0, 2, 'r')  # Go
        plt.vlines(2.66, 0, 2, 'r')  # Stop
        plt.vlines(4.44, 0, 2, 'g')  # Ext. force
        plt.vlines(5.76, 0, 2, 'g')  # Let go
        plt.vlines(6.66, 0, 2, 'r')  # Stop
        plt.vlines(7.255, 0, 2, 'k')  # Back
        plt.vlines(8.55, 0, 2, 'c')  # Stop
        """
    else:
        plt.vlines(0.46, 0, 2, 'r')  # Go
        plt.vlines(1.88, 0, 2, 'r')  # Stop
        plt.vlines(4.29, 0, 2, 'g')  # Ext. force
        plt.vlines(5.68, 0, 2, 'g')  # Let go
        plt.vlines(6.68, 0, 2, 'r')  # Stop
        plt.vlines(7.67, 0, 2, 'k')  # Back
        plt.vlines(9.28, 0, 2, 'c')  # Stop
    plt.xlabel('Time [s]')
    plt.ylabel('Real current [A]')

    plt.subplot(413)
    plt.plot(time_vec, feedback_vec)
    if "scope_13" in filename:
        plt.vlines(1.72, 0, 2, 'r')  # Go
        plt.vlines(2.8, 0, 2, 'r')  # Stop
        plt.vlines(4.61, 0, 2, 'g')  # Ext. force
        plt.vlines(6.1, 0, 2, 'g')  # Let go
        plt.vlines(6.81, 0, 2, 'r')  # Stop
        #plt.vlines(0, 0, 2, 'k')  # Back
        plt.vlines(8.57, 0, 2, 'c')  # Stop
    elif "scope_14" in filename:
        """
        plt.vlines(0.82, 0, 2, 'r')  # Go
        plt.vlines(2.8, 0, 2, 'r')  # Stop
        plt.vlines(4.7, 0, 2, 'g')  # Ext. force
        plt.vlines(6.01, 0, 2, 'g')  # Let go
        plt.vlines(6.80, 0, 2, 'r')  # Stop
        #plt.vlines(0, 0, 2, 'k')  # Back
        plt.vlines(8.49, 0, 2, 'c')  # Stop
        """
    else:
        plt.vlines(0.73, 0, 2, 'r')  # Go
        plt.vlines(2.02, 0, 2, 'r')  # Stop
        plt.vlines(4.36, 0, 2, 'g')  # Ext. force
        plt.vlines(5.74, 0, 2, 'g')  # Let go
        plt.vlines(6.83, 0, 2, 'r')  # Stop
        plt.vlines(7.59, 0, 2, 'k')  # Back
        plt.vlines(9.15, 0, 2, 'c')  # Stop
    plt.xlabel('Time [s]')
    plt.ylabel('Ref. compression [mm]')

    plt.subplot(414)
    plt.plot(time_vec, sensor_dist_vec)
    if "scope_13" in filename:
        plt.vlines(1.85, 0, 2, 'r')  # Go
        plt.vlines(2.83, 0, 2, 'r')  # Stop
        plt.vlines(4.64, 0, 2, 'g')  # Ext. force
        plt.vlines(6.1, 0, 2, 'g')  # Let go
        plt.vlines(6.81, 0, 2, 'r')  # Stop
        #plt.vlines(0, 0, 2, 'k')  # Back
        plt.vlines(8.66, 0, 2, 'c')  # Stop
    elif "scope_14" in filename:
        """
        plt.vlines(1.25, 0, 2, 'r') # Go
        plt.vlines(2.825, 0, 2, 'r') # Stop
        plt.vlines(4.75, 0, 2, 'g') # Ext. force
        plt.vlines(6.015, 0, 2, 'g') # Let go
        plt.vlines(6.82, 0, 2, 'r') # Stop
        #plt.vlines(0, 0, 2, 'k') # Back
        plt.vlines(8.666, 0, 2, 'c') # Stop
        """
    else:
        plt.vlines(1.01, 0, 2, 'r')  # Go
        plt.vlines(2.27, 0, 2, 'r')  # Stop
        plt.vlines(4.4, 0, 2, 'g')  # Ext. force
        plt.vlines(6.16, 0, 2, 'g')  # Let go
        plt.vlines(7.36, 0, 2, 'r')  # Stop
        #plt.vlines(0, 0, 2, 'k')  # Back
        #plt.vlines(8.666, 0, 2, 'c')  # Stop
    plt.xlabel('Time [s]')
    plt.ylabel('Compression [mm]')

    figure_directory = 'figs/'
    if not os.path.exists(figure_directory):
        os.makedirs(figure_directory)
    fig.savefig(figure_directory + filename[:-4] + '_latency_plot.jpg')
    #plt.close(fig)

    plt.show()
