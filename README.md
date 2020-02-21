# Haunted Desk Project

Automated desk that goes up and down on its own periodically.
The goal here is to collect data from several desks for analysis.

## Global architecture

![Haunted Desk Project Global Architecture](https://github.com/PervasiveWellbeingTech/HauntedDeskProject/blob/master/architecture.png)

An Arduino module is connected to each desk that we want to control. This module will make the desk to move and record the raw data of
these movements.  
A RaspberryPi is associated to several Arduino modules, in order to collect the raw data files and save them locally.  
All the RaspberryPi send their data to a Google Drive to bring everything together in one place.  

Workflow (we consider here one desk with its Arduino module and one RaspberryPi, to simplify):
- during the day, the Arduino module controls its desk
- at night, the RaspberryPi collects the file saved by the Arduino module during the day
- the RaspberryPi synchronizes its files with the Google Drive

See below for a detailed workflow.

## Detailed workflow

- From 6 a.m. to 9 p.m (this can be changed, see RaspberryPi and Arduino folders) the desk is in "working" mode. The desk will move up
or down every 30 minutes (can be changed too). If a user leaves his desk and comes back, the desk will not move for the next period (the
user moved from himself, we do not need to make him to move). During the day, the RaspberryPi is in "waiting" mode.
- At 9 p.m., the desk stops working and the Arduino module waits for a RaspberryPi message.
- The RaspberryPi sends "data" to the Arduino module. The Arduino module responds by sending the file name and the file size of the day
(we have one data file per day, with all movements of the desk in it). The RaspberryPi finally sends "ok" and the Arduino starts sending
the data file. It is basically a handshake. If the handshake fails, the RaspberryPi tries again all night long (until 6 a.m.). If the 
RaspberryPi has to manage several Arduino modules, it sends them a message ("data") one by one.
- At the end of the night (6 a.m.), the RaspberryPy syncs with the Google Drive and the desk switchs on "working" mode.

**Why do we need to record data during the day only ?**  
We can't save data (record desk movements) and send data (to the RaspberryPi) at the same time. So we chose to record data during the day
and transfer them during the night.

For more details on each part - Arduino, RaspberryPi, Google Drive sync - you can take a look at the README of the corresponding part.
