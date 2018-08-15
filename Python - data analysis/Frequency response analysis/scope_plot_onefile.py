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
import pickle


#scope3 from real robot testing is best
directory = "20180801_pilot_step_tracking2/"


PHOTO_MIN_LEFT = 550
PHOTO_MAX_LEFT = 780
PHOTO_MIN_RIGHT = 600
PHOTO_MAX_RIGHT = 763
MAX_DISPLACEMENT_UM = 5.0
counter_vec = [1, 2, 5, 6, 1, 2, 5, 6]

def sensor2dist(sensor_value, min_val, max_val):
    # maps the measured value to the distance (assumed linearity) in micrometers
    return MAX_DISPLACEMENT_UM - (sensor_value - min_val) * MAX_DISPLACEMENT_UM / (max_val - min_val)

"""
for filename in os.listdir(directory):
    if "csv" not in filename:
        continue
    print(filename)
    # plotting
    df = pd.read_csv(directory + filename, delimiter=',')


    for i in range(len(df.iloc[:,3]) -3):
        # convert sensor values to mm
        #print(i)
        df.iloc[i + 3, 0] = float(df.iloc[i + 3, 0])
        df.iloc[i + 3, 1] = float(df.iloc[i + 3, 1])  # photoreceptor measured distance
        df.iloc[i + 3, 2] = sensor2dist(-float(df.iloc[i + 3, 2])/5 * 1024, PHOTO_MIN_LEFT, PHOTO_MAX_LEFT)  # reference from wave generator
        df.iloc[i + 3, 3] = float(df.iloc[i + 3, 3])  # applied motor voltage

    #Osc3: joystick (A0) in channel 1 and feedback (current mode) in channel 2; dist sensor (A2) in channel 3
    time_vec = df.iloc[3:, 0] - df.iloc[3, 0]
    ref_vec = df.iloc[3:, 1]
    photoreceptor_vec = df.iloc[3:, 2]
    motor_volt_vec = df.iloc[3:, 3]
    sensor_dist_vec = df.iloc[3:, 3]

    fig = plt.figure(figsize=(15.0, 6.5))
    plt.subplot(2, 1, 1)
    fig.suptitle('Pilot tracking performance')
    plt.plot(time_vec, ref_vec)  # plot reference
    plt.plot(time_vec, photoreceptor_vec)  # plot reference
    plt.legend(['Reference', 'Sensor left'])
    plt.xlabel('Time [s]')
    plt.ylabel('Compression [mm]')


    plt.subplot(2, 1, 2)
    plt.plot(time_vec, motor_volt_vec)  # plot reference
    #plt.legend(['Reference', 'Sensor left'])
    plt.xlabel('Time [s]')
    plt.ylabel('Motor voltage [V]')

    fig.savefig(directory + 'figs/' + filename[:-4] + 'plot.jpg')
    with open(directory + 'figs/' + filename[:-4] + '_raw.pkl', "wb") as fp:
        pickle.dump(fig, fp, protocol=4)
    plt.close(fig)  # for not plotting all the pictures
    #plt.show()
"""

counter = 0
for filename in os.listdir(directory):
    if "csv" not in filename:
        continue
    print(filename)
    # plotting
    df = pd.read_csv(directory + filename, delimiter=',')

    for i in range(len(df.iloc[:, 3]) - 3):
        # convert sensor values to mm
        # print(i)
        df.iloc[i + 3, 0] = float(df.iloc[i + 3, 0])
        df.iloc[i + 3, 1] = float(df.iloc[i + 3, 1])  # photoreceptor measured distance
        df.iloc[i + 3, 2] = sensor2dist(-float(df.iloc[i + 3, 2]) / 5 * 1024, PHOTO_MIN_LEFT,
                                        PHOTO_MAX_LEFT)  # reference from wave generator
        df.iloc[i + 3, 3] = float(df.iloc[i + 3, 3])  # applied motor voltage

    # Osc3: joystick (A0) in channel 1 and feedback (current mode) in channel 2; dist sensor (A2) in channel 3
    time_vec = df.iloc[3:, 0] - df.iloc[3, 0]
    ref_vec = df.iloc[3:, 1]
    photoreceptor_vec = df.iloc[3:, 2]
    motor_volt_vec = df.iloc[3:, 3]
    sensor_dist_vec = df.iloc[3:, 3]

    fig = plt.figure(int(counter/4)+1, figsize=(15.0, 8))
    plt.subplot(4, 2, counter_vec[counter])
    fig.suptitle('Pilot tracking performance')

    plt.plot(time_vec, ref_vec)  # plot reference
    plt.plot(time_vec, photoreceptor_vec)  # plot reference
    plt.legend(['Reference', 'Sensor left'])
    plt.xlabel('Time [s]')
    plt.ylabel('Compression [mm]')
    plt.ylim([0, 4.5])


    plt.subplot(4, 2, counter_vec[counter]+2)
    plt.plot(time_vec, motor_volt_vec)  # plot reference
    # plt.legend(['Reference', 'Sensor left'])
    plt.xlabel('Time [s]')
    plt.ylabel('Motor voltage [V]')
    plt.ylim([-20.2, 22.2])

    if counter%4 == 3:
        fig.savefig(directory + 'figs/pilot_tracking_perf' + str(counter) + '.jpg')
        with open(directory + 'figs/pilot_tracking_perf' + str(counter) + '.pkl', "wb") as fp:
            pickle.dump(fig, fp, protocol=4)
        plt.close(fig)  # for not plotting all the pictures
    counter = counter + 1
    # plt.show()