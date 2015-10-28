__author__ = '최재혁'

import win32com.client
import pythoncom
import os
import time


file주식종목 = "주식종목조회.csv"

class XAQueryEvents:
    queryState = 0
    countTR = 0
    timefirst = 0
    def __init__(self):
        time.sleep(3)
        if XAQueryEvents.timefirst == 0 :
            XAQueryEvents.timefirst = time.time()
        XAQueryEvents.countTR  += 1
        # print("current countTR, %s"%XAQueryEvents.countTR)
        if XAQueryEvents.countTR >= 200 and (time.time() - XAQueryEvents.timefirst) < 600.0  :
            print("sleeping until new TR is available")
            time.sleep(time.time()-XAQueryEvents.timefirst)
            XAQueryEvents.timefirst = 0
            XAQueryEvents.countTR = 0

    def OnReceiveData(self, szTrCode):
        print("ReceiveData")
        XAQueryEvents.queryState = 1
    def OnReceiveMessage(self, systemError, mesageCode, message):
        print(message)


listResFieldDictname = [ "fieldnameHan", "fieldnameEng", "fieldnameEng1", "datatype", "datasize"]

class GETRESATTR( ) :
    def __init__(self, dictlistdictres ):
        self.dictlistdictres = dictlistdictres

    def getFieldNames(self, nameblock, nameresfieldname):
        if nameblock in self.dictlistdictres.keys() :
            if not nameresfieldname in listResFieldDictname :
                return []
            listdictitem = self.dictlistdictres[nameblock]
            listvalue = []
            for dictitem in listdictitem :
                listvalue.append( dictitem[nameresfieldname])
            return listvalue
        else:
            return []

    def getFieldNamesEng(self, nameblock ):
        return self.getFieldNames(nameblock, "fieldnameEng" )

    def getFieldNamesHan(self, nameblock ):
        return self.getFieldNames(nameblock, "fieldnameHan" )
    def getFieldType(self, nameblock ):
        # 날짜는 숫자로 바꾸어 추급한다.
        listnamehan = self.getFieldNamesHan( nameblock )
        listtype = self.getFieldNames(nameblock, "datatype" )
        for i in  range(len(listnamehan)) :
            listtype[i] = "long" if listnamehan[i] == "날짜" else listtype[i]
        return listtype


def parsingRESfile(filenameRes) :
    '''
    filenameRes 를 parsing하고, 해당 정보를 담고 있는 GETRESATTR class을 반환한다.
    parse the res file and create the dict-type result .
    :param filenameres:
    :return: object of GETRESITEMS
    '''

    listblockindicator = [ "output", "input", "occurs"]
    listdatatype = ["char", "long", "float", "double"]

    nameblock = ""
    listdictentry = []
    dictlistdictres = {}
    for line in open(filenameRes) :
        line = line.strip()
        if len(line) == 0 :
            continue
        if line == "begin" :
            listdictentry = []
        elif line == "end" and len(nameblock) > 0 and len(listdictentry) > 0 :
            dictlistdictres[nameblock] = listdictentry
        elif line[-1] == ";" :
            listitem = line[:-1].split(",")
            if listitem[-1] in listblockindicator :
                # begin block
                nameblock = listitem[0]
            elif listitem[-2] in listdatatype and len(nameblock) > 0 :
                # begin the entry.
                listdictentry.append(dict(zip(listResFieldDictname, listitem)))
    return GETRESATTR(dictlistdictres)



def t8430_주식종목조회():
    '''
    모든 종목에 대해  dict type으로  종목이름, shcode, 고가,저가,...현재가, 등을 Listdict type으로 반환한다.
    이 때, 기존에 산출한 file주식종목.csv file이 존해하면, 이를 활용한다.  그렇지 않으면, 새로 산출한다.
    :param update:
    :return:
    '''

    resFileName = "C:\\eBEST\\xingAPI\\Res\\t8430.res"
    clsResAttr = parsingRESfile(resFileName)
    listFieldName = clsResAttr.getFieldNamesEng("t8430OutBlock")
    listFieldNameHan = clsResAttr.getFieldNamesHan("t8430OutBlock")

    listdictJongmokjohoi = []


    inXAQuery = win32com.client.DispatchWithEvents("XA_DataSet.XAQuery", XAQueryEvents)
    inXAQuery.LoadFromResFile(resFileName)
    inXAQuery.SetFieldData('t8430InBlock', 'gubun', 0, 0)
    inXAQuery.Request(0)

    while XAQueryEvents.queryState == 0:
        pythoncom.PumpWaitingMessages()

    # Get FieldData
    nCount = inXAQuery.GetBlockCount('t8430OutBlock')
    for i in range(nCount):
        listtemp = []
        for j in range(len(listFieldName)) :
            listtemp.append(inXAQuery.GetFieldData('t8430OutBlock', listFieldName[j], i))
        #make the dict type
        listdictJongmokjohoi.append(dict(zip(listFieldNameHan,listtemp)))

    return  listdictJongmokjohoi




def t8413_주식차트_일주월(shcode, dwm, startdate, enddate) :
    '''
    shcode 입력에 대해 startdate 부터 enddate까지 주식차트의 정보를  listdict type으로 반환한다.
    :param shcode:
    :param dwm: 2:day, 3:week, 4:month
    :param startdate: startdate와 enddate은 같은 날짜를 사용해서는 안된다.
    :param enddate:
    :return:
    '''
    resFileName = "C:\\eBEST\\xingAPI\\Res\\t8413.res"
    inXAQuery = win32com.client.DispatchWithEvents("XA_DataSet.XAQuery", XAQueryEvents)
    inXAQuery.LoadFromResFile(resFileName)
    inXAQuery.SetFieldData('t8413InBlock', 'shcode', 0, shcode)
    inXAQuery.SetFieldData('t8413InBlock', 'gubun', 0, str(dwm))
    inXAQuery.SetFieldData('t8413InBlock', 'sdate', 0, str(startdate))
    inXAQuery.SetFieldData('t8413InBlock', 'edate', 0, str(enddate))
    inXAQuery.SetFieldData('t8413InBlock', 'comp_yn', 0, 'N')
    inXAQuery.Request(0)

    while XAQueryEvents.queryState == 0:
        pythoncom.PumpWaitingMessages()

    # Get FieldData
    nCount = inXAQuery.GetBlockCount('t8413OutBlock1')
    clsResAttr = parsingRESfile(resFileName)
    listFieldName = clsResAttr.getFieldNamesEng("t8413OutBlock1")
    listFieldNameHan = clsResAttr.getFieldNamesHan("t8413OutBlock1")
    listFieldType = clsResAttr.getFieldType("t8413OutBlock1")

    listdictchart = []
    for i in range(nCount):
        listFieldValue = []
        for FieldName in listFieldName :
            listFieldValue.append(inXAQuery.GetFieldData('t8413OutBlock1', FieldName, i))
        for i  in range(len(listFieldType)):
            listFieldValue[i] = int(listFieldValue[i]) if listFieldType[i] == "long" else ( float(listFieldValue[i]) if listFieldType[i] == "double" else listFieldValue[i] )
        listdictchart.append(dict(zip(listFieldNameHan, listFieldValue)))

    XAQueryEvents.queryState = 0

    return  listdictchart


def t3320_FNG_요약(shcode) :
    '''
    :param shcode:
    :return:
    '''
    resFileName = "C:\\eBEST\\xingAPI\\Res\\t3320.res"
    inXAQuery = win32com.client.DispatchWithEvents("XA_DataSet.XAQuery", XAQueryEvents)
    inXAQuery.LoadFromResFile(resFileName)
    inXAQuery.SetFieldData('t3320InBlock', 'gicode', 0, shcode)
    inXAQuery.Request(0)

    while XAQueryEvents.queryState == 0:
        pythoncom.PumpWaitingMessages()


    clsResAttr = parsingRESfile(resFileName)
    listFieldName = clsResAttr.getFieldNamesEng("t3320OutBlock")
    listFieldNameHan = clsResAttr.getFieldNamesHan("t3320OutBlock")
    listFieldType = clsResAttr.getFieldType("t3320OutBlock")

    listFieldValue = []
    for FieldName in listFieldName :
        listFieldValue.append(inXAQuery.GetFieldData('t3320OutBlock', FieldName,  0).strip())
    for i  in range(len(listFieldType)):
        listFieldValue[i] = int(listFieldValue[i]) if listFieldType[i] == "long" else ( float(listFieldValue[i]) if listFieldType[i] in ["float","double"] else listFieldValue[i] )
    dictret = dict(zip(listFieldNameHan, listFieldValue))

    listFieldName = clsResAttr.getFieldNamesEng("t3320OutBlock1")
    listFieldNameHan = clsResAttr.getFieldNamesHan("t3320OutBlock1")
    listFieldType = clsResAttr.getFieldType("t3320OutBlock1")

    listFieldValue = []
    for FieldName in listFieldName :
        listFieldValue.append(inXAQuery.GetFieldData('t3320OutBlock1', FieldName, 0).strip())
    for i  in range(len(listFieldType)):
        try:
            listFieldValue[i] = int(listFieldValue[i]) if listFieldType[i] == "long" else ( float(listFieldValue[i]) if listFieldType[i] in ["float", "double"] else listFieldValue[i] )
        except:
            print("______ invalid value : %s"%(listFieldValue[i]))
            listFieldValue[i] = 0

    dictret.update( dict(zip(listFieldNameHan, listFieldValue)) )

    XAQueryEvents.queryState = 0

    return  dictret