import csv
import pandas as pd
import datetime
from . import sendEmailtoTheUser
import psycopg2
from . import constVariables

def get_connection():
    return psycopg2.connect(
        host = constVariables.CVAL.host,
        database = constVariables.CVAL.database,
        user = constVariables.CVAL.user,
        password = constVariables.CVAL.password,
        port = constVariables.CVAL.port)

def reportThePCC(content):
    title = "PCC"
    sendEmailtoTheUser.main(content, title)

def readDatafromdataDB():
    now = datetime.datetime.now()
    todays_date = str(now.strftime("%Y%m%d")) 
    conn = get_connection()
    cur = conn.cursor()
    # dbをpandasで読み出す。
    # df = pd.read_sql('SELECT * FROM data', conn)
    cur.execute('SELECT * FROM data')
    content =""
    for row in cur:
        if (str(row[1]) == todays_date):
            content = content + "Time: "+ str(row[2]) +" PCC in 60 minutes: " +str(row[3]) +"\n"
        else:
            pass
    reportThePCC(content)
    cur.close()
    conn.close()

def readDatafromresultDB():
    conn = get_connection()
    cur = conn.cursor()
    # dbをpandasで読み出す。
    df = pd.read_sql('SELECT * FROM percent', conn)
    try:
        print("successfully converted to csv file")
    except:
        print("failed to convert to csv file")
   
    cur.close()
    conn.close()

def readDatafromresultDBandShowTheRateOfWin():
    conn = get_connection()
    cur = conn.cursor()
    # dbをpandasで読み出す。
    cur.execute('SELECT * FROM percent')
    totalWin =0
    toalGame = 0
    for row in cur:
        win =0
        draw = 99999
        try:
            win = float(row[3])
        except:
            win = -1
        try:
            draw = float(row[5])
        except:
            pass
        if (win >= 0.0):
            totalWin +=1
            toalGame +=1
        elif (draw == 0):
            pass
        else:
            toalGame +=1
    rateOfWin = (totalWin/toalGame)*100
    msg = "So far you have tried " + str(toalGame) + " times and won " +str(totalWin) +" times.\nSo your rate of win is " + str(rateOfWin) + "%."
    print(msg)
    cur.close()
    conn.close()
    return msg

def writeResult(rate, now, todays_date):
    #日付を取得
    rate = float(rate)
    current_time = 'h' + now.strftime("%H")
    # result.dbを作成する
    # すでに存在していれば、それにアスセスする。
    conn = get_connection()
    # sqliteを操作するカーソルオブジェクトを作成
    cur = conn.cursor()
    # personsというtableを作成してみる
    # 大文字部はSQL文。小文字でも問題ない。
    try:
        cur.execute('CREATE TABLE percent(id SERIAL NOT NULL, date text, time text, win text, lose text, draw text, PRIMARY KEY (id))')
    except:
        conn.rollback()
        pass
    #日付を入れる
    # "PCC"に"pcc(引数）"を入れる
    if(rate >0):
        try:
            cur.execute('INSERT INTO percent(date, time, win) VALUES(%s,%s,%s)',(todays_date,current_time,rate))
        except:
            conn.rollback()
        pass
    elif(rate<0):
        try:
            cur.execute('INSERT INTO percent(date, time, lose) VALUES(%s,%s,%s)',(todays_date,current_time,rate))
        except:
            conn.rollback()
        pass
    else:
        try:
            cur.execute('INSERT INTO percent(date, time, draw) VALUES(%s,%s,%s)',(todays_date,current_time,rate))
        except:
            conn.rollback()
        pass
    #いらない欄を消す
    # sql = 'DELETE FROM data WHERE id=?'
    # データベースへコミット。これで変更が反映される。  
    conn.commit()
    cur.execute('SELECT * FROM percent')
    print(cur.fetchall())
    cur.close()
    # データベースへのコネクションを閉じる。(必須)
    conn.close()

def createAndWriteDB(pcc):
    #日付を取得
    pcc =str(pcc)
    now = datetime.datetime.now()
    todays_date = str(now.strftime("%Y%m%d")) 
    # 日付data.dbを作成する
    # すでに存在していれば、それにアスセスする。
    targetTime = int(now.strftime("%H"))+1
    if(targetTime == 24):
            now = now + datetime.timedelta(hours=1) 
            todays_date = str(now.strftime("%Y%m%d")) 
            targetTime = '00'
    else:
        if(targetTime<10):
            targetTime = '0' + str(targetTime)
        targetTime = str(targetTime)
    current_time = 'h' + targetTime
    conn = get_connection()
    # sqliteを操作するカーソルオブジェクトを作成
    cur = conn.cursor()
    # personsというtableを作成してみる
    # 大文字部はSQL文。小文字でも問題ない。
    try:
        cur.execute('CREATE TABLE data(id SERIAL NOT NULL, date text, time text, PCC60min text, PRIMARY KEY (id));')
    except:
        conn.rollback()
        pass
    #日付を入れる
    # "PCC"に"pcc(引数）"を入れる
    try:
        # cur.execute('ALTER TABLE data')
        postgres_insert_query = "INSERT INTO data(date, time, PCC60min) VALUES(%s,%s,%s)"
        record_to_insert = (todays_date, current_time, pcc)
        cur.execute(postgres_insert_query, record_to_insert)
        print("success to insert info into data")
        conn.commit()
    except:
        print(cur.query)
        print("failed to insert info into data")
    #いらない欄を消す
    # sql = 'DELETE FROM data WHERE id=?'
    # データベースへコミット。これで変更が反映される。  
    
    cur.execute('SELECT * FROM data')
    # print(cur.fetchall())
    cur.close()
    # データベースへのコネクションを閉じる。(必須)
    conn.close()
