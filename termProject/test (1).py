from tkinter import *
from tkinter.ttk import *
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
import map_view_demo
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
            parking_rate = fulloccupancyrate.calculate(int(total_space), remaining_parking_space)

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
            #tkinter.messagebox.showerror("Error", "Invalid address")
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

map_label=Label(another_frame,text="지도")
map_label.pack()
#--------------



map_widget = TkinterMapView(another_frame, width=800, height=600, corner_radius=0)
map_widget.place(x=0, y=30)

search_bar = Entry(another_frame, width=50)
search_bar.place(x=900, y=0)
search_bar.focus()

search_bar_button = Button(another_frame, width=8, text="Search", command=search)
search_bar_button.place(x=1280, y=0)

search_bar_clear = Button(another_frame, width=8, text="Clear", command=clear)
search_bar_clear.place(x=1350, y=0)

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

map_widget.set_address("서울")

#--------------
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
combobox1.bind("<<ComboboxSelected>>", update_parking_areas)
combobox1.place(x=20, y=200)

combobox2 = Combobox(main_frame, height=15)
combobox2.config(state='readonly')
combobox2.set("구역을 고르세요")
combobox2.bind("<<ComboboxSelected>>", display_parking_info)
combobox2.place(x=20, y=300)

buttonEmail = Button(main_frame, text="메일", command=lambda: [update_body(), send_email(subject, body, to_email)])
buttonEmail.place(x=20, y=400, width=100, height=50)

label_info = Label(main_frame, text='', font=(15),background='snow')
label_info.place(x=220, y=220)

parking_areas = {}

graph_canvas = Canvas(main_frame, width=1000, height=450, background='snow')
graph_canvas.place(x=550, y=100)

thread = threading.Thread(target=teller.start)
thread.start()

window.mainloop()
