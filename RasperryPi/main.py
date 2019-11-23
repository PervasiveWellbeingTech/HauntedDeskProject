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


START_RECORD = 75600  # 21 hours in seconds
STOP_RECORD = 21600   # 6 hours in seconds
record = None

recorded_desk = [0] * len(desks)

while True:
    current_time = datetime.now()
    time.sleep(3)
    
    """
  DateTime currentDateTime = rtc.now();
  unsigned long currentSecond = currentDateTime.second();
  unsigned long currentMinute = currentDateTime.minute();
  unsigned long currentHour = currentDateTime.hour();

  unsigned long currentTimeInSeconds = currentSecond + 60 * currentMinute + 3600 * currentHour;
  
  //if ((currentHour >= 21) || (currentHour < 6)) {
  if ((currentTimeInSeconds >= 75600) || (currentTimeInSeconds < 21600)) {
    unsigned long maxTime = 0;

    if (currentTimeInSeconds >= 75600) {
      maxTime += 86400 - currentTimeInSeconds + 21600;
    }
    else if (currentTimeInSeconds < 21600) {
      maxTime += 21600 - currentTimeInSeconds;
    }
    """
    
    current_time_in_seconds = utils.get_time_in_seconds()
    
    if current_time_in_seconds >= START_RECORD or current_time_in_seconds < STOP_RECORD:
        
        if sum(recorded_desk) == 0:
            print("New day")
            record = Record(DATA_PATH)
        
        if LOG:
            record.write_log("INFO: Record created")
        
        while current_time_in_seconds >= START_RECORD or current_time_in_seconds < STOP_RECORD:
            print(current_time_in_seconds >= START_RECORD or current_time_in_seconds < STOP_RECORD)
            print(current_time_in_seconds)
            current_time_in_seconds = utils.get_time_in_seconds()
            
            if sum(recorded_desk) != len(recorded_desk):
                print("In while")
                for i, pipe in enumerate(pipes):
                    if not recorded_desk[i]:
                        if LOG:
                            record.write_log("INFO: Desk " + desks[i])
                            
                        print("Pipe", i)
                        radio.openWritingPipe(pipe[0])
                        radio.openReadingPipe(1, pipe[1])
                        
                        utils.send_message(radio, "data", DEBUG)

                        file_info_received, file_info = utils.listen_file_info(radio, DEBUG)
                        
                        if file_info_received:
                            file_name, file_size = file_info
                            
                            if LOG:
                                record.write_log("INFO: File info received ({} - {} bytes)".format(file_name, file_size))
                            
                            for _ in range(100):
                                utils.send_message(radio, "ok", DEBUG)
                                  
                            temp_time_in_seconds = utils.get_time_in_seconds()
                            
                            temp_stop_record = 0
                            if temp_time_in_seconds > START_RECORD:
                                temp_stop_record = 86400 - temp_time_in_seconds + 21600;
                            elif temp_time_in_seconds < STOP_RECORD:
                                temp_stop_record = 21600 - temp_time_in_seconds
                            
                            file_reception = utils.real_timed_receive_file(radio, record.path + "/" + desks[i] + "_" + file_name, file_size, temp_stop_record, DEBUG)
                            if file_reception == "interrupted":
                                if LOG:
                                    record.write_log("WARNING: Transmission interrupted.")
                                break
                            recorded_desk[i] = 1
                            if LOG:
                                record.write_log("INFO: Desk " + desks[i] + " , success record.")
                        else:
                            warning_message = file_info[0]
                            if LOG:
                                record.write_log("WARNING: " + warning_message)
                        print()
                    else:
                        if LOG:
                            record.write_log("INFO: Desk " + desks[i] + " already recorded.")
                            
        if LOG:
            record.write_log("INFO: End of recording")                
        recorded_desk = [0] * len(desks)           
    else:
        print("Wait", current_time_in_seconds)

# ------------ 1 minute day simulation (30s day, 30s night)
"""
START_RECORD = 20
STOP_RECORD = 50
record = None  
counter = 0

recorded_desk = [0] * len(desks)

while True:
    current_time = datetime.now()
    time.sleep(3)
    
    if current_time.second >= START_RECORD and current_time.second < STOP_RECORD:
        
        print("Go", current_time.second)
        
        if sum(recorded_desk) == 0:
            print("New day")
            counter += 1  # simulates a new day
            record = Record(DATA_PATH + str(counter) + "_")
        
        if LOG:
            record.write_log("INFO: Record created")
        
        while datetime.now().second < STOP_RECORD:
            if sum(recorded_desk) != len(recorded_desk):
                print("In while")
                for i, pipe in enumerate(pipes):
                    if not recorded_desk[i]:
                        if LOG:
                            record.write_log("INFO: Desk " + desks[i])
                            
                        print("Pipe", i, "- day:", counter)
                        radio.openWritingPipe(pipe[0])
                        radio.openReadingPipe(1, pipe[1])
                        
                        utils.send_message(radio, "data", DEBUG)

                        file_info_received, file_info = utils.listen_file_info(radio, DEBUG)
                        
                        if file_info_received:
                            file_name, file_size = file_info
                            
                            if LOG:
                                record.write_log("INFO: File info received ({} - {} bytes)".format(file_name, file_size))
                            
                            for _ in range(100):
                                utils.send_message(radio, "ok", DEBUG)
                            file_reception = utils.timed_receive_file(radio, record.path + "/" + desks[i] + "_" + file_name, file_size, STOP_RECORD, DEBUG)
                            if file_reception == "interrupted":
                                if LOG:
                                    record.write_log("WARNING: Transmission interrupted.")
                                break
                            recorded_desk[i] = 1
                            if LOG:
                                record.write_log("INFO: Desk " + desks[i] + " , success record.")
                        else:
                            warning_message = file_info[0]
                            if LOG:
                                record.write_log("WARNING: " + warning_message)
                        print()
                    else:
                        if LOG:
                            record.write_log("INFO: Desk " + desks[i] + " already recorded.")
                            
        if LOG:
            record.write_log("INFO: End of recording")                
        recorded_desk = [0] * len(desks)           
    else:
        print("Wait", current_time.second)
"""