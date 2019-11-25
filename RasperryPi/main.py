import time
import utils
import spidev
import datetime as dt
import RPi.GPIO as GPIO
from lib_nrf24.lib_nrf24 import NRF24
from record import Record

DEBUG = True
DATA_PATH = "data/"
OK_RETRIES = 100

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


START_RECORD = dt.timedelta(hours=12).seconds
STOP_RECORD = dt.timedelta(hours=14, minutes=41).seconds
DAY_IN_SECONDS = 24 * 3600

record = None
recorded_desks = [0] * len(desks)


def is_time_in_interval(current_time, start_time, stop_time):
    if start_time <= stop_time:
        return start_time <= current_time < stop_time
    else:
        return start_time <= current_time or current_time < stop_time


def is_new_day(recorded_desks):
    return sum(recorded_desks) == 0
    

def are_all_desks_recorded(recorded_desks):
    return sum(recorded_desks) == len(recorded_desks)


def record_desk(radio, record, desk_name, recorded_desks):
    record.write_log("INFO: Desk " + desk_name)
                            
    print("Pipe", i)
    radio.openWritingPipe(pipe[0])
    radio.openReadingPipe(1, pipe[1])
    
    utils.send_message(radio, "data", DEBUG)
    file_info_received, file_info = utils.listen_file_info(radio, DEBUG)
    
    if file_info_received:
        file_name, file_size = file_info
        record.write_log("INFO: File info received ({} - {} bytes)".format(file_name, file_size))
        
        for _ in range(OK_RETRIES):
            utils.send_message(radio, "ok", DEBUG)
        
        file_reception = utils.real_timed_receive_file(radio, record.path + "/" + desk_name + "_" + file_name,
                                                       file_size, STOP_RECORD, START_RECORD, DEBUG)
        if file_reception == "interrupted":
            record.write_log("WARNING: Transmission interrupted.")
            return "interrupted"
        recorded_desks[i] = 1
        record.write_log("INFO: Desk " + desk_name + " , success record.")
    else:
        warning_message = file_info[0]
        record.write_log("WARNING: " + warning_message)
    print()


while True:
    time.sleep(3)
    current_time_in_seconds = utils.get_time_in_seconds()
    
    if is_time_in_interval(current_time_in_seconds, START_RECORD, STOP_RECORD):
        
        if is_new_day(recorded_desks):
            record = Record(DATA_PATH)
            record.write_log("INFO: Record created")
        
        while is_time_in_interval(current_time_in_seconds, START_RECORD, STOP_RECORD):
            print("Transmission", current_time_in_seconds)
            current_time_in_seconds = utils.get_time_in_seconds()
            
            if not are_all_desks_recorded(recorded_desks):
                for i, pipe in enumerate(pipes):
                    if not recorded_desks[i]:
                        desk_name = desks[i]
                        record_result = record_desk(radio, record, desk_name, recorded_desks)
                        if record_result and record_result == "interrupted":
                            break
                    else:
                        record.write_log("INFO: Desk " + desk_name + " already recorded.")
                            
        record.write_log("INFO: End of recording")                
        recorded_desks = [0] * len(desks)           
    else:
        print("Wait", current_time_in_seconds)


# ------------ 1 minute day simulation (30s day, 30s night)
"""
START_RECORD = 20
STOP_RECORD = 50
record = None  
counter = 0

recorded_desks = [0] * len(desks)

while True:
    current_time = dt.datetime.now()
    time.sleep(3)
    
    if current_time.second >= START_RECORD and current_time.second < STOP_RECORD:
        
        print("Go", current_time.second)
        
        if sum(recorded_desks) == 0:
            print("New day")
            counter += 1  # simulates a new day
            record = Record(DATA_PATH + str(counter) + "_")
        
        record.write_log("INFO: Record created")
        
        while dt.datetime.now().second < STOP_RECORD:
            if sum(recorded_desks) != len(recorded_desks):
                print("In while")
                for i, pipe in enumerate(pipes):
                    if not recorded_desks[i]:
                        record.write_log("INFO: Desk " + desks[i])
                            
                        print("Pipe", i, "- day:", counter)
                        radio.openWritingPipe(pipe[0])
                        radio.openReadingPipe(1, pipe[1])
                        
                        utils.send_message(radio, "data", DEBUG)

                        file_info_received, file_info = utils.listen_file_info(radio, DEBUG)
                        
                        if file_info_received:
                            file_name, file_size = file_info
                            
                            record.write_log("INFO: File info received ({} - {} bytes)".format(file_name, file_size))
                            
                            for _ in range(100):
                                utils.send_message(radio, "ok", DEBUG)
                            file_reception = utils.timed_receive_file(radio, record.path + "/" + desks[i] + "_" + file_name, file_size, STOP_RECORD, DEBUG)
                            if file_reception == "interrupted":
                                record.write_log("WARNING: Transmission interrupted.")
                                break
                            recorded_desks[i] = 1
                            record.write_log("INFO: Desk " + desks[i] + " , success record.")
                        else:
                            warning_message = file_info[0]
                            record.write_log("WARNING: " + warning_message)
                        print()
                    else:
                        record.write_log("INFO: Desk " + desks[i] + " already recorded.")
                            
        record.write_log("INFO: End of recording")                
        recorded_desks = [0] * len(desks)           
    else:
        print("Wait", current_time.second)
"""