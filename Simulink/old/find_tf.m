
clc
close all
clear all
%syms s 
%syms b_sp
b_sp = 100
b_op = 1000000000
k_op = 1000000000
K_V2dist = -1%(4-2.2)*10^(-3)/5
K_P = 1.0
K_D = 0
K_I = 0
K_PID2Va = 20/(3E-3) % -MOTOR_MAX_V/assumed_max_displ
n = 112
J_T =  1.25E-3 / n / n
L_CL = 20E-3
k_eq = 6
m_2 = 7E-3
L_a = 5.8E-3
R_a  = 118.6
K_tau = 31.4E-3 % [Nm/A]
K_emf = 3.29E-3 / 60 % [V/s]
%simplify(K_V2dist * (K_P + K_D * s + K_I/s) * K_PID2Va / (-J_T * s^2 * n/L_CL *( 1 + (k_eq+b_sp*s)/(m_2*s^2 +b_op*s + k_op))* (L_a*s + R_a) /K_tau - K_emf * s * J_T*s^2*n/L_CL*( 1 + (k_eq+b_sp*s)/(m_2*s^2 +b_op*s + k_op)) - (k_eq + b_sp*s)*L_CL* (L_a*s + R_a) /K_tau / n - (K_P + K_D * s + K_I/s) * K_PID2Va))
s = tf('s');
%old_formula my_transfer = tf(K_V2dist * (K_P + K_D * s + K_I/s) * K_PID2Va / (-J_T * s^2 * n/L_CL *( 1 + (k_eq+b_sp*s)/(m_2*s^2 +b_op*s + k_op))* (L_a*s + R_a) /K_tau - K_emf * s * J_T*s^2*n/L_CL*( 1 + (k_eq+b_sp*s)/(m_2*s^2 +b_op*s + k_op)) - (k_eq + b_sp*s)*L_CL* (L_a*s + R_a) /K_tau / n - (K_P + K_D * s + K_I/s) * K_PID2Va))
% normal operator:
my_transfer = tf((K_P + K_D*s + K_I/s)*K_PID2Va/(L_a*s + R_a)*K_tau/(-J_T*s^2*n/L_CL*(1+(k_eq + b_sp*s)/(m_2*s^2 + b_op*s + k_op)) -(k_eq + b_sp*s)*L_CL/n - (K_P + K_D*s + K_I/s)/(L_a*s + R_a)*K_tau*K_PID2Va - K_emf/(L_a*s + R_a)*K_tau*s*n/L_CL *(1 + (k_eq + b_sp*s)/(m_2*s^2 + b_op*s + k_op))))

% blocked by wall:
my_transfer = tf(-(K_P + K_D*s + K_I/s)*K_PID2Va/(L_a*s + R_a)*K_tau/(J_T*s^2*n_LCL*DX +(k_eq + b_sp*s)*L_CL/n + (K_P + K_D*s + K_I/s)*K_PID2Va/(L_a*s + R_a)*K_tau + K_emf*s/(L_a*s + R_a)*K_tau*n_LCL) )
bode(my_transfer)


%%%%% Revised version: E = DX_ref - DX
%not blocked
(K_P + K_D*s + K_I /s)*K_PIDV2a/(L_a*s + R_a)*K_tau/(-J_T *s^2*n/L_CL*(1+(k_eq + b_sp*s)/(m_2*s^2 + b_op*s+ k_op)) + (K_P + K_D*s + K_I /s)*K_PID2Va/(L_a*s + R_a)*K_tau - K_emf*s/(L_a*s + R_a)*K_tau*n/L_CL - (k_eq + b_sp*s)*L_CL/n)  = DX/DX_ref

%blocked
(K_P + K_D*s + K_I /s)*K_PIDV2a/(L_a*s + R_a)*K_tau/(-J_T *s^2*n/L_CL + (K_P + K_D*s + K_I /s)*K_PID2Va/(L_a*s + R_a)*K_tau - K_emf*s/(L_a*s + R_a)*K_tau*n/L_CL - (k_eq + b_sp*s)*L_CL/n)  = DX/DX_ref




