import pickle
import os
import numpy as np
import matplotlib.pyplot as plt

from helpers import allignArrays, computeWeightCombinations

####################################################################
#This script takes a set of stocks as input and computes the ideal portfolio (in terms of combinations of stocks) by devising which portfolio provides the highest Sharpe-ratio. 
####################################################################

with open(os.getcwd()+"/Pickle/pickled_info.dat", "rb") as f:
    pickle_library = pickle.load(f)

stocks = pickle_library['stocks']
markets = pickle_library['markets']

K = 7000 #Amount of available capital
stocklist = ['AutoNation', 'Avianca Holdings S.A.', 'Aware', 'AVG Technologies N.V.'] #Select a number of stocks that seem to be good
n_stocks = len(stocklist) #Number of stocks
prices_of_stocks = [stocks[name]['open_price_last'] for name in stocklist] #Prices (today) of the stocks, (which should be the price at which you buy them).


portfolio = {'stocknames': stocklist, 'K': K}
portfolio['stock_returns']  = {}
portfolio['stock_dates'] = {}
for n in portfolio['stocknames']:
    portfolio['stock_returns'] [n] = stocks[n]['returns']
    portfolio['stock_dates'][n] = stocks[n]['dates']

#Stocks don't always have entries on equal dates. Sometimes date 1 for stock A is not listed for stock B. This code ensures that for all stocks in the portfolio, all entries that are not similar, are removed. It is done by repeatedly calling the allignArrays() method (which alligns 2 stocks each time) as defined in the helpers.py script. 
for _ in range(2): #This whole thing has to be done twice to make sure everything is on equal length!
    for i in range(0,n_stocks):
        if i == n_stocks-1:
            i_next = 0
        else:
            i_next = i + 1
        (r1,r2,d1,d2) = allignArrays(portfolio['stock_returns'][stocklist[i]],
                                     portfolio['stock_returns'][stocklist[i_next]],
                                     portfolio['stock_dates'][stocklist[i]],
                                     portfolio['stock_dates'][stocklist[i_next]])
        portfolio['stock_returns'] [stocklist[i_next]] = r2
        portfolio['stock_dates'][stocklist[i_next]] = d2

fig3 = plt.figure()
ax3 =  fig3.add_subplot(111)
ax3.set_ylabel(r"$E[R_{P}]\ (\%)$", fontsize = 14)
ax3.set_xlabel(r"$\sigma_{P}\ (\%)$", fontsize = 14)
ax3.set_title('Portfolio-combinations', loc='left')
ax3.set_xlim([1,1.6])
#ax3.set_ylim([0,1.05*max(means)])

sharpes=[]
outf = open("outf.txt", "w")
r_f = 0.003
weight_combs = computeWeightCombinations(n_stocks, 0.05)
for i,w in enumerate(weight_combs):
    beta_P = np.sum([w[j]*stocks[name]['beta'] for j,name in enumerate(portfolio['stocknames'])]) #The beta of the portfolio is just equal to the weighted sum of the individual beta's of the stocks. 
    portfolio['beta_P'] = beta_P
    vec = [0]*len(portfolio['stock_returns'][portfolio['stocknames'][0]]) #Initialise a list of 0's with a length equal to the amount of returns for an arbitrary stock. Here we took the first one (0th entry), as it doesn't matter which one since all stock returns were put on equal length in the codeblock above.
    for j, name in enumerate(portfolio['stocknames']):
        weighted_returns = map(lambda x: x*w[j],portfolio['stock_returns'][name]) #Map takes a function as an argument and an iterable object. Here the function x*w[j] will be applied to all x's who are the returns (as lists) from all the stocks in your portfolio, it thus generates the weighted_returns. 
        vec =  map(sum, zip(vec, weighted_returns))
    portfolio['P_returns'] = vec #This is equal to the weighted returns for every date. This value is only needed to compute the SD(R_P) which includes the correlation coefficient of each individual stock's returns with the returns of the portfolio. 
    sum_sd = 0.0
    for j,n in enumerate(portfolio['stocknames']):
        sum_sd += w[j]*np.std(portfolio['stock_returns'][n])*np.corrcoef(portfolio['stock_returns'][n], portfolio['P_returns'])[0][1]
    portfolio['SD_P'] = sum_sd 
    outf.write(str(sum_sd) + ' \t')
    ER_Mkt = sum([w[j]*np.mean(markets[stocks[name]['market']]['returns']) for j,name in enumerate(stocklist)]) #The ER_Mkt is not just one market average. It's a weighted sum of market averages since stocks don't necessarily come from one and the same market. 
    portfolio['ER_CAPM'] = r_f + portfolio['beta_P']*(ER_Mkt-r_f)
    outf.write(str(portfolio['ER_CAPM'])+'\t')
    ax3.scatter(portfolio['SD_P'], portfolio['ER_CAPM'])
    sharpe = (portfolio['ER_CAPM'] - r_f) / portfolio['SD_P']
    sharpes.append(sharpe)
    outf.write(str(sharpe)+'\n')    

print "The following portfolio was found to be optimal: " + str(stocklist) + " , with:"  
print "Sharpe-ratio: " + str(max(sharpes)) + " Weights: " + str(weight_combs[sharpes.index(max(sharpes))])


plt.show()
