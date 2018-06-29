%calculate J_TOT
n = 112
m_CL = 18.5E-3 % kg
A = 10E-3 % m
B = 6E-3 % m
L_CL = 20E-3 % m
m_base = 7E-3 % kg
m_BL = 2E-3 % kg
m_guideway = 5E-3 % kg
m_shaft = 2E-3 % kg
m_carr = m_base + m_BL + m_guideway + m_shaft % kg

J_motor = 6.8E-8 % kg*m^2
J_CL = m_CL/12 * (A^2 + B^2 + 12*(L_CL/2)^2) % kg*m^2
J_carr = m_carr*L_CL^2 % kg*m^2

J_TOT_motor = J_motor + J_CL/n^2 + J_carr/n^2 % kg*m^2
%J_TOT_refl = J_TOT_load / n^2