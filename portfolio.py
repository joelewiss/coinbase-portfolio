"""
COINBASE Portfolio Viewer
Joe Lewis 2020
MIT Licence
"""

import time
import sys
import json
import colorama as cr
from requests import get
from terminaltables import SingleTable



"""
positions dictionary
{
    symbol: "ETH",
    price:  608.77,
    qty:    0.0788641,
    fee:    1.99,
}
"""
def read_positions():
    try:
        f = open("positions.json", "r")
    except OSError:
        print("Could not open positions.json file, exiting now")
        sys.exit(1)

    
    pos = json.load(f)
    f.close()
    return pos



"""
Retreives price data for symbols, limiting duplicate requests
pos     (dict)      Positions dictionary


returns (dict       Dictionary with prices in the following format
                    { "symbol": priceNow, ... }
"""
def get_prices(pos):
    prices = dict()
    
    for p in pos:
        symb = p["symbol"]
        if symb not in prices:
            url = "https://api.coinbase.com/v2/prices/{}-USD/spot".format(symb)
            res = get(url)

            if (res.status_code == 200):
                json = res.json()
                prices[symb] = float(json["data"]["amount"])
            else:
                print(f"Could not retrieve price data for {symb}")
                print(f"Got status code {res.status_code} from API")
                print("Stoping program now")
                sys.exit(1)

    return prices

"""
Prints out entire portfolio to stdout in a fancy table with colors
pos     (dict)      Positions dictionary
clear   (bool)      Determines if terminal is cleared and table is printed at
                    1,1


Symbol,Last Price $,Change $,Change %,Qty,Price Paid,Day's Gain,Total Gain $,Total Gain %
"""
def print_portfolio(pos, clear=False):
    table = [["Symbol", "Last Price ($)", "Change ($)", "Change (%)", "Qty", 
        "Price Paid ($)", "Total Gain ($)", "Total Gain (%)"]]
    prices = get_prices(pos)

    # Keep track of useful totals
    tpricep = 0
    tgain = 0

    for p in pos:
        # Construct table row by row
        row = []
        # Convience variable
        symb = p["symbol"]

        # Symbol
        row.append(symb)

        # Last price
        if (prices[symb] < 10):
            row.append("{:,.4f}".format(prices[symb]))
        else:
            row.append("{:,.2f}".format(prices[symb]))

        # Change $
        chgd = prices[symb] - p["price"]
        if (chgd < 0):
            color = cr.Fore.RED
        else:
            color = cr.Fore.GREEN

        if (abs(chgd) < 10):
            chgd = "{}{:,.4f}".format(color, chgd)
        else:
            chgd = "{}{:,.2f}".format(color, chgd)

        chgd += cr.Fore.RESET
        row.append(chgd)

        # Change %
        chgp = (prices[symb] - p["price"]) / p["price"]
        row.append("{:+.2%}".format(chgp))

        # Qty
        row.append(p["qty"])

        # Price Paid
        ppaid = (p["price"] * p["qty"]) + p["fee"]
        row.append("{:,.2f}".format(ppaid))
        tpricep += ppaid

        # Total Gain $
        tgd = (prices[symb] - p["price"]) * p["qty"]
        tgd -= p["fee"]
        if (tgd < 0):
            color = cr.Fore.RED
        else:
            color = cr.Fore.GREEN

        if (abs(tgd) < 10):
            row.append("{}{:,.4f}{}".format(color, tgd, cr.Fore.RESET))
        else:
            row.append("{}{:,.2f}{}".format(color, tgd, cr.Fore.RESET))

        tgain += tgd

        # Total Gain %
        tgp = tgd / (p["price"] * p["qty"])
        row.append("{:+.2%}".format(tgp))


        table.append(row) 

    
    # Add in useful totals
    totals = [""] * 8
    totals[0] = "TOTAL"
    # Total price paid is col 5
    totals[5] = "{:,.2f}".format(tpricep)
    # Total gain is col 6
    totals[6] = "{:,.2f}".format(tgain)
    # Calculate gain percentage
    gain = tgain / tpricep
    totals[7] = "{:+.2%}".format(gain)
    table.append(totals)


    if clear:
        # Clear screen using colorama helper functions
        print(cr.ansi.clear_screen())
        # Position at top of screen 
        print(cr.Cursor.POS(1, 1))

    # Print table
    stbl = SingleTable(table, title="Portfolio")
    stbl.inner_footing_row_border = True
    print(stbl.table)

    # Print portfolio value
    tvalue = 0
    for p in pos:
        symb = p["symbol"]
        tvalue += prices[symb] * p["qty"]

    print(f"{cr.Style.BRIGHT}TOTAL PORTFOLIO VALUE: {tvalue:,.2f}" + 
          f"{cr.Style.RESET_ALL}")


    print(time.strftime("%I:%M %p"))



if __name__ == "__main__":
    pos = read_positions()
    cr.init()
    print_portfolio(pos)

