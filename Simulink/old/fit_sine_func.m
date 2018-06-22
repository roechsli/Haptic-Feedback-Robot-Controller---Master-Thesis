function [phase, amplitude, bias] = fit_sine_func(x_val, time_vec, freq)
    b = x_val;
    t = time_vec;
    A = [ [sin(freq*2*pi*t)]', [cos(freq*2*pi*t)]', (t*0 + 1)'];
    w = A\b;
    phase = atan2(w(2),w(1))*180/pi;
    amplitude = norm(w(1:2));
    bias = w(3);
end