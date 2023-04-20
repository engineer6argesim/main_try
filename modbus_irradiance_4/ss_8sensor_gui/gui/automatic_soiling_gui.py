'''
Created on 25 Dec 2021

@author: sy
'''




from base import *
#from gui.base import *
from serial_msc import *
#from gui.serial_msc import *
from PyQt5.QtWidgets import *
from PyQt5 import Qt
from PyQt5.Qt import *
from gui_msc import *
#from gui.gui_msc import *
from iap_lib import *
#from gui.iap_lib import *
import time
import serial
import threading
import crcmod
import serial.tools.list_ports as port_list
from time import thread_time, sleep
from PyQt5.QtWidgets import (QMessageBox,QWidget,QFileDialog)
from sensor_scan import sensor_scan
from log_file import LogFileThread
#from gui.sensor_scan import sensor_scan
#from gui.log_file import LogFileThread

class TabBarFilter(QObject):
    
    eventSignal = pyqtSignal()


    def __init__(self, parent=None):
        super(TabBarFilter,self).__init__(parent)
        #Created for a object eventFilter which it
        # can not do any event before password message box
    def eventFilter(self, object, event):
        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Tab and event.modifiers() & Qt.ControlModifier:
                # Ctrl+Tab tuş kombinasyonu algılandı, olayı ele alma
                return True
        if event.type() == QEvent.KeyRelease:
            if event.key() == Qt.Key_Tab and event.modifiers() & Qt.ControlModifier:
                # Ctrl+Tab tuş kombinasyonu algılandı, olayı ele alma
                return True
        if event.type() in[QEvent.MouseButtonRelease, QEvent.MouseButtonDblClick]:
            return True
        if event.type() == QEvent.MouseButtonPress:
            return self.showInputDialog()
        return False

    def showInputDialog(self)-> bool:
        text, ok = QInputDialog.getText(None, 'Password Dialog', 'Enter password:', QLineEdit.Password)
        if ok:
                if text == '1919':
                    QMessageBox.warning(None, 'Correct', 'Password is correct')
                    #Created for a object eventFilter which 
                    #it can not do any event before password message box
                    self.eventSignal.emit()
                    return False
                else:
                   QMessageBox.warning(None, 'Incorrect', 'Password is not correct')
                   return True
        else:
            return True

class MyWorker(QThread):
    my_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

    def run(self,value):
        QMessageBox.warning(None, 'Warning', value)
        
        # Ana uygulama i� par�ac���na i�lem postalan�r
        #QMetaObject.invokeMethod(self, "show_message", Qt.QueuedConnection)

        


class Ui_MainWindow_ss(Ui_MainWindow):
#============================================================================
#  
 

    def __init__(self):
        super().__init__()
        
        
#============================================================================
#About connection        
    def init_com(self):

        time_interval="1000"
        self.modbusid=1
        self.actual_baud=9600
        self.actual_parity=serial.PARITY_EVEN
        self.actual_stop_bits=serial.STOPBITS_ONE
        self.new_baud=9600
        self.new_parity=serial.PARITY_EVEN
        self.new_stop_bits=serial.STOPBITS_ONE
        self.BaudComboBoxActual.addItems(baudrate_list)
        self.BaudComboBoxActual.setCurrentText(str(self.actual_baud))
        self.BaudComboboxNew.addItems(baudrate_list)
        self.Baud_Range.addItems(baudrate_list)
        self.BaudComboboxNew.setCurrentText(str(self.new_baud))
        self.ParityActual.addItems(parity_list)
        self.ParityNew.addItems(parity_list)
        self.Parity_Range.addItems(parity_list)
        self.IntervalLine.setText(str(time_interval))
        self.progressBar.setValue(0)
        self.isTimerCreated = False
        self.set_com()
        self.UpdateFirmware.blockSignals(True)
        self.status_logfile = True
        self.set_onetime=0;

#============================================================================
#            
    def set_com(self):
        self.ModBusNew.setText(str(self.modbusid))
        self.ModBusActual.setText(str(self.modbusid))   #TODO Update with actual parameter
        self.ID_Range_1.setText("-")
        self.ID_Range_2.setText("-")
        
#============================================================================
#   
    def set_comport(self):
        ports=list(port_list.comports())
        for p in ports:
            self.PortComboBox.addItem(p.device)
#============================================================================
#       
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
#       
    def get_data_from_stream(self,stream,index):
        return int.from_bytes(self.stream[index*2-1:index*2], "big")
    
#============================================================================
#
    def module_init(self):        
        self.init_com()
#         self.set_wind_cal_data_flg=False
#         self.set_sensor_config_flg=False
#         self.set_sel_config_flg=False
#         self.baud_set_config_flg=False
        self.set_comport()
        self.PortConnect.stateChanged.connect(self.get_sel_comport)     #Set handler of connect radio button
        self.logFileState.clicked.connect(self.log_to_file)
        #self.logFileState.stateChanged.connect(self.log_to_file)
        self.sensorScanbtn.clicked.connect(self.sensor_scan)
        self.sensorScanbtn_2.clicked.connect(self.sensor_scan)
        #self.ComButWriteAndResetBuuton.clicked.connect(self.button_set_flag_func(self.ComButWriteAndResetBuuton))
        #######################################################################################
        #to initialize the eventFilter
        self.tab_bar = self.tabWidget.tabBar()
        self.event_filter = TabBarFilter()
        self.tab_bar.installEventFilter(self.event_filter) ##TODO NOT CIKARILACAK
        self.event_filter.eventSignal.connect(self.password_condition)
        #self.password = "123456"
        #############################################################################################
        self.worker = MyWorker()
        self.worker.my_signal.connect(self.worker.run)
        self.button_group=QButtonGroup()        
        self.button_group.addButton(self.ComButWriteAndResetBuuton,buttons_ids['ComButWriteAndResetBuuton'])
        #=======================================================================


        # self.button_group.addButton(self.modRatesWrButton,buttons_ids['modRatesWrButton'])
        # self.button_group.addButton(self.WindSenWrButton,buttons_ids['WindSenWrButton'])
        #=======================================================================
        #=======================================================================
        # self.button_group.addButton(self.soilingSenWrButton,buttons_ids['soilingSenWrButton'])
        #=======================================================================
        self.button_group.addButton(self.AdcWrButton,buttons_ids['AdcWrButton'])
        self.button_group.addButton(self.SensorCalWRB,buttons_ids['SensorCalWRB'])
        #=======================================================================
        # self.button_group.addButton(self.TimeIntWrButton,buttons_ids['TimeIntWrButton'])
        #=======================================================================
        self.button_group.addButton(self.SetSerNumPB,buttons_ids['SetSerNoButton'])
        self.button_group.addButton(self.DeviceInfWrButton,buttons_ids['SetDevInfoWrButton'])
        self.button_group.addButton(self.Set_Time_Button,buttons_ids['SetTimeInfo'])
        self.button_group.addButton(self.SetRangeBtn,buttons_ids['SetStableRange'])
        self.button_group.addButton(self.setDataCounterBtn,buttons_ids['SetStableMin'])
        self.button_group.addButton(self.setLocateBtn,buttons_ids['setLocateBtn'])

        self.ComButWriteAndResetBuuton_flg=False
        self.modRatesWrButton_flg=False
        self.WindSenWrButton_flg=False
        #=======================================================================
        # self.soilingSenWrButton_flg=False
        #=======================================================================
        self.AdcWrButton_flg=False
        self.SensorCalWRB_flg=False
        self.TimeIntWrButton_flg=False
        self.SetSerNumButton_flg=False
        self.SetDevInfWr_flg=False
        self.Set_Time_Button_flg=False
        self.SetRangeBtn_flg=False
        self.setDataCounterBtn_flg=False
        self.setLocateBtn_flg = False
        self.button_group.buttonClicked[int].connect(self.button_set_flag_func)
#         self.modRatesWrButton.clicked.connect(self.button_set_flag_func)
#         self.WindSenWrButton.clicked.connect(self.button_set_flag_func)
#         self.soilingSenWrButton.clicked.connect(self.button_set_flag_func)
        self.AdcWrButton.clicked.connect(self.button_set_flag_func)
#         self.SensorCalWRB.clicked.connect(self.button_set_flag_func)
#         self.TimeIntWrButton.clicked.connect(self.button_set_flag_func)
        #connect Dialog button    
        self.file_select.clicked.connect(self.open_binay_file)
        self.UpdateFirmware.clicked.connect(self.upgrade_firmware_func) 
        self.Reset_Com_Settings.clicked.connect(self.reset_com_settings)

        self.stopSensorScan.clicked.connect(self.sensor_stop_scan)
        self.stopSensorScan_2.clicked.connect(self.sensor_stop_scan)
        self.ser=serial.Serial()     
        
        
    def eventFilter(self, object, event):
        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Tab and event.modifiers() & Qt.ControlModifier:
                # Ctrl+Tab tuş kombinasyonu algılandı, olayı ele alma
                return True
        if event.type() == QEvent.KeyRelease:
            if event.key() == Qt.Key_Tab and event.modifiers() & Qt.ControlModifier:
                # Ctrl+Tab tuş kombinasyonu algılandı, olayı ele alma
                return True
        return False
    def showInputDialog(self)-> bool:
        text, ok = QInputDialog.getText(None, 'Password Dialog', 'Enter password:', QLineEdit.Password)
        if ok:
                if text == '1919':
                    QMessageBox.warning(None, 'Correct', 'Password is correct')
                    #Created for a object eventFilter which 
                    #it can not do any event before password message box
                    self.main_eventSignal.emit()
                    return False
                else:
                   QMessageBox.warning(None, 'Incorrect', 'Password is not correct')
                   return True
        else:
            return True
#============================================================================

    def on_change_list(self,log_list):
        self.LogFileThread_ins.data_log = log_list

#============================================================================
    def password_condition(self):
        #to remove the eventFilter after password condition
        self.tab_bar.removeEventFilter(self.event_filter)

#Connection Request Call back function
    def get_sel_comport(self):
        self.isTimerCreated = False
        self.is_value_error = False
        if(self.PortConnect.isChecked()):
            try:
                self.progressBar.setValue(0)
                self.FileNameLine.setText('')
                self.activePort = self.PortComboBox.currentText()        #FURKAN
                self.period     = int(self.IntervalLine.text())
                self.modbusid   = int(self.ModBusNew.text())
            except ValueError:
                self.value_error_msg=QMessageBox()
                self.value_error_msg.setWindowTitle("Error")
                self.value_error_msg.setText("Please fill the parameters.")
                self.value_error_msg.setIcon(QMessageBox.Warning)
                self.PortConnect.setChecked(False)
                self.value_error_msg.exec_()
                self.is_value_error = True
            if self.is_value_error== False and str(self.activePort)!= '':
                #Take baudrate info from GUI and set baudrate
                self.ser.port=self.activePort
                self.ser.baudrate=self.BaudComboBoxActual.currentText()
                #Take data from GUI and set stop bits 
                selected_stop_bit=self.ParityActual.currentText()
            #if NONE/1STOP
            if(selected_stop_bit=="none/1"): 
                self.ser.parity=serial.PARITY_NONE
                self.ser.stopbits=serial.STOPBITS_ONE
                self.Parity_Value = "None/1"
            elif(selected_stop_bit=="none/2"):
                self.ser.parity=serial.PARITY_NONE
                self.ser.stopbits=serial.STOPBITS_TWO
                self.Parity_Value = "None/2"
            elif(selected_stop_bit=="Even/1"):
                self.ser.parity=serial.PARITY_EVEN
                self.ser.stopbits=serial.STOPBITS_ONE
                self.Parity_Value = "Even"
            elif(selected_stop_bit=="Odd/1"):
                self.ser.parity=serial.PARITY_ODD
                self.ser.stopbits=serial.STOPBITS_ONE
                self.Parity_Value = "Odd"

                
            self.ser.timeout=1
            if(self.ser.is_open==False):
                self.ser.open()
            else:
                self.ser.close()
                self.ser.open()
            #firstly read Version etc.
            radio_button_state=self.PortConnect.checkState()
            if(radio_button_state==2):
                self.get_ver_data()
            else: 
                self.connection=False
                if(self.isTimerCreated): 
                    self.timer.quit()
                    self.isTimerCreated = False
                self.ser.close()
            
            if(self.connection==True): #TODO
                self.get_ser_data()
                self.get_cal_data()
                self.get_user_data()
                self.get_time()
                #self.timer=TimerThread()
                self.timer=threading.Timer(self.period/1000,self.read_data)
                #self.thread_timer = QTimer()
                #self.thread_timer.setInterval(self.period)
                #self.thread_timer.timeout.connect(self.on_timeout)
                #self.thread_timer.start()

                #self.timer.update_data.connect(self.read_data)
                self.timer.start()
                self.kill_timer=False
                self.isTimerCreated = True
                #self.timer.start()
                self.device_ID_variable.setText(str(self.modbusid))           #FURKAN
                self.baud_rate_variable.setText(str(self.actual_baud))
                self.Parity_variable.setText(str(selected_stop_bit))
#             else:
#                 if self.timer in locals():
#                     self.timer.cancel()
        else:       
            self.kill_timer=True
            self.ser.close()
            self.PortConnect.setChecked(False)
            self.sensorScanbtn.blockSignals(False)
            self.stopSensorScan.blockSignals(False)
            self.device_ID_variable.setText("-")           #FURKAN
            self.baud_rate_variable.setText("-")
            self.Parity_variable.setText("-")
            


#####################################################################

#============================================================================
#Request Serial Number and production date
    def get_ser_data(self):
        
        cmd_getserNum=self.send_modbus_cmd(modbus_func_codes['sensor_specific'], modbus_sensorspec_reg_addr['get_serial'],0, 0)
        rsp_getserNum=self.ser.read(cmd_res_size['r_ser_data'])


        pro_year=int.from_bytes(rsp_getserNum[3:4], "big")
        pro_code=int.from_bytes(rsp_getserNum[4:5], "big")
        cell_ser=int.from_bytes(rsp_getserNum[5:7], "little")
        board_ser=int.from_bytes(rsp_getserNum[7:8], "big")
        box_ser=int.from_bytes(rsp_getserNum[8:9], "big")
        irr_ser=int.from_bytes(rsp_getserNum[9:11], "little")
        product_day=int.from_bytes(rsp_getserNum[11:12], "big")
        product_month=int.from_bytes(rsp_getserNum[12:13], "big")
        product_year=int.from_bytes(rsp_getserNum[13:14], "big")
        cal_day_1=int.from_bytes(rsp_getserNum[14:15], "big")
        cal_month_1=int.from_bytes(rsp_getserNum[15:16], "big")
        cal_year_1=int.from_bytes(rsp_getserNum[16:17], "big")
        cal_day_2=int.from_bytes(rsp_getserNum[17:18], "big")
        cal_month_2=int.from_bytes(rsp_getserNum[18:19], "big")
        cal_year_2=int.from_bytes(rsp_getserNum[19:20], "big")

        serialNum=str(pro_year).zfill(2)+"."+ \
                str(pro_code).zfill(2)+ "."+\
                str(cell_ser).zfill(3)+"."+\
                str(board_ser).zfill(2)+"."+\
                str(box_ser).zfill(2)+ "."+\
                str(irr_ser).zfill(4)
        self.ser_num = serialNum
        mandata=str(product_day)+"."+str(product_month)+".20"+str(product_year)
        caldate1=str(cal_day_1)+"."+str(cal_month_1)+".20"+str(cal_year_1)
        caldate2=str(cal_day_2)+"."+str(cal_month_2)+".20"+str(cal_year_2)
        self.ProductionD_1.setText(mandata)
        self.Calib_Date_1.setText(caldate1)
        self.Calib_Date_2.setText(caldate2)
        self.SerNumD_1.setText(serialNum)

        self.ProductionD_2.setText(mandata)
        self.Calib_Date_3.setText(caldate1)
        self.Calib_Date_4.setText(caldate2)
        self.SerNumD_2.setText(serialNum)

        self.PrYearlineEdit.setText(str(pro_year))
        self.PrCodelineEdit.setText(str(pro_code))
        self.CellCerNolineEdit.setText(str(cell_ser))
        self.BoardSerNolineEdit.setText(str(board_ser))
        self.BoxSerNolineEdit.setText(str(box_ser))
        self.IrrSerNolineEdit.setText(str(irr_ser))
        self.CalDateDaylineEdit.setText(str(cal_day_1))
        self.CalDateMonlineEdit.setText(str(cal_month_1))
        self.CalDateYearlineEdit.setText(str(cal_year_1))
        self.CalDateDaylineEdit_2.setText(str(cal_day_2))
        self.CalDateMonlineEdit_2.setText(str(cal_month_2))
        self.CalDateYearlineEdit_2.setText(str(cal_year_2))
        self.ProDateDaylineEdit.setText(str(product_day))
        self.ProDateMonlineEdit.setText(str(product_month))
        self.ProDateYearlineEdit.setText(str(product_year))

        
    #def change_background_color(self):
    ## QLineEdits'ın arka plan rengi değiştiriliyor
    #    for line_edit in self.line_edits:
    #        palette = QPalette()
    #        palette.setColor(QPalette.Base, QColor("white"))
    #        line_edit.setPalette(palette)
        
        #^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#Setting Device Informations such as Date, Calibration Date, Software and Hardware Version
    def SetDevInfWr_conf(self):
        try:
            calDateDay=int(self.CalDateDaylineEdit.text())
            calDateMon=int(self.CalDateMonlineEdit.text())
            calDateYear=int(self.CalDateYearlineEdit.text())
            calDateDay_1=int(self.CalDateDaylineEdit_2.text())
            calDateMon_1=int(self.CalDateMonlineEdit_2.text())
            calDateYear_1=int(self.CalDateYearlineEdit_2.text())
            proDateDay=int(self.ProDateDaylineEdit.text())
            proDateMon=int(self.ProDateMonlineEdit.text())
            proDateYear=int(self.ProDateYearlineEdit.text())
            hwVersion=int((float(self.HWversionlineEdit.text())*100))  
            swVersion=int((float(self.SWlineEdit.text())*100))
            
        except:
            self.worker.my_signal.emit("At least one value is not set on the device Info field")
            return True
            
        calDate_stream=calDateDay.to_bytes(1, byteorder='big', signed=False) +\
                       calDateMon.to_bytes(1, byteorder='big', signed=False)+\
                       calDateYear.to_bytes(1, byteorder='big', signed=False)+\
                       calDateDay_1.to_bytes(1, byteorder='big', signed=False) +\
                       calDateMon_1.to_bytes(1, byteorder='big', signed=False)+\
                       calDateYear_1.to_bytes(1, byteorder='big', signed=False)
        
        cmd_calDate=self.send_modbus_cmd(modbus_func_codes['sensor_specific'], modbus_sensorspec_reg_addr['set_cal_date'],0, calDate_stream)
        rsp_calDate=self.ser.read(cmd_res_size['set_cal_date'])
        
        if(rsp_calDate==cmd_calDate):
            self.CalDateDaylineEdit.setStyleSheet("background-color: rgb(51, 255, 51);;")
            self.CalDateMonlineEdit.setStyleSheet("background-color: rgb(51, 255, 51);;")
            self.CalDateYearlineEdit.setStyleSheet("background-color: rgb(51, 255, 51);;")
            self.CalDateDaylineEdit_2.setStyleSheet("background-color: rgb(51, 255, 51);;")
            self.CalDateMonlineEdit_2.setStyleSheet("background-color: rgb(51, 255, 51);;")
            self.CalDateYearlineEdit_2.setStyleSheet("background-color: rgb(51, 255, 51);;")

        else:
            self.CalDateDaylineEdit.setStyleSheet("background-color: red;")
            self.CalDateMonlineEdit.setStyleSheet("background-color: red;")
            self.CalDateYearlineEdit.setStyleSheet("background-color: red;")
            self.CalDateDaylineEdit_2.setStyleSheet("background-color: red;")
            self.CalDateMonlineEdit_2.setStyleSheet("background-color: red;")
            self.CalDateYearlineEdit_2.setStyleSheet("background-color: red;")
        
        pro_date_stream=proDateDay.to_bytes(1, byteorder='big', signed=False)+ \
                        proDateMon.to_bytes(1, byteorder='big', signed=False)+ \
                        proDateYear.to_bytes(1, byteorder='big', signed=False)
        
        cmd_proDate=self.send_modbus_cmd(modbus_func_codes['sensor_specific'], modbus_sensorspec_reg_addr['set_pro_date'],0, pro_date_stream)
        rsp_proDate=self.ser.read(cmd_res_size['set_pro_date'])
    
        if(rsp_proDate==cmd_proDate):
            self.ProDateDaylineEdit.setStyleSheet("background-color: rgb(51, 255, 51);;")
            self.ProDateMonlineEdit.setStyleSheet("background-color: rgb(51, 255, 51);;")
            self.ProDateYearlineEdit.setStyleSheet("background-color: rgb(51, 255, 51);;")
        else:
            self.ProDateDaylineEdit.setStyleSheet("background-color: red;")
            self.ProDateMonlineEdit.setStyleSheet("background-color: red;")
            self.ProDateYearlineEdit.setStyleSheet("background-color: red;")
            
        hw_version_stream=hwVersion.to_bytes(2, byteorder='big', signed=False)+\
                          swVersion.to_bytes(2, byteorder='big', signed=False)
            
        cmd_hwsw=self.send_modbus_cmd(modbus_func_codes['sensor_specific'], modbus_sensorspec_reg_addr['set_hwsw_version'],0, hw_version_stream)
        rsp_hwsw=self.ser.read(cmd_res_size['set_hwsw_ver'])
        
        if(cmd_hwsw==rsp_hwsw):
            self.HWversionlineEdit.setStyleSheet("background-color: rgb(51, 255, 51);;")
            self.SWlineEdit.setStyleSheet("background-color: rgb(51, 255, 51);;")
        else:
            self.HWversionlineEdit.setStyleSheet("background-color: red;")
            self.SWlineEdit.setStyleSheet("background-color: red;")

        cmd_send=self.send_modbus_cmd(modbus_func_codes['systemreset'],modbus_diognastic_reg_addr['reset'], 0, 0)   
        time.sleep(0.1)  
        self.ser.close() 
        
        self.open_comport_again()
        self.get_ser_data()
        self.ser.reset_input_buffer()
        time.sleep(0.4)
        self.get_ver_data()
            
    
        self.CalDateDaylineEdit.setStyleSheet("background-color: lightgray;;")
        self.CalDateMonlineEdit.setStyleSheet("background-color: lightgray;;")
        self.CalDateYearlineEdit.setStyleSheet("background-color: lightgray;;")
        self.CalDateDaylineEdit_2.setStyleSheet("background-color: lightgray;;")
        self.CalDateMonlineEdit_2.setStyleSheet("background-color: lightgray;;")
        self.CalDateYearlineEdit_2.setStyleSheet("background-color: lightgray;;")
        self.ProDateDaylineEdit.setStyleSheet("background-color: lightgray;;")
        self.ProDateMonlineEdit.setStyleSheet("background-color: lightgray;;")
        self.ProDateYearlineEdit.setStyleSheet("background-color: lightgray;;")
        self.HWversionlineEdit.setStyleSheet("background-color: lightgray;;")
        self.SWlineEdit.setStyleSheet("background-color: lightgray;;")

######################################################################################################################################
        
    def get_user_data(self):
        get_caldata_cmd=self.modbusid.to_bytes(1, byteorder='big', signed=False)+cmd_dict["r_data_user"]
        crc_data=self._crc16(get_caldata_cmd)
        get_caldata_cmd=get_caldata_cmd+crc_data.to_bytes(2, byteorder='little', signed=False)
        self.ser.write(get_caldata_cmd)
        caldata=self.ser.read(cmd_res_size["r_data_user"])
        #Calculate values 
        module_rate_1			 =(int.from_bytes(caldata[3:5],"big"))
        module_rate_2			 =(int.from_bytes(caldata[5:7],"big"))
        analog_sensor_sel        =(int.from_bytes(caldata[7:9],"big"))
        wind_sensor_offset		 =float(int.from_bytes(caldata[9:11],"big"))
        wind_sensor_slope  	     =float(int.from_bytes(caldata[11:15],"big"))   
        wind_meas_interval		 =(int.from_bytes(caldata[15:17],"big"))
        stable_data_range        =(int.from_bytes(caldata[17:19],"big"))
        stable_data_min          =(int.from_bytes(caldata[19:21],"big"))
        latitude_inf             =float(int.from_bytes(caldata[21:23],"big",signed=True)/100)
        longitude_inf            =float(int.from_bytes(caldata[23:25],"big", signed=True)/100)
        timezone_inf             =(int.from_bytes(caldata[26:27],"big", signed=True))

        #self.WindSlope_data.setText(str(wind_sensor_slope))
        #self.WindMeasInterval_data.setText(str(wind_meas_interval))
        #self.ModuleRate1_data.setText(str(module_rate_1))
        #self.ModuleRate2_data.setText(str(module_rate_2))
        #self.ModRateLine1.setText(str(module_rate_1))
        #self.ModRateLine2.setText(str(module_rate_2))
        #self.total_mod.setText(str(module_rate_1 + module_rate_2))
        #self.WindOffset_data.setText(str(wind_sensor_offset))
        self.stable_data_counter.setText(str(stable_data_min))
        self.stable_data_range.setText(str(stable_data_range ))
        self.stable_data_counter_data_2.setText(str(stable_data_min))
        self.stable_data_range_data.setText(str(stable_data_range))
        self.stable_data_range_data_2.setText(str(stable_data_range))
        self.latitude_data.setText(str(latitude_inf))
        self.longitude_data.setText(str(longitude_inf))
        self.latitude.setText(str(latitude_inf))
        self.longitude.setText(str(longitude_inf))
        self.timezone.setText(str(timezone_inf))
        self.timezone_data.setText(str(timezone_inf))
        #self.OffsetLine.setText(str(wind_sensor_offset))
        #self.InttervalLine.setText(str(wind_meas_interval))
        #self.SlopeLine.setText(str(wind_sensor_slope))       
        
       #============================================================================
#Request Device Version Data 
    def get_ver_data(self):
        for x in range(3):
            self.send_modbus_cmd(modbus_func_codes['sensor_specific'],modbus_sensorspec_reg_addr['version'],0,0)
            self.ver_data=self.ser.read(cmd_res_size["r_version"])
            #if number of the data is less then expected value, read again  
            if(len(self.ver_data)==cmd_res_size["r_version"]):                
                self.connection=True
                break
            else:
                self.connection=False
            sleep(1)
                
        if(self.connection==False):
            self.PortConnect.setCheckState(0)
            msg = QMessageBox()
            msg.setWindowTitle("SevenSensor")
            msg.setText("Connection Fail!")
            msg.setIcon(QMessageBox.Critical)
            x = msg.exec_()
        else:
            hw_version=int.from_bytes(self.ver_data[3:5], "little", signed=False)/100
            self.HardVerD.setText(str(hw_version))
            self.HWversionlineEdit.setText(str(hw_version))
            sf_version=int.from_bytes(self.ver_data[5:7], "little", signed=False)/100
            self.SoftVerD.setText(str(sf_version)) 
            self.SWlineEdit.setText(str(sf_version))
            self.HardVerD_2.setText(str(hw_version))
            self.SoftVerD_2.setText(str(sf_version))

#============================================================================
#Request calibration data 
    def get_cal_data(self):
        self.ser.reset_input_buffer()
        get_caldata_cmd=self.modbusid.to_bytes(1, byteorder='big', signed=False)+cmd_dict["r_data_calib"]
        crc_data=self._crc16(get_caldata_cmd)
        get_caldata_cmd=get_caldata_cmd+crc_data.to_bytes(2, byteorder='little', signed=False)
        self.ser.write(get_caldata_cmd)
        caldata=self.ser.read(cmd_res_size["r_data_calib"])
        #Calculate values 
        sensor_cal_1			 =float(int.from_bytes(caldata[7:9],"big")/10)
        sensor_cal_2			 =float(int.from_bytes(caldata[9:11],"big")/10)
        tk_cell_1 			     =float(int.from_bytes(caldata[11:13],"big")/1000)
        tk_cell_2 			     =float(int.from_bytes(caldata[13:15],"big")/1000)
        ADC_offset_digits_1		 =(int.from_bytes(caldata[15:17],"big"))   
        ADC_offset_digits_2		 =(int.from_bytes(caldata[17:19],"big"))
        #temp_sensor_count        =(int.from_bytes(caldata[19:21],"big")) ##GUI calculates the number of temp_sensor
        avg_numb_module          =(int.from_bytes(caldata[21:23],"big"))
        t90_time			     =(int.from_bytes(caldata[23:25],"big"))
        wind_sensor_offset		 =float(int.from_bytes(caldata[25:27],"big")/1000)
        #=======================================================================
        # soiling_sen_en           =(int.from_bytes(caldata[39:41],"big"))
        #=======================================================================
        
        self.Sensor1calibration_data.setText(str(sensor_cal_1))
        self.Sensor2Calibration_data.setText(str(sensor_cal_2))
        self.TkCell1_data.setText(str(tk_cell_1))
        self.TkCell2_data.setText(str(tk_cell_2))
        self.ADC1OffDig_data.setText(str(ADC_offset_digits_1))
        self.ADC2OffDig_data.setText(str(ADC_offset_digits_2))
        ##################################################################
        self.Sensor1calibration_data_.setText(str(sensor_cal_1))
        self.Sensor2Calibration_data_.setText(str(sensor_cal_2))
        self.TempOff_data_1_.setText(str(tk_cell_1))
        self.TempOff_data_2_.setText(str(tk_cell_2))
        self.ADC1OffDig_data_.setText(str(ADC_offset_digits_1))
        self.ADC2OffDig_data_.setText(str(ADC_offset_digits_2))
        #self.mV10Dig1_data.setText(str(mv10_digits_1))
        #self.dig100mV1_data.setText(str(mv100_digits_1))
        #self.mV10Dig2_data.setText(str(mv10_digits_2))
        #self.dig100mV2_data.setText(str(mv100_digits_2))
        #=======================================================================
        # if(soiling_sen_en==1):
        #     self.soilingSensor_CB.setCheckState(1)
        # else:
        #     self.soilingSensor_CB.setCheckState(0)
        #=======================================================================
        self.CalLine.setText(str(sensor_cal_1))
        self.CalLine_2.setText(str(sensor_cal_2))
        self.TempOffLine.setText(str(tk_cell_1))
        self.TempOffLine_2.setText(str(tk_cell_2))
        self.ADCOffset1_data.setText(str(ADC_offset_digits_1))
        self.ADCOffset2_data.setText(str(ADC_offset_digits_2))
#         if(self.analog_sensor==1):
#             self.ResDD.setText(sensors[0])
#         elif(self.analog_sensor==2):
#             self.ResDD.setText(sensors[1])
#         else:
#             self.ResDD.setText("no device selected") 
            
 #============================================================================
#Request sensor data periodically
    def read_data(self):
        #sendat-->Sensor Data
        self.sensorScanbtn.blockSignals(True)
        self.stopSensorScan.blockSignals(True)
        self.sensorScanbtn_2.blockSignals(True)
        self.stopSensorScan_2.blockSignals(True)
        if(self.ComButWriteAndResetBuuton_flg==True):
            self.ComButWriteAndResetBuuton_flg=False
            self.set_baud_conf_fnc()      
        #=======================================================================

        #=======================================================================
        elif(self.AdcWrButton_flg==True):
            self.AdcWrButton_flg=False
            self.set_adc_config()
        elif(self.SensorCalWRB_flg==True):
            self.SensorCalWRB_flg=False
            self.set_sensor_config()
        elif( self.TimeIntWrButton_flg==True):
            self.TimeIntWrButton_flg=False
            self.set_t90_interval_config()
        elif(self.SetSerNumButton_flg==True):
            self.SetSerNumButton_flg=False
            self.set_serial_number_config()
        elif(self.SetDevInfWr_flg==True):
            self.SetDevInfWr_flg=False
            self.SetDevInfWr_conf()
        elif(self.Set_Time_Button_flg==True):
            self.Set_Time_Button_flg=False
            self.set_time()
        elif( self.setDataCounterBtn_flg==True):
             self.setDataCounterBtn_flg=False
             self.set_stable_data_min_enable()
        elif( self.SetRangeBtn_flg ==True):
             self.SetRangeBtn_flg=False
             self.set_stable_data_range_enable()
        elif(self.setLocateBtn_flg==True):
            self.setLocateBtn_flg=False
            self.set_locate()
        else:
            get_sendata_cmd=self.modbusid.to_bytes(1, byteorder='big', signed=False)+cmd_dict["r_data_sensor"]
            crc_data=self._crc16(get_sendata_cmd)
            get_sendata_cmd=get_sendata_cmd+crc_data.to_bytes(2, byteorder='little', signed=False)
            #QtWidgets.QApplication.processEvents()
            if(self.ser.is_open):   
                self.ser.write(get_sendata_cmd)
                sendata=self.ser.read(cmd_res_size["r_data_sensor"])
                irradiance_1			=(int.from_bytes(sendata[3:5],"big")/10)
                irradiance_2  			=(int.from_bytes(sendata[5:7],"big")/10)
                total_effct_irradiance  =(int.from_bytes(sendata[7:9],"big")/10)
                temp_comp_irradiance_1  =(int.from_bytes(sendata[9:11],"big")/10)
                temp_comp_irradiance_2  =(int.from_bytes(sendata[11:13],"big")/10)
                irradiance_raw_1		=(int.from_bytes(sendata[13:15],"big")/10)
                irradiance_raw_2		=(int.from_bytes(sendata[15:17],"big")/10)
                digit_val_adc_1         =(int.from_bytes(sendata[17:19],"big"))
                digit_val_adc_2         =(int.from_bytes(sendata[19:21],"big"))
                internal_temp_1			=(int.from_bytes(sendata[21:23],"big",signed=True)/10)
                internal_temp_2			=(int.from_bytes(sendata[23:25],"big",signed=True)/10) 
                #modul_temp_1			=(int.from_bytes(sendata[25:27],"big")/10)
                #modul_temp_2			=(int.from_bytes(sendata[27:29],"big")/10)
                #total_effct_module_temp =(int.from_bytes(sendata[29:31],"big")/10)
                #ambient_temp			=(int.from_bytes(sendata[31:33],"big")/10)
                #sht21_temp              =(int.from_bytes(sendata[33:35],"big")/10)
                #relative_humidity       =(int.from_bytes(sendata[35:37],"big")/10)
                #wind_speed              =(int.from_bytes(sendata[37:39],"big")/10)
                #num_of_winds_pulse_high =(int.from_bytes(sendata[39:41],"big"))
                #num_of_winds_pulse_low  =(int.from_bytes(sendata[41:43],"big"))
                #wind_direction          =(int.from_bytes(sendata[43:45],"big")/10)
                #pressure                =(int.from_bytes(sendata[45:47],"big"))
                #rain_gauge              =(int.from_bytes(sendata[47:49],"big")/10)
                soiling_ratio			=(int.from_bytes(sendata[49:51],"big")/10)
                daily_avg_soiling_ratio =(int.from_bytes(sendata[51:53],"big")/10)
                stable_counter          =(int.from_bytes(sendata[53:55],"big"))
                #QtWidgets.QApplication.processEvents()

                self.irradiance1_data.setText(str(121.34))            
                self.irradiance2_data.setText(str(65.2))
                self.IrradianceComp1_data.setText(str(119.23))
                self.IrradianceComp2_data.setText(str(63.3))
                self.InternalTemp1_data.setText(str(23.5))
                self.InternalTemp2_data.setText(str(24.7))
                self.Soiling_Ratio.setText(str(45.2))
                self.Daily_Soiling_Ratio.setText(str(soiling_ratio))
                self.stable_data_counter_data.setText(str(5))
                #self.stable_data_counter_data.setText
                #self.voltage1_data.setText(str(irradiance_raw_1))
                #self.Voltage2_data.setText(str(irradiance_raw_2))
                #self.ADC1digits_data.setText(str(digit_val_adc_1))
                #self.ADC2Digits_data.setText(str(digit_val_adc_2))
                #QtWidgets.QApplication.processEvents()
                if(self.status_logfile == False):
                    self.data_log = [irradiance_1,irradiance_2,temp_comp_irradiance_1,temp_comp_irradiance_2,irradiance_raw_1,irradiance_raw_2,
                                     digit_val_adc_1,digit_val_adc_2,internal_temp_1,internal_temp_2,soiling_ratio,daily_avg_soiling_ratio]
                    self.LogFileThread_ins.start()
                    self.LogFileThread_ins.list_signal.emit(self.data_log)
                    #self.timer.main_to_log.emit(self.data_log)
                #self.timer.quit()
                #self.timer.start()
                self.get_time()
                #sens_count_1            =(bool.from_bytes(sendata[27:29],"big"))
                #sens_count_2            =(bool.from_bytes(sendata[29:31],"big"))
                #total_temp_list = [sens_count_1,sens_count_2]
                #num_temp_sens = 0        
                #for x in total_temp_list:
                #    if (x == True):
                #        num_temp_sens += 1
                #        counter = num_temp_sens
                
                #self.TempSensCount_data.setText(str(num_temp_sens))         
        if(self.kill_timer==False):
            #self.timer= TimerThread()
            #self.timer.update_data.connect(self.read_data)
            #self.timer.start()
            self.timer=threading.Timer(self.period/1000,self.read_data)
            self.timer.start()

        self.sensorScanbtn.blockSignals(False)
        self.stopSensorScan.blockSignals(False)
        self.sensorScanbtn_2.blockSignals(False)
        self.stopSensorScan_2.blockSignals(False)
        #self.timer.start()

#============================================================================
#Calculate CRC
    def _crc16(self, data):
        crc16 = crcmod.mkCrcFun(0x18005, rev=True, initCrc=0xFFFF)
        checkSum = crc16(data)
        return checkSum 

#======================================================================================================================================
#Connect Push Button Calback Function
    def button_set_flag_func(self,id):
            if(id== buttons_ids['ComButWriteAndResetBuuton']):
                self.ComButWriteAndResetBuuton_flg=True
            #===================================================================
            # elif(id==buttons_ids['soilingSenWrButton']):
            #     self.soilingSenWrButton_flg=True
            #===================================================================
            elif(id==buttons_ids['SensorCalWRB']):
                self.SensorCalWRB_flg=True
            elif(id==buttons_ids['AdcWrButton']):
                self.AdcWrButton_flg=True            
            elif(id==buttons_ids['TimeIntWrButton']):
                self.TimeIntWrButton_flg=True
            elif(id==buttons_ids['SetSerNoButton']):
                self.SetSerNumButton_flg=True
            elif(id==buttons_ids['SetDevInfoWrButton']):
                self.SetDevInfWr_flg=True
            elif(id==buttons_ids['SetTimeInfo']):
                self.Set_Time_Button_flg=True
            elif(id==buttons_ids['SetStableRange']):
                self.SetRangeBtn_flg=True
            elif(id==buttons_ids['SetStableMin']):
                self.setDataCounterBtn_flg=True
            elif(id==buttons_ids['setLocateBtn']):
                self.setLocateBtn_flg=True




####################################################
#Push Button Functions 
    def set_baud_conf_fnc(self):
        new_mod_bus_id  =int(self.ModBusActual.text())
        new_baud_rate   =self.BaudComboboxNew.currentText()
        new_parity      =self.ParityNew.currentText()
        #Set bus ID    
        cmd_send=self.send_modbus_cmd(modbus_func_codes['sensor_specific'],modbus_sensorspec_reg_addr['bus_id'],0,new_mod_bus_id.to_bytes(1, byteorder='big', signed=False))
        winds_rsp=self.ser.read(cmd_res_size["w_set_wind"])
        if(winds_rsp==cmd_send):
            self.ModBusActual.setStyleSheet("background-color: rgb(51, 255, 51);;")
        else:
            self.ModBusActual.setStyleSheet("background-color: red;")

        data_com_par=baud_dict[new_baud_rate].to_bytes(1,byteorder='big',signed=False)+parity_dict[new_parity].to_bytes(1,byteorder='big',signed=False)
        com_par_cmd=self.send_modbus_cmd(modbus_func_codes['sensor_specific'],modbus_sensorspec_reg_addr['com_parameters'],0,data_com_par)
        #Set Parity and baud rate 
        com_par_rsp=self.ser.read(cmd_res_size["w_set_wind"])
#         #after configuration Reset the Device and reconnect
        if(com_par_rsp==com_par_cmd):
            self.BaudComboboxNew.setStyleSheet("background-color: rgb(51, 255, 51);;")
            self.ParityNew.setStyleSheet("background-color: rgb(51, 255, 51);;")
            #after configuration Reset the Device and reconnect
            cmd_send=self.send_modbus_cmd(modbus_func_codes['diognastic'], modbus_diognastic_reg_addr['reset'], 0, 0)
            time.sleep(0.1)
            #configure Comport With new values
            #set values for modbus
            self.ser.close() 
            self.modbusid       =int(self.ModBusActual.text())
            self.actual_baud    =new_baud_rate
            self.actual_parity  =new_parity
            self.ser.baudrate=self.actual_baud
            if(self.actual_parity=="none/1"): 
                self.ser.parity=serial.PARITY_NONE
                self.ser.stopbits=serial.STOPBITS_ONE
            elif(self.actual_parity=="none/2"):
                self.ser.parity=serial.PARITY_NONE
                self.ser.stopbits=serial.STOPBITS_TWO
            elif(self.actual_parity=="Even/1"):
                self.ser.parity=serial.PARITY_EVEN
                self.ser.stopbits=serial.STOPBITS_ONE
            elif(self.actual_parity=="Odd/1"):
                self.ser.parity=serial.PARITY_ODD
                self.ser.stopbits=serial.STOPBITS_ONE
            #Take data from GUI and set stop bits 
            self.ser.timeout=1
            self.ser.open()
            #Update Combobox Texts
            self.BaudComboBoxActual.setCurrentText(str(self.actual_baud))    
            self.ParityActual.setCurrentText(str(self.actual_parity))

            self.Parity_variable.setText(str(self.actual_parity))  
            self.device_ID_variable.setText(str(self.modbusid))
            self.baud_rate_variable.setText(str(self.actual_baud))

            self.set_com();
            #Clear Combobox Background Color
            self.BaudComboboxNew.setStyleSheet("background-color: lightgray;;")
            self.ParityNew.setStyleSheet("background-color: lightgray;;")
            self.ModBusActual.setStyleSheet("background-color:lightgray;;")
           
        else:
            self.BaudComboboxNew.setStyleSheet("background-color: red;")
            self.ParityNew.setStyleSheet("background-color: red;")
        sleep(0.5)
        self.BaudComboboxNew.setStyleSheet("background-color: lightgray;;")
        self.ParityNew.setStyleSheet("background-color: lightgray;;")

    
#============================================================================
    def set_mod_rates(self):
        mod_rate_1=int(self.ModRateLine1.text())
        mod_rate_2=int(self.ModRateLine2.text())
        cmd_send=self.send_modbus_cmd(modbus_func_codes['write_single_holding_register'], modbus_wrsingleholding_reg_addr['mode_rate_1'], 0, mod_rate_1.to_bytes(2, byteorder='big', signed=False))
        hold_reg_rsp=self.ser.read(cmd_res_size["r_hold_reg"])
        if(cmd_send==hold_reg_rsp):
            self.ModRateLine1.setStyleSheet("background-color: rgb(51, 255, 51);;")
        else:
            self.ModRateLine1.setStyleSheet("background-color:red;;")

        sleep(0.1);
       # mod_rate_2=int(self.ModRateLine2.text())
        cmd_send=self.send_modbus_cmd(modbus_func_codes['write_single_holding_register'], modbus_wrsingleholding_reg_addr['mode_rate_2'], 0, mod_rate_2.to_bytes(2, byteorder='big', signed=False))
        hold_reg_rsp=self.ser.read(cmd_res_size["r_hold_reg"])
        if(cmd_send==hold_reg_rsp):
            self.ModRateLine2.setStyleSheet("background-color: rgb(51, 255, 51);;")
        else:
            self.ModRateLine2.setStyleSheet("background-color:red;;")
        
        sleep(1)
        self.ModRateLine1.setStyleSheet("background-color: lightgray;;")
        self.ModRateLine2.setStyleSheet("background-color: lightgray;;")

    
#============================================================================
    def set_stable_data_min_enable(self):
        stable_data_counter_inf=int(self.stable_data_counter.text())
        cmd_send=self.send_modbus_cmd(modbus_func_codes['write_single_holding_register'], modbus_wrsingleholding_reg_addr['stable_min'], 0, stable_data_counter_inf.to_bytes(2, byteorder='big', signed=False))
        hold_reg_rsp=self.ser.read(cmd_res_size["r_hold_reg"])
        if(cmd_send==hold_reg_rsp):
            cmd_send=self.send_modbus_cmd(modbus_func_codes['systemreset'],modbus_diognastic_reg_addr['reset'], 0, 0)    
            time.sleep(0.1)  
            self.ser.close()
            self.open_comport_again()
            self.stable_data_counter.setStyleSheet("background-color: rgb(51, 255, 51);;")
            self.get_user_data()
        else:
            self.stable_data_counter.setStyleSheet("background-color:red;;")
            return True
        time.sleep(0.1)
        self.stable_data_counter.setStyleSheet("background-color: lightgray;;")

    def set_stable_data_range_enable(self):
        stable_data_range_inf=int(self.stable_data_range.text())
        cmd_send=self.send_modbus_cmd(modbus_func_codes['write_single_holding_register'], modbus_wrsingleholding_reg_addr['stable_range'], 0, stable_data_range_inf.to_bytes(2, byteorder='big', signed=False))
        hold_reg_rsp=self.ser.read(cmd_res_size["r_hold_reg"])
        if(cmd_send==hold_reg_rsp):
            cmd_send=self.send_modbus_cmd(modbus_func_codes['systemreset'],modbus_diognastic_reg_addr['reset'], 0, 0)    
            time.sleep(0.1)  
            self.ser.close()
            self.open_comport_again()
            self.stable_data_range.setStyleSheet("background-color: rgb(51, 255, 51);;")
            self.get_user_data()
        else:
            self.stable_data_range.setStyleSheet("background-color:red;;")
            return True
        time.sleep(0.1)    
        self.stable_data_range.setStyleSheet("background-color: lightgray;;")
            #self.longitude.setStyleSheet("background-color: lightgray;;")
            

#============================================================================
    def sensor_scan(self):
        if(hasattr(self,"sensor_scan_ins")==False):
            self.sensor_scan_ins=sensor_scan(parent=None,comport=self.PortComboBox.currentText())
             
            self.sensor_scan_ins.baud_rate.connect(self.sensor_scan_baud_up)    
            self.sensor_scan_ins.dev_id.connect(self.sensor_scan_dev_id_up)    
            self.sensor_scan_ins.parity.connect(self.sensor_scan_parity_up)    
            self.sensor_scan_ins.completed_tr.connect(self.sensor_scan_completed)
            self.sensor_scan_ins.message_error.connect(self.message_box)
            ##############################################################
        self.sensor_scan_ins.refresh_comport(self.PortComboBox.currentText())
        if(self.ID_Range_1.text()!="-" and self.ID_Range_1.text()!=''):
            if(int(self.ID_Range_1.text())<=255):
                self.sensor_scan_ins.chosen_id_1 = int(self.ID_Range_1.text())
            else:
                self.message_box("Invalid ID")
                return
        else:
            self.sensor_scan_ins.chosen_id_1 = 0
            
        if(self.ID_Range_2.text()!="-" and self.ID_Range_2.text()!=''):
            self.sensor_scan_ins.chosen_id_2 = int(self.ID_Range_2.text()) 
        else:
            self.sensor_scan_ins.chosen_id_2 = 255 
        self.sensor_scan_ins.chosen_baud = self.Baud_Range.currentIndex()
        self.sensor_scan_ins.chosen_parity = self.Parity_Range.currentIndex()
            
            
            #TODO
        self.sensor_scan_ins.start()
        self.sensorScanbtn.blockSignals(True)
        self.UpdateFirmware.blockSignals(True)
        self.file_select.blockSignals(True)
#         self.stopSensorScan.blockSignals(True)
        self.sensorScanbtn.blockSignals(True)
        
    def sensor_scan_baud_up(self,value=0): 
        self.baud_rate_variable.setText(str(value))

    def sensor_scan_dev_id_up(self,value=2400):
        self.device_ID_variable.setText(str(value))
        

    def sensor_scan_parity_up(self,value=None):
        self.Parity_variable.setText(str(value))
        
    def sensor_scan_completed(self,status=None):
        if(status!=True):
            self.message_box("Sensor Device is not found")
        else:
            self.message_box("Sensor Device is found")
            self.modbusid=self.device_ID_variable.text()
            self.actual_baud=self.baud_rate_variable.text()
            self.actual_parity=self.Parity_variable.text()
            self.ModBusActual.setText(str(self.modbusid))
            self.BaudComboBoxActual.setCurrentText(str(self.actual_baud))
            self.ParityActual.setCurrentText(str(self.actual_parity))
            self.set_com()
        self.sensor_scan_ins.stop() 
        self.sensorScanbtn.blockSignals(False)
        self.UpdateFirmware.blockSignals(False)
        self.file_select.blockSignals(False)
        self.stopSensorScan.blockSignals(False)
        self.sensorScanbtn.blockSignals(False)
  
    def sensor_stop_scan(self):
        if(hasattr(self,"sensor_scan_ins")):
            self.sensor_scan_ins.stop()
            self.sensorScanbtn.blockSignals(False)
            self.UpdateFirmware.blockSignals(False)
            self.file_select.blockSignals(False) 
            self.stopSensorScan.blockSignals(False)
            self.sensorScanbtn.blockSignals(False)



    def set_windsensor_config(self):
        wind_bias=int((float(self.OffsetLine.text())*1000))
        wind_interval=int(self.InttervalLine.text())
        wind_slope=int((float(self.SlopeLine.text()))*100000)
        wind_slope_array=wind_slope.to_bytes(4,byteorder='big', signed=False)
        cmd_send=self.send_modbus_cmd(modbus_func_codes['write_single_holding_register'], modbus_wrsingleholding_reg_addr['wind_bias'], 0, wind_bias.to_bytes(2, byteorder='big', signed=False))
        hold_reg_rsp=self.ser.read(cmd_res_size["r_hold_reg"])
        if(cmd_send==hold_reg_rsp):
            self.OffsetLine.setStyleSheet("background-color: rgb(51, 255, 51);;")
        else:
            self.OffsetLine.setStyleSheet("background-color:red;;")     
        
        cmd_send=self.send_modbus_cmd(modbus_func_codes['write_single_holding_register'], modbus_wrsingleholding_reg_addr['wind_interval'], 0, wind_interval.to_bytes(2, byteorder='big', signed=False))
        hold_reg_rsp=self.ser.read(cmd_res_size["r_hold_reg"])
        if(cmd_send==hold_reg_rsp):
            self.InttervalLine.setStyleSheet("background-color: rgb(51, 255, 51);;")
        else:
            self.InttervalLine.setStyleSheet("background-color:red;;")     
        wind_slope_high=wind_slope_array[0:2]
        wind_slope_low =wind_slope_array[2:]
        cmd_send=self.send_modbus_cmd(modbus_func_codes['write_single_holding_register'],modbus_wrsingleholding_reg_addr['wind_slope_high'],0,wind_slope_high)
        hold_reg_rsp=self.ser.read(cmd_res_size["r_hold_reg"])
        sleep(0.1)
        cmd_send=self.send_modbus_cmd(modbus_func_codes['write_single_holding_register'],modbus_wrsingleholding_reg_addr['wind_slope_low'],0,wind_slope_low)
        hold_reg_rsp=self.ser.read(cmd_res_size["r_hold_reg"])
        if(cmd_send==hold_reg_rsp):
            self.SlopeLine.setStyleSheet("background-color: rgb(51, 255, 51);;")
        else:
            self.SlopeLine.setStyleSheet("background-color:red;;")     

        sleep(1)
        self.OffsetLine.setStyleSheet("background-color: lightgray;;")
        self.InttervalLine.setStyleSheet("background-color: lightgray;;")
        self.SlopeLine.setStyleSheet("background-color: lightgray;;")


#============================================================================
    def set_sensor_config(self):
        calibration_1=int(float(self.CalLine.text())*10)
        calibration_2=int(float(self.CalLine_2.text())*10)
        tempcoef_1   =int(float(self.TempOffLine.text())*1000)
        tempcoef_2   =int(float(self.TempOffLine_2.text())*1000)
        
        cmd_send=self.send_modbus_cmd(modbus_func_codes['write_single_holding_register'], modbus_wrsingleholding_reg_addr['calibration_1'], 0, calibration_1.to_bytes(2, byteorder='big', signed=False))
        hold_reg_rsp=self.ser.read(cmd_res_size["r_hold_reg"])
        if(cmd_send==hold_reg_rsp):
            self.CalLine.setStyleSheet("background-color: rgb(51, 255, 51);;")
        else:
            self.CalLine.setStyleSheet("background-color:red;;")     

        cmd_send=self.send_modbus_cmd(modbus_func_codes['write_single_holding_register'], modbus_wrsingleholding_reg_addr['calibration_2'], 0, calibration_2.to_bytes(2, byteorder='big', signed=False))
        hold_reg_rsp=self.ser.read(cmd_res_size["r_hold_reg"])
        if(cmd_send==hold_reg_rsp):
            self.CalLine_2.setStyleSheet("background-color: rgb(51, 255, 51);;")
        else:
            self.CalLine_2.setStyleSheet("background-color:red;;")  

        cmd_send=self.send_modbus_cmd(modbus_func_codes['write_single_holding_register'], modbus_wrsingleholding_reg_addr['temp_coeff_1'], 0, tempcoef_1.to_bytes(2, byteorder='big', signed=False))
        hold_reg_rsp=self.ser.read(cmd_res_size["r_hold_reg"])
        if(cmd_send==hold_reg_rsp):
            self.TempOffLine.setStyleSheet("background-color: rgb(51, 255, 51);;")
        else:
            self.TempOffLine.setStyleSheet("background-color:red;;")  
            
        cmd_send=self.send_modbus_cmd(modbus_func_codes['write_single_holding_register'], modbus_wrsingleholding_reg_addr['temp_coeff_2'], 0, tempcoef_2.to_bytes(2, byteorder='big', signed=False))
        hold_reg_rsp=self.ser.read(cmd_res_size["r_hold_reg"])
        if(cmd_send==hold_reg_rsp):
            self.TempOffLine_2.setStyleSheet("background-color: rgb(51, 255, 51);;")

            cmd_send=self.send_modbus_cmd(modbus_func_codes['systemreset'],modbus_diognastic_reg_addr['reset'], 0, 0)    
            time.sleep(0.1)  
            self.ser.close()
     
            self.open_comport_again()
            self.get_cal_data()
            #self.get_user_data()
        else:
            self.TempOffLine_2.setStyleSheet("background-color:red;;")   
        
        sleep(1)    
        self.CalLine.setStyleSheet("background-color: lightgray;;")
        self.CalLine_2.setStyleSheet("background-color:lightgray;;")  
        self.TempOffLine.setStyleSheet("background-color: lightgray;;")
        self.TempOffLine_2.setStyleSheet("background-color: lightgray;;")

  #============================================================================
    def set_adc_config(self):
        try:
            adc_1=int(self.ADCOffset1_data.text())
            adc_2=int(self.ADCOffset2_data.text())
        except:
            self.worker.my_signal.emit("At least one value is not set on the device Info field")
            return True

        cmd_send=self.send_modbus_cmd(modbus_func_codes['write_single_holding_register'], modbus_wrsingleholding_reg_addr['ADC_offset_1'], 0, adc_1.to_bytes(2, byteorder='big', signed=False))
        hold_reg_rsp=self.ser.read(cmd_res_size["r_hold_reg"])
        if(cmd_send==hold_reg_rsp):
            self.ADCOffset1_data.setStyleSheet("background-color: rgb(51, 255, 51);;")
        else:
            self.ADCOffset1_data.setStyleSheet("background-color:red;;")
        
        cmd_send=self.send_modbus_cmd(modbus_func_codes['write_single_holding_register'], modbus_wrsingleholding_reg_addr['ADC_offset_2'], 0, adc_2.to_bytes(2, byteorder='big', signed=False))
        hold_reg_rsp=self.ser.read(cmd_res_size["r_hold_reg"])
        if(cmd_send==hold_reg_rsp):
            self.ADCOffset2_data.setStyleSheet("background-color: rgb(51, 255, 51);;")

            cmd_send=self.send_modbus_cmd(modbus_func_codes['systemreset'],modbus_diognastic_reg_addr['reset'], 0, 0)    
            time.sleep(0.1)  
            self.ser.close()
     
            self.open_comport_again()
            self.get_cal_data()
        else:
            self.ADCOffset2_data.setStyleSheet("background-color:red;;")
        
        sleep(1)    
        self.ADCOffset1_data.setStyleSheet("background-color: lightgray;;")
        self.ADCOffset2_data.setStyleSheet("background-color: lightgray;;")
            
            
  #============================================================================
    def set_t90_interval_config(self):          
        t90_int=int(self.t90Line.text())
        
        cmd_send=self.send_modbus_cmd(modbus_func_codes['write_single_holding_register'], modbus_wrsingleholding_reg_addr['t90_int'], 0, t90_int.to_bytes(2, byteorder='big', signed=False))
        hold_reg_rsp=self.ser.read(cmd_res_size["r_hold_reg"])
        if(cmd_send==hold_reg_rsp):
            self.t90Line.setStyleSheet("background-color: rgb(51, 255, 51);;")
            cmd_send=self.send_modbus_cmd(modbus_func_codes['systemreset'],modbus_diognastic_reg_addr['reset'], 0, 0)    
            time.sleep(0.1)  
            self.ser.close()
     
            self.open_comport_again()
            self.get_cal_data()
        else:
            self.t90Line.setStyleSheet("background-color:red;;")
            
        sleep(1)    
        self.t90Line.setStyleSheet("background-color: lightgray;;")
            
  #============================================================================
    def set_time(self):
        #day_info = int(self.day_value.text())
        #month_info = int(self.month_value.text())
        #year_info = int(self.year_value.text())
        #hour_info = int(self.hour_Value.text())
        #minute_info = int(self.minute_Value.text())
        self.set_onetime=0;

        if(int(self.year_value.text()) > 100):
            self.year_value.setStyleSheet("background-color: red;")
            sleep(0.5)
            self.year_value.setStyleSheet("background-color: white;")


        elif(int(self.month_value.text()) > 12):
            self.month_value.setStyleSheet("background-color: red;")
            sleep(0.5)
            self.month_value.setStyleSheet("background-color: white;")

        elif(int(self.day_value.text()) > 31):
            self.day_value.setStyleSheet("background-color: red;")
            sleep(0.5)
            self.day_value.setStyleSheet("background-color: white;")

        else:
            year_info = '0x' + (self.year_value.text())
            month_info = '0x' + (self.month_value.text())
            day_info = '0x' + (self.day_value.text())
            hour_info = '0x' + (self.hour_value.text())
            minute_info = '0x' + (self.minute_value.text())

            hex_day_info = int(day_info, base = 16)
            hex_month_info = int(month_info, base = 16)
            hex_year_info = int(year_info, base = 16)
            hex_hour_info = int(hour_info, base = 16)
            hex_minute_info = int(minute_info, base = 16)

            set_time_inf=hex_year_info.to_bytes(1, byteorder='big', signed=False)+ \
                hex_month_info.to_bytes(1, byteorder='big', signed=False)+ \
                hex_day_info.to_bytes(1, byteorder='big', signed=False)+ \
                hex_hour_info.to_bytes(1, byteorder='big', signed=False)+ \
                hex_minute_info.to_bytes(1, byteorder='big', signed=False)

            cmd_setTimeInf=self.send_modbus_cmd(modbus_func_codes['sensor_specific'], modbus_sensorspec_reg_addr['set_time'],0, set_time_inf)
            rsp_setTimeInf=self.ser.read(cmd_res_size['set_time_inf'])
        
            if(rsp_setTimeInf==cmd_setTimeInf):
                self.day_value.setStyleSheet("background-color: rgb(51, 255, 51);;")
                self.hour_value.setStyleSheet("background-color: rgb(51, 255, 51);;")
                self.month_value.setStyleSheet("background-color: rgb(51, 255, 51);;")
                self.year_value.setStyleSheet("background-color: rgb(51, 255, 51);;")
                self.minute_value.setStyleSheet("background-color: rgb(51, 255, 51);;")
            else:
                self.day_value.setStyleSheet("background-color: red;")
                self.hour_value.setStyleSheet("background-color: red;")
                self.month_value.setStyleSheet("background-color: red;")
                self.year_value.setStyleSheet("background-color: red;")
                self.minute_value.setStyleSheet("background-color: red;")
            
            sleep(1)       
            self.day_value.setStyleSheet("background-color: lightgray;;")
            self.hour_value.setStyleSheet("background-color: lightgray;;")
            self.month_value.setStyleSheet("background-color: lightgray;;")
            self.year_value.setStyleSheet("background-color: lightgray;;")
            self.minute_value.setStyleSheet("background-color: lightgray;;")
        
        self.get_time()

    def set_locate(self):
        self.latitue_info = int(float(self.latitude.text())*100)
        self.longitude_info = int(float(self.longitude.text())*100)
        self.timezone_info =int(self.timezone.text())


        if(float(self.latitude.text())>90 or float(self.latitude.text())<-90):
            self.worker.my_signal.emit("Out of the range")
            return True
        if(float(self.longitude.text())>180 or float(self.longitude.text())<-180):
            self.worker.my_signal.emit("Out of the range")
            return True
        if len(self.latitude.text().split('.')[-1]) > 2:
            self.worker.my_signal.emit("Must be 2 digits after the comma")
            return True
        if len(self.longitude.text().split('.')[-1]) > 2:
            self.worker.my_signal.emit("Must be 2 digits after the comma")
            return True

        set_locate_msg = self.latitue_info.to_bytes(2, byteorder='big', signed=True) + \
                        self.longitude_info.to_bytes(2, byteorder='big', signed=True) + \
                        self.timezone_info.to_bytes(1, byteorder='big', signed=True)

        cmd_setLocatInf=self.send_modbus_cmd(modbus_func_codes['sensor_specific'], modbus_sensorspec_reg_addr['set_locate'],0, set_locate_msg)
        rsp_setLocatInf=self.ser.read(cmd_res_size['set_locate_inf'])

        if(cmd_setLocatInf==rsp_setLocatInf):
            self.latitude.setStyleSheet("background-color: rgb(51, 255, 51);;")
            self.longitude.setStyleSheet("background-color: rgb(51, 255, 51);;") 
            self.timezone.setStyleSheet("background-color: rgb(51, 255, 51);;")
            cmd_send=self.send_modbus_cmd(modbus_func_codes['systemreset'],modbus_diognastic_reg_addr['reset'], 0, 0)    #FURKAN 
            time.sleep(0.1)  
            self.ser.close() 
       

            self.open_comport_again() 
            self.get_user_data()
        else:
            self.latitude.setStyleSheet("background-color: red;")
            self.longitude.setStyleSheet("background-color: red;")
            self.timezone.setStyleSheet("background-color: lightgray;;")


        self.latitude.setStyleSheet("background-color: lightgray;;")
        self.longitude.setStyleSheet("background-color: lightgray;;")
        self.timezone.setStyleSheet("background-color: lightgray;;")

  #============================================================================
    def get_time(self):
        cmd_gettimeInf=self.send_modbus_cmd(modbus_func_codes['sensor_specific'], modbus_sensorspec_reg_addr['get_time'],0, 0)
        try: 
            rsp_gettimeInf=self.ser.read(cmd_res_size['get_time_inf'])
        except:
            return True

        year_info=int.from_bytes(rsp_gettimeInf[3:5], "big")
        month_info=int.from_bytes(rsp_gettimeInf[5:7], "big")
        day_info=int.from_bytes(rsp_gettimeInf[7:9], "big")
        hour_info=int.from_bytes(rsp_gettimeInf[9:11], "big")
        minute_info=int.from_bytes(rsp_gettimeInf[11:13], "big")

        date_month_year_inf=str(day_info)+"."+str(month_info)+".20"+str(year_info)
        self.date_month_year_inf_label.setText(date_month_year_inf)

        if(hour_info<10 and minute_info<10):
            hour_min_inf="0"+str(hour_info)+":0"+str(minute_info)
            self.hour_min_label.setText(hour_min_inf)
        elif(hour_info<10):
            hour_min_inf="0"+str(hour_info)+":"+str(minute_info)
            self.hour_min_label.setText(hour_min_inf)
        elif(minute_info<10):
            hour_min_inf=str(hour_info)+":0"+str(minute_info)
            self.hour_min_label.setText(hour_min_inf)
        else:
            hour_min_inf=str(hour_info)+":"+str(minute_info)
            self.hour_min_label.setText(hour_min_inf)
        if(self.set_onetime==0):
            self.set_onetime += 1;
            self.year_value.setText(str(year_info))
            self.month_value.setText(str(month_info))
            self.day_value.setText(str(day_info))
            self.hour_value.setText(str(hour_info))
            self.minute_value.setText(str(minute_info))

  #============================================================================

    def set_serial_number_config(self):
        try:
            prYear=int(self.PrYearlineEdit.text())
            prCode=int(self.PrCodelineEdit.text())
            cellSer=int(self.CellCerNolineEdit.text())
            boardSer=int(self.BoardSerNolineEdit.text())
            boxSer=int(self.BoxSerNolineEdit.text())
            irrSer=int(self.IrrSerNolineEdit.text())
        except:
            self.worker.my_signal.emit("At least one value is not set on the device Info field")
            return True
        
        serial_num=prYear.to_bytes(1, byteorder='big', signed=False)+ \
                    prCode.to_bytes(1, byteorder='big', signed=False)+ \
                    cellSer.to_bytes(2, byteorder='big', signed=False)+ \
                    boardSer.to_bytes(1, byteorder='big', signed=False)+ \
                    boxSer.to_bytes(1, byteorder='big', signed=False)+ \
                    irrSer.to_bytes(2, byteorder='big', signed=False)
                 
        cmd_serNum=self.send_modbus_cmd(modbus_func_codes['sensor_specific'], modbus_sensorspec_reg_addr['set_serial'],0, serial_num)
        rsp_serNum=self.ser.read(cmd_res_size['set_ser_num'])
        
        if(rsp_serNum==cmd_serNum):
            self.PrYearlineEdit.setStyleSheet("background-color: rgb(51, 255, 51);;")
            self.PrCodelineEdit.setStyleSheet("background-color: rgb(51, 255, 51);;")
            self.CellCerNolineEdit.setStyleSheet("background-color: rgb(51, 255, 51);;")
            self.BoardSerNolineEdit.setStyleSheet("background-color: rgb(51, 255, 51);;")
            self.BoxSerNolineEdit.setStyleSheet("background-color: rgb(51, 255, 51);;")
            self.IrrSerNolineEdit.setStyleSheet("background-color: rgb(51, 255, 51);;")

            cmd_send=self.send_modbus_cmd(modbus_func_codes['systemreset'],modbus_diognastic_reg_addr['reset'], 0, 0)    #FURKAN 
            time.sleep(0.1)  
            self.ser.close() 
       

            self.open_comport_again()    
            #self.get_cal_data()
            self.get_ser_data()
        else:
            self.PrYearlineEdit.setStyleSheet("background-color: red;")
            self.PrCodelineEdit.setStyleSheet("background-color: red;")
            self.CellCerNolineEdit.setStyleSheet("background-color: red;")
            self.BoardSerNolineEdit.setStyleSheet("background-color: red;")
            self.BoxSerNolineEdit.setStyleSheet("background-color: red;")
            self.IrrSerNolineEdit.setStyleSheet("background-color: red;")
            
        sleep(1)       
        self.PrYearlineEdit.setStyleSheet("background-color: lightgray;;")
        self.PrCodelineEdit.setStyleSheet("background-color: lightgray;;")
        self.CellCerNolineEdit.setStyleSheet("background-color: lightgray;;")
        self.BoardSerNolineEdit.setStyleSheet("background-color: lightgray;;")
        self.BoxSerNolineEdit.setStyleSheet("background-color: lightgray;;")
        self.IrrSerNolineEdit.setStyleSheet("background-color: lightgray;;")


#============================================================================
            
    def set_sel_config(self):
        sensor_sel_text=self.SensorSelComboBox.currentText()  
        if(sensor_sel_text==sensors[0]):
            sensor_sel_val=0
        elif (sensor_sel_text==sensors[1]):
            sensor_sel_val=1
        else:
            sensor_sel_val=2      
            
        set_ang_sen_sel_cmd=self.modbusid.to_bytes(1, byteorder='big', signed=False)+cmd_dict["w_set_an_sen_sel"] + sensor_sel_val.to_bytes(2,byteorder='big', signed=False)
        crc_data=self._crc16(set_ang_sen_sel_cmd)
        set_ang_sen_sel_cmd=set_ang_sen_sel_cmd+crc_data.to_bytes(2, byteorder='little', signed=False)
        self.ser.write(set_ang_sen_sel_cmd)
        winds_rsp=self.ser.read(cmd_res_size["w_set_wind"])
        #Read Response and Check, If its okay set background color Green, else red 
        if(winds_rsp==set_ang_sen_sel_cmd):
            self.SensorSelComboBox.setStyleSheet("background-color: rgb(51, 255, 51);;")
        else:
            self.SensorSelComboBox.setStyleSheet("background-color: red;")
            
        sleep(1)            
        self.SensorSelComboBox.setStyleSheet("background-color: rgb(51, 255, 51);;")
             
    def open_binay_file(self):
        #this function will open the dialog and select the file which will send to the cpu 
        self.fname = QFileDialog.getOpenFileName(None, "Open file", "C:/","Bin File(*.bin)")
        self.FileNameLine.setText(str(self.fname[0]))
        self.UpdateFirmware.blockSignals(False)

    def update_progress_bar(self,value):    
        self.progressBar.setValue(value)

    def fileTransmitdone(self):
        self.UpdateFirmware.blockSignals(False)
        self.file_select.blockSignals(False)
        self.run_iap.stop()
        
        
    
    def upgrade_firmware_func(self):
        #Switch to the boot-loader application (CPU Side) 
        #Get C character to confirm that boot-loader application is running 
        #Open File
        if(self.PortConnect.isChecked()):
            self.kill_timer=True
            self.connection=False
            self.timer.join()
            cmd_send=self.send_modbus_cmd(modbus_func_codes['systemreset'],modbus_diognastic_reg_addr['reset'], 0, 0)
            if(self.timer.isAlive()):
                self.timer.cancel()
            self.isTimerCreated = False
            self.ser.close()
            self.PortConnect.setCheckState(0)
        #TODO   
        if(hasattr(self, "fname")):
            iap_protocol.res_com_flag=0
            self.run_iap=iap_protocol(parent=None,comport=self.PortComboBox.currentText(),file_name=self.fname[0])
            self.run_iap.start()
            self.run_iap.percentoffile.connect(self.update_progress_bar)    
            self.run_iap.message_error.connect(self.message_box)    
            self.run_iap.filetransmitdoneflg.connect(self.fileTransmitdone)    
            self.UpdateFirmware.blockSignals(True)
            self.Reset_Com_Settings.blockSignals(True)
            self.file_select.blockSignals(True)
            self.stopSensorScan.blockSignals(True)
            self.sensorScanbtn.blockSignals(True)
            self.worker.my_signal.emit("Please wait while the system is being updated.")
        else:
            print("the file is not selected!!")

    def reset_com_settings(self):        
        #Switch to the boot-loader application (CPU Side) 
        #Get C character to confirm that boot-loader application is running 
        print("start reset_com_settings function")
        #if():
        iap_protocol.res_com_flag = 1
        self.run_iap=iap_protocol(parent=None,comport=self.PortComboBox.currentText(),file_name=None)
        self.run_iap.start()
        self.run_iap.message_error.connect(self.message_box) 
        #self.run_iap.message_error.connect(self.message_box)  
        self.Reset_Com_Settings.blockSignals(True)
        self.UpdateFirmware.blockSignals(True)
        self.file_select.blockSignals(True)
        self.stopSensorScan.blockSignals(True)
        self.sensorScanbtn.blockSignals(True)

        

    def log_to_file(self):
        if(self.logFileState.isChecked() and self.PortConnect.isChecked()):
            if(hasattr(self,"LogFileThread_ins")==False):
                self.LogFileThread_ins = LogFileThread()
                self.LogFileThread_ins.status_signal.connect(self.logfile_status_index)
                self.LogFileThread_ins.list_signal.connect(self.on_change_list)
                self.LogFileThread_ins.BaudRate = self.ser.baudrate
                self.LogFileThread_ins.ID = self.modbusid
                self.LogFileThread_ins.Parity = self.Parity_Value
                self.LogFileThread_ins.SerNum = self.ser_num

            self.LogFileThread_ins.start()

            print("started")
        else:
            if(hasattr(self,"LogFileThread_ins")):
                self.LogFileThread_ins.stop_log_file()




        #else:
        #    self.LogFileThread_ins.stop_signal.connect(self.stop_log_file)


    def logfile_status_index(self,value=None):
        self.status_logfile = value
        #if(value == False):
            #self.LogFileThread_ins.stop()

    def open_comport_again(self):
        sleep(1) 
        self.modbusid       =int(self.ModBusNew.text())
        self.actual_baud    =self.BaudComboBoxActual.currentText()
        self.actual_parity  =self.ParityActual.currentText()                         #FURKAN
        self.ser.baudrate = self.actual_baud
        if(self.actual_parity=="none/1"): 
            self.ser.parity=serial.PARITY_NONE
            self.ser.stopbits=serial.STOPBITS_ONE
        elif(self.actual_parity=="none/2"):
            self.ser.parity=serial.PARITY_NONE
            self.ser.stopbits=serial.STOPBITS_TWO
        elif(self.actual_parity=="Even/1"):
            self.ser.parity=serial.PARITY_EVEN
            self.ser.stopbits=serial.STOPBITS_ONE
        elif(self.actual_parity=="Odd/1"):
            self.ser.parity=serial.PARITY_ODD
            self.ser.stopbits=serial.STOPBITS_ONE
        #Take data from GUI and set stop bits 
        self.ser.timeout=1
        self.ser.open()
        self.ser.reset_input_buffer()


    def message_box(self,message=None):
        self.msg=QMessageBox()
        self.msg.setWindowTitle("warning")
        self.msg.setText(message)
        self.msg.setIcon(QMessageBox.Warning)
        x=self.msg.exec() 