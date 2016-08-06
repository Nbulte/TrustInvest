import pickle
import os
import numpy as np
import matplotlib.pyplot as plt
from helpers import AnnoteFinder
from math import *


####################################################################
#This script makes a summarising plot listing the computed stock E[R]'s in function of the volatilities (risks).
####################################################################

with open(os.getcwd()+"/Pickle/pickled_info.dat", "rb") as f:
    pickle_library = pickle.load(f)

names = pickle_library['names']
means = pickle_library['means']
sigmas = pickle_library['sigmas']

#max_returns = reversed(sorted(range(len(means)), key=lambda i: means[i])) #Returns list of highest index values in "means"

fig = plt.figure()
ax = fig.add_subplot(111)
ax.set_xlim([0.9,4])
if 1.05*max(means) > 0.20:
    ax.set_ylim([0,0.20])
else:
    ax.set_ylim([0,1.05*max(means)])
k = 0
# for i in max_returns:
#     x = sigmas[i]
#     y = means[i]
#     name = names[i]
#     ax.plot(x, y, 'bo')
#     ax.annotate(name, (x,y), fontsize=9)

ax.scatter(sigmas,means)
af = AnnoteFinder(sigmas,means,names, ax=ax)
fig.canvas.mpl_connect('button_press_event',af)

ax.set_ylabel(r"$E[R]\ (\%)$", fontsize = 14)
ax.set_xlabel(r"$\sigma\ (\%)$", fontsize = 14)

plt.show()

#fig.savefig(os.getcwd()+"/Plots/Teststocks/Summary/Summary.pdf", format='pdf')
print "Fig saved in: " + str(os.getcwd()+"/Plots/Teststocks/Summary/Summary.pdf")
