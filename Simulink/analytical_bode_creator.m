spring_damping_vec = [200 300 400 500 600 700 800];
BOOL_SEVERAL_PLOTS = 0;

%k_op = 200
%b_op = 20
K_P = 0.2
K_D = 0
K_I = 0
K_PID2Vardu = 1/51 % [V]
um_gain = -1000000 % [um/m]
K_ampl = 10
V_offset = -25
bit_offset = 128
n = 112
J_T =  1.25E-3 / n / n
L_CL = 20E-3
k_eq = 6
m_2 = 7E-3
L_a = 5.8E-3
R_a  = 118.6
K_tau = 31.4E-3 % [Nm/A]
K_emf = 3.29E-3 / 60 % [V/s]
s = tf('s');


if BOOL_SEVERAL_PLOTS
    for k = 1:length(spring_damping_vec)
        b_sp = spring_damping_vec(k)

        s = tf('s');
        % operator:
        % blocked by walls
        my_transfer = tf(um_gain*(K_P + K_D*s +K_I/s)*K_PID2Vardu*K_ampl*K_tau/(-J_T*s^2*n/L_CL*(L_a*s+R_a) - (k_eq + b_sp*s)*L_CL/n*(L_a*s+R_a) - K_emf*s*n/L_CL*K_tau  + um_gain*(K_P + K_D*s +K_I/s)*K_PID2Vardu*K_ampl*K_tau))
        %Plot figure and save
        fig = figure('units','normalized','outerposition',[0 0 1 1]);%,'DefaultAxesFontSize',36
        PlotHandle= bodeplot(my_transfer);
        %title(['Spring damping: ' num2str(spring_damping_vec(k))
        %'Ns/m'],'fontsize',20)
        h = gcr
        ylims{1} = [-50, 10];
        ylims{2} = [-270, 0];
        setoptions(h,'FreqUnits','Hz','YLimMode','manual','YLim',ylims);
        set(findall(fig, 'type','axes'),'fontsize',16)
        PlotOptions= getoptions(PlotHandle);
        PlotOptions.Title.String= '';
        PlotOptions.XLabel.FontSize= 20;
        PlotOptions.YLabel.FontSize= 20;
        PlotHandle.setoptions(PlotOptions)

        set(findall(gcf,'Type','line'),'LineWidth',4)
        xlim([1 120])
        grid on
        hold on
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
else
    k =1;
    b_sp = spring_damping_vec(k)
    my_transfer = tf(um_gain*(K_P + K_D*s +K_I/s)*K_PID2Vardu*K_ampl*K_tau/(-J_T*s^2*n/L_CL*(L_a*s+R_a) - (k_eq + b_sp*s)*L_CL/n*(L_a*s+R_a) - K_emf*s*n/L_CL*K_tau  + um_gain*(K_P + K_D*s +K_I/s)*K_PID2Vardu*K_ampl*K_tau));
    fig = figure('units','normalized','outerposition',[0 0 1 1]);%,'DefaultAxesFontSize',36
    PlotHandle= bodeplot(my_transfer);
    h = gcr
    ylims{1} = [-50, 10];
    ylims{2} = [-270, 0];
    setoptions(h,'FreqUnits','Hz','YLimMode','manual','YLim',ylims);
    set(findall(fig, 'type','axes'),'fontsize',16)
    PlotOptions= getoptions(PlotHandle);
    PlotOptions.Title.String= '';
    PlotOptions.XLabel.FontSize= 20;
    PlotOptions.YLabel.FontSize= 20;
    PlotHandle.setoptions(PlotOptions)

    xlim([1 120])
    grid on 
    hold on
    s = tf('s');
    for k = 2:length(spring_damping_vec)
        b_sp = spring_damping_vec(k)
        % operator:
        % blocked by walls
        my_transfer = tf(um_gain*(K_P + K_D*s +K_I/s)*K_PID2Vardu*K_ampl*K_tau/(-J_T*s^2*n/L_CL*(L_a*s+R_a) - (k_eq + b_sp*s)*L_CL/n*(L_a*s+R_a) - K_emf*s*n/L_CL*K_tau  + um_gain*(K_P + K_D*s +K_I/s)*K_PID2Vardu*K_ampl*K_tau))
        bodeplot(my_transfer);
    end
    legend(int2str(spring_damping_vec'), 'Location', 'southwest')%'2','3','4','5','6','7','8'
    set(findall(gcf,'Type','line'),'LineWidth',4)
    %Plot figure and save
    filename = ['figures/bode_all_combined'];
    saveas(gcf, [filename  '.png'])
    saveas(gcf, [filename  '.m'])
end




%old transfer function = tf((K_P + K_D*s +
%K_I/s)*K_PID2Va/(L_a*s + R_a)*K_tau/(J_T*s^2*n/L_CL +(k_eq +
%b_sp*s)*L_CL/n + (K_P + K_D*s + K_I/s)*K_PID2Va/(L_a*s + R_a)*K_tau + K_emf*s/(L_a*s + R_a)*K_tau*n/L_CL) )