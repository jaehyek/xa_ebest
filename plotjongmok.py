__author__ = '최재혁'


import matplotlib.pyplot as plt
from matplotlib.dates import MONDAY
from matplotlib.dates import date2num, MonthLocator, WeekdayLocator, DateFormatter, AutoDateFormatter
from matplotlib.widgets import Cursor
from datetime import datetime

def plotjongmok(jongmokname, listdatestr, listprice, listdealquantity) :

    # first, convert listdatestr to floating date number.
    # 20150321 --> 735678.0
    listnum = [ date2num(datetime(int(aa/10000), int((aa%10000)/100), aa%100 )) for aa in listdatestr]

    datemax = max(listnum)
    datemin = min(listnum)

    pricemax = max(listprice)
    pricemin = min(listprice)

    fig, (ax1, ax2) = plt.subplots(2,1)
    locatorMon = MonthLocator(range(1, 13), bymonthday=1, interval=1)
    locatorday = WeekdayLocator(MONDAY)

    ax1.plot_date(listnum, listprice, '-')

    ax1.xaxis.set_major_locator(locatorMon)
    ax1.xaxis.set_major_formatter(AutoDateFormatter(locatorMon))
    ax1.xaxis.set_minor_locator(locatorday)
    ax1.set_title('closed price')
    cursor = Cursor(ax1, useblit=True, color='red', linewidth=1 )

    ax2.plot_date(listnum, listdealquantity, '.')
    ax2.vlines(listnum, [0],listdealquantity )
    # ax2.bar(listnum, listdealquantity)
    ax2.xaxis.set_major_locator(locatorMon)
    ax2.xaxis.set_major_formatter(AutoDateFormatter(locatorMon))
    ax2.xaxis.set_minor_locator(locatorday)
    ax2.set_title('deal amount')
    cursor = Cursor(ax2, useblit=True, color='red', linewidth=1 )

    # ax.xaxis.grid(True, 'major')
    fig.autofmt_xdate()
    # plt.title(jongmokname)


    plt.show()

