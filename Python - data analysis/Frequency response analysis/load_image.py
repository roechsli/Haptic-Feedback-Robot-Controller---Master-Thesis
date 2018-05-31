import matplotlib.pyplot as plt
import pickle

#matplotlib notebook

with open('figs/f2/2_raw.pkl','rb') as fid:
    ax = pickle.load(fid)
plt.show()
