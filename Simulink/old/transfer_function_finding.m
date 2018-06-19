clc
close all
clear all

% this is for calculating the transfer function of the palm stimulator
% setup

syms s DX_ref K_V2dist DX E K_P K_D K_I K_PID2Va V_a K_emf theta_m L_a R_a...
    K_tau F_coupled J_T k_eq b_sp L_CL n m_2 k_op

eqns = [DX_ref*K_V2dist + DX == E, (K_P + K_D*s + K_I/s)*E*K_PID2Va == V_a,...
    (V_a - K_emf*s*theta_m)/(L_a*s + R_a)*K_tau + F_coupled == J_T*s^2*theta_m,...
    F_coupled == (k_eq + b_sp*s)*DX*L_CL/n, J_T*s^2*theta_m == -J_T*s^2*n/L_CL*...
    ((k_eq + b_sp*s)/(m_2*s^2 + b_sp*s + k_op) + 1)*DX];

%sol = solve(eqns, F_coupled)
syms a b x c d f
eqns2 = [(a/f)^d==b*x+c]
solve(eqns2, a)