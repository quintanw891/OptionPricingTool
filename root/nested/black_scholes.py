'''
black_scholes.py
Created on Oct 11, 2018

@author: William Quintano
'''
from scipy.stats import norm
import math

'''
Calculates the price of a stock option using the black scholes model
:param s strike price
:param t remaining lifespan of option in years
:param u price of underlying stock (To get call buying or put selling price: u = highest bid for stock.
    To get call selling or put buying price: u = asking price for stock.)
:param r risk-free-rate. This should be the rate of a US treasury bill/bond with a duration close to t
:param v volatility
:param c option type. True for call, false for put
'''
def black_scholes(s,t,u,r,v,c):
    if(c):
        sign=1
    else:
        sign=-1 
    d1 = sign*(math.log(u/s)+(r+.5*v**2)*t)/(v*t**.5)
    d2 = sign*(d1 - v*t**.5)
    return sign*(u*norm.cdf(d1,0,1)) - sign*((s*norm.cdf(d2,0,1))/math.exp(r*t))