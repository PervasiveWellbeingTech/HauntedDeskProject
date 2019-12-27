# Haunted Desk Project - Arduino part

For the electronic setup you can look here: https://github.com/PervasiveWellbeingTech/Ultraslow-StandingDesk/tree/master/New_Desk_Summer_2019

All the code to manage the desk and the data transmission to the RaspberryPi is contained in one file.  


## Code upload

When you modify the code, you have to upload it to the Arduino card to update the code contained in it.

Important points to check before uploading:

### Time
The time of the Arduino card will be synchronized with the time of the computer used to upload the code. Make sure that this time is the same than the RaspberryPi one.

### Desk ID
Make sure that the desk ID and the pipes ID are correct (particularly when you want to add a new desk).  
```
const uint64_t pipes[2] = {0x1DECAF0001LL, 0x2DECAF0001LL}; // receiver and sender
String deskId = "0001";
```

Details for a pipe ID (0x1DECAF0001LL):
- **0x** because it is an hexadecimal value
- **1** for the receiver pipe (**2** for the sender one)
- **DECAF** for no particular reason (we needed a 10 bits sized ID, so this is to fill the gap)
- **0001** desk ID
- **LL** C++ long-long suffix


## Configuration changes

### Recording hours

These hours are used to send data to the RaspberryPi.
Initially, it is from 9 p.m. to 6 a.m. the next day. If you want to change that, you can modify this part of the code:
```
unsigned long RECORD_START_TIME = 75600;
unsigned long RECORD_STOP_TIME = 21600;
```
*see the code for more details on how to calculate these values*

### Retries

When the Arduino card send a packet to the RaspberryPi, it waits for an acknowledgement packet.  
If it does not receive this acknowledgement, it sends the packet again. It will retry N times before stopping.  
This number of retries is defined in the function `bool rf24SendR(String content, int retries)`.

If there is a bad connection between the Arduino card and the RaspberryPi, you can try to increase the number of retries to reduce the number of lost packets.
