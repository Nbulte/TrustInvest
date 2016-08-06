import pandas as pd
import Quandl
import numpy as np
import os
import math
import time

from helpers import writeOutError
from info import stocks, markets

#This Script fetches financial data and writes it to .txt files. 

date_start = '2009-01-01'

def fetch(date_start, token = '7zHdqqF_5wBuSvgyj2ap', suffix='', which_markets='all'): #This function only requires a date_start, arguments that are of the form arg = [...] are already filled in but can be changed if required.

    if which_markets != 'all' and isinstance(which_markets, list) == False:
        print "Available markets: " + ", ".join(markets.keys())
        raise Exception("Do not specify the which_markets argument or give a list/array containing one or more of the above listed entries as strings")
    markets_to_fetch = markets.keys() if which_markets == 'all' else which_markets
    print "Retrieving Financial Data from " + ", ".join(markets_to_fetch)

    errorfile = open("errorStocks.txt","r") #Some stocks/markets will give errors, the program ignores those shares, but writes them here for convenience.
    exceptionlist = [err_stock.replace("\n","") for err_stock in errorfile.readlines()] #Stocks from an earlier run that gave an error are loaded here, so they aren't looked at again. 

    for key in sorted(stocks.keys()) + sorted(markets.keys()):
        if key in exceptionlist: #Ignore stocks that are in the exceptionlist.
             continue
        if r"/" in key:
            key.replace("/","")
        if key in stocks.keys():
            if stocks[key]['market'] not in markets_to_fetch:
                continue
            library = stocks
            prefix = 's_'
            print 'Retrieving data from: ' + key + " (" + stocks[key]['market'] + ")"
        if key in markets.keys():
            library = markets
            prefix = 'm_'

        try:
            data = Quandl.get(library[key]['quandlcode'], authtoken=token, trim_start=date_start) #.get(code, token, date)
        except Quandl.ErrorDownloading:
            writeOutError(key)
            continue
        except Quandl.DatasetNotFound:
            writeOutError(key)
            continue

        for value in list(data.columns.values): #Remove everything but Open or Volume entries
            if value != 'Open' and value != 'Volume' and value != 'Index Value':
                del data[value]

        if 'Open' in data:
            open_prices = data['Open'].tolist()
        else:
            try:
                open_prices = data['Index Value'].tolist() #Some markets don't have an "Open" entry but "Index Value" instead.
            except KeyError: 
                writeOutError(key)
                continue            

        returns = len(open_prices)*[0] #Initialise a returns array of equal length filled with zeros

        i=1 #Keep first entry (index 0) equal to zero, as there is no return to be calculated for earliest data point
        try:
            while(i<len(open_prices)): #Fill the returns list
                returns[i] = math.ceil((float(open_prices[i])-float(open_prices[i-1]))/float(open_prices[i-1])*10000000000)/10000000000 #Calculate returns and round off to 8 numbers
                i+=1
        except ZeroDivisionError:
            writeOutError(key)
            continue            

        df = pd.DataFrame(returns,index=data.index) #Create a new dataframe with same indices as 'data'
        try:
            df.columns=['Returns'] #Add column name
        except ValueError:
            writeOutError(key)
            continue
        data = pd.concat([data,df], axis=1) #Concatenate two dataframes together

        outfile_name = prefix +  key + suffix
        if "/" in outfile_name: #Make sure there's no / in your name or you're in trouble for the next command.
            outfile_name = outfile_name.replace("/","") 

        if prefix == 's_':
            outfile = open(os.path.join(os.getcwd()+'/Data/Stocks',outfile_name+'.txt'), 'w') #open(location, read or write)
        if prefix == 'm_':
            outfile = open(os.path.join(os.getcwd()+'/Data/Markets',outfile_name+'.txt'), 'w') #open(location, read or write)
        out_text = data.to_string(index_names=False)
        outfile.write(out_text)
        outfile.close()
#        time.sleep(0.25)

fetch(date_start)
