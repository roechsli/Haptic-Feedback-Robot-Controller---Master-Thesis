"""
This program reads out the raw data saved in the csv files from the oscilloscope
Then it plots the figures using matplotlib
Version: 1.0
Roman Oechslin
Master Thesis - University of Tokyo

"""

import os
import matplotlib.pyplot as plt
import pickle
import pandas as pd

directory = "../../Data/PID_quality/20180703_4th_PID_243_63_00126/ardu_ref_tracking/"
destination = "tmp_ardu_ref_plots/"

filter_value = [1.6, 1.6, 1.6, 1.6, 4.2, 4.2, 4.2, 4.2, 8.8, 8.8, 8.8, 8.8]

INTMAX = 65535
PHOTO_MIN_LEFT = 640
PHOTO_MAX_LEFT = 840
PHOTO_MIN_RIGHT = 700
PHOTO_MAX_RIGHT = 880
MAX_DISPLACEMENT_UM = 1800

def sensor2dist(sensor_value, min_val, max_val):
  # maps the measured value to the distance (assumed linearity) in micrometers
  return (MAX_DISPLACEMENT_UM - (sensor_value - min_val) * MAX_DISPLACEMENT_UM / (max_val - min_val) ) / 1000


for filename in os.listdir(directory):
    print(filename)
    source= open(directory + filename, "r")
    destination_file = open(destination + filename[:-4] + "_csv" + ".csv", "w")
    for line in source:
        buf = ""
        for character in line:
            if character == ";":
                destination_file.write(str(int(buf, 16)) + ";")
                buf = ""
            elif character == "\n":
                destination_file.write("\n")
                buf = ""
            else:
                buf = buf + character
    source.close()
    destination_file.close()

counter = 0
for filename in os.listdir(destination):
    if ".csv" not in filename:
        continue
    df = pd.read_csv(destination + filename, delimiter=';')
    # make timeline continuous (no overflow), change [us] to [s] convert sensor value to [mm]
    for i in range(len(df.iloc[:,3]) -1):
        if df.iloc[i,3] > df.iloc[i+1,3]:
            df.iloc[i+1:,3] = df.iloc[i+1:,3] + INTMAX
    for i in range(len(df.iloc[:,3])):
        df.iloc[i, 3] = df.iloc[i, 3] / 1000000  # convert to seconds
        df.iloc[i,0] = df.iloc[i,0] / 1000  # convert reference to mm
        # convert sensor values to mm
        df.iloc[i,1] = sensor2dist(df.iloc[i,1], PHOTO_MIN_LEFT, PHOTO_MAX_LEFT)
        df.iloc[i,2] = sensor2dist(df.iloc[i,2], PHOTO_MIN_RIGHT, PHOTO_MAX_RIGHT)
    print("plotting file " + filename[:-4])
    fig = plt.figure()
    # plot left and right sensor data,zoom and save
    plt.plot(df.iloc[:, 3], df.iloc[:, 1])
    plt.plot(df.iloc[:, 3], df.iloc[:, 2])
    plt.plot(df.iloc[:, 3], df.iloc[:, 0])  # plot reference
    fig.suptitle('Tracking behavior - Filter: ' + str (filter_value[counter]) + 'Hz')
    plt.xlabel('Time [s]')
    plt.ylabel('Compression [mm]')
    # plt.axis([2, 3.6, -0.05, 0.5])
    plt.axis([2.2, 4, 0, 2])
    plt.legend(["left sensor", "right sensor", "reference signal"])
    figure_directory = destination + 'figs/'
    if not os.path.exists(figure_directory):
        os.makedirs(figure_directory)
    fig.savefig(figure_directory + '/' + filename[:-8] + 'plot_zoom.jpg')
    with open(figure_directory + '/' + filename[:-8] + '_raw.pkl', "wb") as fp:
        pickle.dump(fig, fp, protocol=4)
    plt.close(fig)  # for not plotting all the pictures
    counter = counter + 1