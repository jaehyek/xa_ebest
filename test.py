from __future__ import print_function

import login
from XAUtil import *
import pymongo
import os
import XATrends
import XAQuery



if __name__ == "__main__":
    # if login.login() == False :
    #     print("login failed")
    #     exit()

    # XATrends.plotchart("LG전자")
    # XATrends.plotchart("LG화학")
    # XATrends.plotchart("삼성전자")
    # XATrends.createHistorgramOfPERPBRByMarket()
    XATrends.createHistogramOfJongmok("삼성전자")
    pass


