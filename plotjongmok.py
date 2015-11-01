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
    # dateformatter = DateFormatter('%Y-%m-%d')

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

    # format the coords message box
    ax1.format_xdata = DateFormatter('%Y-%m-%d')
    ax2.format_xdata = DateFormatter('%Y-%m-%d')

    # ax.xaxis.grid(True, 'major')
    fig.autofmt_xdate()
    # plt.title(jongmokname)
    plt.show()

def plotHistogram(listlistvalue, listtitle):
    '''
    value들의 list 혹은 listlist 을 입력으로 해서, histogram을 그린다.
    historgram은 normalize을 하고, color을 입힌다.
    :param listlistvalue:
    :param listtitle: 각 value의 list들의 title 제목이다.
    :return: 없음.
    '''
    num_bins = 50
    listcolor = ["blue", "green", "red", "cyan", "magenta","yellow","black" ]
    if len(listcolor) < len(listlistvalue) :
        print("list lengths are too many comparing to color list")
        return

    lenlist = len(listlistvalue)
    n, bins, patches = plt.hist(listlistvalue, num_bins, normed=1,histtype ="bar",  color=listcolor[:lenlist],label=listtitle, alpha=0.7)
    plt.ylabel('Probability')
    plttitle = "Histogram of "
    idx = 0
    for title in listtitle :
        plttitle += "%s : %s, " %(title, listcolor[idx])
        idx += 1
    plt.title(plttitle)

    # Tweak spacing to prevent clipping of ylabel
    plt.subplots_adjust(left=0.2)
    plt.show()