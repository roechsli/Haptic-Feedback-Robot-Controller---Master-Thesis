clc
close all
clear all
%TODO:
%verify m_2, measure friction coefficients (springs, motor)
% Simulation
freq = 1 % [Hz]

% Motor
R_a = 118.6 % [Ohm]
L_a = 5.8E-3 % [Henri]
K_tau = 31.4E-3 % [Nm/A]
K_emf = 3.29E-3 / 60 % [V/s]
n = 112 % [-] reduction ratio

% Mechanical
assumed_max_displ = 3E-3 % [m] // is what is expected to be the biggest 
% compression (this is dynamic, not static) --> still dx_max?
J_T = 1.25E-3 / n / n % [kg m^2] %estimated to be 0.2 kg m^2
m_2 = 7E-3% [kg]
L_CL = 20E-3 % [m]
b_1 = 0 % [Ns/m] // since it is too difficult to keep it apart from 
% b_spring, it can be neglected and both are incorporated in the same variable

% Springs
k_eq = 6E3 % [N/m]
b_spring = 100 % [Ns/m] damping coefficient of springs, should be measured 
% of found in simulation

% Operator // can be very high to simulate a wall or moderate for the real
% operator evnironment
k_op = 1E10%200 % [N/m] (stiffness of operators hand)
b_op = 1E9%20 % [Ns/m] (damping of operators hand)

% Arduino
MOTOR_MAX_V = 20 % [V]
dist_min = 2.2E-3 % [m]
dist_max = 4E-3 % [m]
dx_max = dist_min - dist_max % [m] // Delta x / dx_max * 255 gives 8bit 
% from Delta x
K_V2dist = dx_max/5 % [m/V]
K_PID2Va = -MOTOR_MAX_V/assumed_max_displ % [V] // pid value to voltage 
% conversion (results in final desired armature voltage)

%limit_val = 2 * MOTOR_MAX_V * K_Vto8bit / K_ampl % [-]

% Amplifier
K_ampl = 10 % [V/V]
V_offset = -MOTOR_MAX_V % [V]
