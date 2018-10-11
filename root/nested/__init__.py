import tkinter
import http.client
import json
from datetime import datetime
from tkinter.constants import LEFT
from tkinter import StringVar
from test.test_optparse import DurationOption
from audioop import ratecv

entry_window = tkinter.Tk()
entry_window.title('Option Pricing Tool')

NUM_RISK_FREE_RATES = 4

#widgets
display_frame = tkinter.Frame(entry_window)
entry_prompt = tkinter.Text(entry_window,height=4,width=40)
prompt = 'Enter a symbol and your estimation of\nits volatility. The next screen will\ngenerate pricings for existing options\nand compare them to asking prices'
entry_prompt.insert(tkinter.END,chars=prompt)
symbol_error_prompt = StringVar()
symbol_error = tkinter.Label(entry_window,fg='red',textvariable=symbol_error_prompt)
symbol_label = tkinter.Label(entry_window,text='Symbol:')
volatility_error_prompt = StringVar()
volatility_error = tkinter.Label(entry_window,fg='red',textvariable=volatility_error_prompt)
volatility_label = tkinter.Label(entry_window,text='Volatility:')
symbol_entry = tkinter.Entry(entry_window, bd=5,width=10)
volatility_entry = tkinter.Entry(entry_window,bd=5,width=10)
def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False
class treasury_rate:
    def __init__(self,rate,duration):
        self.rate = rate
        self.duration = duration
def generate_prices():    
    symbol = symbol_entry.get()
    volatility = volatility_entry.get()
    if not symbol or not volatility or not RepresentsInt(volatility):
        if not symbol:
            symbol_error_prompt.set('Symbol is a required field')
        else:
            symbol_error_prompt.set('')
        if not volatility:
            volatility_error_prompt.set('Volatility is a required field')
        else:
            volatility_error_prompt.set('')
            if not RepresentsInt(volatility):
                volatility_error_prompt.set('Volatility must be numeric')
    else:
        symbol_error_prompt.set('')
        volatility_error_prompt.set('')
        connection = http.client.HTTPSConnection('sandbox.tradier.com', 443, timeout = 30)
        
        # Headers
        
        headers = {"Accept":"application/json",
                   "Authorization":"Bearer dMl12anAyqC3RGdOZC32ziU96XfT"}
        
        # Send synchronously
        connection.request('GET', '/v1/markets/options/expirations?symbol='+symbol, None, headers)
        try:
            response = connection.getresponse()
            content = response.read()
            # Success
            #print('Response status ' + str(response.status))
            expiration_data = json.loads(content)
            if expiration_data['expirations']:#Symbol is valid and has options
                symbol_error_prompt.set('')
                volatility_error_prompt.set('')
                
                #for d in expiration_data['expirations']['date']:
                    #print (d)
                    
                #get risk free rates
                rf_rates = [0] * NUM_RISK_FREE_RATES
                rate_index = 0
                try:
                    #13 week US treasury bill
                    connection.request('GET', '/v1/markets/quotes?symbols=IRX', None, headers)
                    response = connection.getresponse()
                    content = response.read()
                    #print('13 week:\t'+str(json.loads(content)['quotes']['quote']['last']/10))
                    rf_rates[rate_index] = treasury_rate(json.loads(content)['quotes']['quote']['last']/10, 13*7)
                    rate_index+=1
                    
                    #5 year US treasury bill
                    connection.request('GET', '/v1/markets/quotes?symbols=FVX', None, headers)
                    response = connection.getresponse()
                    content = response.read()
                    #print('5 year:\t\t'+str(json.loads(content)['quotes']['quote']['last']/10))
                    rf_rates[rate_index] = treasury_rate(json.loads(content)['quotes']['quote']['last']/10, 365*5)
                    rate_index+=1
                    
                    #10 year US treasury bond
                    connection.request('GET', '/v1/markets/quotes?symbols=TNX', None, headers)
                    response = connection.getresponse()
                    content = response.read()
                    #print('10 year:\t'+str(json.loads(content)['quotes']['quote']['last']/10))
                    rf_rates[rate_index] = treasury_rate(json.loads(content)['quotes']['quote']['last']/10, 10*365)
                    rate_index+=1
                    
                    #30 year US treasury bond
                    connection.request('GET', '/v1/markets/quotes?symbols=TYX', None, headers)
                    response = connection.getresponse()
                    content = response.read()
                    #print('30 year:\t'+str(json.loads(content)['quotes']['quote']['last']/10))
                    rf_rates[rate_index] = treasury_rate(json.loads(content)['quotes']['quote']['last']/10, 30*365)
                    rate_index+=1
                    
                except http.client.HTTPException:
                    # Exception
                    print('Exception during request')
                    
                rate_index = 0
                
                #get price of underlying stock
                connection.request('GET', '/v1/markets/quotes?symbols='+symbol, None, headers)
                try:
                    response = connection.getresponse()
                    content = response.read()
                    #print('underlying ask:\t'+str(json.loads(content)['quotes']['quote']['ask']))
                    #print('underlying bid:\t'+str(json.loads(content)['quotes']['quote']['bid']))
                except http.client.HTTPException:
                    # Exception
                    print('Exception during request')
                #print()
                #print ('v value:\t'+str(volatility))
                #print()
                
                #get expiration dates
                display_header_symbol = tkinter.Label(display_frame,text='symbol')
                display_header_buy_at = tkinter.Label(display_frame,text='buy at')
                display_header_ask = tkinter.Label(display_frame,text='ask')
                display_header_sell_at = tkinter.Label(display_frame,text='sell at')
                display_header_bid = tkinter.Label(display_frame,text='bid')
                display_header_symbol.grid(row=0,column=0)
                display_header_buy_at.grid(row=0,column=1)
                display_header_ask.grid(row=0,column=2)
                display_header_sell_at.grid(row=0,column=3)
                display_header_bid.grid(row=0,column=4)
                row = 1
                for date in expiration_data['expirations']['date']:
                    #print (date+' options:')
                    expiration = datetime.strptime(date , '%Y-%m-%d')
                    now = datetime.today()
                    lifespan = expiration-now
                    t = lifespan.days/365.0
                    #get appropriate risk free rate for this expiration date
                    while(rate_index<len(rf_rates)-1 
                    and lifespan.days > rf_rates[rate_index].duration 
                    and lifespan.days-rf_rates[rate_index].duration > abs(lifespan.days-rf_rates[rate_index+1].duration)):
                        rate_index += 1
                    #print('t value:\t'+str(t))
                    #print('r value:\t'+str(rf_rates[rate_index].rate))
                    connection.request('GET', '/v1/markets/options/chains?symbol='+symbol+'&expiration='+date, None, headers)
                    try:
                        response = connection.getresponse()
                        content = response.read()
                        # Success
                        #print('Response status ' + str(response.status))
                        json_data = json.loads(content)
                        date_symbol = tkinter.Label(display_frame,text=date+' options')
                        date_symbol.grid(row=row,column=0,columnspan=5)
                        row+=1
                        for i in json_data['options']['option']:
                            #create labels for output
                            option_symbol = tkinter.Label(display_frame,text=i['symbol'])
                            option_buy_at = tkinter.Label(display_frame,text='TBD')
                            option_ask = tkinter.Label(display_frame,text=str(round(i['ask'],2)))
                            option_sell_at = tkinter.Label(display_frame,text='TBD')
                            option_bid = tkinter.Label(display_frame,text=str(round(i['bid'],2)))
                            #add labels to layout
                            option_symbol.grid(row=row,column=0)
                            option_buy_at.grid(row=row,column=1)
                            option_ask.grid(row=row,column=2)
                            option_sell_at.grid(row=row,column=3)
                            option_bid.grid(row=row,column=4)
                            row +=1
                            #print ('symbol:\t'+i['symbol']+'\tstrike:\t'+str(i['strike'])+'\task:\t'+str(i['ask'])+'\tbid:\t'+str(i['bid'])+'\n')
                    except http.client.HTTPException:
                        # Exception
                        print('Exception during request')
            else:#symbol is invalid or has no options
                symbol_error_prompt.set('Invalid symbol')
        except http.client.HTTPException:
            # Exception
            print('Exception during request')
entry_button = tkinter.Button(entry_window,text='Generate\nPrices',command=generate_prices,width=25)

#layout
entry_prompt.grid(columnspan=3)
symbol_error.grid(row=1,columnspan=2)
symbol_label.grid(row=2,sticky='E')
volatility_error.grid(row=3,columnspan=2)
volatility_label.grid(row=4,sticky='E')
symbol_entry.grid(row=2,column=1)
volatility_entry.grid(row=4,column=1)
entry_button.grid(row=3,column=2,rowspan=2)
display_frame.grid(row=0,rowspan=9999,column=3)
entry_window.mainloop()