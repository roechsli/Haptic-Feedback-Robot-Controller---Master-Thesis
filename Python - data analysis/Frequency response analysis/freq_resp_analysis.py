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
SHORT_CUT = True  # change this, if you want to skip all the calculation
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
    # from: http://exnumerus.blogspot.jp/2010/04/how-to-fit-sine-wave-example-in-python.html
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
    if SHORT_CUT:
        freq_vec = [1.25, 1.6, 100, 10, 12.6, 16, 1, 2.5, 20, 25, 2, 3.17, 32, 40, 4, 50, 5, 6.3, 63, 80, 8]
        amplitude_factor_l = [0.6994285255386264, 0.7060693178843412, 0.1642580358036316, 0.7504272083193917,
                              0.5608147625160623, 0.4350563936262765, 0.6865373796317358, 0.750613957790355,
                              0.28764124380912426, 0.18157383994468917, 0.719141440214737, 0.11841728824778987,
                              0.7841511950211536, 0.08356286691382651, 0.8395411308613303, 0.05160910392066559,
                              0.8761974243234357, 0.8727214341574415, 0.03602633336518485, 0.02369799489660005,
                              0.8238155452976973]
        phasediff_l = [-26.74399667740589, -28.252082139057677, -139.02668442120668, -87.62296455097207,
                       -111.60332053386406, -122.30681291255031, -26.264449481141625, -33.65993410529991,
                       -136.88907219509647, 211.81932574839442, -30.129518435338937, 204.82749776212066,
                       -36.105113701961486, -165.420081452403, -42.83497528042071, 185.87493727039276,
                       -49.77014973321731, -59.48404583982298, -183.0169730842087, 153.6436519113613,
                       -71.90212621011054]
        amplitude_factor_r = [0.002698423806236808, 0.0016442425085835218, 0.042726917043537455, 0.0026442860711027526,
                              0.002109693116543353, 0.000714095040074596, 0.0004954684393076871, 0.002028191543406408,
                              0.003573655272637005, 0.0018125102659706518, 0.0009111882556132023, 0.002321354015034593,
                              0.0009606503908176091, 0.004116386983303665, 0.0006861257226317704, 0.0014236278486540602,
                              0.0022596612864099665, 0.002388333213123135, 0.0012674189965787093, 0.00684975069637002,
                              0.002997922097144885]
        phasediff_r = [54.935068271591334, -104.98856855317769, 18.805709126367418, 9.826501678416832,
                       -27.094197321617585, 44.4046272047869, -218.03744278412796, 4.153093327601631,
                       0.31130603544275814, 314.33969792406447, -315.4842229244386, -28.52875809938429,
                       54.380397810163274, -9.591765076043131, -91.2826756161442, 99.50085940965394, 23.369819555133233,
                       -317.90093511647376, -244.66332388913816, 150.72386693909115, 22.13060360284489]

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
left_lines = axarr_l[0].semilogx([freq_vec[x] for x in indices], [amplitude_factor_l[x] for x in indices], 'o-', linewidth=5.0, label='Left side')
axarr_l[0].set_title('Bode diagram - left side (reduction 33:1)', fontsize=25)
"""
right_lines = axarr_l[0].semilogx([freq_vec[x] for x in indices], [amplitude_factor_r[x] for x in indices], 'o-', linewidth=5.0, label='Right side')
axarr_l[0].legend()
axarr_l[1].semilogx([freq_vec[x] for x in indices], [phasediff_r[x] if phasediff_r[x] < 0 else phasediff_r[x] - 360 for x in indices], 'o-', linewidth=5.0, label='Right side')
axarr_l[0].set_title('Bode diagram (reduction 112:1)', fontsize=25)
#"""
axarr_l[1].semilogx([freq_vec[x] for x in indices], [phasediff_l[x] if phasediff_l[x] < 0 else phasediff_l[x] - 360 for x in indices], 'o-', linewidth=5.0, label='Left side')
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
axarr_r[0].semilogx([freq_vec[x] for x in indices], [amplitude_factor_r[x] for x in indices], 'o-', linewidth=5.0)
axarr_r[0].set_title('Bode diagram - right side (reduction 33:1)', fontsize=25)
axarr_r[1].semilogx([freq_vec[x] for x in indices], [phasediff_r[x] if phasediff_r[x] < 0 else phasediff_r[x] - 360 for x in indices], 'o-', linewidth=5.0)
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