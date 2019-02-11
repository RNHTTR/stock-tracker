'''
Update Google Sheet stock tracker

TODO
    Add percentage gain column. pain in the ass because of indirect formulas.
    This file should not know what TimeSeries is. Refactor to handle that in stock.py
    Handle throttling. Free API only allows 5 requests per miniute.
'''
import argparse
from datetime import datetime
from pprint import pprint

from googlesheetsapi import *
from stock import *


def append_entry(ticker: str, n_shares: int, sheet_id: str, range_name: str, sheets, purchase_date=None):
    '''
    Append an entry to the tracker

    Args:
        ticker: Stock symbol
        n_shares: number of shares purchased
        sheet_id: Google Sheet id
        range_name: range within Google Sheet
        credentials: used to authenticate with Google API
        purchase_date: date on which the stock was purchased
    '''
    # Get stock data
    time_series = TimeSeries(key='6XWA6AS0IP6ABGYC', output_format='pandas')
    intraday = get_stock_data(time_series=time_series, period='intraday', ticker=ticker)
    daily = get_stock_data(time_series=time_series, period='daily', ticker=ticker)
    
    date_format_str_calculate = '%Y-%m-%d'
    date_format_str_sheet = "%m/%d/%Y"

    if not purchase_date:
        purchase_date = datetime.today()
    else:
        print('\nStock price must be updated manually!!\n')
    purchase_price = get_current_stock_price(data=intraday)
    percent_dip = buy_the_fuckin_dip(data=daily, date=purchase_date.strftime(date_format_str_calculate))

    # Dict to track how data is organized in the Google Sheet
    values_dict = {
        'Ticker': ticker,
        '% Dip': percent_dip,
        'Purchase Price': purchase_price,
        '# Shares': n_shares,
        'Current Price': purchase_price,
        'Sell Price': "n/a",
        'Commission': 4.95, # XXX Should this be hard coded?
        'Fees': "",
        'Net Gain': '=if(isnumber(indirect("f"&row())),indirect("f"&row())*indirect("d"&row()) - indirect("c"&row())*indirect("d"&row()) - 2*indirect("g"&row()), indirect("e"&row())*indirect("d"&row()) - indirect("c"&row())*indirect("d"&row()) - 2*indirect("g"&row()))', # NOTE: =IF(ISNUMBER(F6), F6*D6 - C6*D6 - 2*G6, E6*D6 - C6*D6 - 2*G6)
        'Purchase Date': purchase_date.strftime(date_format_str_sheet),
        'Sell Date': 'n/a',
        'Workdays Elapsed': '=if(isdate(INDIRECT("K"&ROW())),NETWORKDAYS(INDIRECT("J"&ROW()),INDIRECT("K"&ROW())), networkdays(INDIRECT("J"&ROW()),today()))', # XXX How to get row number?
        'Total Days Elapsed': '=if(isdate(INDIRECT("K"&ROW())),INDIRECT("K"&ROW())-INDIRECT("J"&ROW()), today()-INDIRECT("J"&ROW()))', # XXX How to get row number?
    }

    # Connect to the Google Gheet
    # sheets = get_spreadsheets(credentials)
    sheet_values = get_spreadsheet_values(sheets)
    value_input_option = 'USER_ENTERED'
    insert_data_option = 'INSERT_ROWS'

    values = list(values_dict.values())

    request_body = {
        'range': range_name,
        'values': [
            values
        ]
    }
    request = sheet_values.append(
        spreadsheetId=sheet_id,
        range=range_name,
        valueInputOption=value_input_option,
        insertDataOption=insert_data_option,
        body=request_body
    )

    # Update Sheet
    response = request.execute()
    pprint(response)


def update_table_with_current_stock_prices(sheets, sheet_id):
    read_range_name = 'Sheet1!A2:A'
    write_range_name = 'Sheet1!E2:E'
    ticker_price_map = {}
    tickers = get_range(spreadsheets=sheets, sheet_id=sheet_id, range_name=read_range_name)
    time_series = TimeSeries(key='6XWA6AS0IP6ABGYC', output_format='pandas')
    failed = []
    for ticker in tickers['values']:
        try:
            data = get_stock_data(time_series=time_series, period='intraday', ticker=ticker)
            ticker_price_map[ticker[0]] = get_current_stock_price(data=data)
        except KeyError:
            failed.append(ticker[0])

    prices = list(ticker_price_map.values())

    values = get_spreadsheet_values(sheets)
    request = values.update(
        spreadsheetId=sheet_id,
        range=write_range_name,
        body={
            'range': write_range_name,
            'values':
                [prices],
            'majorDimension': 'COLUMNS'
        },
        valueInputOption='USER_ENTERED'
    )
    response = request.execute()
    pprint(response)
    if failed:
        print(f'Throttling occured on...\n{failed}')


def main(args):
    sid = '1jk_6MgIPxM0ijm3heWL3AqoJiPXdySJhbRnH7AVhH-U'
    range_name = 'Sheet1!A:M' # XXX For buy only...
    creds = authenticate()
    sheets = get_spreadsheets(creds)

    if args.action == 'buy':
        assert args.ticker, "A ticker must be passed if the selected action is 'buy'"
        assert args.n_shares, "n_shares must be passed if the selected action is 'buy'"
        args.ticker = args.ticker.upper()
        if args.purchase_date:
            date = datetime.strptime(args.purchase_date, '%Y-%m-%d')
        else:
            date = None
        append_entry(
            ticker=args.ticker,
            n_shares=args.n_shares,
            sheet_id=sid,
            range_name=range_name,
            # credentials=creds,
            sheets=sheets,
            purchase_date=date
        )
    elif args.action == 'update':
        update_table_with_current_stock_prices(sheets=sheets, sheet_id=sid)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Stock Tracker Updater')
    parser.add_argument('action', choices=['buy', 'update'], action='store',
                        help='Select an action, buy or update. Buy will append a row to the tracker. Update will refresh the tracker.')
    parser.add_argument('--ticker', action='store',
                        help="Enter the stock symbol")
    parser.add_argument('--n_shares', action='store', type=int,
                        help="Enter the number of shares purchased")
    parser.add_argument('--purchase_date', action='store',
                        help="Enter the purchase date in the form YYYY-mm-dd") # XXX hould we include an atexit to print that the stock price must be updated manually?
    args = parser.parse_args()
    main(args)
