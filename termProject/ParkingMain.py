from tkinter import *
from tkinter.ttk import *
from bs4 import BeautifulSoup
import requests
from datetime import datetime


#GMP-김포국제공항, PUS-김해국제공항, CJU-제주국제공항,TAE-대구국제공항
#KWJ-광주공항, RSU-여수공항, USN-울산공항,KUV-군산공항, WJU-원주공항, CJJ-청주국제공항


url = 'http://openapi.airport.co.kr/service/rest/AirportParking/airportparkingRT'
params ={'serviceKey' : '3BEJFYzZNbYJRrNn4Vmy1iAyZLjxVDPDTbIo/bk1vrGDXFMn/DI+zUaMZNKea8x7tpXfWI3GX9c6H5Eowq03qw==', 'schAirportCode' : 'GMP' }

response = requests.get(url, params=params)
print(response.content)



window=Tk()
window.title("Parking System")
window.geometry("800x600")

label=Label(window, text="실시간 공항 주차 정보 서비스",font=('맑은 고딕',16,'bold'))
label.pack()

#labelTime=Label(window, Text)



combobox=Combobox(window, height=15)
combobox.config(state='readonly')
combobox.set("공항을 고르세요")
combobox.pack(side="left")


window.mainloop()