import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd
from time import sleep
import time
import math
import datetime
from .WriteDBAndReport import readDatafromdataDB, createAndWriteDB
# class monitorExchangeRate:

def getCandles():
    oneHourAgo = datetime.datetime.utcnow() - datetime.timedelta(hours = 1.2)
    now = datetime.datetime.utcnow()
    winterOrSummer = int(now.strftime("%m%d"))
    date_from =""
    date_to =""
        
    API_access_token = "175cc666c9a97c267b957da004cc83eb-9e9d5b50095e0fd1cdc163f494a9472a"
    accountID = "101-001-18171827-001"
    # URLの設定　（デモ口座用非ストリーミングURL）
    API_URL =  "https://api-fxpractice.oanda.com"
    # 通貨ペア
    INSTRUMENT = "USD_JPY"
    
    date_from = timeModified(oneHourAgo)
    date_to = timeModified(now)
    print("ターゲットタイム（UTC）は"+date_from + " to " + date_to)
    # <ろうそく足取得用URLの変数の設定>
    # /v3/instruments/{Account ID}/candles 
    for n in range(5):
        count = 720
        url = API_URL + "/v3/instruments/%s/candles?count=%s&price=M&granularity=S5&smooth=True&from=%s" % (INSTRUMENT, count,date_from)
        # ヘッダー情報の変数の設定
        headers = {
                        "Authorization" : "Bearer " + API_access_token
            }
        # サーバーへの要求
        response = requests.get(url, headers=headers)
        # 処理結果の編集
        Response_Body = response.json()
        # print(json.dumps(Response_Body, indent=2))
        i = 0
        pcc = []
        gatheringTime = []
        class ClassList:
            x = pcc
            y = gatheringTime
        while i<count:
            try:
                pcc5s = float(Response_Body["candles"][i]["mid"]["c"])
            except:
                break
            pcc.append(pcc5s)
            gatheringTime.append(i)
            i = i+1
        maximum = int(len(pcc))
        if(maximum > 0):
            break
        else:
            pass
    try:
        print(maximum)
        print("直前1分間のPCC")
        pcc1min = getEachPCC(ClassList, maximum, 12)
        print("直前5分間のPCC")
        pcc5min = getEachPCC(ClassList, maximum, 60)
        print("直前10分間のPCC")
        pcc10min =getEachPCC(ClassList, maximum, 120)
        print("直前30分間のPCC")
        pcc30min = getEachPCC(ClassList, maximum, 360)
        print("直前60分間のPCC")
        pcc60min = getEachPCC(ClassList, maximum,maximum)
        pcctotal = pcc1min*0.03 + pcc5min*0.07 + pcc10min*0.15 +pcc30min*0.25 + pcc60min*0.5
        pcctotal = str(pcctotal)
        print("I can conclude that the pcc during the period is " + pcctotal)
        print("The start price is " +Response_Body["candles"][0]["mid"]["o"] )
        print("The close price is " +Response_Body["candles"][maximum-1]["mid"]["o"] )
        return float(pcctotal)
    except:
        text = "You have an error for getting a pcc. This is probably due to the number of pcc we got which is most likely 0..."
        main(text, "errorcode=404: PCC not found")
        return 0
    

def getEachPCC(classList, maximumcount,target):
    x = classList.x
    y = classList.y
    tempList = []
    tempTime = []
    class temporaryList:
        x = tempList
        y = tempTime
    reverse = target
    for i in range(target):
        reverse =maximumcount -target+i
        tempList.append(x[reverse])
        tempTime.append(y[i])
    r = pearsonCorrelationCoeffcient(temporaryList)
    return r

def timeModified(date):
    date = str(date)
    choppedStr = date.split(" ")
    ChoppedStr2 = choppedStr[1].split(".")
    modifiedTime = choppedStr[0] +"T"+ChoppedStr2[0] + ".000000000Z"
    return modifiedTime


def pearsonCorrelationCoeffcient(classList):
    x = classList.x
    y = classList.y
    xn = len(x)
    yn = len(y)
    xtotal = 0
    ytotal = 0
    for i in range(xn-1):
        xtotal +=x[i]
        ytotal +=y[i]
    xavg = xtotal/xn
    yavg = ytotal/yn
    numerator = 0
    for i in range(xn-1):
        xi = x[i]
        yi =y[i]
        numerator += (xi-xavg )*(yi-yavg)
    denominatorLeft =0
    denominatorRight =0
    denominator = 0
    for i in range(xn-1):
        xi = x[i]
        yi =y[i]
        denominatorLeft += (xi-xavg )*(xi-xavg )
        denominatorRight += (yi-yavg )*(yi-yavg )
    denominator = math.sqrt(denominatorLeft*denominatorRight)
    #     print("denominator is " +str(denominator))
    try:
        r = float (numerator/denominator)*100
        print("The pearson correlation coeffcient is " + str(r))
    except:
        r = 0
        print(r)
    return r

def job1():
    now = datetime.datetime.now()
    todays_date = int(now.strftime("%Y%m%d")) 
    tommorow = todays_date +1
    while (todays_date != tommorow):  
        current_time = int(now.strftime("%M"))
        timptowait = 0
        if(current_time > 0):
            timetowait = (60 -int(current_time))*60
        else:
            timetowait = 3599
        pcc = getCandles()
        createAndWriteDB(pcc)
        readDatafromdataDB()
        print("I will wait for " + str(timetowait) +"s")
        while (timetowait >600):
            time.sleep(600)
            timetowait -=600
            print("We will take pcc again after " + str(timetowait) +"s")
            now = datetime.datetime.now()
        time.sleep(timetowait)
        now = datetime.datetime.now()
        todays_date = int(now.strftime("%Y%m%d"))
