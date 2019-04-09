import ctypes, UI_Main, sys, serial.tools.list_ports, serial, binascii, time, threading, core,traceback
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
        self.setWindowTitle('376_Special')
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
        self.ui.pushButton.clicked.connect(lambda: threading.Thread(target=self.start_to_connect, daemon=True).start())

    def start_to_connect(self):
        host = '0.0.0.0'
        port = int(self.ui.lineEdit_2.text())
        buffsize = 2048
        ADDR = (host, port)
        tctime = socket(AF_INET, SOCK_STREAM)
        try:
            tctime.bind(ADDR)
            tctime.listen(5)
            print('Wait for connection ...')
            MainWindow._signal_text.emit('Wait for connection ...')
            while True:
                self.tctimeClient, addr = tctime.accept()
                print("Connection from :", addr)
                MainWindow._signal_text.emit("Connection from :"+ addr[0])
                while True:
                    data = self.tctimeClient.recv(buffsize)
                    data = core.makestr(str(binascii.b2a_hex(data))[2:-1])
                    if data is not None or data == '':
                        print('Received message:', data)
                        MainWindow._signal_text.emit('Received message:'+ data)
                        message = core.analysis(data.replace(' ', ''))
                        self.tctimeClient.send(binascii.a2b_hex(message))
                        print('Send message:', core.makestr(message))
                        MainWindow._signal_text.emit('Send message:' + core.makestr(message))
                        MainWindow._signal_warm.emit((1, '已登录'))
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
