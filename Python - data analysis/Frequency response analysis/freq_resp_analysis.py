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
"""
PHOTO_MIN_LEFT = 640
PHOTO_MAX_LEFT = 840
PHOTO_MIN_RIGHT = 700
PHOTO_MAX_RIGHT = 880
MAX_DISPLACEMENT_UM = 1800
directory = "20180809_fra_logs_P02I093/"  # TODO change this if new data shall be analyzed

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
        amplitude_factor_l = [0.7601896652627596, 0.744343848109167, 0.007951997355989955, 0.8550712064038017,
                              0.9661471221820586, 1.1336734397483565, 0.7750527091865916, 0.7045265998811632,
                              1.5910843452341281, 2.232869271026134, 0.7238940008521587, 1.1701038845395058,
                              0.6933593325946599, 0.45486120775583777, 0.6934159970289575, 0.17023098271826864,
                              0.7028216272421962, 0.719649955213483, 0.07137902432654318, 0.02015130350108083,
                              0.7692242649389266]
        phasediff_l = [-31.70998717394236, -30.997229961071668, 178.71648406608347, -38.9593250415772,
                       -40.71144281092042, -44.773124817912084, -33.68977306592595, -28.780400415112638,
                       -56.23587584823737, -105.48693487751852, -30.092770250653615, 200.42078921821667,
                       -28.243049588774838, 178.61588021261676, -26.85340089109842, -209.41666148132595,
                       -26.5848015560761, -26.700004175701906, 143.85613219256902, -214.36946988114835,
                       -27.907238612122665]
        amplitude_factor_r = [0.5689989395716576, 0.5617325101772804, 0.007776265258003794, 0.8029992123311501,
                              0.9464257370896573, 1.1526341426969926, 0.5785204419285449, 0.5532277313962409,
                              1.3447645633183067, 0.8824941058460577, 0.5614300301366614, 0.3641910481977869,
                              0.559547748476853, 0.15015302509012513, 0.5775600081766765, 0.06253738840283483,
                              0.6203363631335826, 0.7162023153846844, 0.030795999786399905, 0.01799758810505321,
                              0.8649445483391283]
        phasediff_r = [-37.92212835769355, -35.92458858071234, 170.56374297883235, -53.33463407055997,
                       -58.99421538328227, -69.60421091852015, -39.68418166137866, -33.94187467637505,
                       -98.4018128491575, -137.08806777246366, -35.02207449587998, 200.3900476873477,
                       -32.65067485764229, 191.89839514220412, -31.894944065586596, -170.6386923024231,
                       -32.63408572631705, -34.7105469868994, -175.79833248234146, -191.51265666131337,
                       -38.095308266568296]

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
        #plt.axis([2, 3.6, -0.05, 0.5])
        plt.axis([2, 3.6, 0.2, 0.7])
        plt.legend(["left sensor", "right sensor", "reference signal"])
        figure_directory = 'figs/f' + frequency
        if not os.path.exists(figure_directory):
            os.makedirs(figure_directory)
        fig.savefig(figure_directory + '/' + frequency + 'plot_zoom_fixed_time.jpg')
        #plt.axis([2, 2 + 3 / frequency_float, -0.05, 0.7])
        plt.axis([2, 2 + 3 / frequency_float, 0.2, 0.7])
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
left_lines = axarr_l[0].semilogx([freq_vec[x] for x in indices], [amplitude_factor_l[x] for x in indices], 'o-', linewidth=5.0, label='Left side')
axarr_l[0].set_title('Bode diagram - left side (reduction 112:1)', fontsize=25)
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
axarr_r[0].set_title('Bode diagram - right side (reduction 112:1)', fontsize=25)
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