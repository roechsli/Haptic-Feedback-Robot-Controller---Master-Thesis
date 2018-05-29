import os
import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from pylab import *
from math import atan2

PLOT_BOOL = True

INTMAX = 65535
PHOTO_MIN_LEFT = 440
PHOTO_MAX_LEFT = 830
PHOTO_MIN_RIGHT = 630
PHOTO_MAX_RIGHT = 875

def get_freq_from_filename(filename):
    if filename[0] == "f" and filename[-8:] == "_csv.csv":
        return filename[1:-8]
    else:
        return ""

def map_to_255(receptor_value, min_val, max_val):
    # this is the same function as in arduino code, that maps the measured value
    # to the range [0..255] =  [normal..compressed]
    converted = (receptor_value - min_val) * 51 / (max_val - min_val) * 5
    converted = 255 - converted
    return converted

def fitSine(tList, yList, freq):
    #from: http://exnumerus.blogspot.jp/2010/04/how-to-fit-sine-wave-example-in-python.html
    '''
        freq in Hz
        tList in sec
    returns
        phase in degrees
    '''
    b = matrix(yList).T
    rows = [[sin(freq * 2 * pi * t), cos(freq * 2 * pi * t), 1] for t in tList]
    A = matrix(rows)
    (w, residuals, rank, sing_vals) = lstsq(A, b)
    phase = atan2(w[1, 0], w[0, 0]) * 180 / pi
    amplitude = norm([w[0, 0], w[1, 0]], 2)
    bias = w[2, 0]
    return phase, amplitude, bias


phasediff_r = []
amplitude_factor_r = []
phasediff_l = []
amplitude_factor_l = []
freq_vec = []
directory = "fra_logs/"
for file in os.listdir(directory):
    if True:  # if you want to skip all this calculation
        freq_vec = [1.25, 1.6, 100, 10, 12.6, 16, 1, 2.5, 20, 25, 2, 3.17, 32, 40, 4, 50, 5, 6.3, 63, 80, 8]
        amplitude_factor_l = [0.18312093655031383, 0.19008585620535026, 0.015550463478211691,
                              0.2791834510627954, 0.318225202275935, 0.39337844196486743,
                              0.2640693861334663, 0.15937256387989965, 0.38442913558776726,
                              0.3368011239491985, 0.26341416323742706, 0.179587380570377,
                              0.1745501197868898, 0.10820490293940287, 0.19803844662374293,
                              0.08153603742180517, 0.23386509533281746, 0.2515841646660729,
                              0.045070733483577624, 0.033746128437573436, 0.2293490151221878]

        phasediff_l = [209.32028861381468, -150.2394102526345, 16.348740203083963,
                       -123.74347056229176, 246.3235080372831, -96.87180529921147,
                       210.56561019430046, -140.12790964226284, -83.89682238439842,
                       305.4530750590407, 213.57525945841107, 223.69998825937347,
                       -34.83878142240319, -20.037439212939162, 220.4153835818249,
                       -7.246983978798568, 228.65728177360177, -133.39059860045023,
                       -0.625870996573866, 26.21769676881804, -131.20258235070216]


        amplitude_factor_r = [0.37804045847813944, 0.40049081380365026, 0.0017208776805125235,
                              0.24154040379733116, 0.17283568553961723, 0.11569976621357908,
                              0.3957775933783711, 0.38435417601557065, 0.07698536204876438,
                              0.05051462446239852, 0.41448318432568554, 0.39907402546710335,
                              0.02871012224402575, 0.01439112649707848, 0.40250562818628777,
                              0.0075704099216118296, 0.3883647221254421, 0.35261224979808753,
                              0.0049664432586177, 0.0026045342448563625, 0.3026066455918329]


        phasediff_r = [207.98768677028977, -147.77310639192558, 55.97828157699515,
                       -70.56664107667996, 305.35723712143783, -38.99482826513405,
                       204.75642028354335, -139.85832051211634, -25.61847064680822,
                       -15.2999187212653, -142.80695875247153, 226.92626461535167,
                       -2.128589352480205, 6.1298593373593775, -125.13742395703514,
                       14.665392440703343, 244.4929408859628, -102.14554577336645,
                       27.36961260908157, 38.95750966221672, -86.31093760972809]


        continue

    if ".csv" not in file:
        continue
    frequency = get_freq_from_filename(file)
    frequency_float = float(frequency)
    print(frequency)

    # to restrict to first file only
    if "f2_csv" not in file:
        pass  # write pass if all files should be treated

    df = pd.read_csv(directory + file, delimiter=';')
    # make timeline continuous and not overflow and change from [us] to [s]
    for i in range(len(df.iloc[:,3]) -1):
        if df.iloc[i,3] > df.iloc[i+1,3]:
            df.iloc[i+1:,3] = df.iloc[i+1:,3] + INTMAX
    for i in range(len(df.iloc[:, 3])):
        df.iloc[i, 3] = df.iloc[i, 3] / 1000000  # convert to seconds

    if PLOT_BOOL:
        print("plotting freq " + frequency)
        fig = plt.figure()
        plt.plot(df.iloc[:, 3],df.iloc[:, 0])  # plot reference
        fig.suptitle('Frequency response (' + frequency + ' Hz)')
        plt.xlabel('Time [s]')
        plt.ylabel('Distance [-]')
        # plot left and right sensor data,zoom and save
        plt.plot(df.iloc[:, 3], map_to_255(df.iloc[:, 1], PHOTO_MIN_LEFT, PHOTO_MAX_LEFT))
        plt.plot(df.iloc[:, 3], map_to_255(df.iloc[:, 2], PHOTO_MIN_RIGHT, PHOTO_MAX_RIGHT))
        plt.axis([2.9, 3.6, 0, 255])
        plt.legend(["distance reference", "left sensor mapped", "right sensor mapped"])
        figure_directory = 'figs/f' + frequency
        if not os.path.exists(figure_directory):
            os.makedirs(figure_directory)
        fig.savefig(figure_directory + '/plot_sensor_zoom.jpg')
        plt.close(fig)

    # frequency response analysis
    # input
    yMeasured_in = df.iloc[:, 0]
    tSamples = df.iloc[:, 3]
    (phaseEst_in, amplitudeEst_in, biasEst_in) = fitSine(tSamples, yMeasured_in, frequency_float)

    # output left
    yMeasured_out_l = df.iloc[:, 1]  # shift of four to have the right side
    (phaseEst_out_l, amplitudeEst_out_l, biasEst_out_l) = fitSine(tSamples, yMeasured_out_l, frequency_float)

    # output right
    yMeasured_out_r = df.iloc[:, 2]  # shift of four to have the right side
    (phaseEst_out_r, amplitudeEst_out_r, biasEst_out_r) = fitSine(tSamples, yMeasured_out_r, frequency_float)
    # magnitude and phase offset
    phasediff_l.append(phaseEst_in - phaseEst_out_l)
    amplitude_factor_l.append(amplitudeEst_out_l / amplitudeEst_in)
    phasediff_r.append(phaseEst_in - phaseEst_out_r)
    amplitude_factor_r.append(amplitudeEst_out_r / amplitudeEst_in)
    freq_vec.append(frequency_float)

# plot Bode diagram (freq_vec, magn_vec) and (freq_vec, phase_offset_vec)
# save figures
indices = np.argsort(freq_vec)
amplitude_factor_l = 20 * np.log(amplitude_factor_l)
amplitude_factor_r = 20 * np.log(amplitude_factor_r)

left_bode, axarr_l = plt.subplots(2, sharex=True)
axarr_l[0].semilogx([freq_vec[x] for x in indices], [amplitude_factor_l[x] for x in indices])
axarr_l[0].set_title('Bode diagram - left side')
axarr_l[1].semilogx([freq_vec[x] for x in indices], [phasediff_l[x] if phasediff_l[x] < 0 else phasediff_l[x] - 360 for x in indices])
#axarr_l[1].semilogx([freq_vec[x] for x in indices], [phasediff_l[x]  for x in indices])
axarr_l[1].set_xlabel('Frequency [rad/sec]')
axarr_l[0].set_ylabel('Magnitude [dB]')
axarr_l[1].set_ylabel('Phase [deg]')
axarr_l[0].grid()
axarr_l[1].grid()
figure_directory = 'figs/'
left_bode.savefig(figure_directory + '/bode_left.jpg')


right_bode, axarr_r = plt.subplots(2, sharex=True)
axarr_r[0].semilogx([freq_vec[x] for x in indices], [amplitude_factor_r[x] for x in indices])
axarr_r[0].set_title('Bode diagram - right side')
axarr_r[1].semilogx([freq_vec[x] for x in indices], [phasediff_r[x] if phasediff_r[x] < 0 else phasediff_r[x] - 360 for x in indices])
#axarr_r[1].semilogx([freq_vec[x] for x in indices], [phasediff_r[x] for x in indices])
axarr_r[1].set_xlabel('Frequency [rad/sec]')
axarr_r[0].set_ylabel('Magnitude [dB]')
axarr_r[1].set_ylabel('Phase [deg]')
axarr_r[0].grid()
axarr_r[1].grid()
figure_directory = 'figs/'
right_bode.savefig(figure_directory + '/bode_right.jpg')

plt.show()