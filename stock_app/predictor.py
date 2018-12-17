
# coding: utf-8

# In[1]:


import requests
import datetime


# In[2]:


class InvestmentPortfolio:
    def __init__(self, tickers, shares):
        self.tickers = tickers
        self.number_of_shares = shares


# In[3]:


def printResults(s):
    if s is not None:
        print("Stocks suggested for you: ", s.tickers)
        print("Corresponding shares for each stock: ", s.number_of_shares)
    else:
        print("Please try again.")


# In[4]:


def get_current_price(stock_symbols):
    cur_prices = None
    symbols_string = ','.join(stock_symbols)
    try:
        req = requests.get('https://api.iextrading.com/1.0/stock/market/batch?symbols=' + symbols_string + '&types=quote,news,chart&range=1m&last=5')
    except:
        return None
    
    if req.status_code == 200:
        req_dict =  req.json()
        cur_prices = {}

        for s in stock_symbols:
            cur_prices[s] = req_dict[s]['quote']['latestPrice']
    else:
        print('Status code: ' + str(req.status_code) + ', ' + req.text)
        
    return cur_prices
        
# In[5]:


def get_monthly_low_high(stock_symbol):
    low, high = None, None
    try: 
        req = requests.get('https://api.iextrading.com/1.0/stock/' + stock_symbol + '/stats')
    except:
        return None, None
    
    if req.status_code == 200:
        req_dict =  req.json()
        low = req_dict['week52low']
        high = req_dict['week52high']
    else:
        print('Status code: ' + str(req.status_code) + ', ' + req.text)
        
    return low, high


# In[6]:


def get_5_previous_days(stock_symbol):
    res = None
    date_res = None
    
    today = datetime.datetime.now()
#     today = datetime.datetime.now() + datetime.timedelta(days=2)

    try:
        req = requests.get('https://api.iextrading.com/1.0/stock/'+ stock_symbol +'/chart/1m')
    except:
        return None, None
    
    if req.status_code == 200:
        req_dict =  req.json()
        res = {}
        date_res = []
        dates = {}
        for i in req_dict:
            dates[i['date']] = i['close']
        
        count = 0
        day = today
        
        while count < 5:
            day = day - datetime.timedelta(days=1)
            day_str = day.strftime("%Y-%m-%d")
            if day_str in dates:
                res[day_str] = dates[day_str]
                date_res.append(day_str)
                count += 1
    else:
        print('Status code: ' + str(req.status_code) + ', ' + req.text)
        
    return res, date_res

# res, ress = get_5_previous_days('AAPL')
# print(res)

def get_5_prev_val(stock_names, num_shares, cash=0):
    hist_vals = []
    dates = None
    total_vals = []

    for i in stock_names:
        res, dates = get_5_previous_days(i)
        if res == None: return None, None
        hist_vals.append(res)
    
    for i in range(len(dates)):
        total_val = 0
        for j in range(len(hist_vals)):
            total_val += hist_vals[j][dates[i]] * num_shares[j]
        total_vals.append(total_val+cash)
    
    return total_vals, dates
        
def get_cur_value(stock_names, num_shares, cash=0):
    cur_prices = get_current_price(stock_names)
    if cur_prices == None: return None, None
    total_val = 0
    
    for i in range(len(num_shares)):
        total_val += cur_prices[stock_names[i]] * num_shares[i]
    return total_val + cash, datetime.datetime.now().strftime("%Y-%m-%d")

def combine_cur(stock_names, num_shares):

    prev_vals, dates = get_5_prev_val(stock_names, num_shares)
    if prev_vals == None: return None
    cur_val, date = get_cur_value(stock_names, num_shares)
    if cur_val == None: return None
    prev_vals.insert(0, cur_val)
    dates.insert(0, date)
    return prev_vals, dates

# prev_vals, dates = combine_cur(['AAPL', 'FB', 'MDB'], [1,2,3])
# print(prev_vals)
# print(dates)


# In[7]:


def distribute(money, stocks_list):
    date = '2018-12-14'
    #stock_name = 'MSFT'
    percent = []
    cur_prices = get_current_price(stocks_list)
    if cur_prices == None: return None
    
    for stock_name in stocks_list:
        print(stock_name)
        low = 100
        high = 200
        low, high = get_monthly_low_high(stock_name)

        current = cur_prices[stock_name]
        print('l,h', low, high)
        print('c', current)
        if current<low and low!=0:
            percent.append([(low-current)/low+1.00,stock_name, current])
        elif current > high:
            print('price too high')
            percent.append([0.01, stock_name, current])
        else:
            print('l,h,c', low, high, current)
            range_ = high-low
            if range_== 0:
                range_ = 1
            loc = (current-low)/range_
            percent.append([-1* loc +1.00, stock_name, current]) 

    #percent.sort( reverse=True)
    percent.sort()
        
    sum_= 0.00
    for p in percent:
        print('p',p[0])
        sum_+= p[0]
    print('sum', sum_)
    if sum_ <=0:
        sum_ = 1
    for p in percent:
        p[0]= p[0]/sum_
    print('new p', percent)
       
    for p in percent:
        
        print('money, price',money, p[2])
        share = int(money*p[0]/p[2])
        print('money, price, share',money, p[2], share)

        p.append(share)
    
    print ('final', percent)
    
    val =0
    for p in percent:
        val+=p[2]*p[3]
    print('val', val)
    return percent


# In[8]:


# distribute(50000, ['AAPL','GOOG'])
#distribute(50000, ['MSFT','TWLO','GOOG','A','FB','AMZN'])


# In[9]:


def get_recommendations(strategy):
    dic=[]
    
    if strategy == 'ethical':  
        print(1)
        dic.append('AAPL')
        dic.append('ADBE')
        dic.append('VOO')
    elif strategy == 'growth':  
        print(2)  
        dic.append('JPM')
        dic.append('BAC')
        dic.append('WFC')
    elif strategy == 'index':
        print(3)
        dic.append('GRPN')
        dic.append('WMT')
        dic.append('AMD')
    elif strategy == 'quality':
        print(4)
        dic.append('GOOGL')
        dic.append('AMZN')
        dic.append('MSFT')

    elif strategy == 'value':
        print(5)
        dic.append('TWLO')
        dic.append('NVDA')
        dic.append('MDB')
    
    return dic    


# In[10]:


def input_validation(lower_case_strategies, investment_amount, strategy1, strategy2=None):
    #input validation
    
    #Minimum is $5000 USD
    if(investment_amount<5000.00):
        error = "Error: Minimum investment amount is $5000 USD. You entered: $"+str(investment_amount)+" USD."
        print(error)
        return False, []
    strategy_list = [] #lower cased strategies
    if strategy1 is not None:
        lower_case_strategy1 = strategy1.lower()
        strategy_list.append(lower_case_strategy1)
    if strategy2 is not None:
        lower_case_strategy2 = strategy2.lower()
        strategy_list.append(lower_case_strategy2)
    error1 = "Error: Strategy must be one of the following: "+ str(lower_case_strategies) 
    error2 = "You entered: "
    flag = False
    if strategy1 is not None and lower_case_strategy1 not in lower_case_strategies:
        error2 += '\''+ strategy1 + '\''
        flag = True
    if strategy2 is not None and lower_case_strategy2 not in lower_case_strategies:
        if flag:
            error2 += ' and '
        error2 += '\''+strategy2 + '\''
        flag = True
    if flag:
        print(error1)
        print(error2)
    return flag, strategy_list


# In[11]:


def getStocks(investment_amount=5000.00, strategy1='Ethical', strategy2=None):
    
    
    #Strategies need to be 'Ethical', 'Growth', 'Index', 'Quality' or 'Value'
    strategies = ['Ethical', 'Growth', 'Index', 'Quality', 'Value' ]
    lower_case_strategies = [s.lower() for s in strategies]
    
    
     #input validation
    invalid, strategy_list = input_validation(lower_case_strategies, investment_amount, strategy1, strategy2)
    if invalid or not strategy_list:
        return
        
    shares=[]
    #tickers = ['TICK', 'SYM', 'BOLS']
    #shares = [10, 20, 30]
    stocks= []
    for strategy in strategy_list:
        stocks.extend(get_recommendations(strategy))
        print(stocks)
        
   
    results = distribute(investment_amount, stocks)
    if results == None: return None
    print('here', results);        
    
    #return(InvestmentPortfolio(stocks, shares))
    return results


# In[12]:


# def get_current_price(stock_symbols):
#     cur_prices = {}
#     symbols_string = ','.join(stock_symbols)
#     req = requests.get('https://api.iextrading.com/1.0/stock/market/batch?symbols=' + symbols_string + '&types=quote,news,chart&range=1m&last=5')
#     if req is not None:
#         req_dict =  req.json()
#         for s in stock_symbols:
#             cur_prices[s] = req_dict[s]['quote']['latestPrice']
    
#     else:
#         print("API access error, please try again later")
        
#     return cur_prices


# In[13]:


# def get_portfolio_value(stock_names, num_shares, cash=0):
#     cur_prices = get_current_price(stock_names)
#     total_val = 0
    
#     print(cur_prices)
#     for i in range(len(num_shares)):
#         total_val += cur_prices[stock_names[i]] * num_shares[i]
#     return total_val + cash

#val = get_portfolio_value(['AAPL', 'FB', 'MDB'], [1,2,3])
#print(val)


# In[15]:


#getStocks(10000, 'ethical', 'growth')


