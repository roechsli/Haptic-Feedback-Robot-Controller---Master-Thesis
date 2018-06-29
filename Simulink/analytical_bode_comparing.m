spring_damping_vec = [200 250 300 350 400];%[1 10 100 1000 10000 100000];%linspace(0,10000,10000/100+1);%
BOOL_SEVERAL_PLOTS = 1;

%k_op = 200
%b_op = 20
K_P = 0.2%1.6
K_I = 0.0%01
K_D = 0.0%14
K_PID2Vardu = 1/51 % [V]
um_gain = -1000000 % [um/m]
K_ampl = 10
V_offset = -25
bit_offset = 128
n = 112
J_T = 1.25E-3 / n / n % without efficiency coeff 7.5E-4 / n / n%
%J_T =  0.1  % kg*m^2
L_CL = 20E-3
k_eq = 6000 % N/m
m_2 = 7E-3
L_a = 5.8E-3
R_a  = 118.6
efficiency = 0.6
K_tau = efficiency*31.4E-3 % [Nm/A]
K_emf = 3.29E-3 / 60 % [V/s]
s = tf('s');
dT = 0.001;



% experim1
freq_vec = [1.25, 1.6, 100, 10, 12.6, 16, 1, 2.5, 20, 25, 2, 3.17, 32, 40, 4, 50, 5, 6.3, 63, 80, 8]
amplitude_factor_l = [1.0052839216458749, 0.9991405271561531, 0.14759776628322555, 1.0465191593492096, 1.0880642215979706, 1.1522190802910368, 1.0046439550041986, 0.9932151356657599, 1.2600947273486607, 1.2842520641164805, 1.0020329809714894, 1.0014693485131245, 1.0150402929231659, 0.7383722966339016, 1.0079895873881333, 0.4908444452676763, 0.9951146354026693, 1.0162473027018177, 0.3248091089212081, 0.21395810442150892, 1.0190435893115852]
phasediff_l = [-2.075830318502497, -2.8844488303323885, 169.60207402532274, -12.596392094963633, -16.551435436977613, -22.312023532948942, -2.142449369453317, -4.4456858870760385, -32.42034397864422, -58.04021679762169, -3.8675024925421297, -4.9991477731368335, -88.79867703452486, 247.1661435303339, -6.019898453018541, -139.14671090346013, -7.620669651037105, -8.855829105472651, 207.42648196699372, 189.67814591921086, -11.574912105096871]
amplitude_factor_r = [1.01528252648064, 1.0061854783791677, 0.06653250415394932, 1.0902513430697414, 1.14045066153976, 1.2004736909239189, 1.0181444949090879, 1.0103853848652116, 1.162145265952185, 0.8688050902240192, 1.0054167780929026, 1.0006278159816782, 0.5739997987858684, 0.39934203430159093, 0.9952954766920439, 0.2651356660318484, 1.0089711572251487, 1.014906857520811, 0.1662665532311567, 0.10588404052157428, 1.0486193030968416]
phasediff_r = [-3.9462055759644983, -4.794697605862581, 170.31264264153552, -20.92739519520042, -28.56990446690955, -42.04673253830194, -2.981093827020544, -6.916031863159901, -63.98332976383682, -93.45599243577922, -5.522214079974674, -8.009198022882693, -115.88709982628073, 228.4711130111851, -9.51822676960225, -144.62395382557736, -11.736703802647355, -14.388214287698673, 199.8738652541653, 186.94808894493073, -17.185092593521006]

%experim2 K_P = 0.2; K_I = 0; K_D = 0
freq_vec = [1.25, 1.6, 100.0, 10.0, 13.0, 16.0, 1.0, 2.5, 20.0, 25.0, 2.0, 32.0, 3.0, 40.0, 4.0, 50.0, 5.0, 6.3, 63.0, 80.0, 8.0]
amplitude_factor_l = [0.8021762720531634, 0.8054151390569485, 0.015545101680621341, 1.0773667825505355, 1.1642926077392948, 1.1103451508176316, 0.8001758873970981, 0.814056941660425, 0.8809965954959127, 0.5443027780892209, 0.8080825031462602, 0.2796958251080355, 0.8204548508774807, 0.16228564296355955, 0.8471466599918783, 0.10547366728162677, 0.8705112782697394, 0.9245682579252669, 0.05343340955353186, 0.024603192099363968, 0.9978075966054786]
phasediff_l = [-13.338637077482488, -14.09045739088748, -215.85673669598538, -48.04116200227554, -73.34441078067667, -100.25217048165923, -13.120541509581287, -16.085908849961044, -133.37888476020055, 201.4902985359118, -14.874321828402891, -176.09087916984802, 342.54636240739, 172.0658999860665, 339.59240015589626, 160.15771192477212, -23.728405952504453, -28.567395522204393, 147.9917576755808, 149.19385839692242, -36.037447598503036]
amplitude_factor_r = [0.7259689909042475, 0.735561475713898, 0.011847747061743118, 0.7807616430080885, 0.6652857160264002, 0.4684605400670259, 0.7127722160221738, 0.7461571487258002, 0.28422778003510263, 0.18648071556469148, 0.7439708501454618, 0.10739962887725536, 0.7525359007020068, 0.07014225593098215, 0.7786568428021221, 0.04585663312767849, 0.8100457909516678, 0.8245672101098731, 0.02640620952087805, 0.017672001900720043, 0.8172666256439353]
phasediff_r = [-16.647751016192103, -18.17293749217521, -237.48339557890603, -84.206485995129, -110.7789491948499, -133.2352471671927, -15.490775194720683, -22.931547230698484, -154.12969771290278, 194.1127967504471, -20.088130391155154, -178.43503982578886, 334.0056876428433, 172.21922748081028, 327.9483761537956, -190.87105537800483, -39.46722121664876, -49.247314509247005, 153.90271170189118, 138.0318425466486, -64.3717766560425]


phasediff_l = -(phasediff_l>0)*360 + phasediff_l;
phasediff_r = -(phasediff_r>0)*360 + phasediff_r;
[f_sort, I] = sort(freq_vec)


if BOOL_SEVERAL_PLOTS
    for k = 1:length(spring_damping_vec)
        b_sp = spring_damping_vec(k)
        s = tf('s');
        %z = tf('z',dT)
        %s = (1-z^-1)/dT
        
        % operator:
        % blocked by walls
        %my_transfer = tf(um_gain*(K_P + K_D*s +K_I/s)*K_PID2Vardu*K_ampl*K_tau/(-J_T*s^2*n/L_CL*(L_a*s+R_a) - (k_eq + b_sp*s)*L_CL/n*(L_a*s+R_a) - K_emf*s*n/L_CL*K_tau  + um_gain*(K_P + K_D*s +K_I/s)*K_PID2Vardu*K_ampl*K_tau))
        a = um_gain*(K_P + K_D*s + K_I/s);
        b = K_PID2Vardu*K_ampl;
        c = -n/L_CL;
        d = (L_a*s + R_a);
        e = (k_eq + b_sp*s)*L_CL/n;
        my_transfer = tf(K_tau*a*b/(c*d*s^2*J_T - e*d + K_emf*K_tau*c*s + a*b*K_tau))
        %Plot figure and save
        fig = figure('units','normalized','outerposition',[0 0 1 1]);%,'DefaultAxesFontSize',36
        semilogx(f_sort, 20*log10(amplitude_factor_l(I')), '*-', 'Color', 'r')
        hold on
        PlotHandle= bodeplot(my_transfer);
        semilogx(f_sort, phasediff_l(I'), '*-', 'Color', 'r')
        %title(['Spring damping: ' num2str(spring_damping_vec(k))
        %'Ns/m'],'fontsize',20)
        h = gcr
        ylims{1} = [-40, 10];
        ylims{2} = [-225, 0];
        setoptions(h,'FreqUnits','Hz','YLimMode','manual','YLim',ylims);
        set(findall(fig, 'type','axes'),'fontsize',16)
        PlotOptions= getoptions(PlotHandle);
        PlotOptions.Title.String= '';
        PlotOptions.XLabel.FontSize= 20;
        PlotOptions.YLabel.FontSize= 20;
        PlotHandle.setoptions(PlotOptions)
        legend(strcat('Analytical: b_{sp} = ', num2str(spring_damping_vec(k)), 'Ns/m'), 'Experimental data', 'Location', 'SouthWest')
        
        set(findall(gcf,'Type','line'),'LineWidth',4)
        xlim([1 120])
        grid on
        hold on
        filename = ['figures/bode_sp_damp' num2str(spring_damping_vec(k))];%backward_
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
    semilogx(f_sort, 20*log10(amplitude_factor_l(I')), '*-', 'Color', 'k')
    hold on
    PlotHandle= bodeplot(my_transfer);
    semilogx(f_sort, phasediff_l(I'), '*-', 'Color', 'k')
    h = gcr
    ylims{1} = [-40, 10];
    ylims{2} = [-225, 0];
    setoptions(h,'FreqUnits','Hz','YLimMode','manual','YLim',ylims);
    set(findall(fig, 'type','axes'),'fontsize',16)
    PlotOptions= getoptions(PlotHandle);
    PlotOptions.Title.String= '';
    PlotOptions.XLabel.FontSize= 20;
    PlotOptions.YLabel.FontSize= 20;
    PlotHandle.setoptions(PlotOptions)

    xlim([1 120])
    grid on 
    %hold on
    s = tf('s');
    for k = 2:length(spring_damping_vec)
        b_sp = spring_damping_vec(k)
        % operator:
        % blocked by walls
        my_transfer = tf(um_gain*(K_P + K_D*s +K_I/s)*K_PID2Vardu*K_ampl*K_tau/(-J_T*s^2*n/L_CL*(L_a*s+R_a) - (k_eq + b_sp*s)*L_CL/n*(L_a*s+R_a) - K_emf*s*n/L_CL*K_tau  + um_gain*(K_P + K_D*s +K_I/s)*K_PID2Vardu*K_ampl*K_tau))
        bodeplot(my_transfer);
    end
    legend( [int2str(spring_damping_vec(1)); 'Exp'; int2str(spring_damping_vec(2:end)')], 'Location', 'southwest')
    set(findall(gcf,'Type','line'),'LineWidth',4)
    %Plot figure and save
    filename = ['figures/bode_all_combined'];
    saveas(gcf, [filename  '.png'])
    saveas(gcf, [filename  '.m'])
end




%old transfer function = tf((K_P + K_D*s +
%K_I/s)*K_PID2Va/(L_a*s + R_a)*K_tau/(J_T*s^2*n/L_CL +(k_eq +
%b_sp*s)*L_CL/n + (K_P + K_D*s + K_I/s)*K_PID2Va/(L_a*s + R_a)*K_tau +
%K_emf*s/(L_a*s + R_a)*K_tau*n/L_CL) )