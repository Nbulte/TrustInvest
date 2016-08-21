This repository contains all necessary code to implement the CAPM into the creation of an optimal stock portfolio. 


Relevant info:

info.py		:	This file contains all info in the Python library format necessary to use the fetchData.py script. It contains a list of the stocks/markets along with its Quandlcodes, currencies, etc. 
fetchData.py 	:	 This script fetches all data necessary for the computation of all relevant variables. Makes use of the imported script Quandl.py (black-box). The script requires a viable start date from which data must be collected. The data is stored in ./data/stocks(or markets) in .txt files.
HistogramMaker.py 	:	This script reads the data .txt files in order to produce plots containing 2 plots: a histogram containing the daily returns for a specified time interval along with a plot containing the opening prices of the stock (or market index) for the same time period.  The script also has another important function, namely to save all necessary information into a pickle-file for the correct implementation of the CAPM such as daily returns, dates, beta-coefficients, etc. This pickle file is later used for SummaryMaker.py
SummaryMaker.py		:	This script reads information from the pickled file made in HistogramMaker.py and makes a summarising plot in which each data point represents a stock with its expected CAPM return with respect to its volatility.
ComputeOptimalPortfolio.py	:	This script takes a given portfolio as an input and computes which combination of stocks delivers the optimal expected return based on which combination proves to have the highest Sharpe-ratio. 
This is a test-line.


