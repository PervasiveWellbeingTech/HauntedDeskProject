import RPi.GPIO as GPIO
import time
import spidev
from lib_nrf24.lib_nrf24 import NRF24  
GPIO.setmode(GPIO.BCM)                 # set the gpio mode

# set the pipe address. this address should be entered on the receiver also
pipes = [[[0xE0, 0xE0, 0xF1, 0xF1, 0xE0], [0xF1, 0xF1, 0xF0, 0xF0, 0xE0]]]

radio = NRF24(GPIO, spidev.SpiDev())   # use the gpio pins
radio.begin(0, 25)                     # start the radio and set the ce,csn pin ce= GPIO08, csn= GPIO25
radio.setPayloadSize(32)               # set the payload size as 32 bytes
radio.setChannel(0x76)                 # set the channel as 76 hex
radio.setDataRate(NRF24.BR_1MBPS)      # set radio data rate
radio.setPALevel(NRF24.PA_MAX)         # set PA level
radio.setAutoAck(True)                 # set acknowledgement as true
radio.setRetries(6,15)
radio.enableDynamicPayloads()
radio.enableAckPayload()


def send_message(message, debug=False):
    radio.write(message)                       # just write the message to radio
    
    if debug:
        print("Message sent: {}".format(message))  # print a message after succesfull send


def listen_message():
    pass


counter = 0

while True:
    counter += 1
    
    for i, pipe in enumerate(pipes):
        print("Pipe", i, "-counter:", counter)
        radio.openWritingPipe(pipe[0])             # open the defined pipe for writing
        radio.openReadingPipe(1, pipe[1])
        
        send_message("abcdefghijklmno123456pqrstuvwxyz", debug=True)
        
        radio.startListening()        # Start listening the radio
        
        start = time.time()
        while not radio.available():
            time.sleep(0.01)
            
            if time.time() - start > 2:
                print("Timed out.")
                break
            
        message_received = []
        radio.read(message_received, radio.getDynamicPayloadSize())
        radio.stopListening()     # close radio  
        print("End of the transmission.")
        
        if message_received:
            message_received.pop()
            message_received = "".join(map(chr, message_received))
            print("Message received:", message_received)
            
            if message_received == "Hello World":
                send_message("ABCDEFGHIJKLMNO123456PQRSTUVWXYZ")
            
        else:
            print("Nothing received.")

