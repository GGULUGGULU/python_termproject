from tkinter import *
from tkinter.ttk import *
from datetime import datetime
import requests
from xml.etree import ElementTree


def update_parking_areas(event):
    selected_airport = combobox1.get()
    airport_code = [code for code, name in airport_codes.items() if name == selected_airport][0]

    # First API
    url1 = 'http://openapi.airport.co.kr/service/rest/AirportParking/airportparkingRT'
    params1 = {'serviceKey': service_key, 'schAirportCode': airport_code}
    react1 = requests.get(url1, params=params1)

    # Second API
    url2 = 'http://apis.data.go.kr/B551177/StatusOfParking/getParkingInfo'
    params2 = {'serviceKey': service_key, 'airport_code': airport_code}
    react2 = requests.get(url2, params=params2)

    parking_areas = []
    

    if react1.status_code == 200:
        root1 = ElementTree.fromstring(react1.content)
        for item in root1.findall('.//item'):
            parking_area = item.find('parkingAirportCodeName').text
            if parking_area not in parking_areas:
                parking_areas.append(parking_area)

    if react2.status_code == 200:
        root2 = ElementTree.fromstring(react2.content)
        for item in root2.findall('.//item'):
            parking_area = item.find('parkingAirportCodeName').text
            if parking_area not in parking_areas:
                parking_areas.append(parking_area)

    if not parking_areas:
        combobox2['values'] = []
        combobox2.set("정보를 가져올 수 없습니다")
    else:
        combobox2['values'] = parking_areas
        combobox2.set("구역을 고르세요")
        
def update_parking_information(event):
    parking_area_name.set(combobox2.get())

def update_clock():
    current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    clock_label.config(text=current_time)
    clock_label.after(1000, update_clock)
    
window = Tk()
window.title("주차장 현황")
window.geometry("800x600")

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
    'ICN': 'ICN-인천국제공항'
}
#전역변수는 라벨텍스트 변경용
global parking_area_name    #주차장 이름
global parking_area_full_rate   #주차장 만차율
global parking_area_count   #주차장 총 자리수
global parking_area_available_count     #주차가능 자리수
global parking_area_fee     #주차요금

parking_area_name = StringVar()
parking_area_full_rate = StringVar()
parking_area_count = StringVar()
parking_area_available_count = StringVar()
parking_area_fee = StringVar()


clock_label=Label(window, font=('Arial', 15))#현재시간
clock_label.pack(anchor='ne')#현재시간 위치
update_clock()#실시간 업데이트

label=Label(window, text="실시간 공항주차 시스템", font=(20))
label.pack()

combobox1 = Combobox(window, height=15)
combobox1.config(state='readonly')
combobox1['values'] = list(airport_codes.values())
combobox1.set("공항을 고르세요")
combobox1.bind("<<ComboboxSelected>>", update_parking_areas)
combobox1.place(x=0, y=300)

combobox2 = Combobox(window, height=15)
combobox2.config(state='readonly')
combobox2.set("구역을 고르세요")
combobox2.bind("<<ComboboxSelected>>", update_parking_information)
combobox2.place(x=0, y=400)

parking_area_case = Label(window, text='주차장 이름: \n\n만차율: \n\n주차장 총 자리수: \n\n주차된 차량 수: \n\n주차가능 자리 수: \n\n주차요금: ', font=15)
parking_area_case.place(x=200, y=300)

parking_area_information = Label(window, font=15)
parking_area_information['textvariable']=parking_area_name
parking_area_information.place(x=350,y=300)

window.mainloop()