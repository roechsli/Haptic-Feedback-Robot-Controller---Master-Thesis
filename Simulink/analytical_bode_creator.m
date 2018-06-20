spring_damping_vec = [0 10 100 215 460 1000];

%K_V2dist = -1%(4-2.2)*10^(-3)/5
K_P = 1.0
K_D = 0
K_I = 0
K_PID2Va = -20/(3E-3) % -MOTOR_MAX_V/assumed_max_displ
n = 112
J_T =  1.25E-3 / n / n
L_CL = 20E-3
k_eq = 6
m_2 = 7E-3
L_a = 5.8E-3
R_a  = 118.6
K_tau = 31.4E-3 % [Nm/A]
K_emf = 3.29E-3 / 60 % [V/s]

for k = 1:length(spring_damping_vec)
    b_sp = spring_damping_vec(k)
    
    s = tf('s');
    % operator:
    %my_transfer = tf((K_P + K_D*s + K_I /s)*K_PIDV2a/(L_a*s + R_a)*K_tau/(-J_T *s^2*n/L_CL*(1+(k_eq + b_sp*s)/(m_2*s^2 + b_op*s+ k_op)) + (K_P + K_D*s + K_I /s)*K_PID2Va/(L_a*s + R_a)*K_tau - K_emf*s/(L_a*s + R_a)*K_tau*n/L_CL - (k_eq + b_sp*s)*L_CL/n))      
    % blocked by walls
    my_transfer = tf((K_P + K_D*s + K_I /s)*K_PID2Va/(L_a*s + R_a)*K_tau/(-J_T *s^2*n/L_CL + (K_P + K_D*s + K_I /s)*K_PID2Va/(L_a*s + R_a)*K_tau - K_emf*s/(L_a*s + R_a)*K_tau*n/L_CL - (k_eq + b_sp*s)*L_CL/n))
    %Plot figure and save
    fig = figure('units','normalized','outerposition',[0 0 1 1]);%,'DefaultAxesFontSize',36
    PlotHandle= bodeplot(my_transfer);
    set(findall(fig, 'type','axes'),'fontsize',16)
    PlotOptions= getoptions(PlotHandle);
    PlotOptions.Title.String= '';
    PlotOptions.XLabel.FontSize= 20;
    PlotOptions.YLabel.FontSize= 20;
    PlotHandle.setoptions(PlotOptions)
    
    set(findall(gcf,'Type','line'),'LineWidth',4)
    xlim([1 120])
    grid on

    filename = ['figures/bode_sp_damp' num2str(spring_damping_vec(k))];
    saveas(gcf, [filename  '.png'])
    dot_pos = strfind(filename,'.');
    if (dot_pos)
        saveas(gcf, [filename(1:dot_pos-1) filename(dot_pos+1:end)  '.m'])
    else
        saveas(gcf, [filename  '.m'])
    end
    close(fig)
end



%old transfer function = tf((K_P + K_D*s +
%K_I/s)*K_PID2Va/(L_a*s + R_a)*K_tau/(J_T*s^2*n/L_CL +(k_eq +
%b_sp*s)*L_CL/n + (K_P + K_D*s + K_I/s)*K_PID2Va/(L_a*s + R_a)*K_tau + K_emf*s/(L_a*s + R_a)*K_tau*n/L_CL) )