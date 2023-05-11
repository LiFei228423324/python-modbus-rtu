import datetime

import serial
from PyQt5.QtWidgets import *
from threading import Thread
import sys
import glob
from PyQt5.QtGui import QFont
from socket import *
from PyQt5 import QtCore
from serial import *

isRuning = False
is_jiexi = False
is_send = False
is_recv = True
is_one = False
shijian = ""
t = ""


def get_time():
    t = datetime.datetime.now()
    hour = '{}'.format(t.hour)
    min = '{}'.format(t.minute)
    second = '{}'.format(t.second)
    if len(hour) == 1: hour = "0" + hour
    if len(min) == 1: min = "0" + min
    if len(second) == 1: second = "0" + second
    return hour + ":" + min + ":" + second


def crc16(data):
    ls = data.split()
    datas = list(ls)
    crc16 = 0xFFFF
    poly = 0xA001
    for data in datas:
        a = int(data, 16)
        crc16 = a ^ crc16
        for i in range(8):
            if 1 & (crc16) == 1:
                crc16 = crc16 >> 1
                crc16 = crc16 ^ poly
            else:
                crc16 = crc16 >> 1
    crc16 = hex(int(crc16))
    crc16 = crc16[2:].upper()
    length = len(crc16)
    high = crc16[0:length - 2].zfill(2)
    high = str(high)
    low = crc16[length - 2:length].zfill(2)
    low = str(low)
    return low.upper(), high.upper()


def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    global cd, d
    d = QLabel(win)
    d.setText("端口：")
    d.setFont(QFont("Microsoft YaHei", 10, 55))
    d.resize(100, 30)
    d.move(450, 50)

    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []

    cd = QComboBox(win)
    cd.resize(100, 30)
    cd.move(500, 50)
    cd.addItem('COM1')

    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
            cd.addItem(port)
        except (OSError, serial.SerialException):
            pass
    cd.setCurrentIndex(1)


def serial_btl():
    global serbtl, btl
    serbtl = QComboBox(win)
    serbtl.resize(100, 30)
    serbtl.move(700, 50)
    serbtl.addItem('1200')
    serbtl.addItem('4800')
    serbtl.addItem('9600')
    serbtl.addItem('19200')
    serbtl.addItem('38400')
    serbtl.addItem('115200')
    serbtl.addItem('256000')

    serbtl.setCurrentText('9600')

    btl = QLabel(win)
    btl.setText("波特率：")
    btl.setFont(QFont("Microsoft YaHei", 10, 55))
    btl.resize(100, 30)
    btl.move(630, 50)


def devices(tag):
    if (tag == '电机调速器（485型）'):

        # 电机
        l1.setVisible(True)
        l2.setVisible(True)
        edit1.setVisible(True)
        edit2.setVisible(True)
        edit11.setVisible(True)
        edit22.setVisible(True)
        b1.setVisible(True)
        b2.setVisible(True)
        b11.setVisible(True)
        b22.setVisible(True)
        st1.setVisible(True)
        st2.setVisible(True)

        # 二氧化碳
        c.setVisible(False)
        v.setVisible(False)
        co2_data.setVisible(False)
        cha.setVisible(False)


    elif (tag == '二氧化碳变送器（485型）'):

        # 电机
        l1.setVisible(False)
        l2.setVisible(False)
        edit1.setVisible(False)
        edit2.setVisible(False)
        edit11.setVisible(False)
        edit22.setVisible(False)
        b1.setVisible(False)
        b2.setVisible(False)
        b11.setVisible(False)
        b22.setVisible(False)
        st1.setVisible(False)
        st2.setVisible(False)

        # 二氧化碳
        c.setVisible(True)
        v.setVisible(True)
        co2_data.setVisible(True)
        cha.setVisible(True)
    else:
        # 二氧化碳
        l1.setVisible(False)
        l2.setVisible(False)
        edit1.setVisible(False)
        edit2.setVisible(False)
        edit11.setVisible(False)
        edit22.setVisible(False)
        b1.setVisible(False)
        b2.setVisible(False)
        b11.setVisible(False)
        b22.setVisible(False)
        st1.setVisible(False)
        st2.setVisible(False)

        # 电机
        c.setVisible(False)
        v.setVisible(False)
        co2_data.setVisible(False)
        cha.setVisible(False)


def NotOfOther(tag):
    if tag == '串口连接':
        serbtl.setVisible(True)
        cd.setVisible(True)
        tcp_port.setVisible(False)
        tcp_ip.setVisible(False)
        d.setText("串口：")
        btl.setText("波特率：")

    elif tag == 'TCP连接':
        serbtl.setVisible(False)
        cd.setVisible(False)
        tcp_ip.setVisible(True)
        tcp_port.setVisible(True)

        d.setText("IP：")
        btl.setText("端口：")


def click():
    tag = button.text()
    if (tag == '连接'):
        global is_recv
        if (connect.currentText() == '串口连接'):
            try:
                global ser
                ser = serial.Serial(cd.currentText(), serbtl.currentText(), 8, 'N', 1)
                print("串口连接成功!!!")
                button.setText("断开")
                cd.setEnabled(False)
                serbtl.setEnabled(False)
                connect.setEnabled(False)
                is_recv = False
                Thread(target=recv).start()
            except:
                print("串口连接失败！！！！！！！！！！！")

        elif (connect.currentText() == 'TCP连接'):
            try:
                # Thread(target=tcp_connect).start()
                global client
                client = socket(AF_INET, SOCK_STREAM)
                client.connect((tcp_ip.text(), int(tcp_port.text())))
                button.setText("断开")
                print("TCP连接成功！！！")
                connect.setEnabled(False)
                tcp_ip.setEnabled(False)
                tcp_port.setEnabled(False)
                is_recv = False
                Thread(target=recv).start()
            except:
                print("TCP连接失败!!!")

    elif (tag == '断开'):

        button.setText("连接")
        is_recv = True
        if (connect.currentText() == '串口连接'):
            ser.close()
            cd.setEnabled(True)
            serbtl.setEnabled(True)
            connect.setEnabled(True)
            print("断开串口成功！")
        elif (connect.currentText() == "TCP连接"):
            client.close()
            connect.setEnabled(True)
            tcp_ip.setEnabled(True)
            tcp_port.setEnabled(True)
            print("断开TCP连接成功！")


def queding():
    global is_send, is_one, is_jiexi
    if (button.text() == '断开'):
        if (dz1.text() != ''):
            dz1.setEnabled(False)
            device.setEnabled(False)
            submit.setEnabled(False)
            button2.setEnabled(True)

            cha.setEnabled(True)
            is_send = False
            is_jiexi = True

            b1.setEnabled(True)
            b11.setEnabled(True)
            b2.setEnabled(True)
            b22.setEnabled(True)
            st1.setEnabled(True)
            st2.setEnabled(True)


def quxiao():
    global is_send, is_one, is_jiexi
    dz1.setEnabled(True)
    device.setEnabled(True)
    submit.setEnabled(True)
    button2.setEnabled(False)

    cha.setEnabled(False)

    is_jiexi = False
    is_send = not is_send
    is_one = False

    b1.setEnabled(False)
    b11.setEnabled(False)
    b2.setEnabled(False)
    b22.setEnabled(False)
    st1.setEnabled(False)
    st2.setEnabled(False)


def recv():
    while is_recv == False:
        if (connect.currentText() == '串口连接' and ser is not None):
            time.sleep(0.2)
            count = ser.inWaiting()
            if count > 0:
                data = ser.read(count)
            else:
                continue
            print("len:", len(data))

        elif (connect.currentText() == 'TCP连接' and client is not None):
            data = client.recv(1024)
        else:
            data = ""

        if is_jiexi == True:
            if (device.currentText() == '电机调速器（485型）'):
                print("电机控制成功")
            elif (device.currentText() == '二氧化碳变送器（485型）'):
                if (len(data) < 7):
                    continue
                else:
                    low = int(data[4]) & 255
                    high = int(data[3]) & 255
                    res = int((high << 8) + low)
                    v.setText(f"Value:{res}")

        st = ""
        for b in data:
            h = hex(b & 0xff)[2:]
            st = st + (h if len(h) >= 2 else ("0" + h)) + " "

        jieshou.append(f"<font color=\"#000000\">{get_time()}:")
        jieshou.append(f"<font color=\"#0000FF\">{st}</font>")

        print(data)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~电机~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

def dianji1():
    global l1, edit1, b1, edit11, b11, st1

    l1 = QLabel(win)
    l1.setText("电机1：")
    l1.setFont(QFont("Microsoft YaHei", 10, 55))
    l1.resize(100, 30)
    l1.move(70, 150)

    edit1 = QLineEdit(win)
    edit1.resize(100, 30)
    edit1.move(150, 150)
    edit1.setStyleSheet(
        'border-width: 1px;border-style: solid;border-color: rgb(0, 0, 0);background-color: rgb(255, 255, 255);')

    b1 = QPushButton(win)
    b1.resize(60, 32)
    b1.move(290, 150)
    b1.setText('正转')
    b1.clicked.connect(djz1)

    edit11 = QLineEdit(win)
    edit11.resize(100, 30)
    edit11.move(150, 190)
    edit11.setStyleSheet(
        'border-width: 1px;border-style: solid;border-color: rgb(0, 0, 0);background-color: rgb(255, 255, 255);')

    b11 = QPushButton(win)
    b11.resize(60, 32)
    b11.move(290, 190)
    b11.setText('反转')
    b11.clicked.connect(djf1)

    st1 = QPushButton(win)
    st1.resize(60, 32)
    st1.move(360, 150)
    st1.setText("停止")
    st1.clicked.connect(ting1)

    b1.setEnabled(False)
    b11.setEnabled(False)
    st1.setEnabled(False)


def dianji2():
    global l2, edit2, b2, edit22, b22, st2

    l2 = QLabel(win)
    l2.setText("电机2：")
    l2.setFont(QFont("Microsoft YaHei", 10, 55))
    l2.resize(100, 30)
    l2.move(450, 150)

    edit2 = QLineEdit(win)
    edit2.resize(100, 30)
    edit2.move(530, 150)
    edit2.setStyleSheet(
        'border-width: 1px;border-style: solid;border-color: rgb(0, 0, 0);background-color: rgb(255, 255, 255);')

    b2 = QPushButton(win)
    b2.resize(60, 32)
    b2.move(670, 150)
    b2.setText('正转')
    b2.clicked.connect(djz2)

    edit22 = QLineEdit(win)
    edit22.resize(100, 30)
    edit22.move(530, 190)
    edit22.setStyleSheet(
        'border-width: 1px;border-style: solid;border-color: rgb(0, 0, 0);background-color: rgb(255, 255, 255);')

    b22 = QPushButton(win)
    b22.resize(60, 32)
    b22.move(670, 190)
    b22.setText('反转')
    b22.clicked.connect(djf2)

    st2 = QPushButton(win)
    st2.resize(60, 32)
    st2.move(740, 150)
    st2.setText("停止")
    st2.clicked.connect(ting2)

    st2.setEnabled(False)
    b2.setEnabled(False)
    b22.setEnabled(False)


def ting1():
    if len(dz1.text()) == 1:
        s = "0" + dz1.text()
    else:
        s = dz1.text()
    ss = s + " 06 00 05 00 00 "
    low, high = crc16(ss)
    l = int(low, 16)
    h = int(high, 16)
    a = int(dz1.text())
    bytes = bytearray([a, 0x06, 0x00, 0x05, 0x00, 0x00, l, h])
    if (connect.currentText() == '串口连接'):
        if (ser.isOpen()):
            ser.write(bytes)

    elif (connect.currentText() == 'TCP连接'):
        client.send(bytes)
    cmd = ""
    for b in bytes:
        h = hex(b & 0xff)[2:]
        cmd = cmd + (h if len(h) >= 2 else ("0" + h)) + " "

    fasong.append(f"<font color=\"#000000\">{get_time()}:")
    fasong.append(f"<font color=\"#00FF00\">{cmd}</font>")


def ting2():
    if len(dz1.text()) == 1:
        s = "0" + dz1.text()
    else:
        s = dz1.text()
    ss = s + " 06 00 0a 00 00 "
    low, high = crc16(ss)
    l = int(low, 16)
    h = int(high, 16)
    a = int(dz1.text())
    bytes = bytearray([a, 0x06, 0x00, 0x0a, 0x00, 0x00, l, h])
    if (connect.currentText() == '串口连接'):
        if (ser.isOpen()):
            ser.write(bytes)

    elif (connect.currentText() == 'TCP连接'):
        client.send(bytes)
    cmd = ""
    for b in bytes:
        h = hex(b & 0xff)[2:]
        cmd = cmd + (h if len(h) >= 2 else ("0" + h)) + " "

    fasong.append(f"<font color=\"#000000\">{get_time()}:")
    fasong.append(f"<font color=\"#00FF00\">{cmd}</font>")


def djz1():
    a = edit1.text()
    if (a == ''):
        return 0
    z = int(a)
    if (z > 100):
        print("输入的条件错误")
    else:
        if len(dz1.text()) == 1:
            s = "0" + dz1.text()
        else:
            s = dz1.text()

        zz = hex(z)
        ss = s + " 10 00 04 00 02 04 00 00 00 " + str(zz)
        low, high = crc16(ss)
        l = int(low, 16)
        h = int(high, 16)
        a = int(dz1.text())
        bytes = bytearray([a, 0x10, 0x00, 0x04, 0x00, 0x02, 0x04, 0x00, 0x00, 0x00, z, l, h])
        if (connect.currentText() == '串口连接'):
            if (ser.isOpen()):
                ser.write(bytes)

        elif (connect.currentText() == 'TCP连接'):
            client.send(bytes)
        cmd = ""
        for b in bytes:
            h = hex(b & 0xff)[2:]
            cmd = cmd + (h if len(h) >= 2 else ("0" + h)) + " "

        fasong.append(f"<font color=\"#000000\">{get_time()}:")
        fasong.append(f"<font color=\"#00FF00\">{cmd}</font>")

        print("电机1正转:")
        print(z)
    edit1.clear()


def djf1():
    a = edit11.text()
    if (a == ''):
        return 0
    z = int(a)
    if (z > 100):
        print("输入的条件错误")
    else:
        if len(dz1.text()) == 1:
            s = "0" + dz1.text()
        else:
            s = dz1.text()

        zz = hex(z)
        ss = s + " 10 00 04 00 02 04 00 01 00 " + str(zz)
        low, high = crc16(ss)
        l = int(low, 16)
        h = int(high, 16)
        a = int(dz1.text())
        bytes = bytearray([a, 0x10, 0x00, 0x04, 0x00, 0x02, 0x04, 0x00, 0x01, 0x00, z, l, h])
        if (connect.currentText() == '串口连接'):
            if (ser.isOpen()):
                ser.write(bytes)

        elif (connect.currentText() == 'TCP连接'):
            client.send(bytes)
        cmd = ""
        for b in bytes:
            h = hex(b & 0xff)[2:]
            cmd = cmd + (h if len(h) >= 2 else ("0" + h)) + " "

        fasong.append(f"<font color=\"#000000\">{get_time()}:")
        fasong.append(f"<font color=\"#00FF00\">{cmd}</font>")

        print("电机1反转:")
        print(z)
    edit11.clear()


def djz2():
    a = edit2.text()
    if (a == ''):
        return 0
    z = int(a)
    if (z > 100):
        print("输入的条件错误")
    else:
        print("电机2正转:")
        print(z)
    edit2.clear()


def djf2():
    a = edit22.text()
    if (a == ''):
        return 0
    z = int(a)
    if (z > 100):
        print("输入的条件错误")
    else:
        print("电机2反转:")
        print(z)
    edit22.clear()


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~二氧化碳变送器~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

def co2():
    global cha, co2_data, v, c
    c = QLabel(win)
    c.setFont(QFont("Microsoft YaHei", 20, 55))
    c.resize(200, 30)
    c.move(430, 150)
    c.setText("二氧化碳")

    v = QLabel(win)
    v.setFont(QFont("Microsoft YaHei", 10, 55))
    v.resize(100, 30)
    v.move(450, 180)
    v.setText("Value:")

    co2_data = QLabel(win)
    co2_data.setFont(QFont("Microsoft YaHei", 10, 55))
    co2_data.resize(100, 30)
    co2_data.move(500, 180)

    cha = QPushButton(win)
    cha.resize(100, 40)
    cha.move(580, 160)
    cha.setText("获取实时值")
    cha.setEnabled(False)
    cha.clicked.connect(co2_btn)

    c.setVisible(False)
    v.setVisible(False)
    co2_data.setVisible(False)
    cha.setVisible(False)

    c.setVisible(False)
    v.setVisible(False)
    co2_data.setVisible(False)
    cha.setVisible(False)


def co2_btn():
    global is_one
    if is_one == False:
        Thread(target=co2_send).start()
        is_one = True


def co2_send():
    global shijian, t
    while is_send == False:
        if (len(dz1.text()) == 1):
            s = "0" + dz1.text()
        else:
            s = dz1.text()
        ss = s + " 03 00 00 00 01"
        low, high = crc16(ss)
        l = int(low, 16)
        h = int(high, 16)
        a = int(dz1.text())
        bytes = bytearray([a, 0x03, 0x00, 0x00, 0x00, 0x01, l, h])

        if (connect.currentText() == '串口连接'):
            if (ser.isOpen()):
                ser.write(bytes)

        elif (connect.currentText() == 'TCP连接'):
            client.send(bytes)

        cmd = ""
        for b in bytes:
            h = hex(b & 0xff)[2:]
            cmd = cmd + (h if len(h) >= 2 else ("0" + h)) + " "

        # t = " "+get_time() +":"+ "\n" + "   " +cmd
        # shijian = t + shijian
        # '<font color=\"#0000FF\">%s</font>'%t
        fasong.append(f"<font color=\"#000000\">{get_time()}:")
        fasong.append(f"<font color=\"#00FF00\">{cmd}</font>")

        time.sleep(1)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~水浸传感器~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~RGB调光控制器~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~超声波传感器~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~光照噪声变送器~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~多合一传感器~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~百叶箱传感器~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#


def clear_fa():
    fasong.clear()


def clear_jie():
    jieshou.clear()

def setCenter(self):
    screen = QDesktopWidget().screenGeometry()
    size = self.geometry()
    self.move(int((screen.width() - size.width()) / 2), int((screen.height() - size.height()) / 2))


if __name__ == '__main__':

    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    global tcp_ip, tcp_port
    
    # thread_1 = Thread(target=Recv).start()
    # thread_2 = Thread(target=request).start()

    app = QApplication(sys.argv)
    win = QMainWindow()

    win.setGeometry(500, 100, 1000, 800)
    win.setWindowTitle("Sensors")
    setCenter(win)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~第一行~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    connect = QComboBox(win)
    connect.addItem('串口连接')
    connect.addItem('TCP连接')
    connect.resize(100, 30)
    connect.move(150, 50)

    con = QLabel(win)
    con.setText("连接方式：")
    con.setFont(QFont("Microsoft YaHei", 10, 55))
    con.resize(100, 30)
    con.move(70, 50)

    connect.currentIndexChanged.connect(lambda: NotOfOther(connect.currentText()))

    serial_ports()
    serial_btl()

    tcp_ip = QLineEdit(win)
    tcp_ip.resize(100, 30)
    tcp_ip.move(500, 50)
    tcp_ip.setVisible(False)
    tcp_ip.setText("192.168.0.101")

    tcp_port = QLineEdit(win)
    tcp_port.resize(100, 30)
    tcp_port.move(700, 50)
    tcp_port.setVisible(False)
    tcp_port.setText("7777")

    button = QPushButton(win)
    button.resize(70, 32)
    button.setText("连接")
    button.move(850, 50)
    button.clicked.connect(click)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~第二行~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    con = QLabel(win)
    con.setText("设备：")
    con.setFont(QFont("Microsoft YaHei", 10, 55))
    con.resize(100, 30)
    con.move(70, 100)

    device = QComboBox(win)
    device.resize(200, 30)
    device.move(150, 100)
    device.addItem('电机调速器（485型）')
    device.addItem('二氧化碳变送器（485型）')
    device.addItem('水浸传感器（485型）')
    device.addItem('RGB调光控制器（485型）')
    device.addItem('超声波传感器（485型）')
    device.addItem('光照噪声变送器（485型）')
    device.addItem('多合一传感器（485型）')
    device.addItem('百叶箱传感器（485型）')
    device.addItem('4行LED屏')
    device.addItem('DAM0404D联动控制器')
    device.addItem('410S串口终端')
    device.addItem('IOT网络数据采集器')
    device.currentIndexChanged.connect(lambda: devices(device.currentText()))

    d1 = QLabel(win)
    d1.setText("设备地址：")
    d1.setFont(QFont("Microsoft YaHei", 10, 55))
    d1.resize(100, 30)
    d1.move(450, 100)

    dz1 = QLineEdit(win)
    dz1.resize(70, 30)
    dz1.move(530, 100)
    dz1.setStyleSheet(
        'border-width: 1px;border-style: solid;border-color: rgb(0, 0, 0);background-color: rgb(255, 255, 255);')

    submit = QPushButton(win)
    submit.resize(100, 32)
    submit.setText("确定")
    submit.move(700, 100)
    submit.clicked.connect(queding)

    button2 = QPushButton(win)
    button2.resize(70, 32)
    button2.setText("取消")
    button2.move(850, 100)
    button2.clicked.connect(quxiao)
    button2.setEnabled(False)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~第三行~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

    dianji1()
    dianji2()

    co2()

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~发送区~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    fa = QLabel(win)
    fa.setFont(QFont("Microsoft YaHei", 10, 55))
    fa.resize(100, 30)
    fa.move(250, 220)
    fa.setText("发送区")

    fas = QPushButton(win)
    fas.resize(100, 32)
    fas.move(650, 460)
    fas.setText("清空发送区")
    fas.clicked.connect(clear_fa)

    fasong = QTextEdit(win)
    fasong.resize(500, 200)
    fasong.move(250, 250)
    fasong.setFontFamily("黑体")
    fasong.setFontPointSize(20)
    fasong.setFocusPolicy(QtCore.Qt.NoFocus)

    fasong.setStyleSheet(
        'border-width: 1px;border-style: solid;border-color: rgb(0, 0, 0);background-color: rgb(255, 255, 255);')

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~接收区~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

    jie = QLabel(win)
    jie.setFont(QFont("Microsoft YaHei", 10, 55))
    jie.resize(100, 30)
    jie.move(250, 470)
    jie.setText("接收区")

    jies = QPushButton(win)
    jies.resize(100, 32)
    jies.move(650, 710)
    jies.setText("清空接收区")
    jies.clicked.connect(clear_jie)

    jieshou = QTextEdit(win)
    jieshou.resize(500, 200)
    jieshou.move(250, 500)
    jieshou.setFontPointSize(18)
    jieshou.setFocusPolicy(QtCore.Qt.NoFocus)

    jieshou.setStyleSheet(
        'border-width: 1px;border-style: solid;border-color: rgb(0, 0, 0);background-color: rgb(255, 255, 255);')

    win.show()
    sys.exit(app.exec_())
