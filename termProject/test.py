from tkinter import *
from tkinter.ttk import *
import requests
from xml.etree import ElementTree
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email import encoders

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
    url3= 'http://openapi.airport.co.kr/service/rest/AirportParkingFee/parkingfee'
    params3 = {'serviceKey': service_key, 'airport_code': airport_code}
    react3 = requests.get(url3, params=params3)

    # 인천국제공항공사_주차장별 요금 부과 기준 정보
    url4= 'http://apis.data.go.kr/B551177/ParkingChargeInfo'
    params4 = {'serviceKey': service_key, 'airport_code': airport_code}
    react4 = requests.get(url4, params=params4)

    parking_areas.clear()
    parking_area=[]
    parking_area_name_combo1=[]
    parking_area_remaining_combo1=[]

    if react1.status_code==200 and selected_airport!='ICN-인천국제공항':
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
            #그래프
            parking_areas[parking_area] = parking_info
            parking_area_name_combo1.append(parking_area)
            parking_area_remaining_combo1.append(int(total_space)-int(remaining_space))
        graph_canvas.delete('all')
        max_remaining_space = max(parking_area_remaining_combo1)
        if max_remaining_space ==0:
            max_remaining_space=1
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
            #그래프
            parking_areas[parking_area] = parking_info
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

    if selected_area in parking_areas:
        info = parking_areas[selected_area]
        total_space = info['total_space']
        remaining_space = info['remaining_space']

        if total_space.isdigit() and remaining_space.isdigit():
            remaining_parking_space = int(total_space) - int(remaining_space)
            parking_rate=int(int(remaining_space)/int(total_space) * 100)

            label_info.config(text=f"주차 구역: {selected_area}\n\n총 주차 공간: {total_space} 대\n\n사용 중인 주차 공간: {remaining_space} 대\n\n남은 주차 공간: {remaining_parking_space} 대\n\n만차율: {parking_rate}%")
            body=f"주차 구역: {selected_area}\n\n총 주차 공간: {total_space} 대\n\n사용 중인 주차 공간: {remaining_space} 대\n\n남은 주차 공간: {remaining_parking_space} 대\n\n만차율: {parking_rate}%"
            #print(body)
            #남은 주차 공간이 음수나올시 불법주차
        else:
            label_info.config(text="정보를 가져올 수 없습니다")
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
            parking_rate = int(int(remaining_space) / int(total_space) * 100)

            body = f"주차 구역: {selected_area}\n\n총 주차 공간: {total_space} 대\n\n사용 중인 주차 공간: {remaining_space} 대\n\n남은 주차 공간: {remaining_parking_space} 대\n\n만차율: {parking_rate}%"
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

window = Tk()
window.title("주차장 현황")
window.geometry("1600x600")

main_canvas = Canvas(window, width=1600, height=600, background='snow')#후보 light pink
main_canvas.place(x=0,y=0)

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

label = Label(window, text="실시간 공항주차 시스템", font=(20),padding=20,background='snow')
label.pack()

clock_label = Label(window, font=('Arial', 15),background='snow')  # 현재시간
clock_label.place(x=1310, y=20)  # 현재시간 위치
update_clock()  # 실시간 업데이트

subject="실시간 주차장 정보"
global body
body=""
to_email="qkrdlf8219@naver.com"

combobox1 = Combobox(window, height=15)
combobox1.config(state='readonly')
combobox1['values'] = list(airport_codes.values())
combobox1.set("공항을 고르세요")
combobox1.bind("<<ComboboxSelected>>", update_parking_areas)
combobox1.place(x=20, y=200)


combobox2 = Combobox(window, height=15)
combobox2.config(state='readonly')
combobox2.set("구역을 고르세요")
combobox2.bind("<<ComboboxSelected>>", display_parking_info)
combobox2.place(x=20, y=300)

buttonEmail = Button(window,text="메일", command=lambda: [update_body(), send_email(subject, body, to_email)])
buttonEmail.place(x=20, y=400,width=100, height=50)

label_info = Label(window, text='', font=(15))
label_info.place(x=220,y=200)

parking_areas = {}

graph_canvas = Canvas(window, width=1000, height=400,background='snow')
graph_canvas.place(x=550, y=100)

window.mainloop()