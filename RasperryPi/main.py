import time
import utils
import gdrive
import spidev
import datetime as dt
import RPi.GPIO as GPIO
from lib_nrf24.lib_nrf24 import NRF24
from record import Record


DEBUG = True      # set to False if you do not want to display debug messages
OK_RETRIES = 100  # number of times we send "ok" to arduino devices
DATA_PATH = "data/"
TIME_EXCEEDED_FLAG = utils.TIME_EXCEEDED_FLAG  # used when a transmission does not have time to end
SIZE_EXCEEDED_FLAG = utils.SIZE_EXCEEDED_FLAG  # used when arduino sends too much packets
DAY_IN_SECONDS = 24 * 3600

# data transmission between START_RECORD and STOP_RECORD
# syntax: timedelta(hours=12, minutes=12, seconds=12)
START_RECORD = dt.timedelta(hours=21).seconds
STOP_RECORD = dt.timedelta(hours=6).seconds

GPIO.setmode(GPIO.BCM)                 # set the gpio mode
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

desks, pipes = utils.get_desks_info()
record = None
recorded_desks = [0] * len(desks)


def is_time_in_interval(current_time, start_time, stop_time):
    """
    Two cases:
        - start and stop times are in the same day (ex: 14h to 22h)
        - stop time is in the day after (ex: 21h to 6h)
    """
    if start_time <= stop_time:
        return start_time <= current_time < stop_time
    else:
        return start_time <= current_time or current_time < stop_time


def is_new_day(recorded_desks):
    """
    recorded_desks = [1, 0, 0, 1] where each item represents a desk
    0: desk not recorded, 1: desk recorded
    We have a new day when no desk is recorded, so when the sum is 0.
    """
    return sum(recorded_desks) == 0
    

def are_all_desks_recorded(recorded_desks):
    """
    recorded_desks = [1, 0, 0, 1] where each item represents a desk
    0: desk not recorded, 1: desk recorded
    All desks are recorded when every item is set to 1,
    so when the sum is equal to the length.
    """
    return sum(recorded_desks) == len(recorded_desks)


def record_desk(radio, record, desk_name, recorded_desks):    
    """
    Full recording process (for one desk):
        - opens writing/reading pipes
        - sends "data" to the arduino device
        - waits for the arduino response
        - the arduino response is a file name and a file size
        - sends "ok" to tell the arduino device to start data transmission
    
    If the data transmission exceeds a certain time, the transmission is
    interrupted and an INTERRUPTED_FLAG is returned.    
    """
    
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
        if file_reception == TIME_EXCEEDED_FLAG:
            record.write_log("WARNING: Transmission interrupted (time exceeded).")
            return file_reception
        
        recorded_desks[i] = 1

        if file_reception == SIZE_EXCEEDED_FLAG:
            record.write_log("WARNING: Transmission interrupted (size exceeded).")
            record.write_log("INFO: Desk " + desk_name + " , success record.")
            return file_reception

        record.write_log("INFO: Desk " + desk_name + " , success record.")

    else:
        warning_message = file_info[0]
        record.write_log("WARNING: " + warning_message)
    print()


while True:
    time.sleep(3)
    current_time_in_seconds = utils.get_time_in_seconds()
    
    if is_time_in_interval(current_time_in_seconds, START_RECORD, STOP_RECORD):

        desks, pipes = utils.get_desks_info()
        
        if is_new_day(recorded_desks):
            record = Record(DATA_PATH)
            record.write_log("INFO: Record created")
        
        while is_time_in_interval(current_time_in_seconds, START_RECORD, STOP_RECORD):
            print("Transmission", current_time_in_seconds)
            current_time_in_seconds = utils.get_time_in_seconds()
            
            if not are_all_desks_recorded(recorded_desks):
                for i, pipe in enumerate(pipes):
                    desk_name = desks[i]
                    if not recorded_desks[i]:
                        record_result = record_desk(radio, record, desk_name, recorded_desks)
                        if record_result == TIME_EXCEEDED_FLAG:
                            break
                    else:
                        record.write_log("INFO: Desk " + desk_name + " already recorded.")
                            
        record.write_log("INFO: End of recording")              
        recorded_desks = [0] * len(desks)

        gdrive.sync()
        record.write_log("INFO: Google Drive synchronization done") 
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
