import os
import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pickle

from pylab import *
from math import atan2

PLOT_BOOL = True  # to overwrite the figures saved in folder /figs
CALC_OPER_FREQ = False  # to calculate the operating frequency for all frequencies
SHORTCUT = False  # change this, if you want to skip all this calculation
only_this_file = "f"  # change this to "f" if all frequencies shall be tested, otherwise "f2_csv"

INTMAX = 65535

PHOTO_MIN_LEFT = 650
PHOTO_MAX_LEFT = 830
PHOTO_MIN_RIGHT = 700
PHOTO_MAX_RIGHT = 870
directory = "20180529_fra_logs/"  # TODO change this if new data shall be analyzed

"""
PHOTO_MIN_LEFT = 440
PHOTO_MAX_LEFT = 830
PHOTO_MIN_RIGHT = 630
PHOTO_MAX_RIGHT = 875
directory = "20180525_fra_logs/"  # TODO change this if new data shall be analyzed
"""

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
for file in os.listdir(directory):
    if SHORTCUT:
        freq_vec = [1.25, 1.6, 100, 10, 12.6, 16, 1, 2.5, 20, 25, 2, 3.17, 32, 40, 4, 50, 5, 6.3, 63, 80, 8]
        amplitude_factor_l = [0.25040974386625153, 0.2594237881575532, 0.027615675914620687, 0.38219172188693584, 0.47191827409663434, 0.5238466025043429, 0.24650137347668222, 0.26367748022198007, 0.5669117047685919, 0.4967456367340987, 0.2579752111106925, 0.2622430220736225, 0.3512160790610284, 0.2115729783355916, 0.27123567888926187, 0.12329271705580712, 0.29890766075845365, 0.3041980262456386, 0.08177886063221472, 0.04690277259918248, 0.32140469939845934]
        phasediff_l = [25.346751456760742, -333.83743080935653, -140.48453388661724, 41.587971433023625, -310.7025187168664, 62.385127717528775, -333.8657640699465, 26.692306129220952, 85.9002546238281, -243.7163884742885, 26.05642069332231, 27.185636254161082, 147.93644342020917, 167.18070426049786, 28.910076563242654, -178.54035880203273, 31.22988735406183, -327.1806573568086, 195.2183048877806, -151.59270834695292, 36.54698007188293]
        amplitude_factor_r = [0.48207975227979577, 0.510317027938587, 0.002602594429631148, 0.3948292635083239, 0.30065153951271084, 0.20629765443139778, 0.4605571125636496, 0.5332757034029528, 0.13188309295611006, 0.08371930254692196, 0.5128804666628917, 0.5415110576890578, 0.04664206757977547, 0.028639349621668753, 0.540092136603179, 0.014026081366043247, 0.5400593997928911, 0.5138843135374294, 0.008108863399352646, 0.004277432865617745, 0.4682817918169037]
        phasediff_r = [24.928190723305732, -331.97006600815985, -139.8440837460424, -259.2744352706402, -242.72997159062953, 134.67319613886136, -337.377971611484, 35.27285553574225, 149.19878538641257, -196.7508052052425, 30.556622452045957, 40.624841128704745, -183.08975741455893, 188.407631597924, 48.25951598818422, -162.8433311689285, 56.591643317067124, -292.3251635190619, 202.70556503559357, -149.52076991621885, -277.33697806039027]

        continue

    if ".csv" not in file:
        continue
    frequency = get_freq_from_filename(file)
    frequency_float = float(frequency)
    print(frequency)

    # to restrict to first file only
    if only_this_file not in file:
        continue

    df = pd.read_csv(directory + file, delimiter=';')
    # make timeline continuous and not overflow and change from [us] to [s]
    for i in range(len(df.iloc[:,3]) -1):
        if df.iloc[i,3] > df.iloc[i+1,3]:
            df.iloc[i+1:,3] = df.iloc[i+1:,3] + INTMAX

    # just to have an average us length of a step:
    if CALC_OPER_FREQ:
        step_sum = 0
        for i in range(len(df.iloc[:,3]) - 1):
            step_sum = step_sum + df.iloc[i+1,3] - df.iloc[i,3]
        # avg_step_len = step_sum / len(df.iloc[:,3])  # more precise mean
        avg_step_len = (df.iloc[-1,3] - df.iloc[0,3]) / len(df.iloc[:,3])  # global mean
        print("average step length for " + frequency + "Hz is " + str(avg_step_len))
    for i in range(len(df.iloc[:, 3])):
        df.iloc[i, 3] = df.iloc[i, 3] / 1000000  # convert to seconds


    if PLOT_BOOL:
        print("plotting freq " + frequency)
        fig = plt.figure()
        plt.plot(df.iloc[:, 3], df.iloc[:, 0] / 255)  # plot reference
        fig.suptitle('Frequency response (' + frequency + ' Hz)')
        plt.xlabel('Time [s]')
        plt.ylabel('Compression [%]')
        # plot left and right sensor data,zoom and save
        plt.plot(df.iloc[:, 3], map_to_255(df.iloc[:, 1], PHOTO_MIN_LEFT, PHOTO_MAX_LEFT) / 255)
        plt.plot(df.iloc[:, 3], map_to_255(df.iloc[:, 2], PHOTO_MIN_RIGHT, PHOTO_MAX_RIGHT) / 255)
        plt.axis([2, 3.6, 0, 1])
        plt.legend(["reference signal", "left sensor", "right sensor"])
        figure_directory = 'figs/f' + frequency
        if not os.path.exists(figure_directory):
            os.makedirs(figure_directory)
        fig.savefig(figure_directory + '/' + frequency + 'plot_zoom_fixed_time.jpg')
        plt.axis([2, 2 + 3 / frequency_float, 0, 1])
        fig.savefig(figure_directory + '/' + frequency + 'plot_zoom.jpg')
        with open(figure_directory + '/' + frequency + '_raw.pkl', "wb") as fp:
            pickle.dump(fig, fp, protocol=4)
        plt.close(fig)  # for not plotting all the pictures

    # frequency response analysis
    # input
    yMeasured_in = df.iloc[:, 0]
    tSamples = df.iloc[:, 3]
    (phaseEst_in, amplitudeEst_in, biasEst_in) = fitSine(tSamples, yMeasured_in, frequency_float)

    # output left
    yMeasured_out_l = map_to_255(df.iloc[:, 1], PHOTO_MIN_LEFT, PHOTO_MAX_LEFT)#df.iloc[:, 1]
    (phaseEst_out_l, amplitudeEst_out_l, biasEst_out_l) = fitSine(tSamples, yMeasured_out_l, frequency_float)

    # output right
    yMeasured_out_r = map_to_255(df.iloc[:, 2], PHOTO_MIN_RIGHT, PHOTO_MAX_RIGHT)#df.iloc[:, 2]
    (phaseEst_out_r, amplitudeEst_out_r, biasEst_out_r) = fitSine(tSamples, yMeasured_out_r, frequency_float)
    # magnitude and phase offset
    phasediff_l.append(phaseEst_in - phaseEst_out_l)
    amplitude_factor_l.append(amplitudeEst_out_l / amplitudeEst_in)
    phasediff_r.append(phaseEst_in - phaseEst_out_r)
    amplitude_factor_r.append(amplitudeEst_out_r / amplitudeEst_in)
    freq_vec.append(frequency_float)

# plot Bode diagram (freq_vec, magn_vec) and (freq_vec, phase_offset_vec)
# save figures
"""
print(amplitude_factor_l)
print(phasediff_l)
print(amplitude_factor_r)
print(phasediff_r)
"""
indices = np.argsort(freq_vec)
amplitude_factor_l = 20 * np.log10(amplitude_factor_l)
amplitude_factor_r = 20 * np.log10(amplitude_factor_r)

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