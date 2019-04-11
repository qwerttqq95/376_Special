import ctypes, UI_Main, sys, serial.tools.list_ports, serial, binascii, time, threading, core, traceback, Comm, B07645, \
    select
# import socket as NET
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QTextCursor
from socket import *

lib = ctypes.cdll.LoadLibrary("E:\C++\Dll1\Debug\Dll1.dll")
lib.hello()


class MainWindow(QMainWindow):
    _signal_text = pyqtSignal(str)
    _signal_warm = pyqtSignal(tuple)

    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = UI_Main.Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.textEdit.moveCursor(QTextCursor.End)
        self.setWindowTitle('376_Special V1.0')
        self.addItem = self.GetSerialNumber()
        while 1:
            if self.addItem == None:
                Warn = QMessageBox.warning(self, '警告', '未检测到串口', QMessageBox.Reset | QMessageBox.Cancel)
                if Warn == QMessageBox.Cancel:
                    self.close()
                if Warn == QMessageBox.Reset:
                    self.addItem = self.GetSerialNumber()
                continue
            else:
                break
        self.addItem.sort()
        for addItem in self.addItem:
            self.ui.comboBox_4.addItem(addItem)
        self._signal_text.connect(self.show_message)
        self._signal_warm.connect(self.warm_message)
        self.ui.pushButton.clicked.connect(lambda: threading.Thread(target=self.start_to_connect_, daemon=True).start())
        self.ui.actionF2040.triggered.connect(self.F2040)
        self.ui.menubar.setDisabled(1)
        self.ui.actionYi.triggered.connect(self.Get_data_1)
        self.ui.actionChushi.triggered.connect(self.data_init)

    def data_init(self):
        message = core.data_init()
        self.tctimeClient.send(binascii.a2b_hex(message.replace(' ', '')))
        self._signal_text.emit('Send message:' + Comm.makestr(message))
        print('Send message:', Comm.makestr(message))

    def Get_data_1(self):  # 一类数据测试
        self._signal_text.emit('开始一类数据测试...')
        print('开始一类数据测试')
        self.meter = threading.Thread(target=self.Meter645, daemon=True)
        self.meter.start()

    def F2040(self):
        message = core.F2040()
        self.tctimeClient.send(binascii.a2b_hex(message.replace(' ', '')))
        self._signal_text.emit('Send message:' + Comm.makestr(message))
        print('Send message:', Comm.makestr(message))

    def Meter645(self):
        time.sleep(5)
        self.serial = serial.Serial()
        self.serial.port = self.ui.comboBox_4.currentText()
        self.serial.baudrate = int(self.ui.comboBox_5.currentText())
        self.serial.parity = self.ui.comboBox_6.currentText()
        self.serial.timeout = 1
        self.serial.open()
        times = 30
        self._signal_warm.emit((2, '打开模拟表等待300s'))
        while times:
            data = ''
            time.sleep(1)
            times -= 1
            num = self.serial.inWaiting()
            data = data + str(binascii.b2a_hex(self.serial.read(num)))[2:-1]
            if data == '':
                continue
            else:
                print('data:', data)
                message = B07645.check(data)
                if message != 1 and message is not None:
                    print('Received: ', message)
                    remessage = B07645.deal_receive(message)
                    self.serial.write(binascii.a2b_hex(remessage))
                    B07645.clear_templist()
                    data = ''
                else:
                    continue
        self._signal_warm.emit((2, '关闭模拟表'))
        print('关闭模拟表')

    def start_to_connect_(self):
        host = '0.0.0.0'
        port = int(self.ui.lineEdit_2.text())

        ADDR = (host, port)
        self.tctime = socket(AF_INET, SOCK_STREAM)
        self.tctime.bind(ADDR)
        self.tctime.listen(5)
        print('Wait for connection ...')
        self._signal_text.emit('Wait for connection ...')
        while 1:
            try:
                readable, [], exception = select.select([self.tctime], [], [self.tctime])
                if self.tctime in readable:
                    connection, self.add = self.tctime.accept()
                    self.tctimeClient = connection
                    threading.Thread(target=self.start_to_connect, daemon=True).start()

                if self.tctime in exception:
                    break
            except:
                break

    def start_to_connect(self):
        buffsize = 2048
        if self.ui.pushButton.text() == '已上线':
            return 0
        try:
            print("Connection from :", self.add)
            self._signal_text.emit("Connection from :" + self.add[0])
            while True:
                try:
                    readable, [], exceptional = select.select([self.tctimeClient], [], [self.tctimeClient], 0)
                    if self.tctimeClient in readable:
                        data = self.tctimeClient.recv(buffsize)
                        data = Comm.makestr(str(binascii.b2a_hex(data))[2:-1])
                        if data is not None and data != '':
                            print('Received message:', data)
                            self._signal_text.emit('Received message:' + data)
                            message = core.analysis(data.replace(' ', ''))
                            print('adssss', message)
                            if message is None:
                                continue
                            if message[0] == 0:
                                print('Send message:', Comm.makestr(message[1]))
                                self._signal_text.emit('Send message:' + Comm.makestr(message[1]))
                                self._signal_warm.emit((1, '已登录/心跳'))
                                self.ui.pushButton.setText('已上线')
                                self.ui.menubar.setDisabled(0)
                                self.ui.lineEdit_2.setDisabled(1)
                                self.tctimeClient.send(binascii.a2b_hex(message[1]))

                            elif message[0] == 1:
                                self._signal_warm.emit((1, message[1]))
                    if self.tctimeClient in exceptional:
                        break
                except:
                    traceback.print_exc(file=open('bug.txt', 'a+'))
                    break
        except:
            self._signal_warm.emit((0, '端口被占用'))
            traceback.print_exc(file=open('bug.txt', 'a+'))

    def show_message(self, text):
        self.ui.textEdit.append(text)

    def warm_message(self, text):
        if text[0] == 0:
            QMessageBox.information(self, '警告', text[1], QMessageBox.Ok)
        elif text[0] == 1:
            orig_text = "<font color=\"#FF0000\">{}</font>".format(text[1])
            self.ui.textEdit.append(orig_text)
            ct = time.time()
            local_time = time.localtime(ct)
            data_head = time.strftime("%H:%M:%S", local_time)
            self.ui.textEdit.append(data_head)
            self.ui.textEdit.append("<font color=\"#000000\">------------------------</font>")
        elif text[0] == 2:
            orig_text = "<font color=\"#DC143C\">{}</font>".format(text[1])
            self.ui.textEdit.append(orig_text)
            ct = time.time()
            local_time = time.localtime(ct)
            data_head = time.strftime("%H:%M:%S", local_time)
            self.ui.textEdit.append(data_head)
            self.ui.textEdit.append("<font color=\"#000000\">------------------------</font>")

    def GetSerialNumber(self):
        SerialNumber = []
        port_list = list(serial.tools.list_ports.comports())
        if len(port_list) <= 0:
            print("The Serial port can't find!")
        else:
            for i in list(port_list):
                SerialNumber.append(i[0])
            return SerialNumber


if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow = MainWindow()
    MainWindow.show()
    sys.exit(app.exec_())
