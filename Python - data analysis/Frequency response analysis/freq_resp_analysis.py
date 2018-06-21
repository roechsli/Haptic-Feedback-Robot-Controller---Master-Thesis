import os
import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pickle

from pylab import *
from math import atan2

PLOT_BOOL = True
CALC_OPER_FREQ = False
SHORT_CUT = True
only_this_file = "f"  # change this to "f" if all frequencies shall be tested, otherwise "f2_csv"

INTMAX = 65535
PHOTO_MIN_LEFT = 650
PHOTO_MAX_LEFT = 830
PHOTO_MIN_RIGHT = 700
PHOTO_MAX_RIGHT = 870
MAX_DISPLACEMENT_UM = 1800
directory = "20180621_fra_logs/"  # TODO change this if new data shall be analyzed

def get_freq_from_filename(filename):
    if filename[0] == "f" and filename[-8:] == "_csv.csv":
        return filename[1:-8]
    else:
        return ""

def sensor2dist(sensor_value, min_val, max_val):
  # maps the measured value to the distance (assumed linearity) in micrometers
  return (MAX_DISPLACEMENT_UM - (sensor_value - min_val) * MAX_DISPLACEMENT_UM / (max_val - min_val) ) / 1000

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
    if SHORT_CUT:  # TODO change this, if you want to skip all the calculation
        freq_vec = [1.25, 1.6, 100, 10, 12.6, 16, 1, 2.5, 20, 25, 2, 3.17, 32, 40, 4, 50, 5, 6.3, 63, 80, 8]
        amplitude_factor_l = [0.42398913976097446, 0.4282153912079033, 0.12378284313044466, 0.711221069409896,
                               0.7225816897317351, 0.7646527825863285, 0.40112267357697934, 0.42743202148716863,
                               0.9914095813817145, 1.2222055794324236, 0.4284915596303108, 0.42862587415289155,
                               1.6182794339223205, 1.264568245831212, 0.4311669676245879, 0.5462780686764698,
                               0.44415703547915164, 0.5944384653289748, 0.2708103187351025, 0.170468881007046,
                               0.6476744573446083]
        phasediff_l = [-29.67419316918162, 329.3954574722484, 151.77595893442785, -34.1606097854003,
                       -37.606370641125956, -40.36468813694745, -30.36855317966672, -31.3116501593979,
                       -47.26522334530678, 306.8163968335256, -30.42922969682391, -32.857491878311464,
                       -97.71371390960005, 201.5446736191579, -33.54162038250308, 190.83991403280896,
                       -34.409877680170055, 329.51955549109414, -178.44505217712023, -191.64710085535776,
                       -31.420544562906162]
        amplitude_factor_r = [0.682529120529401, 0.6881751766721432, 0.0022154853818361154, 0.9234556155923191,
                              0.8826716111054062, 0.6589189142362378, 0.6824321178608364, 0.7149014578498121,
                              0.4682488094473188, 0.2899691163444707, 0.6985377868987559, 0.7410563355373039,
                              0.14053263238672217, 0.05085633307181245, 0.7602497656273546, 0.0258420423441291,
                              0.8079029768733247, 0.8547492932126076, 0.011593031609452593, 0.005914752729396196,
                              0.8929581931654754]
        phasediff_r = [-20.266230280843104, 338.87333291671956, 104.73683443996734, -68.027983641311, -93.7109757424358,
                       238.84336015384935, -19.797341054607188, -24.148441334186202, -140.83812403663828,
                       201.01499505958088, -22.34252685864527, -26.849042440608443, 191.0566801899678,
                       178.3109527558047, -30.078416184330564, 172.97924637960566, -35.34272693855357,
                       317.35253460336855, -176.6359639822056, -204.16704226303582, -52.8252198134289]

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

    # just to have an average us length of a step:
    if CALC_OPER_FREQ:
        step_sum = 0
        for i in range(len(df.iloc[:,3]) - 1):
            step_sum = step_sum + df.iloc[i+1,3] - df.iloc[i,3]
        # avg_step_len = step_sum / len(df.iloc[:,3])  # more precise mean
        avg_step_len = (df.iloc[-1,3] - df.iloc[0,3]) / len(df.iloc[:,3])  # global mean
        print("average step length for " + frequency + "Hz is " + str(avg_step_len))

    if PLOT_BOOL:
        print("plotting freq " + frequency)
        fig = plt.figure()
        plt.plot(df.iloc[:, 3], df.iloc[:, 0] )  # plot reference
        fig.suptitle('Frequency response (' + frequency + ' Hz)')
        plt.xlabel('Time [s]')
        plt.ylabel('Compression [mm]')
        # plot left and right sensor data,zoom and save
        plt.plot(df.iloc[:, 3], df.iloc[:, 1])
        plt.plot(df.iloc[:, 3], df.iloc[:, 2])
        plt.axis([2, 3.6, -0.05, 0.5])
        plt.legend(["reference signal", "left sensor", "right sensor"])
        figure_directory = 'figs/f' + frequency
        if not os.path.exists(figure_directory):
            os.makedirs(figure_directory)
        fig.savefig(figure_directory + '/' + frequency + 'plot_zoom_fixed_time.jpg')
        plt.axis([2, 2 + 3 / frequency_float, -0.05, 0.5])
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
    yMeasured_out_l = df.iloc[:, 1]
    (phaseEst_out_l, amplitudeEst_out_l, biasEst_out_l) = fitSine(tSamples, yMeasured_out_l, frequency_float)

    # output right
    yMeasured_out_r = df.iloc[:, 2]
    (phaseEst_out_r, amplitudeEst_out_r, biasEst_out_r) = fitSine(tSamples, yMeasured_out_r, frequency_float)
    # magnitude and phase offset
    phasediff_l.append(phaseEst_out_l - phaseEst_in)
    amplitude_factor_l.append(amplitudeEst_out_l / amplitudeEst_in)
    phasediff_r.append(phaseEst_out_r - phaseEst_in)
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
print("amplitude_factor_l = ")
print(amplitude_factor_l)
print("phasediff_l = " )
print(phasediff_l)
print("amplitude_factor_r = " )
print(amplitude_factor_r)
print("phasediff_r = ")
print(phasediff_r)
indices = np.argsort(freq_vec)
amplitude_factor_l = 20 * np.log10(amplitude_factor_l)
amplitude_factor_r = 20 * np.log10(amplitude_factor_r)



left_bode, axarr_l = plt.subplots(2, sharex=True)
axarr_l[0].semilogx([freq_vec[x] for x in indices], [amplitude_factor_l[x] for x in indices], linewidth=5.0)
axarr_l[0].set_title('Bode diagram - left side (reduction 33:1)', fontsize=25)
axarr_l[1].semilogx([freq_vec[x] for x in indices], [phasediff_l[x] if phasediff_l[x] < 0 else phasediff_l[x] - 360 for x in indices], linewidth=5.0)
#axarr_l[1].semilogx([freq_vec[x] for x in indices], [phasediff_l[x]  for x in indices])
axarr_l[1].set_xlabel('Frequency [Hz]', fontsize=25)
axarr_l[0].set_ylabel('Magnitude [dB]', fontsize=25)
axarr_l[1].set_ylabel('Phase [deg]', fontsize=25)
axarr_l[0].tick_params(axis='x', labelsize=10)
axarr_l[1].tick_params(axis='x', labelsize=10)
axarr_l[0].tick_params(axis='y', labelsize=10)
axarr_l[1].tick_params(axis='y', labelsize=10)
axarr_l[0].grid()
axarr_l[1].grid()
figure_directory = 'figs/'
mng = plt.get_current_fig_manager()
mng.resize(*mng.window.maxsize())
plt.show()
left_bode.savefig(figure_directory + '/bode_left.jpg')

right_bode, axarr_r = plt.subplots(2, sharex=True)
axarr_r[0].semilogx([freq_vec[x] for x in indices], [amplitude_factor_r[x] for x in indices], linewidth=5.0)
axarr_r[0].set_title('Bode diagram - right side (reduction 112:1)', fontsize=25)
axarr_r[1].semilogx([freq_vec[x] for x in indices], [phasediff_r[x] if phasediff_r[x] < 0 else phasediff_r[x] - 360 for x in indices], linewidth=5.0)
#axarr_r[1].semilogx([freq_vec[x] for x in indices], [phasediff_r[x] for x in indices])
axarr_r[1].set_xlabel('Frequency [Hz]', fontsize=25)
axarr_r[0].set_ylabel('Magnitude [dB]', fontsize=25)
axarr_r[1].set_ylabel('Phase [deg]', fontsize=25)
axarr_r[0].tick_params(axis='x', labelsize=10)
axarr_r[1].tick_params(axis='x', labelsize=10)
axarr_r[0].tick_params(axis='y', labelsize=10)
axarr_r[1].tick_params(axis='y', labelsize=10)
axarr_r[0].grid()
axarr_r[1].grid()
figure_directory = 'figs/'
mng = plt.get_current_fig_manager()
mng.resize(*mng.window.maxsize())
plt.show()
right_bode.savefig(figure_directory + '/bode_right.jpg')

