import pandas_datareader.data as web
import datetime
import matplotlib.pyplot as plt
from zipline.api import order_target, record, symbol, order
from zipline.algorithm import TradingAlgorithm

# Zipline은  a Pythonic Algorithmic Trading Library 으로  알고리즘을 back test 해서
# 알고리즘을 확인해 볼 수 있다.

# zipline은 pandas=0.18.1 과 잘 어울린다. 만일 pandas > 0.18.1 이면 downgrade한다.
# 현재의 zipline=1.1.1 이다.

# TradingAlgorithm 을 수행할 때, C:\Users\jaehyek\.zipline\data\SPY_benchmark.csv 을 참조한다.
# 위 csv file을 기준으로 2016-09-26 부터 가능하다. 이전의 날짜는 index가 없다고 한다.
# zipline=1.1.1 의 버그로 보인다.  upgrade된 version을 확인해 본다. 훗날.
# https://github.com/quantopian/zipline
# http://www.zipline.io/


start = datetime.datetime(2016, 9, 26)
end = datetime.datetime(2017, 9, 19)
data = web.DataReader("078930.KS", "yahoo", start, end)

data = data[['Adj Close']]
data.columns =  ['GS']
data = data.tz_localize('UTC')


# 거래 수수료를 설정하기 위해서는 set_comminsion 메서드를 initialize 메서드에서 호출하면 됩니다
# PerTrade는 거래를 할 때 거래 금액과는 상관없이 일정 수수료를 지급하는 모델
# PerShare는 주당 정해진 금액의 수수료를 지급하는 모델
# PerDollar는 달러당 일정 수수료를 내는 모델

# 유가증권시장/코스닥시장에서는 주식을 매수할 때는 세금을 내지 않지만 매도 시에는 매도 금액의 0.3%에 해당하는 금액인 주식거래세
# 추가로 약 0.015% 정도의 증권사 수수료가 매수와 매도 시점에서 모두 발생
# zipline에서 코스피/코스닥 시장과 정확히 일치하는 수수료 모델을 만들기는 어렵지만 총 0.33%의 부대 비용이 발생하는 것을
# 매수/매도 시점에 나눠서 0.165%씩 설정하면 그나마 비슷하게 설정할 수 있습니다

from zipline.api import set_commission, commission
def initialize(context):
    # PerDollar는 원래는 달러를 기준으로 수수료를 설정하는 것이지만 우리는 원 단위로 생각하면 되기 때문에
    set_commission(commission.PerDollar(cost=0.00165))
    context.i = 0
    context.sym = symbol('GS')
    context.hold = False

def handle_data(context, data):
    context.i += 1
    if context.i < 20:
        return

    buy = False
    sell = False

    ma5 = data.history(context.sym, 'price', 5, '1d').mean()
    ma20 = data.history(context.sym, 'price', 20, '1d').mean()

    if ma5 > ma20 and context.hold == False:
        order_target(context.sym, 100)
        context.hold = True
        buy = True
    elif ma5 < ma20 and context.hold == True:
        order_target(context.sym, -100)
        context.hold = False
        sell = True

    record(GS=data.current(context.sym, "price"), ma5=ma5, ma20=ma20, buy=buy, sell=sell)

algo = TradingAlgorithm( initialize=initialize, handle_data=handle_data )
result = algo.run(data)
plt.plot(result.index, result.GS)
plt.plot(result.index, result.ma5)
plt.plot(result.index, result.ma20)
plt.legend(loc='best')

plt.plot(result.ix[result.buy == True].index, result.ix[result.buy == True]["ma5"], '^')
plt.plot(result.ix[result.sell == True].index, result.ix[result.sell == True]["ma5"], 'v')

plt.show()

