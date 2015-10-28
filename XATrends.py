__author__ = '최재혁'

from XAUtil import *
import jongmokgroup
import plotjongmok

def saveJongMokGroupProfitTrends(filename,dictJongMokGroup, BaseDate, listAfterDates ):
    basedate = DateStrformat(BaseDate)
    listDateStr = [ basedate.getDateStr_nDay( aa) for aa in listAfterDates ]
    listlistRatioMeans = []
    for keyJongMokGroup in dictJongMokGroup :
        print("--- JongMokGroup : %s  ----------------------------------------------------------"%(keyJongMokGroup))


        listdict종가fromJongmokDate = get종가fromListJongmokListday(dictJongMokGroup[keyJongMokGroup], listDateStr)
        # saveListDictToCSV("종목가격0.csv", ["종목명"]+listDateStr, listdict종가fJongmokDate)
        # exit()
        if len(listdict종가fromJongmokDate) == 0 :
            print("??? No 종가 정보 --> skip ")
            continue
        listProportMeans = getProfieLossProportionBasedOnStartDate(listDateStr,listdict종가fromJongmokDate )
        listlistRatioMeans.append([keyJongMokGroup] + listProportMeans)

    saveListListToCSV(filename, ["종목그룹이름"] + listAfterDates[1:], listlistRatioMeans  )

def createJongMokProfitTrends():
    dictJongMokGroup = jongmokgroup.dictJongMokGroup
    listAfterDates = [ 0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 360, 390, 420, 450, 480, 510, 540, 570, 600, 630, 660, 690]
    BaseDate = 20131015
    filename = "매수후기간별손익증감_구성종목.csv"
    saveJongMokGroupProfitTrends(filename, dictJongMokGroup, BaseDate, listAfterDates)


def createJongMokMatchingPBRPER():
    '''
    PBR이 이하, PER가 7이하인 종목들에 대해 20131015을 기준으로  2년간 이익률을 계산.
    :return:
    '''

    listAfterDates = [ 0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 360, 390, 420, 450, 480, 510, 540, 570, 600, 630, 660, 690]
    BaseDate = 20131015

    listJongmokHan = getJongMokMatchingPBRPER(1.0, 7.0)
    #한 좀목으로 group을 만들어 list으로 담는다.
    dictJongMokGroup = {}
    for JongmokHan in listJongmokHan :
        dictJongMokGroup.update({JongmokHan:[JongmokHan]})

    filename = "매수후기간별손익증감_PBRPER.csv"
    saveJongMokGroupProfitTrends(filename, dictJongMokGroup, BaseDate, listAfterDates)

def plotchart(jongmokname) :
    coll주식종목Data = pymongo.MongoClient('localhost', 27017).get_database("xadb").get_collection("주식종목Data")
    dictcondi = {'종목명':jongmokname }
    dictproj = {"주식차트_일주월.날짜":1, "주식차트_일주월.종가":1, "주식차트_일주월.거래량":1, "_id":0}
    objret = coll주식종목Data.find_one(dictcondi, dictproj)

    listdictdatestrprice = objret["주식차트_일주월"]
    listdatestr = []
    listprice = []
    listdealquantity = []
    for dictdatestrprice in listdictdatestrprice :
        listdatestr.append(dictdatestrprice["날짜"])
        listprice.append(dictdatestrprice["종가"])
        listdealquantity.append(dictdatestrprice["거래량"])


    plotjongmok.plotjongmok(jongmokname, listdatestr, listprice, listdealquantity)