import matplotlib.pyplot as plt
import pickle

#matplotlib notebook
directory = "C:/Users/Oechslin/Documents/Haptic_Controller_Code/Python - data analysis/Frequency response analysis/tmp_ardu_ref_plots/figs/"
with open(directory + '_all_in_one_raw.pkl','rb') as fid:
    ax = pickle.load(fid)
plt.show()
