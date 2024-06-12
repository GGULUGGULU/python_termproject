#!/usr/bin/python
# coding=utf-8

import sys
import time
import sqlite3

import bs4
import telepot
from pprint import pprint
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
from datetime import date, datetime, timedelta
from bs4 import XMLParsedAsHTMLWarning
import warnings
import traceback

import fulloccupancyrate

key = '3BEJFYzZNbYJRrNn4Vmy1iAyZLjxVDPDTbIo%2Fbk1vrGDXFMn%2FDI%2BzUaMZNKea8x7tpXfWI3GX9c6H5Eowq03qw%3D%3D'
TOKEN = '7337249876:AAGGw3HHtmk7XLGgKIf-3IuiZSbpf0U0yI0'
MAX_MSG_LENGTH = 300
baseurl_nationwide = 'http://openapi.airport.co.kr/service/rest/AirportParking/airportparkingRT?serviceKey='+key
#전국공항
baseurl_incheon = 'http://apis.data.go.kr/B551177/StatusOfParking/getTrackingParking?serviceKey='+key
#인천공항
bot = telepot.Bot(TOKEN)
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
def getData(loc_param):
    res_list = []
    aprEnd=""
    if(loc_param=="김포국제공항"):
        aprEnd="GMP"
    elif(loc_param=="김해국제공항"):
        aprEnd="PUS"
    elif(loc_param=="제주국제공항"):
        aprEnd="CJU"
    elif(loc_param=="대구국제공항"):
        aprEnd="TAE"
    elif(loc_param=="광주공항"):
        aprEnd="KWJ"
    elif(loc_param=="여수공항"):
        aprEnd="RSU"
    elif(loc_param=="울산공항"):
        aprEnd="USN"
    elif(loc_param=="군산공항"):
        aprEnd="KUV"
    elif(loc_param=="원주공항"):
        aprEnd="WJU"
    elif(loc_param=="청주국제공항"):
        aprEnd="CJJ"
    elif(loc_param=="무안국제공항"):
        aprEnd="MWX"
    elif(loc_param=="사천공항"):
        aprEnd="HIN"
    elif(loc_param=="양양국제공항"):
        aprEnd="YNY"



    if(loc_param!="인천국제공항"):
        url_nationwide = baseurl_nationwide+'&schAirportCode='+aprEnd
        res_body_nationwide = urlopen(url_nationwide).read()
        soup_nationwide = BeautifulSoup(res_body_nationwide, 'html.parser')
        items_nationwide = soup_nationwide.findAll('item')
        for item in items_nationwide:
            item = re.sub('<.*?>', '|', str(item))
            print(item)
            parsed = item.split('||')
            try:
                total_spaces = int(parsed[4])
                used_spaces = int(parsed[9])
                remaining_spaces = total_spaces - used_spaces
                #utilization_rate = (used_spaces / total_spaces) * 100
                utilization_rate=fulloccupancyrate.calculate(total_spaces,used_spaces)
                row = '주차구역: '+parsed[2]+'/'+' 총 주차공간: '+str(total_spaces)+'/ 사용 중인 주차공간: '+str(used_spaces)+ '/ 남은 주차 공간: '+str(remaining_spaces)+ '/ 만차율: {:.1f}%'.format(utilization_rate).strip()
            except IndexError:
                row = item.replace('|', ',')
                
            if row:
                res_list.append(row)
        return res_list
    else:
        url_incheon = 'http://apis.data.go.kr/B551177/StatusOfParking/getTrackingParking?serviceKey=3BEJFYzZNbYJRrNn4Vmy1iAyZLjxVDPDTbIo%2Fbk1vrGDXFMn%2FDI%2BzUaMZNKea8x7tpXfWI3GX9c6H5Eowq03qw%3D%3D&numOfRows=20&pageNo=1&type=xml'
        res_body_incheon = urlopen(url_incheon).read()
        soup_incheon = BeautifulSoup(res_body_incheon, 'html.parser')
        items_incheon = soup_incheon.findAll('item')
        for item in items_incheon:
            item = re.sub('<.*?>', '|', str(item))
            print(item)
            parsed = item.split('||')
            try:
                total_spaces = int(parsed[4])
                used_spaces = int(parsed[3])
                remaining_spaces = total_spaces - used_spaces
                utilization_rate = (used_spaces / total_spaces) * 100

                row = '주차구역: '+parsed[2]+'/'+' 총 주차공간: '+str(total_spaces)+'/ 사용 중인 주차공간: '+str(used_spaces)+ '/ 남은 주차 공간: '+str(remaining_spaces)+ '/ 만차율: {:.1f}%'.format(utilization_rate).strip()                        
                #인천공항
            except IndexError:
                row = item.replace('|', ',')

            if row:
                res_list.append(row.strip())
        return res_list

def sendMessage(user, msg):
    try:
        bot.sendMessage(user, msg)
    except:
        traceback.print_exc(file=sys.stdout)

def run(date_param, param='11710'):
    conn = sqlite3.connect('../logs.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS logs( user TEXT, log TEXT, PRIMARY KEY(user, log) )')
    conn.commit()

    user_cursor = sqlite3.connect('../users.db').cursor()
    user_cursor.execute('CREATE TABLE IF NOT EXISTS users( user TEXT, location TEXT, PRIMARY KEY(user, location) )')
    user_cursor.execute('SELECT * from users')

    for data in user_cursor.fetchall():
        user, param = data[0], data[1]
        print(user, date_param, param)
        res_list = getData( param, date_param )
        msg = ''
        for r in res_list:
            try:
                cursor.execute('INSERT INTO logs (user,log) VALUES ("%s", "%s")'%(user,r))
            except sqlite3.IntegrityError:
                # 이미 해당 데이터가 있다는 것을 의미합니다.
                pass
            else:
                #print( str(datetime.now()).split('.')[0], r )
                if len(r+msg)+1>MAX_MSG_LENGTH:
                    sendMessage( user, msg )
                    msg = r+'\n'
                else:
                    msg += r+'\n'
        if msg:
            sendMessage( user, msg )
    conn.commit()

if __name__=='__main__':
    today = date.today()
    current_month = today.strftime('%Y%m')

    print( '[',today,']received token :', TOKEN )

    pprint( bot.getMe() )

    run(current_month)