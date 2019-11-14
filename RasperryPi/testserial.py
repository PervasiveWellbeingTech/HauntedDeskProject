import serial
import time
import serial_process
from datetime import datetime,timedelta 

USB_PORTS = ["1"]
PERIOD = 5  # seconds
serials = []

for usb_port in USB_PORTS:
    serials.append((usb_port, serial.Serial("/dev/ttyUSB" + usb_port, 9600)))

##d = datetime(2019, 10, 30, 00, 54)

current_date = datetime.now()
period = timedelta(seconds=PERIOD)
next_date = current_date + period


def serials_reader(serials):
    print("serials_reader called")
    
    for usb_port, ser in serials:
        if (ser.inWaiting() > 0):
            # line = ser.readline()
            print("Port {}: Waiting data.".format(usb_port))
        else:
            print("Port {}: ERROR: Can not read.".format(usb_port))


def serials_manager(serials):
    print("serials_manager called")
    
    for usb_port, ser in serials:
        serial_process.run(usb_port, ser)


while True:
    current_date = datetime.now()
    serials_reader(serials)
        
    if current_date > next_date:
        serials_manager(serials)
        next_date = current_date + period
        
    time.sleep(1)
