'''
Various functions to utilize Alpha Vantage API stock data

TODO: Refactor to instantiate time_series objects in this file
NOTE: Throttling occurs sometimes when calling alpha vantage api
'''
# from datetime import datetime

# import pandas as pd
from alpha_vantage.timeseries import TimeSeries


def get_stock_data(time_series: object, period: str, ticker: str): # TODO: Refactor to instantiate time_series objects in this file
    '''
    Get data for a given stock ticker

    Args:
        time_series: Alpha Vantage TimeSeries class
        ticker:      Stock symbol
    
    Returns:
        data: Pandas DF with stock data
    '''
    if period == 'intraday':
        data, meta_data = time_series.get_intraday(symbol=ticker, interval='1min', outputsize='compact')
    elif period == 'daily':
        data, meta_data = time_series.get_daily(symbol=ticker, outputsize='compact')
    return data


def get_current_stock_price(data: object):
    '''
    Get the current stock price from an alpha_vantage Pandas DF

    Args:
        data (pandas.DataFrame): Pandas DF containing data on a given stock

    Returns:
        (int): Current price of the given stock
    '''
    return data.tail(1)['4. close'][0]


def buy_the_fuckin_dip(data: object, date: str):
    '''
    Find how much the stock decreased from period t-1 to period t
    '''
    index = data.index.get_loc(date)
    return 100 * (data.iloc[index-1]['4. close'] / data.iloc[index]['4. close'] - 1) # Stock price day before purchase divided by price day of purchase


# if __name__ == '__main__':
    # TODO: Implement option to update current price in Google SHeet (Separate file)
    # TODO: Implement functionality to update Google Sheet
    # TODO: Implement option for updating sheet when selling
    # date = datetime.today().strftime("%m/%d/%Y")
    # time_series = TimeSeries(key='6XWA6AS0IP6ABGYC', output_format='pandas')
    # ticker = input("\nEnter the purchased stock's symbol\n")
    # n_shares = input("\nEnter the number of shares purchased\n")
    # data = get_stock_data(time_series=time_series, ticker=ticker)
    # percent_dip = 'tbd' # TODO
    # purchase_price = get_current_stock_price(data=data)

    # print('\ndate:', date)
    # print('ticker:', ticker)
    # print('n_shares:', n_shares)
    # print('% dip:', percent_dip)
    # print('purchase price:', purchase_price)