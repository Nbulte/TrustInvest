import numpy as np
import copy
import math
import os
import matplotlib.pyplot as plt
from datetime import datetime
from itertools import combinations_with_replacement

###############################################################################
#The class below is needed for the scrip SummaryMaker.py in order to show annotations on the datapoints after clicking them. 

class AnnoteFinder(object):
    """callback for matplotlib to display an annotation when points are
    clicked on.  The point which is closest to the click and within
    xtol and ytol is identified.

    Register this function like this:

    scatter(xdata, ydata)
    af = AnnoteFinder(xdata, ydata, annotes)
    connect('button_press_event', af)
    """

    def __init__(self, xdata, ydata, annotes, ax=None, xtol=None, ytol=None):
        self.data = list(zip(xdata, ydata, annotes))
        if xtol is None:
            xtol = ((max(xdata) - min(xdata))/float(len(xdata)))/2
        if ytol is None:
            ytol = ((max(ydata) - min(ydata))/float(len(ydata)))/2
        self.xtol = xtol
        self.ytol = ytol
        if ax is None:
            self.ax = plt.gca()
        else:
            self.ax = ax
        self.drawnAnnotations = {}
        self.links = []

    def distance(self, x1, x2, y1, y2):
        """
        return the distance between two points
        """
        return(math.sqrt((x1 - x2)**2 + (y1 - y2)**2))

    def __call__(self, event):

        if event.inaxes:

            clickX = event.xdata
            clickY = event.ydata
            if (self.ax is None) or (self.ax is event.inaxes):
                annotes = []
                # print(event.xdata, event.ydata)
                for x, y, a in self.data:
                    # print(x, y, a)
                    if ((clickX-self.xtol < x < clickX+self.xtol) and
                            (clickY-self.ytol < y < clickY+self.ytol)):
                        annotes.append(
                            (self.distance(x, clickX, y, clickY), x, y, a))
                if annotes:
                    annotes.sort()
                    distance, x, y, annote = annotes[0]
                    self.drawAnnote(event.inaxes, x, y, annote)
                    for l in self.links:
                        l.drawSpecificAnnote(annote)

    def drawAnnote(self, ax, x, y, annote):
        """
        Draw the annotation on the plot
        """
        if (x, y) in self.drawnAnnotations:
            markers = self.drawnAnnotations[(x, y)]
            for m in markers:
                m.set_visible(not m.get_visible())
            self.ax.figure.canvas.draw_idle()
        else:
            t = ax.text(x, y, " - %s" % (annote),)
            m = ax.scatter([x], [y], marker='d', c='r', zorder=100)
            self.drawnAnnotations[(x, y)] = (t, m)
            self.ax.figure.canvas.draw_idle()

    def drawSpecificAnnote(self, annote):
        annotesToDraw = [(x, y, a) for x, y, a in self.data if a == annote]
        for x, y, a in annotesToDraw:
            self.drawAnnote(self.ax, x, y, a)

###############################################################################

def changeDateFormat(date):
    A = date.split("-")
    return A[2] + "/" + A[1] + "/" + A[0][2:]

###############################################################################

def allignArrays(returns1, returns2, dates1, dates2):
    (r1, r2, d1, d2) = (copy.copy(returns1), copy.copy(returns2), copy.copy(dates1), copy.copy(dates2))
    n1 = len(d1)
    n2 = len(d2)
    if d1[0] == d2[0] and d1[n1-1] == d2[n2-1] and n1 == n2: 
        return (r1, r2, d1, d2)
    else:
        poplist1 = []
        poplist2 = []
        for i in range(0,n1):
            if d1[i] not in d2:
                poplist1.append(i)
        for i in range(0,n2):
            if d2[i] not in d1:
                poplist2.append(i)
        d1 = [val for i, val in enumerate(d1) if i not in poplist1]
        r1 = [val for i, val in enumerate(r1) if i not in poplist1]
        d2 = [val for i, val in enumerate(d2) if i not in poplist2]
        r2 = [val for i, val in enumerate(r2) if i not in poplist2]
        if len(r1) != len(r2):
            print "Returns are not alligned."
        if len(d1) != len(d2):
            print "Dates are not alligned."
        return (r1, r2, d1, d2)

###############################################################################

def beta_market(returns_market, returns_other, dates_market, dates_other):
    print "Computing beta..."
    (r1, r2, d1, d2) = allignArrays(returns_market, returns_other, dates_market, dates_other)
    covariance = np.cov(r1,r2)[0][1]
    beta =  covariance/(np.std(r1)**2)
    return beta

###############################################################################

#This function initialises a combination for a portfolio
def initialiseCombinations(col, weight_frac, length):
    A = [weight_frac]*length
    A[col] = 1. - float(np.sum(A)) + weight_frac
    A[col] = round(A[col],2)
    return A

###############################################################################

#How to divide 6 balls in 3 buckets and no bucket can be empty: o o o / o o / o : combination of 3-1 out of 6-1. 
#Give the amount of stocks you have, and specify the weight_frac's you want. The weight_frac is the smallest unit of division for one particular stock. The output of this code is a list of combinations of stocks. For 6 entries a possible outcome could be: [0.25,0.05,0.10,0.15,0.20,0.15], note how all weight_frac's sum up  to 1. 
def computeWeightCombinations(n_stocks, weight_frac):
    if int(round(1.%0.05)) != 0:
        print "1 is probably not divisible by entered weight-fraction"
    comb_list = []
    indexes_A = [i for i in range(0,n_stocks)] 
    frac = weight_frac
    copy_indexes_A = copy.copy(indexes_A)
    copy_indexes_A.pop(0) #Remove the first entry
    end = int(round(((1 - (n_stocks-1)*weight_frac)-weight_frac)/weight_frac,2))
    for m in range(0, end):
        A = initialiseCombinations(0, weight_frac, n_stocks)
        if m == 0:
            comb_list.append(copy.copy(A))
        A[0] -= frac
        A[0] = round(A[0],2)
        n_times = int(round(frac / weight_frac,2))
        remaining_combs = list(combinations_with_replacement(copy_indexes_A, n_times))
        for c in remaining_combs:
            temp_A = copy.copy(A)
            for col in c:
                temp_A[col] += weight_frac
                temp_A[col] = round(temp_A[col],2)
            comb_list.append(temp_A)
        frac  += weight_frac
    return comb_list


###############################################################################
def writeOutError(name):
    f = open("errorStocks.txt","a+") # "a+" append and make it possible to use .read() on it, hence the "+"
    if name not in f.read().split("\n"):
        f.write(name+"\n")
    f.close()
