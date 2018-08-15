clc
close all
clear all
% Simulation
freq = 1 % [Hz]

% Motor
R_a = 118.6 % [Ohm]
L_a = 5.8E-3 % [Henri]
K_tau = 31.4E-3 % [Nm/A]
K_emf = 3.29E-3 / 60 % [V/s]
n = 112 % [-] reduction ratio

% Mechanical
J_T = 1.25E-3 / n / n % [kg m^2] 
m_2 = 7E-3 % [kg]
L_CL = 20E-3 % [m]

% Springs
k_eq = 6E3 % [N/m]
b_spring = 300 % [Ns/m] damping coefficient of springs

% Operator // can be very high to simulate a wall or moderate for the real
% operator evnironment
k_op = 200 % [N/m] (stiffness of operators hand)
b_op = 20 % [Ns/m] (damping of operators hand)

% Arduino
MOTOR_MAX_V = 20 % [V]
dist_min = 2.2E-3 % [m]
dist_max = 4E-3 % [m]
dx_max = dist_min - dist_max % [m]
um_gain = -1000000 % [um/m]
K_V2dist = dx_max/5 % [m/V]
K_PID2Vardu = 1/51 % [V]
bit_offset = 128 % [-]

% Amplifier
K_ampl = 10 % [V/V]
V_offset = -25 % [V]
