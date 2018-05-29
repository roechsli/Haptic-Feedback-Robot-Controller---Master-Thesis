import os
import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from pylab import *
from math import atan2

PLOT_BOOL = True

INTMAX = 65535

PHOTO_MIN_LEFT = 650
PHOTO_MAX_LEFT = 830
PHOTO_MIN_RIGHT = 700
PHOTO_MAX_RIGHT = 870

"""
PHOTO_MIN_LEFT = 440
PHOTO_MAX_LEFT = 830
PHOTO_MIN_RIGHT = 630
PHOTO_MAX_RIGHT = 875
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
directory = "20180529_fra_logs/"  # TODO change this if new data shall be analyzed
for file in os.listdir(directory):
    if False:  # TODO change this, if you want to skip all this calculation
        freq_vec = [1.25, 1.6, 100, 10, 12.6, 16, 1, 2.5, 20, 25, 2, 3.17, 32, 40, 4, 50, 5, 6.3, 63, 80, 8]
        amplitude_factor_l = [0.17675981919970632, 0.18312267399356463, 0.01949341829267395, 0.26978239192019077, 0.33311878171527165, 0.369774072356006, 0.17400096951295416, 0.1861252801566901, 0.40017296807194397, 0.35064397887112764, 0.18210014901931423, 0.18511272146373267, 0.24791723227837462, 0.1493456317662998, 0.19146047921594653, 0.0870301532158636, 0.21099364288831401, 0.2147280185263324, 0.057726254563911, 0.033107839481778374, 0.2268739054577375]
        phasediff_l = [205.3467514567597, -153.83743080935628, -320.4845338866222, -138.41202856697728, -130.70251871686537, -117.61487228247117, -153.8657640699463, 206.6923061292191, -94.09974537617197, -63.71638847428862, -153.943579306678, -152.81436374583922, -32.06355657979239, -12.819295739503332, 208.9100765632432, -358.5403588020346, 211.22988735406227, -147.1806573568082, 15.21830488777887, 28.40729165304161, -143.45301992811727]
        amplitude_factor_r = [0.3213865015198608, 0.3402113519590562, 0.0017350629530853432, 0.2632195090055476, 0.20043435967514273, 0.13753176962093036, 0.30703807504243574, 0.3555171356019676, 0.08792206197073925, 0.0558128683646143, 0.3419203111085945, 0.3610073717927054, 0.031094711719848636, 0.01909289974777871, 0.3600614244021166, 0.009350720910695715, 0.3600395998619217, 0.34258954235828526, 0.005405908932899052, 0.0028516219104144456, 0.31218786121127073]
        phasediff_r = [204.92819072330562, -151.97006600815976, -319.84408374620705, -79.27443527064112, -62.72997159062926, -45.326803861137805, -157.37797161148433, 215.27285553574174, -30.801214613586374, -16.750805205243367, -149.4433775479537, -139.3751588712953, -3.0897574145693305, 8.407631597919078, 228.2595159881846, -342.8433311689313, 236.59164331706756, -112.32516351906195, 22.705565035590723, 30.47923008367799, -97.33697806039062]

        continue

    if ".csv" not in file:
        continue
    frequency = get_freq_from_filename(file)
    frequency_float = float(frequency)
    print(frequency)

    # to restrict to first file only
    if "f2_csv" not in file:
        pass  # TODO change this to continue if only one frequency file should be treated

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
    yMeasured_out_l = map_to_255(df.iloc[:, 1], PHOTO_MIN_LEFT, PHOTO_MAX_LEFT)#df.iloc[:, 1]  # shift of four to have the right side
    (phaseEst_out_l, amplitudeEst_out_l, biasEst_out_l) = fitSine(tSamples, yMeasured_out_l, frequency_float)

    # output right
    yMeasured_out_r = map_to_255(df.iloc[:, 2], PHOTO_MIN_RIGHT, PHOTO_MAX_RIGHT)#df.iloc[:, 2]  # shift of four to have the right side
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
print(amplitude_factor_l)
print(phasediff_l)
print(amplitude_factor_r)
print(phasediff_r)
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