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
Folder used to store desk data.


## Details
