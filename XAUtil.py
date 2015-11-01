__author__ = '최재혁'
from datetime import datetime, timedelta
import XAQuery
import pymongo

class DateStrformat():
    '''
    입력 format은  20150912 처럼 string으로 표현되고, 내부에서는 날짜 개산을 하고,
    같은 format으로 출력한다.
    '''
    def __init__(self, datestr):
        self.boolint = type(datestr) == int
        if self.boolint == True :
            datestr = str(datestr)
        year = datestr[:4]
        mon = datestr[4:6]
        day = datestr[6:8]

        # 계산은 낮 12시를 기준으로 한다.
        self.Refseconds  = self.ConvertDateTimeToMiliSeconds(int(year), int(mon), int(day), 12)

    def ConvertDateTimeToMiliSeconds(self, y, m, d, h = 0 , minute = 0 , s = 0 ):
        daydiff = datetime(y, m, d, h, minute, s) - datetime(1970, 1, 1, 9, 0, 0)
        return int(daydiff.total_seconds())

    def ConvertTimeStampToString ( self, inputsecond ):
        if inputsecond == None:
            return ""
        strfmt = "%Y%m%d"
        outdatetime = datetime(1970, 1, 1) + timedelta(hours= 9, seconds=inputsecond)
        return outdatetime.strftime(strfmt)

    def getDateStr_nDay(self, nDays):
        ret = self.ConvertTimeStampToString( self.Refseconds + 24 * 3600 * nDays)
        if self.boolint == True :
            return int(ret)
        return ret

    def getDateStr_Today(self):
        strfmt = "%Y%m%d"
        ret =  datetime.now().strftime(strfmt)
        if self.boolint == True :
            return int(ret)
        return ret

listdictJongmokjohoi = []
def get주식종목조회(update=False):
    global listdictJongmokjohoi

    if update == False and len(listdictJongmokjohoi) > 1:
        return listdictJongmokjohoi

    coll주식종목조회 = pymongo.MongoClient('localhost', 27017).get_database("xadb").get_collection("t8430_주식종목조회")

    if update == False and coll주식종목조회.count() > 0 :
        listdictJongmokjohoi = [aa for aa in coll주식종목조회.find({}) ]
        return listdictJongmokjohoi


    listdictJongmokjohoi = XAQuery.t8430_주식종목조회()
    coll주식종목조회.insert_many(listdictJongmokjohoi)
    return listdictJongmokjohoi

def getShortCode(JongMokHan) :
    '''
    JongMokHan 에 해당하는 shcode을 반환한다.
    :param JongMokName:
    :return:
    '''
    global listdictJongmokjohoi
    if len(listdictJongmokjohoi) == 0 :
        get주식종목조회()

    for dictJongMok in listdictJongmokjohoi :
        if JongMokHan == dictJongMok["종목명"] :
            return dictJongMok["단축코드"]

def indexing주식종목명() :
    coll주식종목Data = pymongo.MongoClient('localhost', 27017).get_database("xadb").get_collection("주식종목Data")
    if len(coll주식종목Data.index_information().keys()) == 1 :
        # in case of default index
        print("New indexing the 종목명")
        coll주식종목Data.create_index("종목명", background=True)
    else:
        print("Reindexing the 종목명")
        coll주식종목Data.reindex()

def update주식차트(listJongmokHan, DateStrStart, DateStrEnd, boolRebuild=False) :
    '''
    각 한글종목에 대해 주식차트 data를 가져와서, DB에 update한다.
    :param listJongmokHan:
    :param DateStrStart:
    :param DateStrEnd:
    :param boolRebuild: 전부 지우고 할지 말지 결정한다.
    :return: 없음.
    '''

    if len(DateStrStart) == 0 or len(DateStrEnd) == 0 :
        print("length of ListDay is empty....")
        return

    coll주식종목Data = pymongo.MongoClient('localhost', 27017).get_database("xadb").get_collection("주식종목Data")

    if boolRebuild == True :
        coll주식종목Data.delete_many({})

    listdictJongmok = get주식종목조회()
    if len(listJongmokHan) > 0 :
        # make the list of shcode for  listJongmokHan
        listdictJongMoktemp = []
        for JongmokHan in listJongmokHan :
            for dictJongmok in listdictJongmok :
                if JongmokHan == dictJongmok['종목명'] :
                    listdictJongMoktemp.append(dictJongmok)
        listdictJongmok = listdictJongMoktemp

    counttotal = len(listdictJongmok)
    for dictJongmok in listdictJongmok :
        print("XAQuery, order:%s, 종목명:%s"%(str(counttotal), dictJongmok['종목명']))
        counttotal -= 1

        listdictchart = XAQuery.t8413_주식차트_일주월(dictJongmok['단축코드'], 2, DateStrStart, DateStrEnd )
        print(str(len(listdictchart)))
        id =0
        try:
            Obj =coll주식종목Data.insert_one(dictJongmok)
            id = Obj.inserted_id
        except:
            id = coll주식종목Data.find_one(dictJongmok)["_id"]


        for dictchart in listdictchart :
            if coll주식종목Data.find({"_id":id, "주식차트_일주월.날짜":{"$eq":dictchart["날짜"]}}).count() == 0 :
                coll주식종목Data.update_one({"_id":id},{"$push":{"주식차트_일주월":dictchart}})

    indexing주식종목명()

def get예외종목list():
    # return []
    listtemp = []
    for jongmok in open("예외종목.txt") :
        if len(jongmok) > 0 :
            listtemp.append(jongmok.strip())
    return listtemp

def get종가fromListJongmokListday(listJongmokHan, listDateStr) :
    '''
    각 한글 종목에 대해  원하는 날짜들의 종가의 list 구한다.
    만일 listJongmokHan의 길이가 0이면, 전체 종목에 대해 실시한다.
    listDay의 길이는 1 이상이 되어야 한다.
    만일 어떤 종목의 어떤 날자에 종가가 하나라도 존재하지 않으면, 그 종목은 제거하고,
    나머지 종목에 대해 종가를 구한다.
    :param listJongmokHan:
    :param listDateStr:
    :return: dict type으로  한글종목,shcode, 날짜별 기준가 을 준비하고,
            전체를 list type으로 return한다.
    '''
    if len(listDateStr) == 0 :
        print("length of ListDay is empty....")
        return

    # ----------------------------------------------------------------------------------------------------------
    # 요구하는 data에 대비하여, coll주식종목Data 를 update한다.
    # 삼성전자 주식으로 DB내의 종가의 시작날짜와 마지막 날짜를 구한다.

    coll주식종목Data = pymongo.MongoClient('localhost', 27017).get_database("xadb").get_collection("주식종목Data")
    intStockTerms = [aa for aa in coll주식종목Data.distinct("주식차트_일주월.날짜", {"종목명":"삼성전자"}) ]
    dateDBend = max(intStockTerms)
    dateDBstart = min(intStockTerms)

    dateReqend = max(listDateStr)
    dateReqstart = min(listDateStr)

    if dateReqstart < dateDBstart   :
        update주식차트([], dateReqstart,dateDBstart )

    if dateReqend  > dateDBend :
        update주식차트([], dateDBend,dateReqend )

    # ----------------------------------------------------------------------------------------------------------
    # 좀목 list을 만든다.
    listdictJongmok = get주식종목조회()
    if len(listJongmokHan) > 0 :
        # make the list of shcode for  listJongmokHan
        listdictJongMoktemp = []
        for JongmokHan in listJongmokHan :
            listdictJongMoktemp.append( {'종목명':JongmokHan, '단축코드': getShortCode(JongmokHan)})
        listdictJongmok = listdictJongMoktemp

    # ----------------------------------------------------------------------------------------------------------
    # 좀목별, 날짜에 해당하는 종가를 구한다.

    listdictClsoePriceOfJongmokDate = []
    countJongmok = len(listdictJongmok)
    for dictJongmok in listdictJongmok :
        print("MongoDB Search, order:%s,  종목명:%s"%(str(countJongmok), dictJongmok['종목명'] ))
        countJongmok -= 1

        dicttemp = {'종목명':dictJongmok['종목명'] }
        for DateStr in listDateStr :
            counttry = 0
            datestr = DateStrformat(DateStr)
            while counttry < 7 :
                # 공휴일 등, 시장이 휴장인 경우  7일 이전까지 조사한다.
                # in some case, DateStr is holiday,and try to get the previous day's 종가 until maxinum 7 times
                dictcondi = {'종목명':dictJongmok['종목명'] }
                dictproj = {"주식차트_일주월":{"$elemMatch":{"날짜":{"$eq":datestr.getDateStr_nDay(-counttry)}}}, "_id":0}
                objret = coll주식종목Data.find(dictcondi, dictproj)
                # print(objret[0])
                try:
                    dicttemp[DateStr] = objret[0]['주식차트_일주월'][0]["종가"]
                    break
                except:
                    pass
                    counttry += 1
            if counttry == 7 :
                dicttemp[DateStr] = 0
        # 모든 날짜에 종가 값이 전부 존재할 경우만 list에 저장한다.
        if [aa for aa in dicttemp.values()].count(0) == 0 :
            listdictClsoePriceOfJongmokDate.append(dicttemp)

    return listdictClsoePriceOfJongmokDate

def getProfieLossProportionBasedOnStartDate(listDateStr, listdict종가fromJongmokDate):
    '''
    listDateStr 의 첫번째 날짜 가격 대비, 다른 날짜의 가격이 올라는지 내렸는지 Normalize해서 Ratio로 계산하고,
    종목별 전부더해서 평균을 취한다.
    :param listDateStr:
    :param listdict종가fJongmokDate:
    :return:
    '''
    listProportMeans =[0.0 for aa in listDateStr[1:]]
    for dict종가fromJongmokDate in listdict종가fromJongmokDate :
        listPrice = []
        for DateStr in listDateStr :
            listPrice.append(dict종가fromJongmokDate[DateStr])
        listproport = []
        for Price in listPrice[1:] :
            if  listPrice[0] == 0 :
                print("listPrice[0] is '0' 종목명:%s"%dict종가fromJongmokDate['종목명'])
            listproport.append((Price-listPrice[0])/listPrice[0])
        for i in range(len(listproport)) :
            listProportMeans[i] += listproport[i]
    lenListDict = len(listdict종가fromJongmokDate)
    for i  in range(len(listProportMeans)) :
        listProportMeans[i] = listProportMeans[i] / lenListDict

    return listProportMeans

def updateFNG_요약(listJongmokHan) :
    '''
    t3320을 이용하여 기업의 기본정보를 가져온다.
    예를 들면, 본사주소, 결산월, 주당액면가,자본금, 시가총액, PBR, PER등등.
    :param listJongmokHan: None일 경우 모든 항목에 대해 실행한다.
    :return:
    '''

    listdictJongmok = get주식종목조회()
    if len(listJongmokHan) > 0 :
        # make the list of shcode for  listJongmokHan
        listdictJongMoktemp = []
        for JongmokHan in listJongmokHan :
            for dictJongmok in listdictJongmok :
                if JongmokHan == dictJongmok['종목명'] :
                    listdictJongMoktemp.append(dictJongmok)
        listdictJongmok = listdictJongMoktemp

    coll주식종목Data = pymongo.MongoClient('localhost', 27017).get_database("xadb").get_collection("주식종목Data")

    counttotal = len(listdictJongmok)
    for dictJongmok in listdictJongmok :
        print("XAQuery, order:%s, 종목명:%s"%(str(counttotal), dictJongmok['종목명']))
        counttotal -= 1

        dictret = XAQuery.t3320_FNG_요약(dictJongmok['단축코드'] )
        id =0
        try:
            Obj =coll주식종목Data.insert_one(dictJongmok)
            id = Obj.inserted_id
        except:
            id = coll주식종목Data.find_one(dictJongmok)["_id"]

        coll주식종목Data.update_one({"_id":id},{"$set":dictret})

def getJongMokMatchingPBRPER(PBR, PER):
    '''
    updateFNG_요약() 실행이후에,
    PBR, PER의 조건에 맞는 종목 list을 반환한다.
    :param PBR:
    :param PER:
    :return: 한국 종목 list
    '''
    coll주식종목Data = pymongo.MongoClient('localhost', 27017).get_database("xadb").get_collection("주식종목Data")
    cursorret = coll주식종목Data.find({"PBR":{"$lte":PBR, "$gt":0}, "PER":{"$lte":PER, "$gt":0}}, {"종목명":1, "_id":0})
    listret = []
    for jongmok in cursorret :
        listret.append(jongmok["종목명"])

    return listret


def saveListDictToCSV(csvfilename, listfield, listdictrecord) :
    f = open(csvfilename, "w")
    f.write(",".join([ str(aa) for aa in listfield]) + "\n")
    for dictrecord in listdictrecord :
        listtemp = []
        for field in listfield :
            listtemp.append(dictrecord[field])
        f.write(",".join([str(aa) for aa in listtemp]) + "\n")
    f.close()

def saveListListToCSV(csvfilename, listfield, listlistrecord) :
    f = open(csvfilename, "w")
    f.write(",".join([ str(aa) for aa in listfield]) + "\n")
    for listrecord in listlistrecord :
        f.write(",".join([str(aa) for aa in listrecord]) + "\n")
    f.close()

def savedictdictdictToCSV(csvfilename, listkey1, listkey2, dictdictdictrecord) :
    f = open(csvfilename, "w")
    f.write("," + ",".join([ str(aa) for aa in listkey2]) + "\n")
    for key0 in dictdictdictrecord :
        f.write(key0 + "\n")
        dictdictrecord = dictdictdictrecord[key0]
        for key1 in listkey1 :
            dictrecord = dictdictrecord[key1]
            f.write(key1 +"," +  ",".join([str(dictrecord[aa]) for aa in listkey2]) + "\n")
    f.close()


def buildDataBase():
    update주식차트([],"20130930", "20151001" )
    updateFNG_요약([])