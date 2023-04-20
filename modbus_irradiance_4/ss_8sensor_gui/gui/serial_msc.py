'''
Created on 10 Jan 2021

@author: sy
'''
sensor_scan_addr=range(1,31)
#baudrate_list=["38400","19200","9600","4800"]
baudrate_list=["9600","19200","38400","4800"]
#baudrate_list=["4800","9600","19200","38400"]
# baudrate_list=["9600"]


sensors=["Wind Direction Sensor", "Relative Humidity Sensor"]

parity_list=["none/1","none/2","Even/1","Odd/1"]  

modbus_func_codes={
    'read_input_register':b'\x04',
    'write_single_holding_register':b'\x06',
    'diognastic':b'\x08',
    'sensor_specific':b'\x46',
    'systemreset':b'\x09',
} 

modbus_rdinput_reg_addr={
    'sensor_data':b'\x00\x00',
    'sensor_settings':b'\x00\x4D',
    }

modbus_rdinput_word_num={
    'sensor_data':b'\x00\x14',
    'sensor_settings':b'\x00\x12',
    }

modbus_diognastic_reg_addr={
    'reset'             :b'\x00\x00\x00\x00',
    }

modbus_wrsingleholding_reg_addr={
    'wind_bias'         :b'\x00\x5A',
    'wind_slope_high'   :b'\x00\x5B',
    'wind_slope_low'    :b'\x00\x5C',
    'wind_interval'     :b'\x00\x5D',
    'mode_rate_1'       :b'\x00\x5E',
    'mode_rate_2'       :b'\x00\x5F',
    'soiling_sensor_en' :b'\x00\x60',
    'ADC_offset_1'      :b'\x00\x61',
    'ADC_offset_2'      :b'\x00\x62',
    'calibration_1'     :b'\x00\x63',
    'calibration_2'     :b'\x00\x64',
    'temp_coeff_1'      :b'\x00\x65',
    'temp_coeff_2'      :b'\x00\x66',
    't90_int'           :b'\x00\x67',
    'stable_range'      :b'\x00\x68',
    'stable_min'        :b'\x00\x69',
}

modbus_diognastic_reg_addr={
    'reset'             :b'\x00\x00\x00\x00',
    }

modbus_sensorspec_reg_addr={
    
    'bus_id'            :b'\x04',
    'com_parameters'    :b'\x06',
    'version'           :b'\x07',
    'get_serial'        :b'\x08',
    'set_serial'        :b'\x09',
    'set_cal_date'      :b'\x0A',   # Emre
    'set_pro_date'      :b'\x0B',   #Emre
    'set_hwsw_version'  :b'\x0C',   #Emre
    'get_time'          :b'\x0D',
    'set_time'          :b'\x0E',
    'set_locate'        :b'\x0F',
    }


cmd_dict = {
    'r_data_sensor' :b'\x04\x00\x00\x00\x1A', #Get Sensor data #14
    'r_data_calib'  :b'\x04\x00\x3C\x00\x12', #Get manufacturer data
    'r_data_user'    :b'\x04\x00\x6E\x00\x0C', #Get user Data  #12
    'w_set_wind_bias'       :b'\x06\x00\x5A',         #Set Wind Sensor Calibration Data (Base 5A)
    'w_set_wind_slp_high'   :b'\x06\x00\x5B',         #Set Wind Sensor Calibration Data (Base 5A)
    'w_set_wind_slp_low'    :b'\x06\x00\x5C',         #Set Wind Sensor Calibration Data (Base 5A)
    'w_set_wind_interval'   :b'\x06\x00\x5D',         #Set Wind Sensor Calibration Data (Base 5A)
    'w_set_an_sen_sel'		:b'\x06\x00\x5E',               #Write Flash to the analog Sensor Selection
    'w_set_sen_cal'   		:b'\x06\x00\x5F',               #Write Sensor calibration and temperature coefficients
    'w_set_sen_temp'   		:b'\x06\x00\x60',               #Write Sensor calibration and temperature coefficients
    'cal_iap_func'          :b'\x06\x00\x61',
    'w_recon'       		:b'\x08\x00\x00\x00\x00',
    'r_bus_id'      		:b'\x46\x04',
    'r_w_com_par'   		:b'\x46\x06',
    'r_version'     		:b'\x46\x07',
    'r_ser_data'    		:b'\x46\x08',           #Get Serial Number and production Date 
}
cmd_res_size = {
    'r_data_sensor' :60,   #45
    'r_data_calib'  :48,   #48
    'r_data_user'   :29,   #32
    'w_set_wind'    :8,
    'w_recon'       :4,
    'r_bus_id'      :4,
    'r_w_com_par'   :4,
    'r_version'     :10,
    'r_ser_data'    :24,    #22Emre
    'r_w_sen_sel'   :4,
    'r_hold_reg'    :8,
    'set_ser_num'   :15, #8 #13Emre
    'set_cal_date'  :11,
    'set_pro_date'  :10,
    'set_hwsw_ver'  : 9,
    'set_time_inf'  :10,
    'get_time_inf'  :15,
    'set_locate_inf':10,
    }

baud_dict ={
    '1200' :0,
    '2400' :1,
    '9600' :2,
    '19200' :3,
    '38400' :4,
    }
    
parity_dict = {
    'none/1' :0,
    'none/2' :1,
    'Odd/1'  :2,
    'Even/1' :3,
    }
    