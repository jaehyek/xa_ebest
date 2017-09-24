import pandas_datareader.data as web
import datetime
import matplotlib.pyplot as plt
from zipline.api import order_target, record, symbol, order
from zipline.algorithm import TradingAlgorithm

# Zipline은  a Pythonic Algorithmic Trading Library 으로  알고리즘을 back tracing 해서
# 알고리즘을 확인해 볼 수 있다.

# zipline은 pandas=0.18.1 과 잘 어울린다. 만일 pandas > 0.18.1 이면 downgrade한다.
# 현재의 zipline=1.1.1 이다.

# TradingAlgorithm 을 수행할 때, C:\Users\jaehyek\.zipline\data\SPY_benchmark.csv 을 참조한다.
# 위 csv file을 기준으로 2016-09-26 부터 가능하다. 이전의 날짜는 index가 없다고 한다.
# zipline=1.1.1 의 버그로 보인다.  upgrade된 version을 확인해 본다. 훗날.
# https://github.com/quantopian/zipline


start = datetime.datetime(2016, 9, 26)
end = datetime.datetime(2017, 3, 19)
data = web.DataReader("AAPL", "yahoo", start, end)

data = data[['Adj Close']]
data.columns = ['AAPL']
data = data.tz_localize('UTC')
def initialize(context):
    context.i = 0
    context.sym = symbol('AAPL')

def handle_data(context, data):
    context.i += 1
    if context.i < 20:
        return

    ma5 = data.history(context.sym, 'price', 5, '1d').mean()
    ma20 = data.history(context.sym, 'price', 20, '1d').mean()

    if ma5 > ma20:
        order_target(context.sym, 1)
    else:
        order_target(context.sym, -1)

    record(AAPL=data.current(context.sym, "price"), ma5=ma5, ma20=ma20)

algo = TradingAlgorithm(initialize=initialize, handle_data=handle_data)
result = algo.run(data)
result[["ma5", "ma20"]].plot()
plt.show()

