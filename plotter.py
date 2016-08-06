from __future__ import unicode_literals
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from scipy import arange, array, exp

def extrap1d(interpolator):
    xs = interpolator.x
    ys = interpolator.y

    def pointwise(x):
        if x < xs[0]:
            return ys[0]+(x-xs[0])*(ys[1]-ys[0])/(xs[1]-xs[0])
        elif x > xs[-1]:
            return ys[-1]+(x-xs[-1])*(ys[-1]-ys[-2])/(xs[-1]-xs[-2])
        else:
            return interpolator(x)

    def ufunclike(xs):
        return array(map(pointwise, array(xs)))

    return ufunclike

file = open("outf.txt", 'r')
SD = []
ER = []
sharpe = []
for l in file.readlines():
    ER.append(float(l.split('\n')[0].split('\t')[1]))
    SD.append(float(l.split('\n')[0].split('\t')[0]))
    sharpe.append(float(l.split('\n')[0].split('\t')[2]))

max_sharp_index = sharpe.index(max(sharpe))

fig3 = plt.figure()
ax3 =  fig3.add_subplot(111)
ax3.set_ylabel(r"$E[R_{P}]\ (\%)$", fontsize = 14)
ax3.set_xlabel(r"$\sigma_{P}\ (\%)$", fontsize = 14)
ax3.set_title(r'$\mathrm{Portfolio-combinations\ of\ 6\ randomly\ chosen\ stocks}$', loc='left')
ax3.set_xlim([1,1.3])
ax3.set_ylim([0.013,0.029])
ax3.text(0.02,0.05,r'$E[R_{P}]= r_{f} + \beta_{P}\left(E[R_{Mkt}] - r_{f}\right)$', transform=ax3.transAxes, fontsize=18)
#ax3.text(0.02,0.90,'$\mathrm{Sharpe\ Ratio}\ \ \ =\ $' + r'$\frac{E[R_{P}] - r_{f}}{\sigma_{P}}\ =\ 0.020 $', transform=ax3.transAxes, fontsize=13)

#[0.05, 0.15, 0.55, 0.05, 0.05, 0.15]

f_i = interp1d([0,SD[max_sharp_index]],[0.003,ER[max_sharp_index]])
f_x = extrap1d(f_i)

ax3.scatter(SD,ER, s=10, c='g', lw=0)
ax3.plot([0,SD[max_sharp_index],2],[0.003,ER[max_sharp_index], f_x([2])], linewidth=1.5, c='r', ls = '--')
ax3.scatter(SD[max_sharp_index], ER[max_sharp_index], c='r', s = 25, lw=0, label='$\mathrm{Sharpe\ Ratio}\ =\ $' + r'$\frac{E[R_{P}] - r_{f}}{\sigma_{P}}\ =\ 0.02 $')
ax3.legend(loc='upper left', scatterpoints=1, frameon=False)
#plt.show()
plt.savefig("fig", format='png')
