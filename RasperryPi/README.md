# Haunted Desk Project - RaspberryPi part

Each RaspberryPi uses essentially Python code.


## Quick tour

- **main.py**  
Contains the main process.  
It uses the **lib_nrf24** library to manage interactions with the Arduino module.

- **record.py**  
Python class used to create and write in a log file. During the night, the RaspberryPi saves what happened (successfull data transfer,
fail due to a lack of time, ...).

- **utils.py**  
Contains some functions used in the **main.py** file.

- **gdrive.py**  
Calls scripts to launch the Google Drive sync. See the GoogleDrive folder for more details.

- **desks_register.txt**  
Used to configure new desks to be managed by the RaspberryPi.

- **data**  
Folder used to store desks data.


## Details

### main.py

To change the time of data recording (from the Arduino), change this:  
```
START_RECORD = dt.timedelta(hours=21).seconds
STOP_RECORD = dt.timedelta(hours=6).seconds
```
Here the RaspberryPi gathers data from Arduino modules during the night (from 21 p.m. to 6 a.m. the next day).
You can change hours, but also minutes and seconds like this `dt.timedelta(hours=10, minutes=10, seconds=10)`.

Recap of the handshake between a RaspberryPi and an Arduino module:
- RaspberryPi sends "data" to Arduino
- Arduino responds with data file name and file size
- RaspberryPi sends "ok" to Arduino
- Arduino starts the transfer

If the Arduino does not receive one message, the handshake needs to start from the beginning again.  
The RaspberryPi tries to establish a connection with an Arduino module ("data" message) every 3 seconds (`time.sleep(3)` in the while loop) and sends "ok" 100 times (`OK_RETRIES = 100`) before considering a loss of connection.  
So if the connection between a RaspberryPi and an Arduino module seems very bad, you can adjust these parameters to increase the number
of retries.

### utils.py

To stop listening at an Arduino module when the file transmission is completed, the Arduino sends a "EOF" (End Of File) message to the
RaspberryPi. This EOF message is defined on top of the **utils.py** file.  

But there are actually 3 ways to end a transmission between the RaspberryPi and the Arduino module:
- EOF message (everything is fine)
- time exceeded: if the transmission is too long and continues after the end of the night, we have to stop it
- size exceeded: if the Arduino module sends to much packets (according to the given file size), we have to stop the transmission too (this is a bug on the Arduino side that has not been fixed yet)

*Note: When the Arduino module sends a packet to the RaspberryPi, it receives back an acknowledgement message. So when we stop the transmission on the RaspberryPi side, the Arduino module does not receive acknowledgement messages anymore and stops its transmission too.*

### desks_register.txt

This file is used to list all the desks managed by the RaspberryPi.  
It contains something like:
```
desk_0
1DECAF0000
2DECAF0000
desk_1
1DECAF0001
2DECAF0001
```

Here is two desks, the format for each desk is:
- line 1: desk name
- line 2: writing pipe ID (1DECAF0000: **1** for writing pipe, **DECAF** for no particular reason, **0000** desk id which is arbitrary)
- line 3: same as line 2 for reading pipe ID (leading **2** for reading pipe, instead of 1)

Writing and reading pipes ID will are specified in the Arduino code too. It must be the same in both part, so if the RaspberryPi and the Arduino module can't communicate it may come from a typo in one pipe ID.

### data

This folder contains all retrieved data. The structure is:
```
__ day 1 (YYMMDD)
 |__ desk 1 (desk_name_YYMMDD.txt)
 |__ desk 2
 |__ ...
 |__ desk n
__ day 2
...
__ day n
```
