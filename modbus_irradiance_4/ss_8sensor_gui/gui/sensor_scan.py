import serial
import crcmod
from serial_msc import *
#from gui.serial_msc import *
from PyQt5 import QtCore, QtWidgets, QtGui
from time import sleep
from PyQt5.QtWidgets import (QMessageBox,QWidget,QFileDialog)
from pickle import NONE



class sensor_scan(QtCore.QThread):
    #define Static Variables 
    __PARITY_LIST=["none/1","none/2","Even/1","Odd/1"]
    __INIT_PARITY=serial.PARITY_NONE
    __INIT_STOP_BITS=serial.STOPBITS_ONE
    __INIT_BAUD="9600"
    __INIT_BYTESIZE=8
    __INIT_ID=0
    
    dev_id          =QtCore.pyqtSignal(int)
    baud_rate       =QtCore.pyqtSignal(str)
    parity          =QtCore.pyqtSignal(str)
    completed_tr    =QtCore.pyqtSignal(bool)
    message_error   =QtCore.pyqtSignal(str)



###############################################
#     sensor_scan_addr=range(1,31)
#   __PARITY_LIST=["none/1","none/2","Even/1","Odd/1"]
# baudrate_list=["9600","19200","38400","4800"]
##############################################   
    
    def __init__(self,parent=None, comport=None):
        super(sensor_scan,self).__init__(parent)
        self.comport=comport
        self.bl_control=None
        self.devid_control=None
        self.pl_control=None
        self.is_running=True
        self.chosen_id_1 = 0
        self.chosen_id_2 = 255
        self.chosen_baud = 0
        self.chosen_parity = 0
        self.debug_count = 0
        ############################################

        ######################################
        
    def run(self):
        #Firtsly Open the Serial Port 
        self.open_port()
        self.baud_rate.emit(sensor_scan.__INIT_BAUD)
        self.dev_id.emit(sensor_scan.__INIT_ID)
        self.parity.emit(sensor_scan.__PARITY_LIST[0])
        
        find_device=False
        for self.pl_control in sensor_scan.__PARITY_LIST[self.chosen_parity:]:
            #if device found, break loop
            if find_device==True:
                break
            else:
                #New configuration should be done, close the serial port
                if self.ser.is_open==True:
                    self.ser.close()    
                     
                for self.bl_control in baudrate_list[self.chosen_baud:]:
                #if device found, break loop
                    self.ser.close()    
                    sleep(0.1)
                    if find_device==True:
                        break
                    else:
                    #New configuration should be done, close the serial port
                        if self.ser.is_open==True:
                            self.ser.close()    
                        #initialize the Comport            
                        self.ser.port=self.comport
                        #Take baudrate info from GUI and set baudrate
                        self.ser.baudrate=self.bl_control
                        #Take data from GUI and set stop bits 
                        self.selected_stop_bit=self.pl_control
                        #if NONE/1STOP
                        if(self.selected_stop_bit=="none/1"): 
                            self.ser.parity=serial.PARITY_NONE
                            self.ser.stopbits=serial.STOPBITS_ONE
                        elif(self.selected_stop_bit=="none/2"): 
                            self.ser.parity=serial.PARITY_NONE
                            self.ser.stopbits=serial.STOPBITS_ONE
                        elif(self.selected_stop_bit=="Even/1"): 
                            self.ser.parity=serial.PARITY_EVEN
                            self.ser.stopbits=serial.STOPBITS_ONE
                        elif(self.selected_stop_bit=="Odd/1"): 
                            self.ser.parity=serial.PARITY_ODD
                            self.ser.stopbits=serial.STOPBITS_ONE
                        else:
                            self.ser.parity=serial.PARITY_NONE
                            self.ser.stopbits=serial.STOPBITS_TWO
                        self.ser.timeout=0.4
                        try: 
                            self.ser.open()
                        except:
                            break
                            self.message_error.emit("Please select COM Port!")   #FURKAN
    #                    for devid_control in range(1,3):               
                        for self.devid_control in range(self.chosen_id_1,self.chosen_id_2):               
                            self.modbusid=self.devid_control
                            self.send_modbus_cmd(modbus_func_codes['sensor_specific'],modbus_sensorspec_reg_addr['version'],0,0)
                            get_ver_rsp=self.ser.read(cmd_res_size["r_version"])
                            sleep(0.01)
                            self.baud_rate.emit(self.bl_control)
                            self.dev_id.emit(self.devid_control)
                            self.parity.emit(self.pl_control)
                            QtWidgets.QApplication.processEvents()
                            if(len(get_ver_rsp)==cmd_res_size["r_version"]):                
                                find_device=True
                                #self.get_sel_comport()
                                break
                            
        self.ser.close() 
        if find_device==True:
            self.completed_tr.emit(True)
        else:
            self.completed_tr.emit(False)
        #Search The Bus 
        
    def open_port(self):
        self.ser=serial.Serial()     
        self.ser.port=self.comport
        self.ser.baudrate   =sensor_scan.__INIT_BAUD
        self.ser.parity     =sensor_scan.__INIT_PARITY
        self.ser.stopbits   =sensor_scan.__INIT_STOP_BITS
        self.ser.bytesize   =sensor_scan.__INIT_BYTESIZE
        try:
            self.ser.open()
            self.ser.reset_input_buffer()
        except Exception as e:
            self.message_error.emit("comport is not connected")
            #TODO (Check the usage of this exception, will it crash the application or not)
            #raise Exception("Failed to open serial port!")
      
    def refresh_comport(self,comp):
        self.comport = comp

    def stop(self):
        self.is_running=False
        self.terminate() 
        self.ser.close()
        
    
    def send_modbus_cmd(self, func_code, reg_addr,read_word_num,write_data):
        if(func_code==modbus_func_codes['read_input_register']):
            cmd=self.modbusid.to_bytes(1, byteorder='big', signed=False)+func_code+reg_addr+read_word_num
        elif(func_code==modbus_func_codes['write_single_holding_register'] ):
            cmd=self.modbusid.to_bytes(1, byteorder='big', signed=False)+func_code+reg_addr+write_data
        elif(func_code==modbus_func_codes['sensor_specific'] ):
            if(write_data==0):
                cmd=self.modbusid.to_bytes(1, byteorder='big', signed=False)+func_code+reg_addr     
            else:
                cmd=self.modbusid.to_bytes(1, byteorder='big', signed=False)+func_code+reg_addr+write_data
        else:
            cmd=self.modbusid.to_bytes(1, byteorder='big', signed=False)+func_code+reg_addr
        crc_data=self._crc16(cmd)
        cmd=cmd+crc_data.to_bytes(2, byteorder='little', signed=False)
        if(self.ser.is_open):
            self.ser.write(cmd)        
        return cmd 
    
    
#============================================================================
#Calculate CRC
    def _crc16(self, data):
        crc16 = crcmod.mkCrcFun(0x18005, rev=True, initCrc=0xFFFF)
        checkSum = crc16(data)
        return checkSum 
    
    