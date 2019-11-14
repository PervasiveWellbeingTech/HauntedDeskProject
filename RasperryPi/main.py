import RPi.GPIO as GPIO  # import gpio
import time      #import time library
import spidev
from lib_nrf24.lib_nrf24 import NRF24   #import NRF24 library
GPIO.setmode(GPIO.BCM)       # set the gpio mode
  # set the pipe address. this address shoeld be entered on the receiver alo
pipes = [[0xE0, 0xE0, 0xF1, 0xF1, 0xE0], [0xF1, 0xF1, 0xF0, 0xF0, 0xE0]]
radio = NRF24(GPIO, spidev.SpiDev())   # use the gpio pins
radio.begin(0, 25)   # start the radio and set the ce,csn pin ce= GPIO08, csn= GPIO25
radio.setPayloadSize(32)  #set the payload size as 32 bytes
radio.setChannel(0x76) # set the channel as 76 hex
radio.setDataRate(NRF24.BR_1MBPS)    # set radio data rate
radio.setPALevel(NRF24.PA_MAX)  # set PA level
radio.setAutoAck(True)       # set acknowledgement as true 
radio.enableDynamicPayloads()
radio.enableAckPayload()
#radio.openWritingPipe(pipes[1])     # open the defined pipe for writing

#radio.printDetails()      # print basic detals of radio
##sendMessage = list("Hi..Arduino UNO")  #the message to be sent
##while len(sendMessage) < 32:    
##    sendMessage.append("N")

#print(sendMessage)

counter = 0
pipe = True

while True:
    start = time.time()      #start the time for checking delivery time
    
    radio.openWritingPipe(pipes[pipe])     # open the defined pipe for writing
    pipe = not pipe
    sendMessage = str(counter).zfill(32)
    radio.write(sendMessage)   # just write the message to radio
    print("Message sent: {}".format(sendMessage))  # print a message after succesfull send
    
    counter += 1
    time.sleep(0.5)
    
    radio.startListening()        # Start listening the radio
    
    while not radio.available(0):
        time.sleep(1/100)
        if time.time() - start > 3:
            print("Timed out.")  # print errror message if radio disconnected or not functioning anymore
            break
    radio.stopListening()     # close radio
    time.sleep(0.5)  # give delay of 3 seconds
    