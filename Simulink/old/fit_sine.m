clear b t rows A w phase amplitude
b = dx.signals.values;
t = linspace(0,10,length(dx.signals.values));
A = [ [sin(freq*2*pi*t)]', [cos(freq*2*pi*t)]', (t*0 + 1)'];
w = A\b;
phase = atan2(w(2),w(1))*180/pi;
amplitude = norm(w(1:2));
bias = w(3);

b_ref = dx_ref.signals.values;
t_ref = linspace(0,10,length(dx_ref.signals.values));
A_ref = [ [sin(freq*2*pi*t_ref)]', [cos(freq*2*pi*t_ref)]', (t_ref*0 + 1)'];
w_ref = A_ref\b_ref;
phase_ref = atan2(w_ref(2),w_ref(1))*180/pi;
amplitude_ref = norm(w_ref(1:2));
bias_ref = w_ref(3);

amplitude_fac = amplitude / amplitude_ref
phase_lag = phase - phase_ref

% figure(1)
% plot(dx.signals.values)
% hold on
% plot(A*w, 'r')
% plot(dx_ref.signals.values*amplitude_fac, 'g')