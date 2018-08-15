"""
This program reads the oscilloscope data that has been measured for latency tests and plots it

Version: 1.01
Roman Oechslin
Master Thesis - University of Tokyo
Date: August 2018
"""
import os
import pandas as pd
import matplotlib.pyplot as plt


directory = "osc_data/"
PHOTO_MIN_LEFT = 600
PHOTO_MAX_LEFT = 790
PHOTO_MIN_RIGHT = 700
PHOTO_MAX_RIGHT = 880
MAX_DISPLACEMENT_UM = 1800
PHOTO_MIN_LEFT = 550
PHOTO_MAX_LEFT = 780
PHOTO_MIN_RIGHT = 600
PHOTO_MAX_RIGHT = 763
MAX_DISPLACEMENT_UM = 5000


def sensor2dist(sensor_value, min_val, max_val):
    # maps the measured value to the distance (assumed linearity) in micrometers
    return (MAX_DISPLACEMENT_UM - (sensor_value - min_val) * MAX_DISPLACEMENT_UM / (max_val - min_val)) / 1000


for filename in os.listdir(directory):
    print(filename)
    # plotting
    df = pd.read_csv(directory + filename, delimiter=',')
    my_multiplier = 1
    if "b" in filename:
        my_multiplier = 1.800
    elif "a" in filename:
        my_multiplier = 5.000

    for i in range(len(df.iloc[:, 3]) - 3):
        # convert sensor values to mm
        df.iloc[i + 3, 2] = (float(df.iloc[i + 3, 2]) - 0.4)/2.4 * my_multiplier  # sensor
        df.iloc[i + 3, 0] = float(df.iloc[i + 3, 0])  # time
        df.iloc[i + 3, 1] = (float(df.iloc[i + 3, 1]) - 0.4)/2.4 * my_multiplier  # feedback
        df.iloc[i + 3, 3] = float(df.iloc[i + 3, 3])  # motor voltage

    time_vec = df.iloc[3:, 0] - df.iloc[3, 0]
    motor_volt_vec = df.iloc[3:, 3]
    feedback_vec = df.iloc[3:, 1]
    sensor_dist_vec = df.iloc[3:, 2]
    fig = plt.figure(figsize=(15.0, 6.5))
    fig.suptitle('Unity simulation testing')
    plt.subplot(212)
    plt.plot(time_vec, motor_volt_vec)  # plot reference
    plt.xlabel('Time [s]')
    plt.ylabel('Motor voltage [V]')
    # plot left and right sensor data, zoom and save
    plt.subplot(211)
    plt.plot(time_vec, feedback_vec, 'g')
    plt.xlabel('Time [s]')
    plt.ylabel('Desired compression [mm]')
    plt.subplot(211)
    plt.plot(time_vec, sensor_dist_vec, color='darkorange')
    plt.xlabel('Time [s]')
    plt.ylabel('Compression [mm]')
    #plt.axis([2.9, 3.6, 0, 255])
    plt.legend(["reference", "measured"])

    figure_directory = 'figs/'
    if not os.path.exists(figure_directory):
        os.makedirs(figure_directory)
    #print (figure_directory + filename[:-4] + '_latency_plot.jpg')
    fig.savefig(figure_directory + filename[:-4] + '_latency_plot.jpg')
    plt.close(fig)

    #plt.show()
