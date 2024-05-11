from tkinter import *
from tkinter import font

#병원정보 서비스 예제
#https://apis.data.go.kr/B551182/hospInfoServicev2/getHospBasisList?serviceKey=sea100UMmw23Xycs33F1EQnumONR%2F9ElxBLzkilU9Yr1oT4TrCot8Y2p0jyuJP72x9rG9D8CN5yuEs6AS2sAiw%3D%3D&pageNo=1&numOfRows=10&sidoCd=110000&sgguCd=110019
'''
import http.client
conn = http.client.HTTPConnection("apis.data.go.kr")
conn.request("GET","/B551182/hospInfoServicev2/getHospBasisList?serviceKey=sea100UMmw23Xycs33F1EQnumONR%2F9ElxBLzkilU9Yr1oT4TrCot8Y2p0jyuJP72x9rG9D8CN5yuEs6AS2sAiw%3D%3D&pageNo=1&numOfRows=10&sidoCd=110000&sgguCd=110019")
req = conn.getresponse()
print(req.status,req.reason)
print(req.read().decode('utf-8'))
'''
g_Tk = Tk()
g_Tk.geometry("400x600+750+200")
DataList = []
url = "apis.data.go.kr"
query = "/B551182/hospInfoServicev2/getHospBasisList?serviceKey=sea100UMmw23Xycs33F1EQnumONR%2F9ElxBLzkilU9Yr1oT4TrCot8Y2p0jyuJP72x9rG9D8CN5yuEs6AS2sAiw%3D%3D&pageNo=1&numOfRows=10&sidoCd=110000&sgguCd="

# 지역코드
SGGUCD =   [['110001','강남구'],
            ['110002','강동구'],
            ['110003','강서구'],
            ['110004','관악구'],
            ['110005','구로구'],
            ['110006','도봉구'],
            ['110007','동대문구'],
            ['110008','동작구']]

def InitTopText():
    TempFont = font.Font(g_Tk, size=20, weight='bold', family = 'Consolas')
    MainText = Label(g_Tk, font = TempFont, text="[서울시 병원 검색 App]")
    MainText.pack()
    MainText.place(x=20)


def InitSearchListBox():
    global SearchListBox
    ListBoxScrollbar = Scrollbar(g_Tk)
    ListBoxScrollbar.pack()
    ListBoxScrollbar.place(x=150, y=50)

    TempFont = font.Font(g_Tk, size=15, weight='bold', family='Consolas')
    SearchListBox = Listbox(g_Tk, font=TempFont, activestyle='none',
                            width=10, height=5, borderwidth=12, relief='ridge',
                            yscrollcommand=ListBoxScrollbar.set)

    for i in range(8):
        SearchListBox.insert(i+1, SGGUCD[i][1]) #8개 지역 리스트 삽입

    SearchListBox.pack()
    SearchListBox.place(x=10, y=50)

    ListBoxScrollbar.config(command=SearchListBox.yview)


def InitSearchButton():
    TempFont = font.Font(g_Tk, size=12, weight='bold', family = 'Consolas')
    SearchButton = Button(g_Tk, font = TempFont, text="검색",  command=SearchButtonAction)
    SearchButton.pack()
    SearchButton.place(x=330, y=110)


def SearchButtonAction():
    global SearchListBox

    RenderText.configure(state='normal')
    RenderText.delete(0.0, END)
    iSearchIndex = SearchListBox.curselection()[0]

    sgguCD = SGGUCD[iSearchIndex][0] #시구 코드 8개구
    Search(sgguCD)

    RenderText.configure(state='disabled')

def Search(sgguCD):
    import http.client
    conn = http.client.HTTPConnection(url)
    conn.request("GET", query+sgguCD)

    req = conn.getresponse()

    global DataList
    DataList.clear()

    if req.status == 200:
        strXml = req.read().decode('utf-8')
        #print(strXml)
        from xml.etree import ElementTree
        tree = ElementTree.fromstring(strXml)
        # item 엘리먼트를 가져옵니다.
        itemElements = tree.iter("item")  # return list type
        #print(itemElements)
        for item in itemElements:
            addr = item.find("addr")    #병원주소
            name = item.find("yadmNm")  #병원명
            telno = item.find("telno")  #전화번호
            DataList.append((name.text,addr.text,telno.text))


        for i in range(len(DataList)):
            RenderText.insert(INSERT, "[")
            RenderText.insert(INSERT, i + 1)
            RenderText.insert(INSERT, "] ")
            RenderText.insert(INSERT, "병원명: ")
            RenderText.insert(INSERT, DataList[i][0])
            RenderText.insert(INSERT, "\n")
            RenderText.insert(INSERT, "주소: ")
            RenderText.insert(INSERT, DataList[i][1])
            RenderText.insert(INSERT, "\n")
            RenderText.insert(INSERT, "전화번호: ")
            RenderText.insert(INSERT, DataList[i][2])
            RenderText.insert(INSERT, "\n\n")


def InitRenderText():
    global RenderText

    RenderTextScrollbar = Scrollbar(g_Tk)
    RenderTextScrollbar.pack()
    RenderTextScrollbar.place(x=375, y=200)

    TempFont = font.Font(g_Tk, size=10, family='Consolas')
    RenderText = Text(g_Tk, width=49, height=27, borderwidth=12, relief='ridge', yscrollcommand=RenderTextScrollbar.set)
    RenderText.pack()
    RenderText.place(x=10, y=215)
    RenderTextScrollbar.config(command=RenderText.yview)
    RenderTextScrollbar.pack(side=RIGHT, fill=BOTH)

    RenderText.configure(state='disabled')


InitTopText()
InitSearchListBox()
InitSearchButton()
InitRenderText()


g_Tk.mainloop()