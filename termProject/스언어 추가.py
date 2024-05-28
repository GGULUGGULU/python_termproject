from tkinter import *
from tkinter.ttk import *
import requests
from xml.etree import ElementTree

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

label=Label(window, text="실시간 공항주차 시스템", font=(20))
label.pack()

combobox1 = Combobox(window, height=15)
combobox1.config(state='readonly')
combobox1['values'] = list(airport_codes.values())
combobox1.set("공항을 고르세요")
combobox1.bind("<<ComboboxSelected>>", update_parking_areas)
combobox1.pack(side="left")

combobox2 = Combobox(window, height=15)
combobox2.config(state='readonly')
combobox2.set("구역을 고르세요")
combobox2.pack(side="left")

window.mainloop()
