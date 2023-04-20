from time import sleep
from PyQt5 import QtCore, QtWidgets, QtGui
from datetime import datetime

        
class LogFileThread(QtCore.QThread):

    # Create signal to use in thread
    status_signal = QtCore.pyqtSignal(bool)
    list_signal = QtCore.pyqtSignal(list)
    stop_signal = QtCore.pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.data_log = []
        self.flag = 0
        self.ID = 0
        self.BaudRate = 0
        self.Parity = 0
        self.SerNum = 0
    
    def update_data_log(self, new_data_log):
        self.data_log = new_data_log
        self.data_log_changed.emit(self.data_log)

    def run(self):

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if(self.flag == 0):
            self.flag = 1
            self.f = open("Seven Sensor Log.txt", "a")
            self.f.write("Seven Sensor - Automatic Soiling Sensor" + "\n")
            self.f.write("ID: {} - Baud Rate: {} - Parity: {} - Start Reg. Adr. {} ".format(self.ID,self.BaudRate,self.Parity,0) + "\n")
            self.f.write("Serial Number {}".format(self.SerNum) + "\n")
            self.f.write("Time Stamp, IRR1, IRR2, Temp Comp IRR1, Temp Comp IRR2, mV1, mV2, ADC1, ADC2, Int Temp1, Int Temp2, Soil Ratio, Dail Soil Ratio" + "\n")


        self.status_signal.emit(True)        

        self.column = 1

        self.data = self.data_log
        self.f = open("Seven Sensor Log.txt","a")
        self.f.write (current_time + ",")
        for self.data in self.data_log:
            self.f.write(str(self.data) + ",")
        self.f.write("\n")

        self.data_log = []
        self.status_signal.emit(False)

    def stop_log_file(self):
            self.f.close()
            self.terminate()
            print("stop")

            























