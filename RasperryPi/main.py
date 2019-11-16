import time
import utils
import spidev
import RPi.GPIO as GPIO
from lib_nrf24.lib_nrf24 import NRF24
from datetime import datetime
from record import Record

DEBUG = True
LOG = True
DATA_PATH = "data/"
EOF_LINE = [101, 111, 102, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]  # e, o, f, 0, 0, 0...

GPIO.setmode(GPIO.BCM)                 # set the gpio mode

# set the pipe address. this address should be entered on the receiver also
pipes = [[[0x1D, 0xEC, 0xAF, 0x00, 0x00], [0x2D, 0xEC, 0xAF, 0x00, 0x00]],
         [[0x1D, 0xEC, 0xAF, 0x00, 0x01], [0x2D, 0xEC, 0xAF, 0x00, 0x01]]]
desks = ["desk_0", "desk_1"]           # temporary names

radio = NRF24(GPIO, spidev.SpiDev())   # use the gpio pins
radio.begin(0, 25)                     # start the radio and set the ce,csn pin ce= GPIO08, csn= GPIO25
radio.setPayloadSize(32)               # set the payload size as 32 bytes
radio.setChannel(0x76)                 # set the channel as 76 hex
radio.setDataRate(NRF24.BR_1MBPS)      # set radio data rate
radio.setPALevel(NRF24.PA_MAX)         # set PA level
radio.setAutoAck(True)                 # set acknowledgement as true
radio.setRetries(0, 125)
##radio.enableDynamicPayloads()
radio.enableAckPayload()


# ------------ WIP

"""
LIMIT = 30
recorded = False
counter = 0

while True:
    current_time = datetime.now()
    time.sleep(3)
    
    if current_time.second >= LIMIT and not recorded:
        recorded = True
        print()
        counter += 1
        record = Record(DATA_PATH + str(counter) + "_")
        
        if LOG:
            record.write_log("Record created")
        
        for i, pipe in enumerate(pipes):
            if LOG:
                record.write_log("Pipe " + str(i))
                
            print("Pipe", i, "- counter:", counter)
            radio.openWritingPipe(pipe[0])
            radio.openReadingPipe(1, pipe[1])
            
            utils.send_message(radio, "data", DEBUG)

            file_info_received, file_info = utils.listen_file_info(radio, DEBUG)
            
            if file_info_received:
                file_name, file_size = file_info
                
                if LOG:
                    record.write_log(file_name)
                    record.write_log(file_size + " bytes")
                
                for _ in range(100):
                    utils.send_message(radio, "ok", DEBUG)
                utils.receive_file(radio, DATA_PATH + str(i) + "_" + file_name, file_size, DEBUG)
            else:
                if LOG:
                    record.write_log("WARNING: File info not received")
            
            if LOG:
                record.write_log("End of recording")
            print()
    elif current_time.second < LIMIT:
        print("Wait", current_time.second)
        recorded = False
    else:
        print("Wait", current_time.second)

"""

# ------------ END OF WIP

counter = 0

#while True:
for _ in range(1):
    print()
    counter += 1
    record = Record(DATA_PATH)
    
    if LOG:
        record.write_log("Record created")
    
    for i, pipe in enumerate(pipes):
        if LOG:
            record.write_log("Pipe " + str(i))
            
        print("Pipe", i, "- counter:", counter)
        radio.openWritingPipe(pipe[0])
        radio.openReadingPipe(1, pipe[1])
        
        utils.send_message(radio, "data", DEBUG)

        file_info_received, file_info = utils.listen_file_info(radio, DEBUG)
        
        if file_info_received:
            file_name, file_size = file_info
            
            if LOG:
                record.write_log(file_name)
                record.write_log(file_size + " bytes")
            
            for _ in range(100):
                utils.send_message(radio, "ok", DEBUG)
            utils.receive_file(radio, DATA_PATH + str(i) + "_" + file_name, file_size, DEBUG)
        else:
            if LOG:
                record.write_log("WARNING: File info not received")
        
        if LOG:
            record.write_log("End of recording")
        print()
