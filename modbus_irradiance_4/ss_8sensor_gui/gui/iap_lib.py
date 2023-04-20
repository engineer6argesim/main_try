#This class does the Y-Modem protocol 
#Opens the Comport 
#Reads and parses the .bin file
#sends packets 

import serial
import os
from PyQt5 import QtCore, QtWidgets, QtGui
from time import sleep
from Modem import Modem
#from gui.Modem import Modem
from PyQt5.QtWidgets import (QMessageBox,QWidget,QFileDialog)
from sensor_scan import sensor_scan
#from gui.sensor_scan import sensor_scan
from pip._internal.cli.cmdoptions import retries

class iap_protocol(QtCore.QThread):
    #define Static Variables 
    __YMODEM_PCK_SIZE=1024
    __YMODEM_BAUD=9600
    __YMODEM_PARITY=serial.PARITY_NONE
    __YMODEM_STOP=serial.STOPBITS_ONE
    __YMODEM_TIMEOUT=3
    __YMODEM_BYTESIZE=8
    __START_HANDSHAKE="helloseven"
    __START_REC_HANDSHAKE="elloseven"
    __HANDSHAKE_SIZE=10
    __START_RESCOMMES="rescomsett"
    __START_REC_RESCOMMES="escomsett"
    __RECCOMMES_SIZE=10
    res_com_flag=0


    
    percentoffile = QtCore.pyqtSignal(int)
    message_error = QtCore.pyqtSignal(str)
    filetransmitdoneflg=QtCore.pyqtSignal()
    resetcomsetflg=QtCore.pyqtSignal()
    
    def __init__(self,parent=None, comport=None,file_name=None):
        super(iap_protocol,self).__init__(parent)
        self.file_name=file_name
        self.packet_size=0
        self.sended_packet_size=0
        self.comport=comport
        self.is_running=True
    
    def run(self):
        #open Comport  
        self.open_port()

        if(self.res_com_flag == 0):
            if(self.start_handshake()):
                print("if start update handshake")
            #flush the recived data if there is 
            #instantiate Ymodem 
                self.sender=Modem(self.ymodem_read,self.ymodem_write)
            #Open File
                try:
                    self.file_stream=open(self.file_name,"rb")
                    self.file_info = {
                        "name"      :os.path.basename(self.file_name),
                        "length"    :os.path.getsize(self.file_name),
                        "mtime"     :os.path.getmtime(self.file_name),
                        "source"    :"win"
                        }
                    self.status=self.sender.send(self.file_stream,info=self.file_info,callback=self.send_packet_info)
        #             self.status=self.sender.send(self.file_stream,info=self.file_info)
            
                    if(self.status==True):
                        self.message_error.emit("file transmission is completed")
                    else:
                        self.message_error.emit("file transmission is failed")
                except IOError:
                    self.message_error.emit("Error While Opening the file!")

                self.ser.close()
                self.filetransmitdoneflg.emit()

        elif(self.res_com_flag == 1):
            if (self.start_resetcom_handshake()):
                self.message_error.emit("Modbus Com. Parameter was changed!")
                print("Start Com. Res. Handshake")

            self.ser.close()
            print("ser close")
         
        
    def send_packet_info(self,total_packets, success_count, error_count):
        self.total_packet_number=int(os.path.getsize(self.file_name)/iap_protocol.__YMODEM_PCK_SIZE)+1
        self.sended_packet_size=int(success_count/self.total_packet_number*100)
        self.percentoffile.emit(self.sended_packet_size)     
     
    def stop(self):
        self.is_running=False 
        self.terminate()
    
    def open_port(self):
        self.ser=serial.Serial()     
        self.ser.port=self.comport
        self.ser.baudrate=iap_protocol.__YMODEM_BAUD
        self.ser.parity=iap_protocol.__YMODEM_PARITY
        self.ser.stopbits=iap_protocol.__YMODEM_STOP
        self.ser.bytesize=iap_protocol.__YMODEM_BYTESIZE
        try:
            self.ser.open()
            self.ser.reset_input_buffer()
        except Exception as e:
            self.message_error.emit("comport is not connected")
            #TODO (Check the usage of this exception, will it crash the application or not)
            #raise Exception("Failed to open serial port!")
        
    def ymodem_read(self,size,timeout=3):
        self.ser.timeout=timeout
        return self.ser.read(size) or None
            
    def ymodem_write(self,data,timeout=3):
        self.ser.timeout=timeout
        return self.ser.write(data)
    
    def start_handshake(self):
        print("update handshake start")
#         self.ymodem_write(sensor_scan.__START_HANDSHAKE,1)
        for x in range(1,100,1):
            self.ser.write(iap_protocol.__START_HANDSHAKE.encode())
            self.catch_data=self.ymodem_read(iap_protocol.__HANDSHAKE_SIZE,0.5)
            print(self.catch_data)
            if(self.catch_data==iap_protocol.__START_REC_HANDSHAKE.encode()):
                print(self.catch_data)
                return True

        self.message_error.emit("There is no device to configure")
        return False

    def start_resetcom_handshake(self):
        print("start start_resetcom_handshake")
        for x in range(1,100,1):
            self.ser.write(iap_protocol.__START_RESCOMMES.encode())
            self.catch_data=self.ymodem_read(iap_protocol.__RECCOMMES_SIZE,0.5)
            if(self.catch_data==iap_protocol.__START_REC_RESCOMMES.encode()):
                return True


        self.message_error.emit("There is no device to configure")
        return False
    