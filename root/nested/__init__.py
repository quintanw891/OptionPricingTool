import tkinter
import http.client
import json
from tkinter.constants import LEFT
from tkinter import StringVar

entry_window = tkinter.Tk()
entry_window.title('Option Pricing Tool')

#widgets
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
            if expiration_data['expirations']:
                symbol_error_prompt.set('')
                volatility_error_prompt.set('')
                display_window = tkinter.Toplevel(entry_window)
                display_window.title(symbol.upper()+' Option Pricings')
                for d in expiration_data['expirations']['date']:
                    print (d)
                for date in expiration_data['expirations']['date']:
                    #print (date+' options:')
                    connection.request('GET', '/v1/markets/options/chains?symbol='+symbol+'&expiration='+date, None, headers)
                    try:
                      response = connection.getresponse()
                      content = response.read()
                      # Success
                      #print('Response status ' + str(response.status))
                      json_data = json.loads(content)
                      for i in json_data['options']['option']:
                          print ('symbol:\t'+i['symbol']+'\tstrike:\t'+str(i['strike'])+'\texpires:\t'+i['expiration_date']+'\tunderlying:\tasking:\t'+str(i['ask']))
                    except http.client.HTTPException:
                      # Exception
                      print('Exception during request')
            else:
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
entry_button.grid(row=3,column=2,columnspan=2)
entry_window.mainloop()