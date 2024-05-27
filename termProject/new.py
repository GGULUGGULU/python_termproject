from tkinter import *
from tkinter.ttk import *
import requests

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


for code, airport_name in airport_codes.items():
    url = 'http://openapi.airport.co.kr/service/rest/AirportParking/airportparkingRT'
    params = {'serviceKey': service_key, 'schAirportCode': code}
    response = requests.get(url, params=params)
    parking_info = response.text
    print(f"{airport_name} 주차 정보:")
    print(parking_info)
    print("="*50)


combobox = Combobox(window, height=15)
combobox.config(state='readonly')
combobox['values'] = list(airport_codes.values())
combobox.set("공항을 고르세요")
combobox.pack(side="left")

window.mainloop()
