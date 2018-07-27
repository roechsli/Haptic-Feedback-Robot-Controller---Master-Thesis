import os
import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pickle
from scipy import signal

from pylab import *
from math import atan2

PLOT_BOOL = True
CALC_OPER_FREQ = False
SHORT_CUT = False
only_this_file = "f"  # change this to "f" if all frequencies shall be tested, otherwise "f2_csv"

INTMAX = 65535
"""
PHOTO_MIN_LEFT = 650
PHOTO_MAX_LEFT = 830
PHOTO_MIN_RIGHT = 700
PHOTO_MAX_RIGHT = 870
MAX_DISPLACEMENT_UM = 1800

PHOTO_MIN_LEFT = 640
PHOTO_MAX_LEFT = 840
PHOTO_MIN_RIGHT = 690
PHOTO_MAX_RIGHT = 880
MAX_DISPLACEMENT_UM = 1800

PHOTO_MIN_LEFT = 640
PHOTO_MAX_LEFT = 840
PHOTO_MIN_RIGHT = 700
PHOTO_MAX_RIGHT = 880
MAX_DISPLACEMENT_UM = 1800
directory = "20180704_fra_logs_PID_243_63_00126_1perc/"  # TODO change this if new data shall be analyzed


PHOTO_MIN_LEFT = 550
PHOTO_MAX_LEFT = 800
PHOTO_MIN_RIGHT = 700
PHOTO_MAX_RIGHT = 870
MAX_DISPLACEMENT_UM = 3000
directory = "20180719_fra_logs_pilot_P02/"  # TODO change this if new data shall be analyzed
"""
PHOTO_MIN_LEFT = 630
PHOTO_MAX_LEFT = 795
PHOTO_MIN_RIGHT = 550
PHOTO_MAX_RIGHT = 765
MAX_DISPLACEMENT_UM = 5
directory = "20180727_fra_logs_pilot_P10Vmm/"  # TODO change this if new data shall be analyzed
def get_freq_from_filename(filename):
    if filename[0] == "f" and filename[-8:] == "_csv.csv":
        return filename[1:-8]
    else:
        return ""

def sensor2dist(sensor_value, min_val, max_val):
  # maps the measured value to the distance (assumed linearity) in micrometers
  return (MAX_DISPLACEMENT_UM - (sensor_value - min_val) * MAX_DISPLACEMENT_UM / (max_val - min_val) )

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
        amplitude_factor_l = [0.6826234034854604, 0.702374068644084, 0.05610956954278812, 0.3579372634987285, 0.26866083287735826,
         0.19647660916392465, 0.647273557667352, 0.7424797291501742, 0.15264512730303045, 0.11829267140399782,
         0.7117423136609905, 0.0901260959293993, 0.7848023817050434, 0.06615899237338108, 0.7905173847409144,
         0.044896725338400285, 0.7590282516526557, 0.6311748818364169, 0.026049768482241147, 0.017103178371389995,
         0.4879827264237093]
        phasediff_l = [-40.10687754626554, -41.98509752016072, 152.4520139097022, 255.6319030383657, -114.85232848050612,
         -119.33613045636007, -39.078149644094864, -48.631722825286644, -125.30530032192252, 229.22824092038974,
         -44.777581888368445, 217.55446351786463, -53.22182715259622, 208.4141552514917, 297.92861841460507,
         -166.6962457862339, -71.23913013944895, -83.9110927646621, 171.66651258712463, 167.8372131209474,
         -95.63151954764379]
        amplitude_factor_r = [1.000217496008667, 1.0224667693424105, 0.14262450160374648, 0.5439481391284673, 0.39119884378164393,
         0.28047123242674943, 0.9530565602417771, 1.0894258166953414, 0.20496294743197854, 0.14956632734620307,
         1.044891618639843, 0.10853587895896519, 1.1512376656897343, 0.08565315014067588, 1.1669485083013422,
         0.06478991960980265, 1.1083119776877381, 0.9267128544601474, 0.05252185473693241, 0.04482807213226543,
         0.7245426097285498]
        phasediff_r = [-40.22745932910232, -42.80798510252933, 137.79294684175713, 253.88666919350538, -117.93014090329234,
         -121.63329538954531, -39.35752372223705, -49.28601025949844, -126.85033117262097, 226.5150457468216,
         -45.27174647943687, 219.08656716857047, -53.62205292081548, 214.34742948046522, 296.93419365531673,
         -171.53790001253358, -72.39259793369217, -85.77067297709058, 200.7164467428948, 206.21724432342802,
         -97.60000229355124]

        freq_vec = [1.25, 1.6, 100.0, 10.0, 13.0, 16.0, 1.0, 2.5, 20.0, 25.0, 2.0, 32.0, 3.0, 40.0, 4.0, 50.0, 5.0, 6.3, 63.0,
         80.0, 8.0]
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

    print(df.iloc[:,1])
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
        # plot left and right sensor data,zoom and save
        plt.plot(df.iloc[:, 3], df.iloc[:, 1])
        #plt.plot(df.iloc[:, 3], df.iloc[:, 2])
        plt.plot(df.iloc[:, 3], df.iloc[:, 0] )  # plot reference
        fig.suptitle('Frequency response (' + frequency + ' Hz)')
        plt.xlabel('Time [s]')
        plt.ylabel('Compression [mm]')
        #plt.axis([2, 3.6, -0.05, 0.5])
        plt.axis([2, 3.6, 1.0, 4])
        #plt.legend(["left sensor", "right sensor", "reference signal"])
        plt.legend(["left sensor", "reference signal"])
        figure_directory = 'figs/f' + frequency
        if not os.path.exists(figure_directory):
            os.makedirs(figure_directory)
        fig.savefig(figure_directory + '/' + frequency + 'plot_zoom_fixed_time.jpg')
        #plt.axis([2, 2 + 3 / frequency_float, -0.05, 0.7])
        plt.axis([2, 2 + 3 / frequency_float, 1.0, 4])
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
print("freq_vec = ")
print(freq_vec)
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
left_lines = axarr_l[0].semilogx([freq_vec[x] for x in indices], [amplitude_factor_l[x] for x in indices], linewidth=5.0, label='Left side')
axarr_l[0].set_title('Bode diagram - left side (reduction 33:1)', fontsize=25)
"""
right_lines = axarr_l[0].semilogx([freq_vec[x] for x in indices], [amplitude_factor_r[x] for x in indices], linewidth=5.0, label='Right side')
axarr_l[0].legend()
axarr_l[1].semilogx([freq_vec[x] for x in indices], [phasediff_r[x] if phasediff_r[x] < 0 else phasediff_r[x] - 360 for x in indices], linewidth=5.0, label='Right side')
axarr_l[0].set_title('Bode diagram (reduction 112:1)', fontsize=25)
#"""
axarr_l[1].semilogx([freq_vec[x] for x in indices], [phasediff_l[x] if phasediff_l[x] < 0 else phasediff_l[x] - 360 for x in indices], linewidth=5.0, label='Left side')
#axarr_l[1].semilogx([freq_vec[x] for x in indices], [phasediff_l[x]  for x in indices])
axarr_l[1].set_xlabel('Frequency [Hz]', fontsize=25)
axarr_l[0].set_ylabel('Magnitude [dB]', fontsize=25)
axarr_l[1].set_ylabel('Phase [deg]', fontsize=25)
axarr_l[0].tick_params(axis='x', labelsize=10)
axarr_l[1].tick_params(axis='x', labelsize=10)
axarr_l[0].tick_params(axis='y', labelsize=10)
axarr_l[1].tick_params(axis='y', labelsize=10)
axarr_l[0].set_ylim(-50,10)
axarr_l[1].set_ylim(-250,0)
axarr_l[0].grid()
axarr_l[1].grid()
figure_directory = 'figs/'
mng = plt.get_current_fig_manager()
mng.resize(*mng.window.maxsize())
plt.show()
left_bode.savefig(figure_directory + '/bode_left.jpg')

right_bode, axarr_r = plt.subplots(2, sharex=True)
axarr_r[0].semilogx([freq_vec[x] for x in indices], [amplitude_factor_r[x] for x in indices], linewidth=5.0)
axarr_r[0].set_title('Bode diagram - right side (reduction 33:1)', fontsize=25)
axarr_r[1].semilogx([freq_vec[x] for x in indices], [phasediff_r[x] if phasediff_r[x] < 0 else phasediff_r[x] - 360 for x in indices], linewidth=5.0)
#axarr_r[1].semilogx([freq_vec[x] for x in indices], [phasediff_r[x] for x in indices])
axarr_r[1].set_xlabel('Frequency [Hz]', fontsize=25)
axarr_r[0].set_ylabel('Magnitude [dB]', fontsize=25)
axarr_r[1].set_ylabel('Phase [deg]', fontsize=25)
axarr_r[0].tick_params(axis='x', labelsize=10)
axarr_r[1].tick_params(axis='x', labelsize=10)
axarr_r[0].tick_params(axis='y', labelsize=10)
axarr_r[1].tick_params(axis='y', labelsize=10)
axarr_r[0].set_ylim(-50,10)
axarr_r[1].set_ylim(-250,0)
axarr_r[0].grid()
axarr_r[1].grid()
figure_directory = 'figs/'
mng = plt.get_current_fig_manager()
mng.resize(*mng.window.maxsize())
plt.show()
right_bode.savefig(figure_directory + '/bode_right.jpg')

"""
#======================= trial with bode plot
#sys = signal.TransferFunction([9.6e10, -2.8e11, 2.7e11, -8.6e10, 0, 0, 0, 0, 0, 0, 0], [1.9e10, -6.3e11, 7.7e11, -4.1e11, 8.3e10, -3.2e5, 0, 0, 0, 0, 0], dt=0.001)
sys = signal.TransferFunction([9.6e10, -2.8e11, 2.7e11, -8.6e10, 0, 0], [1.9e10, -6.3e11, 7.7e11, -4.1e11, 8.3e10, -3.2e5], dt=0.001)
w, mag, phase = sys.bode()
comp_bode, axarr_comp = plt.subplots(2, sharex=True)
axarr_comp[0].semilogx([freq_vec[x] for x in indices], [amplitude_factor_r[x] for x in indices], linewidth=5.0)
axarr_comp[0].semilogx(w, mag)    # Bode magnitude plot
axarr_comp[0].set_title('Bode diagram - comparison', fontsize=25)
axarr_comp[1].semilogx([freq_vec[x] for x in indices], [phasediff_r[x] if phasediff_r[x] < 0 else phasediff_r[x] - 360 for x in indices], linewidth=5.0)
#axarr_r[1].semilogx([freq_vec[x] for x in indices], [phasediff_r[x] for x in indices])
axarr_comp[1].set_xlabel('Frequency [Hz]', fontsize=25)
axarr_comp[0].set_ylabel('Magnitude [dB]', fontsize=25)
axarr_comp[1].set_ylabel('Phase [deg]', fontsize=25)
axarr_comp[0].tick_params(axis='x', labelsize=10)
axarr_comp[1].tick_params(axis='x', labelsize=10)
axarr_comp[0].tick_params(axis='y', labelsize=10)
axarr_comp[1].tick_params(axis='y', labelsize=10)
#axarr_comp[0].set_ylim(-25,10)
#axarr_comp[1].set_ylim(-200,0)
axarr_comp[0].grid()
axarr_comp[1].grid()
figure_directory = 'figs/'
mng = plt.get_current_fig_manager()
mng.resize(*mng.window.maxsize())
plt.show()
comp_bode.savefig(figure_directory + '/bode_comp.jpg')
"""