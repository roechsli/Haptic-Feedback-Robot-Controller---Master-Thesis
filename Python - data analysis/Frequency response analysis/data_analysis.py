#!/usr/bin/env python
import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from pylab import *
from math import atan2


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
    return (phase, amplitude, bias)



df = pd.read_csv("test.csv", delimiter=';')
df.describe()
sLength = len(df['1'])
timestep = 1/500
ylabel=['Input Voltage [V]','Measured distance []','Measured distance []','Output Voltage [V]','Output Voltage [V]']
multiplier=[-5/255,1,1,20/255,20/255]
titles = ['Feedback','Left Sensor','Right Sensor','Left Motor','Right Motor']
tSamples = np.arange(0,sLength/5*timestep,timestep)

new_index = titles*int(np.floor(sLength/5))
df.reindex(new_index)

phasediff_r = []
amplitude_factor_r = []
phasediff_l = []
amplitude_factor_l = []

for frequency in df:
#frequency = '10'
#if (True):
    print(frequency)
    for i in range(5):
        fig = plt.figure()
        plt.plot(np.arange(0,sLength/5*timestep,timestep),multiplier[i]*df.loc[range(0+i,sLength+i,5),frequency])
        fig.suptitle(titles[i] + ', Frequency of '+frequency+' Hz')
        plt.xlabel('Time [s]')
        plt.ylabel(ylabel[i])
        fig.savefig('figs/f'+frequency+'/plot_'+titles[i]+'.jpg')
        plt.close(fig)

    # do frequency analysis
    freq_float = float(frequency)
    #input
    yMeasured_in = multiplier[0]*df.loc[range(0,sLength,5),frequency] # shift of zero to have the feedback
    (phaseEst_in, amplitudeEst_in, biasEst_in) = fitSine(tSamples, yMeasured_in, freq_float)

    #output left
    yMeasured_out_l = multiplier[3] * df.loc[range(0 + 3, sLength + 3, 5), frequency] # shift of four to have the right side
    (phaseEst_out_l, amplitudeEst_out_l, biasEst_out_l) = fitSine(tSamples, yMeasured_out_l, freq_float)

    #output right
    yMeasured_out_r = multiplier[4] * df.loc[range(0 + 4, sLength + 4, 5), frequency] # shift of four to have the right side
    (phaseEst_out_r, amplitudeEst_out_r, biasEst_out_r) = fitSine(tSamples, yMeasured_out_r, freq_float)
    """
    phasediff_l = [phasediff_l, (phaseEst_in-phaseEst_out_l)]
    amplitude_factor_l = [amplitude_factor_l, (amplitudeEst_out_l/amplitudeEst_in)]
    phasediff_r = [phasediff_r, (phaseEst_in-phaseEst_out_r)]
    amplitude_factor_r = [amplitude_factor_r, (amplitudeEst_out_r/amplitudeEst_in)]
    """
    phasediff_l.append(phaseEst_in-phaseEst_out_l)
    amplitude_factor_l.append(amplitudeEst_out_l/amplitudeEst_in)
    phasediff_r.append(phaseEst_in-phaseEst_out_r)
    amplitude_factor_r.append(amplitudeEst_out_r/amplitudeEst_in)


plot(amplitude_factor_r)
plot(amplitude_factor_l)

print(amplitude_factor_r)
print(amplitude_factor_l)
plt.show()

""""
freq_int = int(frequency)
tSamples = np.arange(0,sLength/5*timestep,timestep)
yMeasured_out = multiplier[4]*df.loc[range(0+4,sLength+4,5),frequency]
(phaseEst_out, amplitudeEst_out, biasEst_out) = fitSine(tSamples, yMeasured_out, freq_int)
yEst_out = amplitudeEst_out * sin(tSamples * freq_int * 2 * pi + phaseEst_out * pi / 180.0) + biasEst_out
yMeasured_in = multiplier[0]*df.loc[range(0,sLength,5),frequency]
(phaseEst_in, amplitudeEst_in, biasEst_in) = fitSine(tSamples, yMeasured_in, freq_int)
yEst_in = amplitudeEst_in * sin(tSamples * freq_int * 2 * pi + phaseEst_in * pi / 180.0) + biasEst_in
figure(1)
plot(tSamples, yMeasured_out, 'b')
plot(tSamples, yEst_out, '-g')
plot(tSamples, yMeasured_in, 'r')
plot(tSamples, yEst_in, '-c')
xlabel('seconds')

print(phaseEst_out)
print(amplitudeEst_out)
print(biasEst_out)
print(phaseEst_in)
print(amplitudeEst_in)
print(biasEst_in)
print("phasediff ", (phaseEst_in-phaseEst_out))
print("amplitude factor ", (amplitudeEst_out/amplitudeEst_in))
show()
"""
