from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import user_passes_test, login_required
from .models import User
from django.contrib import messages
from datetime import datetime, timedelta
from .predictor import getStocks, combine_cur, get_current_price
import json


def about(request):
    return render(request, 'stock_app/about_us.html')

def careers(request):
    return render(request, 'stock_app/careers.html')

def contact(request):
    contxt = {}
    if request.POST:
        contxt = {'showThanks': True}
    return render(request, 'stock_app/contact_us.html', contxt)

def get_stock_suggestions(total_amount, stategy1='ethical', stategy2=None):
    # At least one strategy will be given
    # print('LOLOLOL', stategy1, stategy2)
    x = getStocks(total_amount, stategy1, stategy2)
    if not x:
        return None
    invested_amount = 0
    stocks = []
    for item in x:
        item[2] = round(item[2], 2)
        val = round(item[2]*item[3], 2)
        stocks += [{
            'name': item[1],
            'amount': item[3],
            'price': item[2],
            'value': val
            }]
        invested_amount += val
    residual_amount = total_amount - invested_amount
    return stocks, round(invested_amount, 2), round(residual_amount, 2)


def get_stock_history(stock_tickers, stock_amounts, residual_amount):
    result = combine_cur(stock_tickers, stock_amounts)
    if not result:
        return None
    val, dates = result
    for i in range(len(val)):
        val[i] = round(val[i], 2)
    return val, dates

# def login_error(request):
#     return render(request, 'stock_app/index.html', {})

def signup(request):
    print(request.POST)
    username = request.POST.get('username')
    password =  request.POST.get('password')
    if User.objects.filter(username=username).exists():
        messages.error(request,'User already exists.')
        return redirect('login')
    User.objects.create_user(username=username,password=password)
    messages.error(request,'User created.')
    return redirect('login')
    

# def index(request):
#     return render(request, 'stock_app/index.html', {})

def investment_check(user):
    return user.is_authenticated and user.stocks_selected != ''

@user_passes_test(investment_check, login_url='/stock/select_stock/')
def home(request):
    #if user has selected stocks call view_portfilio()
    #else call select_stock
    # dates = ['today', 'yesterday']
    # for i in range(2, 5):
    #     dates += [datetime.strftime(datetime.now() - timedelta(i), '%Y-%m-%d')]
    user = User.objects.filter(username=request.user.username)[0]
    stocks_selected = eval(user.stocks_selected)
    stock_amounts = eval(user.stock_number)
    result = get_stock_history(stocks_selected, stock_amounts, user.residual_amount)
    if not result:
        return render(request, '500.html')
    values, dates = result
    stocks = []
    curr_prices = get_current_price(stocks_selected)
    if not curr_prices:
        return render(request, '500.html')
    for i in range(len(stocks_selected)):
        stocks += [{
                    'name': stocks_selected[i],
                    'amount': stock_amounts[i],
                    'value': round(curr_prices[stocks_selected[i]] * stock_amounts[i], 2)
                    }]
    return render(request, 'stock_app/home.html', {"username": request.user.username,
                                                    "current_value": values[0],
                                                    "dates": dates[1:],
                                                    "values": values[1:],
                                                    "stocks": stocks,
                                                    "json_stocks": json.dumps(stocks),
                                                    "json_history": json.dumps(values[::-1]),
                                                    "json_dates": json.dumps(dates[::-1]) })


@login_required
def select_stock(request):
    return render(request, 'stock_app/select_stock.html', {"username":request.user.username})

@login_required
def confirm_stock(request):
    prim_strategy = request.POST.get('primary')
    sec_strategy = request.POST.get('secondary')
    if sec_strategy == 'None' or sec_strategy == prim_strategy:
        sec_strategy = None
    amount = float(request.POST.get('amount'))
    print(prim_strategy, sec_strategy, amount)
    result = get_stock_suggestions(amount, prim_strategy, sec_strategy)
    if not result:
        return render(request, '500.html')
    stocks, invested_amount, residual_amount = result
    return render(request, 'stock_app/confirm_stock.html', {"username":request.user.username, 
                                                            "stocks":stocks, 
                                                            'invested_amount': invested_amount, 
                                                            'residual_amount': residual_amount})

@login_required
def commit_stock(request):
    stocks = eval(request.POST.get('stocks'))
    stocks_selected = []
    stock_number = []
    amount_invested = request.POST.get('invested_amount')
    # print(stocks, amount_invested)
    for stock in stocks:
        stocks_selected += [stock['name']]
        stock_number += [stock['amount']]
   
    User.objects.filter(username=request.user.username).update(stocks_selected=stocks_selected,stock_number=stock_number, amount_invested=amount_invested)
    return redirect('home')
