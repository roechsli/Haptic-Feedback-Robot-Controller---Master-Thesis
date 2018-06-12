phase_vec = [];
amplitude_vec = [];
frequency_vec = [1, 1.25, 1.6, 2, 2.5, 3.17, 4, 5, 6.3, 8, 10, 12.6, 16, 20, 25, 32, 40, 50, 63, 80, 100];

for i= 1:length(frequency_vec)
    i
    freq = frequency_vec(i);
    sim('block_diagram.mdl')
    time_vec = linspace(0,10,length(dx.signals.values));
    [phase, amplitude, bias] = fit_sine_func(-dx.signals.values, time_vec, freq);
    [phase_ref, amplitude_ref, bias_ref] = fit_sine_func(dx_ref.signals.values, time_vec, freq);

    phase_vec = [phase_vec phase - phase_ref];
    amplitude_vec = [amplitude_vec amplitude/amplitude_ref];

end

%amplitude_vec
figure(1)
ax1 = subplot(2,1,1);
semilogx(frequency_vec, 20*log10(-amplitude_vec*5/dx_max), '.-')
title(ax1,'Magnitude Plot')
ylabel(ax1,'Magnitude [dB]')
grid on

ax2 = subplot(2,1,2);
semilogx(frequency_vec, phase_vec, '.-')
title(ax2,'Phase Plot')
ylabel(ax2,'Phase lag [deg]')
grid on
title('Bode Plot')
xlabel('Frequency [Hz]')




