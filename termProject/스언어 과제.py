from tkinter import *
from tkinter.ttk import *
import requests
from xml.etree import ElementTree


def update_parking_areas(event):
    selected_airport = combobox1.get()
    airport_code = [code for code, name in airport_codes.items() if name == selected_airport][0]

    url = 'http://openapi.airport.co.kr/service/rest/AirportParking/airportparkingRT'
    params = {'serviceKey': service_key, 'schAirportCode': airport_code}
    react = requests.get(url, params=params)
    if react.status_code == 200: #http 상태코드 확인
        root = ElementTree.fromstring(react.content)
        parking_areas = []
        for item in root.findall('.//item'): # item 태그요소 찾기
            parking_area = item.find('parkingAirportCodeName').text #태그에서 텍스트 가져옴
            parking_areas.append(parking_area) #area 변수에 저장해서 areas 리스트에 넣어서 저장해줌

        combobox2['values'] = parking_areas
        combobox2.set("구역을 고르세요")
    else:
        combobox2['values'] = []
        combobox2.set("정보를 가져올 수 없습니다")


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
    'CJJ': 'CJJ-청주국제공항'
}

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
