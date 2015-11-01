__author__ = '최재혁'

from XAUtil import *
import jongmokgroup
import plotjongmok
import statistics as stat
from scipy import stats

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
    '''
    purpose : 종목 group을 구성하고, 종목 group별로 201310을 기준으로  이익률를 계산하여 파일로 저장한다.
    :return:
    '''
    dictJongMokGroup = jongmokgroup.dictJongMokGroup
    listAfterDates = [ 0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 360, 390, 420, 450, 480, 510, 540, 570, 600, 630, 660, 690]
    BaseDate = 20131015
    filename = "매수후기간별손익증감_구성종목.csv"
    saveJongMokGroupProfitTrends(filename, dictJongMokGroup, BaseDate, listAfterDates)


def createJongMokMatchingPBRPER():
    '''
    PBR이 1이하, PER가 7이하인 종목들에 대해 20131015을 기준으로  2년간 이익률을 계산.
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
    '''
    purpose : 주식 종목을 input parameter으로,  DB에 있는 chart 정로를 읽어와서, plotchart을 보여준다.
              상단에는 종가의 흐름을, 하단에는 거래량을 그려준다.
    :param jongmokname:
    :return: 단순히 chart만 그려준다.
    '''
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

def getMedianAverageCenterIndexOfJongmokGroup(jongmokgroup):
    coll주식종목Data = pymongo.MongoClient('localhost', 27017).get_database("xadb").get_collection("주식종목Data")
    dictdictdictret = {}
    listproj = ["PER", "PBR", "EPS", "ROA", "ROE", "EVEBITDA", "SPS","CPS","BPS","PEG"]
    #make the project for find_one()
    dictproj ={}
    for proj in listproj :
        dictproj[proj] = 1
    dictproj["_id"] = 0

    for keygroup in jongmokgroup :
        print("making median, average,.. of %s"%keygroup)
        listjongmokhan = jongmokgroup[keygroup]

        # dictproj = {"PER":1, "PBR":1, "EPS":1, "ROA":1, "ROE":1, "EVEBITDA":1, "SPS":1,"CPS":1,"BPS":1,"PEG":1, "_id":0}
        listPER = []
        listPBR = []
        listEPS = []
        listROA = []
        listROE = []
        listEVEBITDA = []
        listSPS = []
        listCPS = []
        listBPS = []
        listPEG = []

        for jongmokhan in listjongmokhan :
            dictcondi = {'종목명':jongmokhan }
            objret = coll주식종목Data.find_one(dictcondi, dictproj)
            if objret == None:
                continue
            listPER.append(objret["PER"])
            listPBR.append(objret["PBR"])
            listEPS.append(objret["EPS"])
            listROA.append(objret["ROA"])
            listROE.append(objret["ROE"])
            listEVEBITDA.append(objret["EVEBITDA"])
            listSPS.append(objret["SPS"])
            listCPS.append(objret["CPS"])
            listBPS.append(objret["BPS"])
            listPEG.append(objret["PEG"])

        dictdictdictret[keygroup] = \
            {"PER":{"min":min(listPER), "max":max(listPER), "median":stat.median(listPER), "mean":stat.mean(listPER), "stdev":stat.stdev(listPER, stat.mean(listPER))},
             "PBR":{"min":min(listPBR), "max":max(listPBR), "median":stat.median(listPBR), "mean":stat.mean(listPBR), "stdev":stat.stdev(listPBR, stat.mean(listPBR))},
             "EPS":{"min":min(listEPS), "max":max(listEPS), "median":stat.median(listEPS), "mean":stat.mean(listEPS), "stdev":stat.stdev(listEPS, stat.mean(listEPS))},
             "ROA":{"min":min(listROA), "max":max(listROA), "median":stat.median(listROA), "mean":stat.mean(listROA), "stdev":stat.stdev(listROA, stat.mean(listROA))},
             "ROE":{"min":min(listROE), "max":max(listROE), "median":stat.median(listROE), "mean":stat.mean(listROE), "stdev":stat.stdev(listROE, stat.mean(listROE))},
             "EVEBITDA":{"min":min(listEVEBITDA), "max":max(listEVEBITDA), "median":stat.median(listEVEBITDA), "mean":stat.mean(listEVEBITDA), "stdev":stat.stdev(listEVEBITDA, stat.mean(listEVEBITDA))},
             "SPS":{"min":min(listSPS), "max":max(listSPS), "median":stat.median(listSPS), "mean":stat.mean(listSPS), "stdev":stat.stdev(listSPS, stat.mean(listSPS))},
             "CPS":{"min":min(listCPS), "max":max(listCPS), "median":stat.median(listCPS), "mean":stat.mean(listCPS), "stdev":stat.stdev(listCPS, stat.mean(listCPS))},
             "BPS":{"min":min(listBPS), "max":max(listBPS), "median":stat.median(listBPS), "mean":stat.mean(listBPS), "stdev":stat.stdev(listBPS, stat.mean(listBPS))},
             "PEG":{"min":min(listPEG), "max":max(listPEG), "median":stat.median(listPEG), "mean":stat.mean(listPEG), "stdev":stat.stdev(listPEG, stat.mean(listPEG))}
            }
    return dictdictdictret, listproj, ["min", "max", "median", "mean", "stdev"]

def createMedianAveragePBRPEROfJongmokGroup():
    '''
    purpose : 종목group을 만들고, 각 group에 대해, 주요 지표(PBR, PER, EPS등) 의 중앙값(median), 평균(mean),
              중심값(center )을 구한다.
    :return:
    '''

    coll주식종목Data = pymongo.MongoClient('localhost', 27017).get_database("xadb").get_collection("주식종목Data")
    dictJongMokGroup = jongmokgroup.dictJongMokGroup

    # 코스피 종목구성.
    dictcondi = {'시장구분':"1" }
    dictproj = {"종목명":1, "_id":0}
    objret = coll주식종목Data.find(dictcondi, dictproj)
    dict코스피 = {"코스피":[obj["종목명"]for obj in objret]}
    dictJongMokGroup.update(dict코스피)

    # 코스닥 종목구성.
    dictcondi = {'시장구분':"2" }
    objret = coll주식종목Data.find(dictcondi, dictproj)
    dict코스닥 = {"코스닥":[obj["종목명"]for obj in objret]}
    dictJongMokGroup.update(dict코스닥)

    # 전체 종목 구성.
    dict전체 = {"전체": dict코스피["코스피"] +dict코스닥["코스닥"] }
    dictJongMokGroup.update(dict전체)

    dictdictdictret, listproj, liststat = getMedianAverageCenterIndexOfJongmokGroup(dictJongMokGroup)

    savedictdictdictToCSV("종목그룹별지표통계.csv",listproj,liststat,  dictdictdictret)
    print("Done...")


def createHistorgramOfPERPBRByMarket():
    '''
    purpose : 코스피, 코스탁, 전체시장에 대해 PER, PBR의 histogram을 그린다.
    :return:
    '''
    coll주식종목Data = pymongo.MongoClient('localhost', 27017).get_database("xadb").get_collection("주식종목Data")

    listKOSPIPER = []
    listKOSPIPBR = []

    # 코스피 종목구성.
    dictcondi = {'시장구분':"1" }
    dictproj = {"PER":1, "PBR":1,  "_id":0}
    objret = coll주식종목Data.find(dictcondi, dictproj)
    for obj in objret :
        per = obj["PER"]
        if per > -10 and per <= 100 :
            listKOSPIPER.append(per)
        pbr = obj["PBR"]
        if pbr > -10 and pbr <= 40:
            listKOSPIPBR.append(pbr)

    listKOSDACPER = []
    listKOSDACPBR = []
    # 코스피 종목구성.
    dictcondi = {'시장구분':"2" }
    dictproj = {"PER":1, "PBR":1,  "_id":0}
    objret = coll주식종목Data.find(dictcondi, dictproj)
    for obj in objret :
        per = obj["PER"]
        if per > -10 and per <= 100 :
            listKOSDACPER.append(per)
        pbr = obj["PBR"]
        if pbr > -10 and pbr <= 40:
            listKOSDACPBR.append(pbr)

    plotjongmok.plotHistogram([listKOSPIPBR,listKOSDACPBR ], ["PBR_KOSPI", "PBR_KOSDAC"])
    plotjongmok.plotHistogram([listKOSPIPER,listKOSDACPER ], ["PER_KOSPI", "PER_KOSDAC"])



    chi2, p = stats.chisquare(listKOSPIPER)
    print('chisquare output')
    print('Z-score = ' + str(chi2))
    print('P-value = ' + str(p))

def createHistogramOfJongmok(Jongmokhan) :
    '''
    종목의 종가를 histogram을 그린다.
    :param Jongmokhan:
    :return:
    '''

    coll주식종목Data = pymongo.MongoClient('localhost', 27017).get_database("xadb").get_collection("주식종목Data")
    dictcondi = {'종목명':Jongmokhan }
    dictproj = { "주식차트_일주월.종가":1, "_id":0 }
    objret = coll주식종목Data.find_one(dictcondi, dictproj)
    listdictdatestrprice = objret["주식차트_일주월"]

    listprice = []
    for dictdatestrprice in listdictdatestrprice :
        listprice.append(dictdatestrprice["종가"])

    plotjongmok.plotHistogram([listprice ], [Jongmokhan])

    # 전날 종가대비 가격 변동율의 histogram
    listdiffrate =[]
    priceprev = listprice[0]
    for price in listprice :
        listdiffrate.append((price- priceprev)/priceprev)
        priceprev = price

    plotjongmok.plotHistogram([listdiffrate ], ["price diff rate of " + Jongmokhan])


    # chi2, p = stats.normaltest(listdiffrate)
    # print('normaltest output')
    # print('Z-score = ' + str(chi2))
    # print('P-value = ' + str(p))
    #
    # chi2, p = stats.chisquare(listKOSPIPBR)
    # print('chisquare output')
    # print('Z-score = ' + str(chi2))
    # print('P-value = ' + str(p))

