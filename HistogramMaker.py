import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import copy
import math
import pickle
from itertools import combinations, product, combinations_with_replacement
from math import *
import os
from scipy.stats import kurtosis, skew

from helpers import changeDateFormat, beta_market, computeWeightCombinations, allignArrays, writeOutError
from info import stocks, markets

####################################################################
#This script makes plots of all stock- and market-data. 
#It saves it into a folder called plots. Every plot contains a histogram of the (daily) returns along with the opening prices from the given time horizon up till now. 
####################################################################

data_path = os.getcwd()+'/Data' # CurrentPath/Data

data_files_stocks = [f for f in os.listdir(data_path+'/Stocks') if os.path.isfile(os.path.join(data_path+'/Stocks', f))]
#data_files_stocks = [f for f in os.listdir(data_path+'/Stocks') if os.path.isfile(os.path.join(data_path+'/Stocks', f))] #returns list of strings which are the filenames of datafiles
data_files_markets = [f for f in os.listdir(data_path+'/Markets') if os.path.isfile(os.path.join(data_path+'/Markets', f))]

risk_info = []
means=[] #Means of all stocks
sigmas=[] #All standard deviations of stock returns
names = [] #Names of all stocks

for d in sorted(data_files_markets)+sorted(data_files_stocks): #First markets, then stocks!
    print("Working on " + d + " ...")
    fig = plt.figure()
    ax1 = fig.add_subplot(211)
    ax2 = fig.add_subplot(212)
    if 's_' in d:
        data_file = data_path +'/Stocks/' + d
    if 'm_' in d:
        data_file = data_path +'/Markets/' + d
    dates = []
    open_prices = []
    open_prices_dates = [] #Needed to find highest and lowest values of open_prices on the bottom plot.
    returns = []
    volumes = []
    file = open(data_file, 'r')
    content = file.readlines()
    firstline = content[0]
    content.pop(0) #Remove first line, doesn't contain numbers
    year_indices = []
    date_prev = 0
    for c in content:
        date = c.split('\n')[0].split()[0]
    ##################TEST#################
        if int(date.split("-")[0]) < 2011:
            continue
    #######################################
        open_price = c.split('\n')[0].split()[1]
        if open_price != 'NaN':
            open_prices.append(float(open_price))
            open_prices_dates.append(date)
        if "Volume" in firstline: #Do this because some markets (s.a. NASDAQ) don't have a volume entry.
            volume = float(c.split('\n')[0].split()[2])
            return_price = c.split('\n')[0].split()[3]
        else:
            volume = 10000
            return_price = c.split('\n')[0].split()[2]
        if float(return_price) < 15 and return_price != 'NaN':
            dates.append(date)      
            if int(date.split("-")[0]) > date_prev:
                year_indices.append(dates.index(date))
            date_prev = int(date.split("-")[0])
            returns.append(float(return_price)*100.) 
        volumes.append(volume) #Volume array doesn't have to be on equal length as dates and returns (who are on equal length), we just compute an average in the end. 
    print year_indices
    n, bins, patches = ax1.hist(returns, bins=np.arange(-10,10,0.5), normed=1,facecolor='green', alpha=0.75)
    mean = np.mean(returns)
    standard_deviation = np.std(returns)
    if ('s_' in d):
        name = d.replace('s_','').replace('.txt','')
        try:
            stocks[name]['dates'] = dates
        except KeyError:
            writeOutError(name)
            continue
        stocks[name]['returns'] = returns
        stocks[name]['open_price_last'] = open_prices[len(open_prices)-1]
        ax1.set_title(name + " (" + stocks[name]['market'] + ")" , loc='left')
        curr = markets[stocks[name]['market']]['currency']
        dictionary = {name: {'mean': mean, 'sigma': standard_deviation}}
        risk_info.append(dictionary)
        means.append(mean)
        sigmas.append(standard_deviation)
        names.append(name)
#        savedir = os.getcwd()+'/Plots/Teststocks/'+d.replace('.txt', '')
        savedir = os.getcwd()+'/Plots/Stocks/'+d.replace('.txt', '')
        this_market = markets[stocks[name]['market']]
        if this_market.has_key('returns') and this_market.has_key('dates'):
            beta = beta_market(copy.copy(this_market['returns']), copy.copy(stocks[name]['returns']), copy.copy(this_market['dates']), copy.copy(stocks[name]['dates']))
            stocks[name]['beta'] = beta
    if ('m_' in d):
        name = d.replace('m_','').replace('.txt','')
        markets[name]['dates'] = dates
        markets[name]['returns'] = returns
        ax1.set_title(name, loc='left')
        curr = markets[name]['currency']
        savedir = os.getcwd()+'/Plots/Markets/'+d.replace('.txt', '')

    ax1.text(0.01, 0.90, "Time Interval: "+str(dates[0])+ " to " + str(dates[len(dates)-1]), transform=ax1.transAxes, fontsize=8)
    if ('s_' in d):
        ax1.text(0.01,0.82, r'$\beta^{Mkt} =\ $' + str(round(beta,2)), transform=ax1.transAxes, fontsize=12)
    ax1.text(0.6,0.90,r'$E[R]=' + str(round(mean,4))+'\%' +',\ \sigma=' + str(round(standard_deviation,4))+'\%$', transform=ax1.transAxes)
    ax1.text(0.6,0.82,r'$\gamma =' + str(round(skew(returns),1)) +',\ \kappa =' + str(round(kurtosis(returns),4)) + '$', transform=ax1.transAxes)
    ax1.text(0.6,0.74, 'Average daily volume = ' + str(round(np.mean(volumes),0)), transform=ax1.transAxes, fontsize=8)
    ax1.set_xlim([-10,10])
    ax1.set_xlabel(r"Daily returns $R$ ($\%$)")
    ax1.xaxis.set_label_coords(0.9, -0.1)
    ax1.set_ylabel("Number of entries")

    if 's_' in d:
        dictionary = stocks
    if 'm_' in d:
        dictionary = markets
    n_entries = len(dictionary[name]['dates'])
    ax2.fill_between(np.arange(len(open_prices)),open_prices, facecolor='blue', alpha=0.5)
    year_label_indices = [] #Needed to add labels with year between dashed lines.
    for index in year_indices:
        if index != year_indices[-1]:
            year_label_indices.append(int(round((index+year_indices[year_indices.index(index)+1])/2.)))
        else:
            year_label_indices.append(int(round((index+n_entries)/2.)))
        if year_indices.index(index) == 0:
            continue
        ax2.plot((index,index),(0,10000),'k--')
    current_year = int(dates[0].split("-")[0])
    last_year = int(dates[-1].split("-")[0])
    max_open_prices = {} 
    min_open_prices = {}
    i = current_year
    while i >= current_year and i <= last_year:
        maximum = max(filter(lambda x: int(open_prices_dates[open_prices.index(x)].split("-")[0]) == i, open_prices))
        minimum = min(filter(lambda x: int(open_prices_dates[open_prices.index(x)].split("-")[0]) == i, open_prices))
        max_open_prices[i] = format(maximum,".2f")
        min_open_prices[i] = format(minimum, ".2f")
        i+=1
    for (index_label,index_minmaxvals) in zip(year_label_indices,year_indices):
        ax2.text(index_label,1.0*max(open_prices),str(current_year), ha='center', weight='bold',fontsize=8)
        ax2.text(index_label,0.10*max(open_prices),r'$\Nearrow$'+str(max_open_prices[current_year]), ha='center', weight='bold',fontsize=7)
        ax2.text(index_label,0.05*max(open_prices),r'$\Searrow$'+str(min_open_prices[current_year]), ha='center', weight='bold',fontsize=7)
        current_year += 1
    
    ax2.set_ylim([0,1.10*max(open_prices)])
    ax2.set_xlim([0, n_entries-1])
    ax2.set_ylabel("Opening prices" + " (" + curr  + ")")
    labels = [changeDateFormat(dictionary[name]['dates'][i]) for i in year_indices]
    labels.append(changeDateFormat(dictionary[name]['dates'][n_entries-1]))
    ax2.set_xticks(year_indices)
    ax2.set_xticklabels(labels)

    fig.savefig(savedir, format='pdf')
    plt.close()
    ##### AUTOMATIC HISTOGRAM CHECK #####
    if np.mean(volumes) < 1000:
        print name + " has an average traded daily volume of lower than 1000!"
    bin_content = n.tolist()
    index_maxval = bin_content.index(max(bin_content))
    try:
        if bin_content[index_maxval]/bin_content[index_maxval-1] > 2. or  bin_content[index_maxval]/bin_content[index_maxval+1] > 2.:
            print name + " seems to have a high central bin..."
    except ZeroDivisionError:
        print name + " contains next-to-highest bins with 0 entries."
    ###################################
    
print "Total number of stocks in computation: " + str(len(means))

#Here, we store all info we need for other scripts into a pickle file. This is a file in which arbitrary Python objects can be saved. For instance, the lists names, means, sigmas, etc. will be needed for other scripts, but we don't want to do the loop again which makes all the histograms and extracts this information during that process. It saves it once, which makes it more convenient for use. 

pickle_library = {} #Declare a library that will have the necessary information as keys and elements. 

pickle_library['names'] = names
pickle_library['means'] = means
pickle_library['sigmas'] = sigmas
pickle_library['stocks'] = stocks #Contains all the stocks with their dates, returns, beta's,...
pickle_library['markets'] = markets #Contains all the markets with their dates, returns, beta's,...

PIK = "pickled_info.dat"
with open(os.getcwd()+"/Pickle/"+PIK, "wb") as f:
    pickle.dump(pickle_library,f)

#################################################################################################

# def calculatePortfolioValue(number_of_stocks = None, prices_of_stocks, weights = None, K = None):
#     n = len(number_of_stocks)
#     if weights != None and K == None:
#         print "If weights file was given, K also needs to be given!"
#     if weights == None:
#         product =  [float(number_of_stocks[i])*prices_of_stocks[i] for i in range(0,n)]
#     else:
#         product = [weights[i]*K for i in range(0,n)]
#     return np.sum(product)

def calculatePortfolioValue(weights = None, K = None, number_of_stocks = None, prices_of_stocks = None):
    if weights != None and K!= None:
        n = len(weights)
        product = [weights[i]*K for i in range(0,n)]
    elif number_of_stocks != None and prices_of_stocks != None:
        n = len(weights)
        product =  [float(number_of_stocks[i])*prices_of_stocks[i] for i in range(0,n)]
    else:
        print "Either provide weights and capital, or provide number_of_stocks and prices_of_stocks!"
    return np.sum(product)


#Function returns True if the portfolio value < K and after adding one stock of any of the values is > K 
# def isPortfolioMaximal(prices_of_stocks, number_of_stocks=None, weights = None, K):
#     numbers = copy.copy(number_of_stocks)
#     prices = copy.copy(prices_of_stocks)
#     if weights != None:
#         value = calculatePortfolioValue(numbers, prices, weights, K)
#     else:
#         value = calculatePortfolioValue(numbers, prices)
#     n = len(numbers)
#     if value < K:
#         for i in range(0,n):
#             numbers[i]+=1
#             newval = calculatePortfolioValue(numbers, prices)
#             if newval < K:
#                 return False
#             else:
#                 numbers[i]-=1
#         return True
#     else:
#         return False


        
    
    
