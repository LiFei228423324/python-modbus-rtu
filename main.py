import sys
import time
from socket import *
from threading import Thread

import catch as catch
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QLabel, QPushButton, QTextEdit, QLineEdit
from QCandyUi import CandyWindow
from QCandyUi.CandyWindow import colorful


# PushButton
def click():
    if (isRuning):
        text = tv.toPlainText()
        Thread(target=client.send, args=(text.encode("gbk"),)).start()
    # client.send("你好")


def Recv():
    if(isRuning):
        while True:
            recvData = client.recv(1024)
            print('接受的数据：', recvData.decode('gbk'))
            lable.setText(recvData.decode('gbk'))
    else:print("服务器未连接，即将断开！")

def Data():
    while True:
        time.sleep(1)
        s = edit.text()
        if(s!=""):
            print(s)

isRuning = False

if __name__ == '__main__':
    client = socket(AF_INET, SOCK_STREAM)
    try:
        client.connect(("192.168.0.101", 7777))
        isRuning = True
    except:
        print("未成功连接")


    thread_1 = Thread(target=Recv).start()

    app = QApplication(sys.argv)
    win = QMainWindow()

    win.setGeometry(600, 100, 800, 800)
    win.setWindowTitle("Pyqt5 Hello World!")

    # Lable Text
    lable = QLabel(win)
    lable.setText("你好世界")
    lable.move(20, 20)

    # Button
    button = QPushButton(win)
    button.resize(200, 100)
    button.setText("Send")
    button.move(100, 100)
    button.clicked.connect(click)

    tv = QTextEdit(win)
    tv.move(200, 200)
    tv.resize(300, 50)

    edit = QLineEdit(win)
    edit.resize(100, 30)
    edit.move(400, 100)

    thread_2 = Thread(target=Data).start()

    win.show()
    sys.exit(app.exec_())
