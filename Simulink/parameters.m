clc
close all
clear all
%TODO:
%verify m_2, measure J_T
%amplifier
K_ampl = 10 % V/V
V_offset = -20 % V

%motor
R_a = 118.6 % Ohm
L_a = 5.8E-3 % Henri
K_tau = 31.4E-3 %Nm/A
K_emf = 3.29E-3 / 60 % V/s
n = 112 % reduction ratio

%mechanical
J_T = 1.25E-3 * n * n % kg m^2 %estimated to be 0.2 kg m^2
m_2 = 7E-3% kg
L_CL = 20E-3 % m
b_1 = 0 % Ns/m
b_2 = 0 % Ns/rad


%springs
k_eq = 6 % N/mm

% Arduino
K_Vto8bit = 51 % V^-1
dist_min = 2.2E-3 % m
dist_max = 4E-3 % m
dx_max = dist_min - dist_max % m // Delta x / dx_max * 255 gives 8bit from Delta x

MOTOR_MAX_V = 20
limit_val = 2 * MOTOR_MAX_V * K_Vto8bit / K_ampl
