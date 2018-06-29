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
"""
PHOTO_MIN_LEFT = 640
PHOTO_MAX_LEFT = 840
PHOTO_MIN_RIGHT = 690
PHOTO_MAX_RIGHT = 880
MAX_DISPLACEMENT_UM = 1800
directory = "20180629_fra_logs_p_02/"  # TODO change this if new data shall be analyzed

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
        amplitude_factor_l = [1.0052839216458749, 0.9991405271561531, 0.14759776628322555, 1.0465191593492096, 1.0880642215979706,
         1.1522190802910368, 1.0046439550041986, 0.9932151356657599, 1.2600947273486607, 1.2842520641164805,
         1.0020329809714894, 1.0014693485131245, 1.0150402929231659, 0.7383722966339016, 1.0079895873881333,
         0.4908444452676763, 0.9951146354026693, 1.0162473027018177, 0.3248091089212081, 0.21395810442150892,
         1.0190435893115852]
        phasediff_l = [-2.075830318502497, -2.8844488303323885, 169.60207402532274, -12.596392094963633, -16.551435436977613,
         -22.312023532948942, -2.142449369453317, -4.4456858870760385, -32.42034397864422, -58.04021679762169,
         -3.8675024925421297, -4.9991477731368335, -88.79867703452486, 247.1661435303339, -6.019898453018541,
         -139.14671090346013, -7.620669651037105, -8.855829105472651, 207.42648196699372, 189.67814591921086,
         -11.574912105096871]
        amplitude_factor_r = [1.01528252648064, 1.0061854783791677, 0.06653250415394932, 1.0902513430697414, 1.14045066153976,
         1.2004736909239189, 1.0181444949090879, 1.0103853848652116, 1.162145265952185, 0.8688050902240192,
         1.0054167780929026, 1.0006278159816782, 0.5739997987858684, 0.39934203430159093, 0.9952954766920439,
         0.2651356660318484, 1.0089711572251487, 1.014906857520811, 0.1662665532311567, 0.10588404052157428,
         1.0486193030968416]
        phasediff_r = [-3.9462055759644983, -4.794697605862581, 170.31264264153552, -20.92739519520042, -28.56990446690955,
         -42.04673253830194, -2.981093827020544, -6.916031863159901, -63.98332976383682, -93.45599243577922,
         -5.522214079974674, -8.009198022882693, -115.88709982628073, 228.4711130111851, -9.51822676960225,
         -144.62395382557736, -11.736703802647355, -14.388214287698673, 199.8738652541653, 186.94808894493073,
         -17.185092593521006]
        #freq_vec = 	   [1.25, 1.6, 1, 10, 100, 13, 16, 2.5, 2, 20, 25, 3, 32, 4, 40, 5, 50, 6.3, 63, 8, 80]
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
        # plot left and right sensor data,zoom and save
        plt.plot(df.iloc[:, 3], df.iloc[:, 1])
        plt.plot(df.iloc[:, 3], df.iloc[:, 2])
        plt.plot(df.iloc[:, 3], df.iloc[:, 0] )  # plot reference
        fig.suptitle('Frequency response (' + frequency + ' Hz)')
        plt.xlabel('Time [s]')
        plt.ylabel('Compression [mm]')
        plt.axis([2, 3.6, -0.05, 0.5])
        plt.legend(["left sensor", "right sensor", "reference signal"])
        figure_directory = 'figs/f' + frequency
        if not os.path.exists(figure_directory):
            os.makedirs(figure_directory)
        fig.savefig(figure_directory + '/' + frequency + 'plot_zoom_fixed_time.jpg')
        plt.axis([2, 2 + 3 / frequency_float, -0.05, 0.7])
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
axarr_l[0].set_title('Bode diagram - left side (reduction 112:1)', fontsize=25)
"""
right_lines = axarr_l[0].semilogx([freq_vec[x] for x in indices], [amplitude_factor_r[x] for x in indices], linewidth=5.0, label='Right side')
axarr_l[0].legend()
axarr_l[1].semilogx([freq_vec[x] for x in indices], [phasediff_r[x] if phasediff_r[x] < 0 else phasediff_r[x] - 360 for x in indices], linewidth=5.0, label='Right side')
axarr_l[0].set_title('Bode diagram (reduction 112:1)', fontsize=25)
"""
axarr_l[1].semilogx([freq_vec[x] for x in indices], [phasediff_l[x] if phasediff_l[x] < 0 else phasediff_l[x] - 360 for x in indices], linewidth=5.0, label='Left side')
#axarr_l[1].semilogx([freq_vec[x] for x in indices], [phasediff_l[x]  for x in indices])
axarr_l[1].set_xlabel('Frequency [Hz]', fontsize=25)
axarr_l[0].set_ylabel('Magnitude [dB]', fontsize=25)
axarr_l[1].set_ylabel('Phase [deg]', fontsize=25)
axarr_l[0].tick_params(axis='x', labelsize=10)
axarr_l[1].tick_params(axis='x', labelsize=10)
axarr_l[0].tick_params(axis='y', labelsize=10)
axarr_l[1].tick_params(axis='y', labelsize=10)
axarr_l[0].set_ylim(-25,10)
axarr_l[1].set_ylim(-200,0)
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
axarr_l[0].set_ylim(-25,10)
axarr_l[1].set_ylim(-200,0)
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