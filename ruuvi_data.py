from ruuvitag_sensor.ruuvi import RuuviTagSensor, RunFlag
from collections import OrderedDict
import time
import sys, os, io
import struct

counter = 10

# RunFlag for stopping execution at desired time
run_flag = RunFlag()

tagset = set()
file_object = 0;

sleepTime = 10

#Function to convert battery voltage to percentage for Ruuvi
def _to_percent(mvolts):
    battery_level = 0;
    if mvolts >= 3000:
        battery_level = 100
    elif mvolts > 2900:
        battery_level = 100 - ((3000 - mvolts) * 58) / 100
    elif mvolts > 2740:
        battery_level = 42 - ((2900 - mvolts) * 24) / 160
    elif mvolts > 2440:
        battery_level = 18 - ((2740 - mvolts) * 12) / 300
    elif mvolts > 2100:
        battery_level = 6 - ((2440 - mvolts) * 6) / 340

    return int(battery_level)

def handle_data(found_data):
    global file_object
    global tagset;
    
    # only one reading per tag
    if found_data[0] not in tagset:
        tagset.add(found_data[0])

        #Populate values based on MAC
        mac = found_data[1]['mac']

        #accel_x = found_data[1]['acceleration_x']
        #accel_y = found_data[1]['acceleration_y']
        #accel_z = found_data[1]['acceleration_z']
        batterylevel = _to_percent(found_data[1]['battery'])
        env_temperature = found_data[1]['temperature']
        env_humidity = found_data[1]['humidity']
        env_pressure = found_data[1]['pressure']
        
        valName  = "mode=\"temp_RUUVI_"+mac+"\""
        valName  = "{" + valName + "}"
        dataStr  = f"RUUVI{valName} {env_temperature}"
        print(dataStr, file=file_object)
    
        valName  = "mode=\"hum_RUUVI_"+mac+"\""
        valName  = "{" + valName + "}"
        dataStr  = f"RUUVI{valName} {env_humidity}"
        print(dataStr, file=file_object)
 
        valName  = "mode=\"pres_RUUVI_"+mac+"\""
        valName  = "{" + valName + "}"
        dataStr  = f"RUUVI{valName} {env_pressure}"
        print(dataStr, file=file_object)
 
        valName  = "mode=\"bat_RUUVI_"+mac+"\""
        valName  = "{" + valName + "}"
        dataStr  = f"RUUVI{valName} {batterylevel}"
        print(dataStr, file=file_object)

    global counter
    counter = counter - 1
    if counter < 0:
        run_flag.running = False


# List of MACs of sensors which will execute callback function
macs = ['F7:35:60:36:21:73']

while True:
    file_object = open('/ramdisk/RUUVI.prom.tmp', mode='w')
    # we run this 10 times (see run_flag) to make sure we get data from x devices in range
    run_flag.running = True
    counter = 10
    RuuviTagSensor.get_data(handle_data, macs, run_flag)
    while run_flag.running == True:
        time.sleep(1)
    file_object.flush()
    file_object.close()
    outLine = os.system('/bin/mv /ramdisk/RUUVI.prom.tmp /ramdisk/RUUVI.prom')
    tagset.clear()    
    time.sleep(sleepTime)

