import pandas as pd
import yfinance as yf
import datetime as dt
import pprint
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import plotly.offline as pyo
import plotly.graph_objs as go
import plotly.express as px



def get_data_by_date(stock_code):
    """Gets data using start date and end date"""

    d = yf.Ticker(stock_code)

    df = d.history(period='3y')

    df['Date'] = df.index
    df['Date'] = df['Date'].dt.date
    df['Change'] = (df['Close'].diff())
    df['% Change'] = (df['Close'].pct_change() * 100)

    df = df.reindex(index=df.index[::-1])
    return d.info, df

def get_current_data(stock_code):
    """Gets the most current data"""

    d = yf.Ticker(stock_code)

    df = d.history(period = '1d')
    df['Date'] = df.index
    df['Change'] = (df['Close'].diff())
    df['% Change'] = (df['Close'].pct_change() * 100)

    return df

def RSI_calc(st_name):
    # Calculating RSI
    # Formula 100 - [100 / 1 + (Avg Gain/Avg Loss)]
    # Default Look back period 30 days

    dd = yf.Ticker(st_name)
        
    df1 = dd.history(period='30d')
    change = df1['Close'].diff().dropna()

    gain = change.apply(lambda x : x if x > 0 else 0)
    index_names = gain[ gain == 0 ].index
    gain.drop(index_names, inplace = True)

    loss = change.apply(lambda x : x if x < 0 else 0)
    index_names1 = loss[ loss == 0 ].index
    loss.drop(index_names1, inplace = True)
    loss = loss.abs()

    avg_gain = gain.mean()
    avg_loss = loss.mean()

    avg_g_l = 1 + (avg_gain/avg_loss)
    RSI = 100 - (100 / avg_g_l) 

    return RSI

def SMA_cal(st_name):
    """SMA indicator calculation"""

    dd = yf.Ticker(st_name)
        
    df1 = dd.history(period='30d')
    sma = df1.Close.mean()

    return sma

# def MACD_calc(st_name):

#     dd = yf.Ticker(st_name)
        
#     df1 = dd.history(period='30d')

#     exp1 = df1.Close.ewm(span=12, adjust=False).mean()
#     exp2 = df1.Close.ewm(span=26, adjust=False).mean()
#     macd = exp1 - exp2
#     # macd is pandas series
#     return macd

def MACD_NACDline(st_name):
    """MACD PLOT"""

    dd = yf.Ticker(st_name)
        
    df1 = dd.history(period='1y')

    exp1 = df1.Close.ewm(span=12, adjust=False).mean()
    exp2 = df1.Close.ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2

    exp3 = macd.ewm(span=9, adjust=False).mean()

    trace0 = go.Scatter(
    x = macd.index,
    y = macd,
    mode = 'lines',
    name = 'MACD Line' 
    )

    trace1 = go.Scatter(
    x = exp3.index,
    y = exp3,
    mode = 'lines',
    name = 'MACD Signal Line' 
    )

    data  = [trace0, trace1]
    layout = go.Layout(title=f"MACD Chart for {st_name.upper()}")

    fig = go.Figure(data=data, layout=layout)

    fig.write_html("./templates/plots/macd.html")


def Stock_Line(st_name):
    """LINE PLOT"""

    dd = yf.Ticker(st_name)
        
    df1 = dd.history(period='1y')

    trace0 = go.Scatter(
        x = df1.index,
        y = df1.Close,
        mode = 'lines',
        name = 'Stock Line Chart' 
    )

    data  = [trace0]
    layout = go.Layout(title=f"Line Chart for {st_name.upper()}")

    fig = go.Figure(data=data, layout=layout)
    fig.update_layout(xaxis_range=[df1.index.min(),df1.index.max()])

    fig.update_layout(
            xaxis=dict(
                rangeselector=dict(
                    buttons=list([
                        dict(count=1,
                            step="day",
                            stepmode="backward"),
                    ])
                ),
                rangeslider=dict(
                    visible=True
                ),
            )
    )

    fig.write_html("./templates/plots/line.html")


def Stock_Candel(st_name):
    """CANDLE PLOT"""

    dd = yf.Ticker(st_name)
        
    df1 = dd.history(period='1y')



    fig = go.Figure( data=[
                            go.Candlestick(
                            x = df1.index,
                            low = df1['Low'],
                            high = df1['High'],
                            open = df1['Open'],
                            close = df1['Close'],
                            increasing_line_color = 'green',
                            decreasing_line_color = 'red'
                            )
                        ]
                    )
    fig.update_layout(xaxis_range=[df1.index.min(),df1.index.max()])
    
    return fig

def set_val(ro):
  if ro['diff'] > 0 and ro['shift'] < 0:
    return 1
  if ro['diff'] < 0 and ro['shift'] > 0:
    return -1
  return 0

def buy_sell(st_name):
    """BUY/SELL RECOMMEDATION"""

    dd = yf.Ticker(st_name)
        
    df1 = dd.history(period='6mo')

    exp1 = df1.Close.ewm(span=12, adjust=False).mean()
    exp2 = df1.Close.ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2

    exp3 = macd.ewm(span=9, adjust=False).mean() 

    macd_diff = macd - exp3

    newX = pd.DataFrame()
    newX['diff'] = macd_diff
    newX['shift'] = macd_diff.shift(-1)
    newX['buy/sell'] = 0
        # newX
        # newX['buy/sell'] = newX.apply(lambda x : 1 if (x['diff'] > 0 and x['shift'] < 0) else -1 )
    newX['buy/sell'] = newX.apply(lambda ro : set_val(ro), axis=1)

    buy = newX[newX['buy/sell'] == 1].shape[0]
    sell = newX[newX['buy/sell'] == -1].shape[0]


    rsi = RSI_calc(st_name)

    # get MACD_diff
    if (rsi <= 30 or rsi >= 70):
        if (rsi <= 30):
            return('Oversold', buy, sell) 
        elif (rsi <= 35):
            return('Buy', buy, sell)
        elif (rsi >= 70):
            print('Overbought', buy, sell)
        elif (rsi >= 65):
            return('Sell', buy, sell)

    else:
        if (buy > sell):
            return('Buy', buy, sell)
        else:
            return('Sell', buy, sell)
