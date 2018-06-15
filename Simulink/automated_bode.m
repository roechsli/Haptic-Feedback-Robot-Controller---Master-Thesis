% run the parameters file before running this script

frequency_vec = [1, 1.25, 1.6, 2, 2.5, 3.17, 4, 5, 6.3, 8, 10, 12.6, 16, 20, 25, 32, 40, 50, 63, 80, 100];
stiffness_vec = [100];
damping_vec = [10];
spring_damping_vec = [0 0.0001 0.001 0.01 0.1 1 10];
for b_sp = 1:length(spring_damping_vec)
    b_spring = spring_damping_vec(b_sp)
    for k = 1:length(stiffness_vec)
        k_op = stiffness_vec(k)
        for b = 1:length(damping_vec)
            b_op = damping_vec(b)
            phase_vec = [];
            amplitude_vec = [];
            for i= 1:length(frequency_vec)
                i
                freq = frequency_vec(i);
                sim('block_diagram.mdl')
                time_vec = linspace(0,10,length(dx.signals.values));
                [phase, amplitude, bias] = fit_sine_func(-dx.signals.values, time_vec, freq);
                [phase_ref, amplitude_ref, bias_ref] = fit_sine_func(dx_ref.signals.values, time_vec, freq);

                phase_vec = [phase_vec phase - phase_ref];
                amplitude_vec = [amplitude_vec amplitude/amplitude_ref];

            end
            %Plot figure and save
            fig = figure('units','normalized','outerposition',[0 0 1 1],'DefaultAxesFontSize',18);
            set(fig, 'DefaultLineLineWidth',4)
            ax1 = subplot(2,1,1);
            semilogx(frequency_vec, 20*log10(-amplitude_vec*5/dx_max), '.-', 'MarkerSize', 25)
            title(ax1,'Magnitude Plot')
            ylabel(ax1,'Magnitude [dB]')
            grid on

            ax2 = subplot(2,1,2);
            semilogx(frequency_vec, phase_vec, '.-', 'MarkerSize', 25)
            title(ax2,'Phase Plot')
            ylabel(ax2,'Phase lag [deg]')
            title('Bode Plot')
            xlabel('Frequency [Hz]')
            grid on
            filename = ['figures/bode_op_stiff'  num2str(stiffness_vec(k)) '_op_damp' num2str(damping_vec(b)) 'sp_damp' num2str(spring_damping_vec(b_sp))];
            saveas(gcf, [filename  '.png'])
            dot_pos = strfind(filename,'.');
            if (dot_pos)
                saveas(gcf, [filename(1:dot_pos-1) filename(dot_pos+1:end)  '.m'])
            else
                saveas(gcf, [filename  '.m'])
            end
            close(fig)
        end
    end
end