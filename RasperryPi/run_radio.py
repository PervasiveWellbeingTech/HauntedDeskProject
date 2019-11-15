import RPi.GPIO as GPIO
import time
import spidev
from lib_nrf24.lib_nrf24 import NRF24

DEBUG = True
EOF_LINE = [101, 111, 102, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]  # e, o, f, 0, 0, 0...

GPIO.setmode(GPIO.BCM)                 # set the gpio mode

# set the pipe address. this address should be entered on the receiver also
pipes = [[[0x1D, 0xEC, 0xAF, 0x00, 0x00], [0x2D, 0xEC, 0xAF, 0x00, 0x00]],
         [[0x1D, 0xEC, 0xAF, 0x00, 0x01], [0x2D, 0xEC, 0xAF, 0x00, 0x01]]]

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


def send_message(message, debug=False):    
    result = radio.write(message)
    print("Result of sending:", result)
    if debug:
        print("Message sent: {}".format(message))


def listen_message_light(time_out=2, debug=False):
    """
    Waits for a certain time (time_out).
    If a message is received, the message is read and store in a list.
    Else, returns an empty list.
    """
    start = time.time()
    while not radio.available():
        time.sleep(0.01)
        
        if time.time() - start > time_out:
            if debug:
                print("WARNING: Time out - Stop listening.")
                return []
        
    message_received = []
    radio.read(message_received, radio.getDynamicPayloadSize())
    
    if debug:
        print("Message received.")
    
    return message_received


def listen_message(time_out=2, debug=False):
    """
    Same as listen_message_light but with a start/stop listening
    at the begining/end of the function
    """
    if debug:
        print("Start listening.")
        
    radio.startListening()
    message_received = listen_message_light(time_out, debug)
    radio.stopListening()
    
    if debug:
        print("Stop listening.")
        
    return message_received    


def clean_message(message, debug=False):
    """
    message -> list
    Removes the last character of the message.
    Converts the message in ASCII.
    Returns the message as a string.
    """
    if message:
        message = "".join(map(chr, message))
        if debug:
            print("Message cleaned:", message)
        return message
    return ""


def listen_file_info():
    """
    TODO: simplify
    Listens for two piece of information:
        - a file name
        - a file size
    If both pieces of information are received,
    returns a True flag and the information.
    Else, returns a False flag and empty strings.
    """
    file_name_message = listen_message(debug=DEBUG)
    if file_name_message:
        file_size_message = listen_message(debug=DEBUG)
        if file_size_message:
            file_name = clean_message(file_name_message, DEBUG).rstrip(chr(0))
            file_size = clean_message(file_size_message, DEBUG).rstrip(chr(0))
            return True, (file_name, file_size)
    return False, ("", "")


def receive_file(file_name, file_size, debug=False):
    if debug:
        print("Start receiving file {} ({} bytes)".format(file_name, file_size))
    
    radio.startListening()
    counter = 0
    
    with open(file_name, "wb") as file:
        line = listen_message_light(debug=DEBUG)
        while line and line != EOF_LINE:
            counter += 32
            print(counter, file_size)
            file.write(bytes(line))
            line = listen_message_light()
    
    radio.stopListening()
    
    if debug:
        print("File received.")
        

counter = 0

while True:
    print()
    counter += 1
    
    for i, pipe in enumerate(pipes):
        print("Pipe", i, "- counter:", counter)
        radio.openWritingPipe(pipe[0])
        radio.openReadingPipe(1, pipe[1])
        
        send_message("data", DEBUG)

        file_info_received, file_info = listen_file_info()
        
        if file_info_received:
            file_name, file_size = file_info
            for _ in range(100):
                send_message("ok", DEBUG)
            receive_file("data/" + str(i) + "_" + file_name, file_size, DEBUG)
        
        print()

