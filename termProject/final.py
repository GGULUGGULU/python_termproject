from tkinter import *
from tkinter.ttk import *
import tkinter.messagebox
import requests
from xml.etree import ElementTree
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import threading
import teller
from PIL import Image, ImageTk
import os
import pickle

from tkintermapview import TkinterMapView

import fulloccupancyrate  # 만차율 계산 c/c++라이브러리 연동
'''
global marker_list
global marker_path
global search_marker
global search_in_progress
marker_list = []
marker_path = None
search_marker = None
search_in_progress = False
'''

def update_parking_areas(event):
    selected_airport = combobox1.get()
    airport_code = [code for code, name in airport_codes.items() if name == selected_airport][0]

    # 한국공항공사_전국공항 실시간 주차정보
    url1 = 'http://openapi.airport.co.kr/service/rest/AirportParking/airportparkingRT'
    params1 = {'serviceKey': service_key, 'schAirportCode': airport_code}
    react1 = requests.get(url1, params=params1)

    # 인천국제공항공사_주차 정보
    url2 = 'http://apis.data.go.kr/B551177/StatusOfParking/getTrackingParking'
    params2 = {'serviceKey': service_key, 'numOfRows': '20', 'pageNo': '1', 'type': 'xml'}
    react2 = requests.get(url2, params=params2)

    # 한국공항공사_전국공항 주차요금
    url3 = 'http://openapi.airport.co.kr/service/rest/AirportParkingFee/parkingfee'
    params3 = {'serviceKey': service_key, 'airport_code': airport_code}
    react3 = requests.get(url3, params=params3)

    # 인천국제공항공사_주차장별 요금 부과 기준 정보
    url4 = 'http://apis.data.go.kr/B551177/ParkingChargeInfo'
    params4 = {'serviceKey': service_key, 'airport_code': airport_code}
    react4 = requests.get(url4, params=params4)

    parking_areas.clear()
    parking_area = []
    parking_area_name_combo1 = []
    parking_area_remaining_combo1 = []

    if react1.status_code == 200 and selected_airport != 'ICN-인천국제공항':
        root1 = ElementTree.fromstring(react1.content)
        for item in root1.findall('.//item'):
            parking_area = item.find('parkingAirportCodeName').text
            total_space = item.find('parkingFullSpace').text if item.find('parkingFullSpace') is not None else '정보 없음'
            remaining_space = item.find('parkingIstay').text if item.find('parkingIstay') is not None else '정보 없음'
            parking_info = {
                'parking_name': parking_area,
                'total_space': total_space,
                'remaining_space': remaining_space
            }
            # 그래프
            parking_areas[parking_area] = parking_info
            parking_area_name_combo1.append(parking_area)
            parking_area_remaining_combo1.append(int(total_space) - int(remaining_space))
        graph_canvas.delete('all')
        max_remaining_space = max(parking_area_remaining_combo1)
        if max_remaining_space == 0:
            max_remaining_space = 1
        bar_width = 20
        x_gap = 30
        x0 = 60
        y0 = 250
        for i in range(len(parking_area_name_combo1)):
            x1 = x0 + i * (bar_width + x_gap)
            y1 = y0 - 200 * parking_area_remaining_combo1[i] / max_remaining_space
            graph_canvas.create_rectangle(x1, y1, x1 + bar_width, y0, fill='light pink')
            graph_canvas.create_text(x1 + bar_width / 2, y0 + 100, text=parking_area_name_combo1[i], anchor='n', angle=90)
            graph_canvas.create_text(x1 + bar_width / 2, y1 - 10, text=parking_area_remaining_combo1[i], anchor='s')

    elif react2.status_code == 200 and selected_airport == 'ICN-인천국제공항':
        root2 = ElementTree.fromstring(react2.content)
        for item in root2.findall('.//item'):
            parking_area = item.find('floor').text
            total_space = item.find('parkingarea').text if item.find('parkingarea') is not None else '정보 없음'
            remaining_space = item.find('parking').text if item.find('parking') is not None else '정보 없음'
            parking_info = {
                'parking_name': parking_area,
                'total_space': total_space,
                'remaining_space': remaining_space
            }
            # 그래프
            parking_areas[parking_area] = parking_info
            parking_area_name_combo1.append(parking_area)
            parking_area_remaining_combo1.append(int(total_space) - int(remaining_space))
        graph_canvas.delete('all')
        max_remaining_space = max(parking_area_remaining_combo1)
        if max_remaining_space == 0:
            max_remaining_space = 1
        bar_width = 20
        x_gap = 30
        x0 = 60
        y0 = 250
        for i in range(len(parking_area_name_combo1)):
            x1 = x0 + i * (bar_width + x_gap)
            y1 = y0 - 200 * parking_area_remaining_combo1[i] / max_remaining_space
            graph_canvas.create_rectangle(x1, y1, x1 + bar_width, y0, fill='light pink')
            graph_canvas.create_text(x1 + bar_width / 2, y0 + 100, text=parking_area_name_combo1[i], anchor='n', angle=90)
            graph_canvas.create_text(x1 + bar_width / 2, y1 - 10, text=parking_area_remaining_combo1[i], anchor='s')

    if not parking_areas:
        combobox2['values'] = []
        combobox2.set("정보를 가져올 수 없습니다")
    else:
        combobox2['values'] = list(parking_areas.keys())
        combobox2.set("구역을 고르세요")
def display_parking_info(event):
    total_space = 0
    remaining_space = 0
    selected_area = combobox2.get()
    latNlon={
        '김포국제공항': '37.5657339, 126.8013067',
        '국내선 제1주차장':'37.5599088,126.8045184',
        '국내선 제2주차장':'37.5580888,126.8073806',
        '국제선 지하':'37.5648768,126.8021283',
        '국제선 주차빌딩':'37.5648768,126.8021283',
        '화물청사':'37.553386,126.811351',
        #------김포------
        '김해국제공항':'35.1728688,128.9471783',
        'P3여객(화물)':'35.1786538,128.9501167',
        '여객주차장(P1+P2)':'35.173886,128.948987',
        #------김해------
        '제주국제공항':'33.5070772,126.4934311',
        'P1주차장':'33.5045273,126.495835',
        'P2장기주차장':'33.5045273,126.495835',
        '화물주차장':'33.5060124,126.4987847',
        #------제주------
        '대구국제공항':'35.899067,128.639159',
        '여객주차장':'35.8993791,128.637196',
        '화물주차장':'35.8991797,128.6380648',
        #------대구------
        '광주공항':'35.1398831,126.81078',
        '여객주차장(제1+제2)':'35.1406269,126.8100525',
        #------광주------
        '여수공항':'34.8401522,127.6140359',
        '여객주차장':'34.8400345,127.6132359',#
        #------여수------
        '울산공항':'35.5929642,129.3557708',
        '여객주차장':'35.5940067,129.3564615',#
        #------울산------
        '군산공항':'35.9259206,126.6156607',
        '여객주차장':'35.9267451,126.6157272',#
        #------군산------
        '원주공항':'37.4592324,127.9771537',
        '여객주차장':'37.4588026,127.977656',#
        #------원주------
        '청주국제공항':'36.7219682,127.4958842',
        '여객 제1주차장':'36.7227417,127.4952786',
        '여객 제2주차장':'36.7227417,127.4952786',
        '여객 제3주차장':'36.7227417,127.4952786',
        '여객 제4주차장':'36.725765,127.5003441',
        #------청주------
        '인천국제공항':'37.458666,126.4419679',
        'T1 장기 P2 주차장':'37.4440157,126.452802',
        'T1 장기 P3 주차장':'37.4447875,126.4577912',
        'T1 장기 P4 주차장':'37.4418634,126.452749',
        'T1 P5 예약주차장':'37.4412859,126.4561102',
        'T2 장기 주차장':'37.4703,126.4336',
        'T2 예약 주차장':'37.4680, 126.4370',
        'T1 단기주차장지상층':'37.4602,126.4407',
        'T1 단기주차장지하1층':'37.4602,126.4407',
        'T1 단기주차장지하2층':'37.4602,126.4407',
        'T2 단기주차장지상1층':'37.46890554,126.4323741',
        'T2 단기주차장지상2층':'37.46890554,126.4323741',
        'T2 단기주차장지상3층':'37.46890554,126.4323741',
        'T2 단기주차장지상4층':'37.46890554,126.4323741',
        'T2 단기주차장지하M층':'37.46890554,126.4323741',
        'T1 장기 P1 주차장':'37.44649, 126.4564',
        'T1 장기 P1 주차타워':'37.446667, 126.455281',
        'T1 장기 P2 주차타워':'37.445329, 126.455273',
        #------인천------
        '여객주차장':'34.99362514,126.3895907',
        #------무안------
        '여객주차창':'35.09291434,128.0872057',
        #------사천------
        '여객주차장':'38.05794534,128.6622425'
        #------양양------
    }
    
    if selected_area in parking_areas:
        info = parking_areas[selected_area]
        total_space = info['total_space']
        remaining_space = info['remaining_space']
        if total_space.isdigit() and remaining_space.isdigit():
            remaining_parking_space = int(total_space) - int(remaining_space)
            parking_rate = fulloccupancyrate.calculate(int(total_space),int(remaining_space))

            label_info.config(text=f"주차 구역: {selected_area}\n\n총 주차 공간: {total_space} 대\n\n사용 중인 주차 공간: {remaining_space} 대\n\n남은 주차 공간: {remaining_parking_space} 대\n\n만차율: {parking_rate:.2f}%")
        else:
            label_info.config(text="정보를 가져올 수 없습니다")
        if combobox2.get() == "화물주차장":
            if combobox1.get() =="CJU-제주국제공항":
                combo_search('33.5060124,126.4987847')
            elif combobox1.get() =="TAE-대구국제공항":
                combo_search('35.8991797,128.6380648')
            
        if combobox2.get() == "여객주차장":
            if combobox1.get() =="TAE-대구국제공항":
                combo_search('35.8993791,128.637196')
                return
            elif combobox1.get() =="RSU-여수공항":
                combo_search('34.8400345,127.6132359')
                return
            elif combobox1.get() =="USN-울산공항":
                combo_search('35.5940067,129.3564615')
                return
            elif combobox1.get() =="KUV-군산공항":
                combo_search('35.9267451,126.6157272')
                return
            elif combobox1.get() =="WJU-원주공항":
                combo_search('37.4588026,127.977656')
                return
            elif combobox1.get() =="MWX-무안국제공항":
                combo_search('37.4588026,127.977656')
                return
            elif combobox1.get() =="HIN-사천공항":
                combo_search('35.09291434,128.0872057')
                return
            elif combobox1.get() =="YNY-양양국제공항":
                combo_search('38.05794534,128.6622425')
                return
                
            
        if combobox2.get() in latNlon:
            combo_search(latNlon[combobox2.get()])
    else:
        label_info.config(text="정보를 가져올 수 없습니다")

def update_clock():
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    clock_label.config(text=current_time)
    clock_label.after(1000, update_clock)

def update_body():
    global body
    selected_area = combobox2.get()

    if selected_area in parking_areas:
        info = parking_areas[selected_area]
        total_space = info['total_space']
        remaining_space = info['remaining_space']

        if total_space.isdigit() and remaining_space.isdigit():
            remaining_parking_space = int(total_space) - int(remaining_space)
            parking_rate = fulloccupancyrate.calculate(int(total_space),int(remaining_space))

            body = f"공항: {combobox1.get()}\n\n주차 구역: {selected_area}\n\n총 주차 공간: {total_space} 대\n\n사용 중인 주차 공간: {remaining_space} 대\n\n남은 주차 공간: {remaining_parking_space} 대\n\n만차율: {parking_rate:.2f}%"
        else:
            body = "정보를 가져올 수 없습니다"
    else:
        body = "정보를 가져올 수 없습니다"

def send_email(subject, body, to_email):
    gmail_user = 'qkrdlf8219@gmail.com'
    gmail_password='opir webo truh thda'

    # 이메일 구성
    msg = MIMEMultipart()
    msg['From'] = gmail_user
    msg['To'] = to_email
    msg['Subject'] = subject

    # 이메일 본문 추가
    msg.attach(MIMEText(body, 'plain'))

    # 이메일 서버를 통해 이메일 전송
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(gmail_user, gmail_password)
    text = msg.as_string()
    server.sendmail(gmail_user, to_email, text)
    server.quit()
    subject=""
    print("button click")

def load_images(image_folder):
    image_files = [os.path.join(image_folder, f) for f in os.listdir(image_folder) if f.endswith(('png', 'jpg', 'jpeg', 'gif'))]
    image_files.sort()  # 이미지 파일 이름순으로 정렬
    images = [ImageTk.PhotoImage(Image.open(img)) for img in image_files]
    return images

def update_image(label, images, delay, index):
    label.config(image=images[index])
    index +=1
    if index == len(images):
        index = 0
    label.after(delay, update_image, label, images, delay, index)

def combo_search(str):
    newstr=str.replace("'","")
    address = newstr
    map_widget.set_address(address, marker=True)
def search(event=None):
    global search_marker
    #search_marker = None
    global search_in_progress
    #search_in_progress = False
    global marker_list
    #marker_list = []
    if not search_in_progress:
        search_in_progress = True
        if search_marker and search_marker not in marker_list:
            map_widget.delete(search_marker)
            search_marker.image = None  # Release image resource
        address = search_bar.get()
        search_marker = map_widget.set_address(address, marker=True)
        if not search_marker:
            #showerror("Error", "Invalid address")
            search_marker = None
        search_in_progress = False

def save_marker():
    if search_marker is not None:
        marker_list_box.insert(END, f"{len(marker_list)}. {search_marker.text}")
        marker_list_box.see(END)
        marker_list.append(search_marker)

def clear_marker_list():
    for marker in marker_list:
        map_widget.delete(marker)
        marker.image = None  # Release image resource

    marker_list_box.delete(0, END)
    marker_list.clear()
    connect_marker()

def connect_marker():
    global marker_path
    #marker_path = None
    position_list = [marker.position for marker in marker_list]

    if marker_path is not None:
        map_widget.delete(marker_path)

    if position_list:
        marker_path = map_widget.set_path(position_list)

def clear():
    global search_marker
    search_marker = None
    search_bar.delete(0, END)
    if search_marker:
        map_widget.delete(search_marker)
        search_marker.image = None  # Release image resource
        search_marker = None
    
#------------------------bookmark    
def bookmark_update_parking_areas():
    selected_airport = combobox1.get()
    airport_code = [code for code, name in airport_codes.items() if name == selected_airport][0]

    # 한국공항공사_전국공항 실시간 주차정보
    url1 = 'http://openapi.airport.co.kr/service/rest/AirportParking/airportparkingRT'
    params1 = {'serviceKey': service_key, 'schAirportCode': airport_code}
    react1 = requests.get(url1, params=params1)

    # 인천국제공항공사_주차 정보
    url2 = 'http://apis.data.go.kr/B551177/StatusOfParking/getTrackingParking'
    params2 = {'serviceKey': service_key, 'numOfRows': '20', 'pageNo': '1', 'type': 'xml'}
    react2 = requests.get(url2, params=params2)

    # 한국공항공사_전국공항 주차요금
    url3 = 'http://openapi.airport.co.kr/service/rest/AirportParkingFee/parkingfee'
    params3 = {'serviceKey': service_key, 'airport_code': airport_code}
    react3 = requests.get(url3, params=params3)

    # 인천국제공항공사_주차장별 요금 부과 기준 정보
    url4 = 'http://apis.data.go.kr/B551177/ParkingChargeInfo'
    params4 = {'serviceKey': service_key, 'airport_code': airport_code}
    react4 = requests.get(url4, params=params4)

    parking_areas.clear()
    parking_area = []
    parking_area_name_combo1 = []
    parking_area_remaining_combo1 = []

    if react1.status_code == 200 and selected_airport != 'ICN-인천국제공항':
        root1 = ElementTree.fromstring(react1.content)
        for item in root1.findall('.//item'):
            parking_area = item.find('parkingAirportCodeName').text
            total_space = item.find('parkingFullSpace').text if item.find('parkingFullSpace') is not None else '정보 없음'
            remaining_space = item.find('parkingIstay').text if item.find('parkingIstay') is not None else '정보 없음'
            parking_info = {
                'parking_name': parking_area,
                'total_space': total_space,
                'remaining_space': remaining_space
            }
            # 그래프
            parking_areas[parking_area] = parking_info
            parking_area_name_combo1.append(parking_area)
            parking_area_remaining_combo1.append(int(total_space) - int(remaining_space))
        graph_canvas.delete('all')
        max_remaining_space = max(parking_area_remaining_combo1)
        if max_remaining_space == 0:
            max_remaining_space = 1
        bar_width = 20
        x_gap = 30
        x0 = 60
        y0 = 250
        for i in range(len(parking_area_name_combo1)):
            x1 = x0 + i * (bar_width + x_gap)
            y1 = y0 - 200 * parking_area_remaining_combo1[i] / max_remaining_space
            graph_canvas.create_rectangle(x1, y1, x1 + bar_width, y0, fill='light pink')
            graph_canvas.create_text(x1 + bar_width / 2, y0 + 100, text=parking_area_name_combo1[i], anchor='n', angle=90)
            graph_canvas.create_text(x1 + bar_width / 2, y1 - 10, text=parking_area_remaining_combo1[i], anchor='s')

    elif react2.status_code == 200 and selected_airport == 'ICN-인천국제공항':
        root2 = ElementTree.fromstring(react2.content)
        for item in root2.findall('.//item'):
            parking_area = item.find('floor').text
            total_space = item.find('parkingarea').text if item.find('parkingarea') is not None else '정보 없음'
            remaining_space = item.find('parking').text if item.find('parking') is not None else '정보 없음'
            parking_info = {
                'parking_name': parking_area,
                'total_space': total_space,
                'remaining_space': remaining_space
            }
            # 그래프
            parking_areas[parking_area] = parking_info
            parking_area_name_combo1.append(parking_area)
            parking_area_remaining_combo1.append(int(total_space) - int(remaining_space))
        graph_canvas.delete('all')
        max_remaining_space = max(parking_area_remaining_combo1)
        if max_remaining_space == 0:
            max_remaining_space = 1
        bar_width = 20
        x_gap = 30
        x0 = 60
        y0 = 250
        for i in range(len(parking_area_name_combo1)):
            x1 = x0 + i * (bar_width + x_gap)
            y1 = y0 - 200 * parking_area_remaining_combo1[i] / max_remaining_space
            graph_canvas.create_rectangle(x1, y1, x1 + bar_width, y0, fill='light pink')
            graph_canvas.create_text(x1 + bar_width / 2, y0 + 100, text=parking_area_name_combo1[i], anchor='n', angle=90)
            graph_canvas.create_text(x1 + bar_width / 2, y1 - 10, text=parking_area_remaining_combo1[i], anchor='s')

    if not parking_areas:
        combobox2['values'] = []
        combobox2.set("정보를 가져올 수 없습니다")
    else:
        combobox2['values'] = list(parking_areas.keys())
        combobox2.set("구역을 고르세요")

def bookmark_display_parking_info():
    total_space = 0
    remaining_space = 0
    selected_area = combobox2.get()
    latNlon={
        '김포국제공항': '37.5657339, 126.8013067',
        '국내선 제1주차장':'37.5599088,126.8045184',
        '국내선 제2주차장':'37.5580888,126.8073806',
        '국제선 지하':'37.5648768,126.8021283',
        '국제선 주차빌딩':'37.5648768,126.8021283',
        '화물청사':'37.553386,126.811351',
        #------김포------
        '김해국제공항':'35.1728688,128.9471783',
        'P3여객(화물)':'35.1786538,128.9501167',
        '여객주차장(P1+P2)':'35.173886,128.948987',
        #------김해------
        '제주국제공항':'33.5070772,126.4934311',
        'P1주차장':'33.5045273,126.495835',
        'P2장기주차장':'33.5045273,126.495835',
        '화물주차장':'33.5060124,126.4987847',
        #------제주------
        '대구국제공항':'35.899067,128.639159',
        '여객주차장':'35.8993791,128.637196',
        '화물주차장':'35.8991797,128.6380648',
        #------대구------
        '광주공항':'35.1398831,126.81078',
        '여객주차장(제1+제2)':'35.1406269,126.8100525',
        #------광주------
        '여수공항':'34.8401522,127.6140359',
        '여객주차장':'34.8400345,127.6132359',#
        #------여수------
        '울산공항':'35.5929642,129.3557708',
        '여객주차장':'35.5940067,129.3564615',#
        #------울산------
        '군산공항':'35.9259206,126.6156607',
        '여객주차장':'35.9267451,126.6157272',#
        #------군산------
        '원주공항':'37.4592324,127.9771537',
        '여객주차장':'37.4588026,127.977656',#
        #------원주------
        '청주국제공항':'36.7219682,127.4958842',
        '여객 제1주차장':'36.7227417,127.4952786',
        '여객 제2주차장':'36.7227417,127.4952786',
        '여객 제3주차장':'36.7227417,127.4952786',
        '여객 제4주차장':'36.725765,127.5003441',
        #------청주------
        '인천국제공항':'37.458666,126.4419679',
        'T1 장기 P2 주차장':'37.4440157,126.452802',
        'T1 장기 P3 주차장':'37.4447875,126.4577912',
        'T1 장기 P4 주차장':'37.4418634,126.452749',
        'T1 P5 예약주차장':'37.4412859,126.4561102',
        'T2 장기 주차장':'37.4703,126.4336',
        'T2 예약 주차장':'37.4680, 126.4370',
        'T1 단기주차장지상층':'37.4602,126.4407',
        'T1 단기주차장지하1층':'37.4602,126.4407',
        'T1 단기주차장지하2층':'37.4602,126.4407',
        'T2 단기주차장지상1층':'37.46890554,126.4323741',
        'T2 단기주차장지상2층':'37.46890554,126.4323741',
        'T2 단기주차장지상3층':'37.46890554,126.4323741',
        'T2 단기주차장지상4층':'37.46890554,126.4323741',
        'T2 단기주차장지하M층':'37.46890554,126.4323741',
        'T1 장기 P1 주차장':'37.44649, 126.4564',
        'T1 장기 P1 주차타워':'37.446667, 126.455281',
        'T1 장기 P2 주차타워':'37.445329, 126.455273',
        #------인천------
        '여객주차장':'34.99362514,126.3895907',
        #------무안------
        '여객주차창':'35.09291434,128.0872057',
        #------사천------
        '여객주차장':'38.05794534,128.6622425'
        #------양양------
    }

    if selected_area in parking_areas:
        info = parking_areas[selected_area]
        total_space = info['total_space']
        remaining_space = info['remaining_space']
        if total_space.isdigit() and remaining_space.isdigit():
            remaining_parking_space = int(total_space) - int(remaining_space)
            parking_rate = fulloccupancyrate.calculate(int(total_space), remaining_parking_space)

            label_info.config(text=f"주차 구역: {selected_area}\n\n총 주차 공간: {total_space} 대\n\n사용 중인 주차 공간: {remaining_space} 대\n\n남은 주차 공간: {remaining_parking_space} 대\n\n만차율: {parking_rate:.2f}%")
        else:
            label_info.config(text="정보를 가져올 수 없습니다")
        if combobox2.get() == "화물주차장":
            if combobox1.get() =="CJU-제주국제공항":
                combo_search('33.5060124,126.4987847')
            elif combobox1.get() =="TAE-대구국제공항":
                combo_search('35.8991797,128.6380648')

        if combobox2.get() == "여객주차장":
            if combobox1.get() =="TAE-대구국제공항":
                combo_search('35.8993791,128.637196')
            elif combobox1.get() =="RSU-여수공항":
                combo_search('34.8400345,127.6132359')
            elif combobox1.get() =="USN-울산공항":
                combo_search('35.5940067,129.3564615')
            elif combobox1.get() =="KUV-군산공항":
                combo_search('35.9267451,126.6157272')
            elif combobox1.get() =="WJU-원주공항":
                combo_search('37.4588026,127.977656')
            elif combobox1.get() =="MWX-무안국제공항":
                combo_search('37.4588026,127.977656')
            elif combobox1.get() =="HIN-사천공항":
                combo_search('35.09291434,128.0872057')
            elif combobox1.get() =="YNY-양양국제공항":
                combo_search('38.05794534,128.6622425')

        if combobox2.get() in latNlon:
            combo_search(latNlon[combobox2.get()])
    else:
        label_info.config(text="정보를 가져올 수 없습니다")
        
def bookmark_add(bookmarks, bookmark_lisbox):
    bookmark=combobox1.get()+"~"+combobox2.get()
    bookmarks.append(bookmark)
    update_bookmark_list(bookmarks, bookmark_listbox)
    bookmarks_save(bookmarks)

def bookmarks_load(bookmarks, bookmark_listbox):
    if os.path.exists("bookmarks.txt"):
        with open("bookmarks.txt", "r") as file:
            bookmarks.clear()
            bookmarks.extend([line.strip() for line in file.readlines()])
            update_bookmark_list(bookmarks, bookmark_listbox)

def bookmarks_save(bookmarks):
    with open("bookmarks.txt", "w") as file:
        for bookmark in bookmarks:
            file.write(bookmark + "\n")
        
def bookmark_delete(bookmarks, bookmark_listbox):
    try:
        selected_index = bookmark_listbox.curselection()[0]
        del bookmarks[selected_index]
        update_bookmark_list(bookmarks, bookmark_listbox)
        bookmarks_save(bookmarks)
    except IndexError:
        pass
        #messagebox.showerror("Error", "삭제할 북마크를 선택해주세요.")

def update_bookmark_list(bookmarks, bookmark_listbox):
    bookmark_listbox.delete(0, END)
    for bookmark in bookmarks:
        bookmark_listbox.insert(END, bookmark)
        
def bookmark_data_load():
    try:
        selected_index = bookmark_listbox.curselection()[0]
        selected_bookmark = bookmark_listbox.get(selected_index)
        if '~' in selected_bookmark:
            left, right = selected_bookmark.split('~')
            combobox1.set(left.strip())
            bookmark_update_parking_areas()  # 첫 번째 콤보박스의 값에 따라 함수 호출
            combobox2.set(right.strip())
            bookmark_display_parking_info()  # 두 번째 콤보박스의 값에 따라 함수 호출

    except IndexError:
        pass
        #messagebox.showerror("Error", "북마크를 선택해주세요.")
#---------------------------------------------main-------------------------------------------
marker_list = []
marker_path = None
search_marker = None
search_in_progress = False

window = Tk()
window.title("주차장 현황")
window.geometry("1600x600")

style = Style()
# Set the background color of the Notebook and Frame widgets
#style.theme_use('clam')  # Choose an appropriate theme
style.configure('TNotebook', background='snow')  # Set the background color of the Notebook
style.configure('TFrame', background='snow')  # Set the background color of the Frame

# Create Notebook
notebook = Notebook(window)
notebook.pack(expand=True, fill='both')

# Create main frame
main_frame = Frame(notebook)
notebook.add(main_frame, text="Main")

# Create another tab
another_frame = Frame(notebook)
notebook.add(another_frame, text="Map")

map_label=Label(another_frame,text="지도",background='snow')
map_label.pack()

#-----------------------------------지도-------------------------------------------
map_widget = TkinterMapView(another_frame, width=800, height=600, corner_radius=0)
map_widget.place(x=0, y=30)

search_bar = Entry(another_frame, width=50)
search_bar.place(x=900, y=0)
search_bar.focus()

search_bar_button = Button(another_frame, width=8, text="Search", command=search)
search_bar_button.place(x=1280, y=0)

search_bar_clear = Button(another_frame, width=8, text="Clear", command=clear)
search_bar_clear.place(x=1350, y=0)
'''
marker_list_box = Listbox(another_frame,width=50, height=8)
marker_list_box.place(x=900, y=50)

listbox_button_frame = Frame(another_frame,width=8,height=10)
listbox_button_frame.place(x=1100, y=150)


save_marker_button = Button(another_frame, text="save current marker",
                                         command=save_marker)
save_marker_button.place(x=1350,y=50, width=150, height=50)

clear_marker_button = Button(another_frame, text="clear marker list",
                                          command=clear_marker_list)
clear_marker_button.place(x=1350,y=100, width=150, height=50)

connect_marker_button = Button(another_frame, text="connect marker with path",
                                            command=connect_marker)
connect_marker_button.place(x=1350,y=150, width=150, height=50)
'''
map_widget.set_address("서울")

#--------------------------------------지도-----------------------------------

service_key = '3BEJFYzZNbYJRrNn4Vmy1iAyZLjxVDPDTbIo/bk1vrGDXFMn/DI+zUaMZNKea8x7tpXfWI3GX9c6H5Eowq03qw=='
airport_codes = {
    'GMP': 'GMP-김포국제공항',
    'PUS': 'PUS-김해국제공항',
    'CJU': 'CJU-제주국제공항',
    'TAE': 'TAE-대구국제공항',
    'KWJ': 'KWJ-광주공항',
    'RSU': 'RSU-여수공항',
    'USN': 'USN-울산공항',
    'KUV': 'KUV-군산공항',
    'WJU': 'WJU-원주공항',
    'CJJ': 'CJJ-청주국제공항',
    'MWX': 'MWX-무안국제공항',
    'HIN': 'HIN-사천공항',
    'YNY': 'YNY-양양국제공항',
    'ICN': 'ICN-인천국제공항'
}

label = Label(main_frame, text="실시간 공항주차 시스템", font=(30), padding=20, background='snow')
label.place(x=600, y=20)

clock_label = Label(main_frame, font=('Arial', 15), background='snow')  # 현재시간
clock_label.place(x=1310, y=20)  # 현재시간 위치
update_clock()  # 실시간 업데이트

subject="실시간 주차장 정보"
global body
body=""
to_email="qkrdlf8219@naver.com"

image_folder = 'mm300200'
images = load_images(image_folder)
gif_label = Label(main_frame)
gif_label.place(x=0,y=0, width=300,height=200)
gif_label.images = images
update_image(gif_label, images, 80, 0)

combobox1 = Combobox(main_frame, height=15)
combobox1.config(state='readonly')
combobox1['values'] = list(airport_codes.values())
combobox1.set("공항을 고르세요")
#combobox1.bind("<<ComboboxSelected>>", update_parking_areas)
combobox1.bind("<<ComboboxSelected>>", update_parking_areas)
combobox1.place(x=20, y=220)

combobox2 = Combobox(main_frame, height=15)
combobox2.config(state='readonly')
combobox2.set("구역을 고르세요")
combobox2.bind("<<ComboboxSelected>>", display_parking_info)
combobox2.place(x=20, y=300)

buttonEmail = Button(main_frame, text="메일", command=lambda: [update_body(), send_email(subject, body, to_email)])
buttonEmail.place(x=20, y=350, width=100, height=50)
#-----------------------------북마크
bookmarks=[]
bookmark_listbox=Listbox(main_frame,height=6,width=40)
bookmark_listbox.place(x=220,y=410)

button_bookmark_add=Button(main_frame,text="추가",command=lambda:bookmark_add(bookmarks,bookmark_listbox))
button_bookmark_add.place(x=20, y=410, width=100, height=30)

button_bookmark_load=Button(main_frame,text="정보 불러오기",command=lambda:bookmark_data_load())
button_bookmark_load.place(x=20, y=450, width=100, height=30)

button_bookmark_del=Button(main_frame,text="삭제",command=lambda:bookmark_delete(bookmarks,bookmark_listbox))
button_bookmark_del.place(x=20, y=490, width=100, height=30)

#----------------------------------------
label_info = Label(main_frame, text='', font=(15),background='snow')
label_info.place(x=220, y=220)
parking_areas = {}

graph_canvas = Canvas(main_frame, width=1000, height=450, background='snow')
graph_canvas.place(x=550, y=100)

thread = threading.Thread(target=teller.start)
thread.start()

bookmarks_load(bookmarks, bookmark_listbox)

window.mainloop()