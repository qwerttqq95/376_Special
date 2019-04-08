import ctypes,UI_Main,sys,serial.tools.list_ports,serial,binascii, time
from PyQt5.QtWidgets import QApplication, QMainWindow,QMessageBox
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QTextCursor
from socket import *
lib = ctypes.cdll.LoadLibrary("E:\C++\Dll1\Debug\Dll1.dll")
lib.hello()


class MainWindow(QMainWindow):
    _signal_text = pyqtSignal(str)
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

    def show_message(self,text):
        self.ui.textEdit.append(text)

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
