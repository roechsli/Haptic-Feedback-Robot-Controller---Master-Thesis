freq_vec = [1.25, 1.6, 100, 10, 12.6, 16, 1, 2.5, 20, 25, 2, 3.17, 32, 40, 4, 50, 5, 6.3, 63, 80, 8]
amplitude_factor_l = [1.0052839216458749, 0.9991405271561531, 0.14759776628322555, 1.0465191593492096, 1.0880642215979706, 1.1522190802910368, 1.0046439550041986, 0.9932151356657599, 1.2600947273486607, 1.2842520641164805, 1.0020329809714894, 1.0014693485131245, 1.0150402929231659, 0.7383722966339016, 1.0079895873881333, 0.4908444452676763, 0.9951146354026693, 1.0162473027018177, 0.3248091089212081, 0.21395810442150892, 1.0190435893115852]
phasediff_l = [-2.075830318502497, -2.8844488303323885, 169.60207402532274, -12.596392094963633, -16.551435436977613, -22.312023532948942, -2.142449369453317, -4.4456858870760385, -32.42034397864422, -58.04021679762169, -3.8675024925421297, -4.9991477731368335, -88.79867703452486, 247.1661435303339, -6.019898453018541, -139.14671090346013, -7.620669651037105, -8.855829105472651, 207.42648196699372, 189.67814591921086, -11.574912105096871]
amplitude_factor_r = [1.01528252648064, 1.0061854783791677, 0.06653250415394932, 1.0902513430697414, 1.14045066153976, 1.2004736909239189, 1.0181444949090879, 1.0103853848652116, 1.162145265952185, 0.8688050902240192, 1.0054167780929026, 1.0006278159816782, 0.5739997987858684, 0.39934203430159093, 0.9952954766920439, 0.2651356660318484, 1.0089711572251487, 1.014906857520811, 0.1662665532311567, 0.10588404052157428, 1.0486193030968416]
phasediff_r = [-3.9462055759644983, -4.794697605862581, 170.31264264153552, -20.92739519520042, -28.56990446690955, -42.04673253830194, -2.981093827020544, -6.916031863159901, -63.98332976383682, -93.45599243577922, -5.522214079974674, -8.009198022882693, -115.88709982628073, 228.4711130111851, -9.51822676960225, -144.62395382557736, -11.736703802647355, -14.388214287698673, 199.8738652541653, 186.94808894493073, -17.185092593521006]

phasediff_l = -(phasediff_l>0)*360 + phasediff_l;
phasediff_r = -(phasediff_r>0)*360 + phasediff_r;
[f_sort, I] = sort(freq_vec)
semilogx(f_sort, 20*log10(amplitude_factor_l(I')), '*-', 'Color', 'r')
hold on
PlotHandle= bodeplot(my_transfer);
semilogx(f_sort, phasediff_l(I'), '*-', 'Color', 'r')
h = gcr
ylims{1} = [-30, 10];
ylims{2} = [-200, 0];
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