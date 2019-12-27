# Haunted Desk Project - Google Drive sync

To setup the Google Drive synchronization on a RaspberryPi, follow this tutorial: https://medium.com/@artur.klauser/mounting-google-drive-on-raspberry-pi-f5002c7095c2

The synchronization will be launched automatically every morning (see the RaspberryPi part to change that).  
If you want to do it manually, you can use two scripts:
- **connect_to_gdrive.sh** to connect the RaspberryPi to the drive
- **sync_with_gdrive.sh** to synchronize the files (`--delete` parameter is used to removed Drive files that are not on the RaspberryPi, this was used for testing purpose, but in "production" it is better to remove this parameter, to prevent data loss)

*Note: you can launch both scripts running `gdrive.py` contained in the RaspberryPi folder.*
